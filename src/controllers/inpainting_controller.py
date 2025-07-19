from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse, JSONResponse
import numpy as np
from PIL import Image
import io
import os
import torch
import base64
from pathlib import Path
import shutil

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

def get_project_root():
    """
    获取项目根目录的绝对路径
    """
    # 当前文件路径
    current_file = os.path.abspath(__file__)
    # 从controllers目录上升两级到达项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
    return project_root

def get_local_lama_model_path():
    """
    获取lama模型路径，优先检查系统缓存目录
    """
    # 首先检查系统缓存目录
    cache_model_dir = os.path.join(os.path.expanduser("~"), ".cache", "iopaint", "lama")
    cache_model_file = os.path.join(cache_model_dir, "big-lama.pt")
    
    if os.path.exists(cache_model_file):
        logger.info(f"在系统缓存目录找到lama模型: {cache_model_file}")
        return cache_model_file
    
    # 如果系统缓存目录没有，检查项目本地目录
    project_root = get_project_root()
    local_model_dir = os.path.join(project_root, "model")
    local_lama_dir = os.path.join(local_model_dir, "lama")
    local_model_file = os.path.join(local_lama_dir, "big-lama.pt")
    
    if os.path.exists(local_model_file):
        logger.info(f"在项目本地目录找到lama模型: {local_model_file}")
        return local_model_file
    
    logger.warning(f"警告: 未找到lama模型文件")
    return None

