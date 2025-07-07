from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse, JSONResponse
import numpy as np
from PIL import Image
import io
import os
import torch
import base64
from pathlib import Path

from iopaint.schema import InpaintRequest, HDStrategy, LDMSampler, SDSampler, ApiConfig, Device, RealESRGANModel, InteractiveSegModel, RemoveBGModel
from iopaint.model_manager import ModelManager
from iopaint.helper import load_img, numpy_to_bytes, pil_to_bytes
from pydantic import BaseModel
from src.utils.response import Response
from src.utils import get_inpainting_logger

# 获取应用日志器
logger = get_inpainting_logger()

# 定义请求模型
class InpaintingRequest(BaseModel):
    image_base64: str
    mask_base64: str
    model_name: str = "lama"  # 默认使用lama模型
    prompt: str = ""
    negative_prompt: str = ""
    sd_steps: int = 50
    sd_sampler: SDSampler = SDSampler.uni_pc
    sd_strength: float = 1.0
    # 添加可选的高级参数，允许客户端覆盖默认值
    hd_strategy: str = "ORIGINAL"  # 可选：ORIGINAL、CROP、RESIZE
    match_histograms: bool = True  # 启用直方图匹配以保持颜色一致性
    crop_margin_scale: float = 3.0  # 裁剪边缘比例

# 简单的内存缓存，用于存储模型
# 在生产环境中，您可能需要更复杂的模型管理策略
model_manager = None

def get_model_manager():
    global model_manager
    if model_manager is None:
        # 创建一个默认的模型存储路径
        model_dir = os.path.join(os.path.expanduser("~"), ".cache", "iopaint")
        os.makedirs(model_dir, exist_ok=True)

        print(f"Initializing model manager with model dir: {model_dir}")
        logger.info(f"初始化模型管理器，模型目录: {model_dir}")

        # 检查可用的模型
        available_models = []
        preferred_model = "lama"  # 首选lama模型
        
        try:
            # 尝试获取可用模型列表
            from iopaint.model_manager import ModelManager as MM
            available_models = MM.available_models()
            logger.info(f"可用的模型列表: {available_models}")
        except Exception as e:
            logger.warning(f"获取可用模型列表失败: {str(e)}")
            # 默认假设cv2可用
            available_models = ["cv2"]
        
        # 如果首选模型不可用，则使用备用模型
        if preferred_model not in available_models and len(available_models) > 0:
            preferred_model = available_models[0]
            logger.warning(f"首选模型 'lama' 不可用，降级使用: {preferred_model}")
        
        # 优化配置参数，根据官方推荐设置
        config = ApiConfig(
            host="127.0.0.1",
            port=8080,
            inbrowser=False,
            model=preferred_model,  # 使用可用的模型
            no_half=False,  # 使用半精度浮点数以节省内存
            low_mem=False,  # 对于大多数现代服务器，可以设为False以获得更好性能
            cpu_offload=True,  # 启用CPU卸载以优化内存使用
            disable_nsfw_checker=True,  # 禁用NSFW检查器以提高性能
            local_files_only=False,
            cpu_textencoder=False,
            device=Device.cpu,  # 使用CPU，如果有GPU可以改为Device.cuda
            input=None,
            mask_dir=None,
            output_dir=None,
            quality=95,  # 设置较高的质量
            enable_interactive_seg=False,
            interactive_seg_model=InteractiveSegModel.vit_b,
            interactive_seg_device=Device.cpu,
            enable_remove_bg=False,
            remove_bg_device=Device.cpu,
            remove_bg_model=RemoveBGModel.briaai_rmbg_1_4,
            enable_anime_seg=False,
            enable_realesrgan=False,
            realesrgan_device=Device.cpu,
            realesrgan_model=RealESRGANModel.realesr_general_x4v3,
            enable_gfpgan=False,
            gfpgan_device=Device.cpu,
            enable_restoreformer=False,
            restoreformer_device=Device.cpu,
        )

        try:
            logger.info(f"尝试初始化模型管理器，使用模型: {config.model}")
            model_manager = ModelManager(
                name=config.model,
                device=torch.device(config.device),
                no_half=config.no_half,
                cpu_offload=config.cpu_offload,
                disable_nsfw_checker=config.disable_nsfw_checker,
                local_files_only=config.local_files_only,
                cpu_textencoder=config.cpu_textencoder,
                model_dir=Path(model_dir),
                enable_controlnet=False,
                controlnet_method=None,
            )
            logger.info(f"模型管理器初始化成功，当前模型: {model_manager.name}")
        except Exception as e:
            logger.error(f"模型管理器初始化失败: {str(e)}", exc_info=True)
            
            # 如果初始化失败，尝试使用cv2模型
            if config.model != "cv2" and "cv2" in available_models:
                logger.info("尝试使用cv2模型作为备选")
                config.model = "cv2"
                try:
                    model_manager = ModelManager(
                        name=config.model,
                        device=torch.device(config.device),
                        no_half=config.no_half,
                        cpu_offload=config.cpu_offload,
                        disable_nsfw_checker=config.disable_nsfw_checker,
                        local_files_only=config.local_files_only,
                        cpu_textencoder=config.cpu_textencoder,
                        model_dir=Path(model_dir),
                        enable_controlnet=False,
                        controlnet_method=None,
                    )
                    logger.info(f"成功使用备选模型初始化: {model_manager.name}")
                except Exception as backup_e:
                    logger.error(f"备选模型初始化也失败: {str(backup_e)}", exc_info=True)
                    raise
            else:
                raise
            
    return model_manager

