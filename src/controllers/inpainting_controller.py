from fastapi import APIRouter, UploadFile, File, Form, Depends
from fastapi.responses import StreamingResponse
import numpy as np
from PIL import Image
import io
import os
import torch
from pathlib import Path

from iopaint.schema import InpaintRequest, HDStrategy, LDMSampler, SDSampler, ApiConfig, Device, RealESRGANModel, InteractiveSegModel, RemoveBGModel
from iopaint.model_manager import ModelManager
from iopaint.helper import load_img, numpy_to_bytes, pil_to_bytes

# 简单的内存缓存，用于存储模型
# 在生产环境中，您可能需要更复杂的模型管理策略
model_manager = None

def get_model_manager():
    global model_manager
    if model_manager is None:
        # 使用一个简约的配置来初始化 ModelManager
        # 您可以根据需要进行调整
        # 创建一个默认的模型存储路径
        model_dir = os.path.join(os.path.expanduser("~"), ".cache", "iopaint")
        os.makedirs(model_dir, exist_ok=True)

        print(f"Initializing model manager with model dir: {model_dir}")

        config = ApiConfig(
            host="127.0.0.1",
            port=8080,
            inbrowser=False,
            model="lama",
            no_half=False,
            low_mem=False,
            cpu_offload=False,
            disable_nsfw_checker=False,
            local_files_only=False,
            cpu_textencoder=False,
            device=Device.cpu,
            input=None,
            mask_dir=None,
            output_dir=None,
            quality=95,
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
    return model_manager

router = APIRouter()

@router.post("/inpaint", tags=["inpainting"])
async def inpaint(
    image: UploadFile = File(..., description="原始图片"),
    mask: UploadFile = File(..., description="蒙版图片，白色部分为修复区域"),
    model_name: str = Form("lama", description="使用的修复模型"),
    prompt: str = Form("", description="Prompt for diffusion models."),
    negative_prompt: str = Form("", description="Negative prompt for diffusion models."),
    sd_steps: int = Form(50, description="Steps for diffusion models."),
    sd_sampler: SDSampler = Form(SDSampler.uni_pc, description="Sampler for diffusion model."),
    sd_strength: float = Form(1.0, description="Strength for diffusion models."),
    manager: ModelManager = Depends(get_model_manager)
):
    """
    接收图片和蒙版，使用 iopaint 进行图像修复。
    """
    try:
        # 加载图片和蒙版
        image_bytes = await image.read()
        mask_bytes = await mask.read()

        # 将字节转换为 numpy 数组
        # load_img 会返回一个 (H, W, 3) 的 RGB numpy 数组和一个 (H, W, 1) 的 alpha numpy 数组
        image_np, _ = load_img(image_bytes)
        mask_np, _ = load_img(mask_bytes, gray=True)
        
        # 将模型名称切换到请求的模型
        if manager.name != model_name:
            manager.switch(model_name)

        # 构造 InpaintRequest
        inpaint_request = InpaintRequest(
            hd_strategy=HDStrategy.CROP,
            prompt=prompt,
            negative_prompt=negative_prompt,
            sd_steps=sd_steps,
            sd_sampler=sd_sampler,
            sd_strength=sd_strength,
        )

        # 执行修复
        result_np = manager(image_np, mask_np, inpaint_request)

        # 将结果转换为字节流
        result_bytes = numpy_to_bytes(result_np, "png")

        return StreamingResponse(io.BytesIO(result_bytes), media_type="image/png")

    except Exception as e:
        return {"error": str(e)} 