def get_model_manager():
    global model_manager
    if model_manager is None:
        # 检查lama模型路径
        local_model_file = get_local_lama_model_path()
        
        # 确定模型目录
        if local_model_file:
            # 使用模型所在的父目录作为模型目录
            model_dir = os.path.dirname(os.path.dirname(local_model_file))
            logger.info(f"使用模型所在目录: {model_dir}")
        else:
            # 如果没找到模型，使用系统缓存目录
            model_dir = os.path.join(os.path.expanduser("~"), ".cache", "iopaint")
            logger.warning(f"未找到lama模型，使用系统缓存目录: {model_dir}")
        
        os.makedirs(model_dir, exist_ok=True)
        
        # 如果找不到本地模型，记录警告
        if not local_model_file:
            logger.warning("未找到lama模型，模型质量可能受到影响")
            preferred_model = "cv2"
            logger.warning(f"将使用cv2作为备选模型")
        else:
            # 如果找到了本地模型，强制使用lama
            preferred_model = "lama"
            logger.info(f"已找到lama模型，将优先使用")
        
        logger.info(f"初始化模型管理器，模型目录: {model_dir}")
        
        # 检查CUDA是否可用
        device_type = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"检测到设备类型: {device_type}")
        
        # 优化配置参数，提升图像修复质量
        config = ApiConfig(
            host="127.0.0.1",
            port=8080,
            inbrowser=False,
            model=preferred_model,  # 使用确定的模型
            no_half=False,  # 对于高端GPU可以设为True以获得更高质量
            low_mem=False,  # 对于大多数现代服务器，设为False以获得更好性能
            cpu_offload=False if device_type == "cuda" else True,  # 如果是GPU，禁用CPU卸载以提高性能
            disable_nsfw_checker=True,  # 禁用NSFW检查器以提高性能
            local_files_only=True,  # 设为True，仅使用本地文件
            cpu_textencoder=False,
            device=Device.cuda if device_type == "cuda" else Device.cpu,  # 优先使用GPU
            input=None,
            mask_dir=None,
            output_dir=None,
            quality=95,  # 设置较高的质量
            enable_interactive_seg=False,
            interactive_seg_model=InteractiveSegModel.vit_b,
            interactive_seg_device=Device.cuda if device_type == "cuda" else Device.cpu,
            enable_remove_bg=False,
            remove_bg_device=Device.cuda if device_type == "cuda" else Device.cpu,
            remove_bg_model=RemoveBGModel.briaai_rmbg_1_4,
            enable_anime_seg=False,
            enable_realesrgan=True,  # 启用超分辨率以提高质量
            realesrgan_device=Device.cuda if device_type == "cuda" else Device.cpu,
            realesrgan_model=RealESRGANModel.realesr_general_x4v3,
            enable_gfpgan=True,  # 启用面部增强
            gfpgan_device=Device.cuda if device_type == "cuda" else Device.cpu,
            enable_restoreformer=True,  # 启用修复增强
            restoreformer_device=Device.cuda if device_type == "cuda" else Device.cpu,
        )

        # 记录详细的模型配置信息
        logger.info(f"模型配置信息: 模型={config.model}, 设备={config.device}, GPU加速={device_type == 'cuda'}")
        logger.info(f"增强功能: 超分辨率={config.enable_realesrgan}, 面部增强={config.enable_gfpgan}, 修复增强={config.enable_restoreformer}")

        try:
            logger.info(f"尝试初始化模型管理器，使用模型: {config.model}")
            model_manager = ModelManager(
                name=config.model,
                device=torch.device(config.device),
                no_half=config.no_half,
                cpu_offload=config.cpu_offload,
                disable_nsfw_checker=config.disable_nsfw_checker,
                local_files_only=config.local_files_only,  # 仅使用本地文件
                cpu_textencoder=config.cpu_textencoder,
                model_dir=Path(model_dir),  # 使用确定的模型目录
                enable_controlnet=False,
                controlnet_method=None,
                # 增强功能配置
                enable_realesrgan=config.enable_realesrgan,
                realesrgan_device=torch.device(config.realesrgan_device),
                realesrgan_model=config.realesrgan_model,
                enable_gfpgan=config.enable_gfpgan,
                gfpgan_device=torch.device(config.gfpgan_device),
                enable_restoreformer=config.enable_restoreformer,
                restoreformer_device=torch.device(config.restoreformer_device),
            )
            logger.info(f"模型管理器初始化成功，当前模型: {model_manager.name}")
            
            # 如果初始化成功但使用的不是lama，提供详细日志
            if model_manager.name != "lama":
                logger.warning(f"注意：当前使用的模型是 {model_manager.name}，不是首选的lama模型。这可能影响修复质量。")
                if model_manager.name == "cv2":
                    logger.warning("cv2模型仅提供基本的修复功能，效果可能不如lama模型理想。")
                
        except Exception as e:
            logger.error(f"模型管理器初始化失败: {str(e)}", exc_info=True)
            
            # 如果初始化失败并且不是使用cv2，尝试使用cv2作为备选
            if config.model != "cv2":
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
                        # 增强功能配置
                        enable_realesrgan=config.enable_realesrgan,
                        realesrgan_device=torch.device(config.realesrgan_device),
                        realesrgan_model=config.realesrgan_model,
                        enable_gfpgan=config.enable_gfpgan,
                        gfpgan_device=torch.device(config.gfpgan_device),
                        enable_restoreformer=config.enable_restoreformer,
                        restoreformer_device=torch.device(config.restoreformer_device),
                    )
                    logger.info(f"成功使用备选模型初始化: {model_manager.name}")
                    logger.warning("注意：当前使用的是cv2备选模型，这可能导致修复效果不理想。")
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
        # 强制使用已加载的模型，不尝试切换模型
        # 解码base64字符串为字节
        logger.debug("解码base64字符串")
        image_bytes = decode_base64_to_bytes(request.image_base64)
        mask_bytes = decode_base64_to_bytes(request.mask_base64)

        # 将字节转换为 numpy 数组
        logger.debug("转换图像到numpy数组")
        image_np, _ = load_img(image_bytes)
        mask_np, _ = load_img(mask_bytes, gray=True)
        
        # 检查并确保图像和蒙版尺寸一致
        logger.debug(f"原始图像尺寸: {image_np.shape}, 蒙版尺寸: {mask_np.shape}")
        if image_np.shape[:2] != mask_np.shape[:2]:
            logger.warning(f"图像和蒙版尺寸不一致，正在调整蒙版尺寸以匹配图像")
            # 使用PIL调整蒙版尺寸以匹配原图
            from PIL import Image
            mask_pil = Image.fromarray(mask_np)
            mask_pil = mask_pil.resize((image_np.shape[1], image_np.shape[0]), Image.LANCZOS)
            mask_np = np.array(mask_pil)
            logger.debug(f"调整后的蒙版尺寸: {mask_np.shape}")
        
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
        logger.info(f"开始执行图像修复，当前使用模型: {manager.name}")
        result_np = manager(image_np, mask_np, inpaint_request)

        # 将结果转换为字节流
        logger.debug("转换结果到字节流")
        result_bytes = numpy_to_bytes(result_np, "png")
        
        # 将结果转换为base64编码
        result_base64 = base64.b64encode(result_bytes).decode('utf-8')
        
        logger.info(f"图像修复成功完成，使用模型: {manager.name}")
        # 使用统一的响应格式返回结果
        return Response.success({"image_base64": result_base64}, "图像修复成功")

    except Exception as e:
        logger.error(f"图像修复失败: {str(e)}", exc_info=True)
        return Response.error(str(e)) 