router = APIRouter()

def decode_base64_to_bytes(base64_str: str) -> bytes:
    """将base64字符串解码为字节"""
    # 移除可能存在的base64前缀（如data:image/png;base64,）
    if ',' in base64_str:
        base64_str = base64_str.split(',', 1)[1]
    return base64.b64decode(base64_str)

@router.post("/inpaint", tags=["inpainting"])
async def inpaint(
    request: InpaintingRequest,
    manager: ModelManager = Depends(get_model_manager)
):
    """
    接收原始图片和蒙版的base64编码，使用iopaint进行图像修复。
    
    - **image_base64**: 原始图片的base64编码
    - **mask_base64**: 蒙版图片的base64编码，白色部分为修复区域
    """
    logger.info(f"开始处理图像修复请求，使用模型: {request.model_name}")
    try:
        # 检查请求的模型是否可用，如果不可用则使用当前已加载的模型
        available_models = []
        try:
            # 尝试获取可用模型列表
            from iopaint.model_manager import ModelManager as MM
            available_models = MM.available_models()
            logger.info(f"可用的模型列表: {available_models}")
        except Exception as e:
            logger.warning(f"获取可用模型列表失败: {str(e)}")
            available_models = ["cv2"]  # 默认只有cv2可用
            
        # 如果请求的模型不可用，使用当前已加载的模型
        if request.model_name not in available_models:
            logger.warning(f"请求的模型 {request.model_name} 不可用，将使用当前模型: {manager.name}")
            # 不进行模型切换
        elif manager.name != request.model_name:
            # 如果请求的模型可用且不是当前模型，则尝试切换
            logger.info(f"切换模型从 {manager.name} 到 {request.model_name}")
            try:
                manager.switch(request.model_name)
            except Exception as e:
                logger.error(f"模型切换失败: {str(e)}")
                # 模型切换失败，继续使用当前模型
                
        # 解码base64字符串为字节
        logger.debug("解码base64字符串")
        image_bytes = decode_base64_to_bytes(request.image_base64)
        mask_bytes = decode_base64_to_bytes(request.mask_base64)

        # 将字节转换为 numpy 数组
        logger.debug("转换图像到numpy数组")
        image_np, _ = load_img(image_bytes)
        mask_np, _ = load_img(mask_bytes, gray=True)
        
        # 构造 InpaintRequest，优化参数设置
        logger.debug(f"创建修复请求，提示词: {request.prompt}, 步数: {request.sd_steps}")
        
        # 确定HDStrategy枚举值
        hd_strategy_map = {
            "ORIGINAL": HDStrategy.ORIGINAL,
            "CROP": HDStrategy.CROP,
            "RESIZE": HDStrategy.RESIZE
        }
        hd_strategy = hd_strategy_map.get(request.hd_strategy.upper(), HDStrategy.ORIGINAL)
        
        inpaint_request = InpaintRequest(
            hd_strategy=hd_strategy,  # 使用客户端指定的策略
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            sd_steps=request.sd_steps,
            sd_sampler=request.sd_sampler,
            sd_strength=request.sd_strength,
            match_histograms=request.match_histograms,  # 启用直方图匹配以保持颜色一致性
            crop_margin_scale=request.crop_margin_scale,  # 裁剪边缘比例
        )

        # 执行修复
        logger.info("开始执行图像修复")
        result_np = manager(image_np, mask_np, inpaint_request)

        # 将结果转换为字节流
        logger.debug("转换结果到字节流")
        result_bytes = numpy_to_bytes(result_np, "png")
        
        # 将结果转换为base64编码
        result_base64 = base64.b64encode(result_bytes).decode('utf-8')
        
        logger.info("图像修复成功完成")
        # 使用统一的响应格式返回结果
        return Response.success({"image_base64": result_base64}, "图像修复成功")

    except Exception as e:
        logger.error(f"图像修复失败: {str(e)}", exc_info=True)
        return Response.error(str(e)) 