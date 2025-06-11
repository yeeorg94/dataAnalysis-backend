from fastapi import APIRouter, UploadFile, Form, File, Body
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional, Dict, Any
from hivision import IDCreator
from hivision.error import FaceError
from hivision.creator.layout_calculator import (
    generate_layout_array,
    generate_layout_image,
)
from hivision.creator.choose_handler import choose_handler
from hivision.utils import (
    add_background,
    resize_image_to_kb,
    bytes_2_base64,
    base64_2_numpy,
    hex_to_rgb,
    add_watermark,
    save_image_dpi_to_bytes,
)
import numpy as np
import cv2
from src.utils import get_app_logger

# 获取日志记录器
logger = get_app_logger()

# 创建APIRouter对象
router = APIRouter(
    prefix="/idphoto",
    tags=["idphoto"],
    responses={404: {"description": "Not found"}},
)

creator = IDCreator()

# 定义请求模型
class IdPhotoCreateRequest(BaseModel):
    input_image_base64: str
    height: int = 413
    width: int = 295
    human_matting_model: str = "modnet_photographic_portrait_matting"
    face_detect_model: str = "mtcnn"
    hd: bool = True
    dpi: int = 300
    face_align: bool = False
    head_measure_ratio: float = 0.2
    head_height_ratio: float = 0.45
    top_distance_max: float = 0.12
    top_distance_min: float = 0.10
    brightness_strength: float = 0
    contrast_strength: float = 0
    sharpen_strength: float = 0
    saturation_strength: float = 0

class HumanMattingRequest(BaseModel):
    input_image_base64: str
    human_matting_model: str = "hivision_modnet"
    dpi: int = 300

class AddBackgroundRequest(BaseModel):
    input_image_base64: str
    color: str = "000000"
    kb: Optional[int] = None
    dpi: int = 300
    render: int = 0

class LayoutRequest(BaseModel):
    input_image_base64: str
    height: int = 413
    width: int = 295
    kb: Optional[int] = None
    dpi: int = 300

class WatermarkRequest(BaseModel):
    input_image_base64: str
    text: str = "Hello"
    size: int = 20
    opacity: float = 0.5
    angle: int = 30
    color: str = "#000000"
    space: int = 25
    kb: Optional[int] = None
    dpi: int = 300

class ResizeRequest(BaseModel):
    input_image_base64: str
    dpi: int = 300
    kb: int = 50

class CropRequest(BaseModel):
    input_image_base64: str
    height: int = 413
    width: int = 295
    face_detect_model: str = "mtcnn"
    hd: bool = True
    dpi: int = 300
    head_measure_ratio: float = 0.2
    head_height_ratio: float = 0.45
    top_distance_max: float = 0.12
    top_distance_min: float = 0.10

# 统一响应结构函数
def success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    创建统一的成功响应结构
    """
    return {
        "code": 200,
        "data": data,
        "msg": "success"
    }

def error_response(message: str, code: int = 400) -> Dict[str, Any]:
    """
    创建统一的错误响应结构
    """
    return {
        "code": code,
        "data": {},
        "msg": message
    }

# 证件照智能制作接口
@router.post("/create")
async def idphoto_inference(request: IdPhotoCreateRequest):  
    logger.info("证件照制作请求")
    # 使用base64解码
    img = base64_2_numpy(request.input_image_base64)

    # ------------------- 选择抠图与人脸检测模型 -------------------
    choose_handler(creator, request.human_matting_model, request.face_detect_model)

    # 将字符串转为元组
    size = (int(request.height), int(request.width))
    try:
        result = creator(
            img,
            size=size,
            head_measure_ratio=request.head_measure_ratio,
            head_height_ratio=request.head_height_ratio,
            head_top_range=(request.top_distance_max, request.top_distance_min),
            face_alignment=request.face_align,
            brightness_strength=request.brightness_strength,
            contrast_strength=request.contrast_strength,
            sharpen_strength=request.sharpen_strength,
            saturation_strength=request.saturation_strength,
        )
    except FaceError:
        logger.error("未检测到人脸或检测到多个人脸")
        return error_response("未检测到人脸或检测到多个人脸")
    # 如果检测到人脸数量等于1, 则返回标准证和高清照结果（png 4通道图像）
    else:
        result_image_standard_bytes = save_image_dpi_to_bytes(cv2.cvtColor(result.standard, cv2.COLOR_RGBA2BGRA), None, request.dpi)
        
        result_data = {
            "status": True,
            "image_base64_standard": bytes_2_base64(result_image_standard_bytes),
        }

        # 如果hd为True, 则增加高清照结果（png 4通道图像）
        if request.hd:
            result_image_hd_bytes = save_image_dpi_to_bytes(cv2.cvtColor(result.hd, cv2.COLOR_RGBA2BGRA), None, request.dpi)
            result_data["image_base64_hd"] = bytes_2_base64(result_image_hd_bytes)

    return success_response(result_data)


# 人像抠图接口
@router.post("/human_matting")
async def human_matting_inference(request: HumanMattingRequest):
    logger.info("人像抠图请求")
    img = base64_2_numpy(request.input_image_base64)

    # ------------------- 选择抠图与人脸检测模型 -------------------
    choose_handler(creator, request.human_matting_model, None)

    try:
        result = creator(
            img,
            change_bg_only=True,
        )
    except FaceError:
        logger.error("人像抠图失败")
        return error_response("人像抠图失败")
    else:
        result_image_standard_bytes = save_image_dpi_to_bytes(cv2.cvtColor(result.standard, cv2.COLOR_RGBA2BGRA), None, request.dpi)
        result_data = {
            "status": True,
            "image_base64": bytes_2_base64(result_image_standard_bytes),
        }
    return success_response(result_data)


# 透明图像添加纯色背景接口
@router.post("/add_background")
async def photo_add_background(request: AddBackgroundRequest):
    logger.info("添加背景请求")
    render_choice = ["pure_color", "updown_gradient", "center_gradient"]

    img = base64_2_numpy(request.input_image_base64)

    color = hex_to_rgb(request.color)
    color = (color[2], color[1], color[0])

    result_image = add_background(
        img,
        bgr=color,
        mode=render_choice[request.render],
    ).astype(np.uint8)

    result_image = cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR)
    if request.kb:
        result_image_bytes = resize_image_to_kb(result_image, None, int(request.kb), dpi=request.dpi)
    else:
        result_image_bytes = save_image_dpi_to_bytes(result_image, None, dpi=request.dpi)

    result_data = {
        "status": True,
        "image_base64": bytes_2_base64(result_image_bytes),
    }

    return success_response(result_data)


# 六寸排版照生成接口
@router.post("/layout")
async def generate_layout_photos(request: LayoutRequest):
    logger.info("六寸排版请求")
    img = base64_2_numpy(request.input_image_base64)

    size = (int(request.height), int(request.width))

    typography_arr, typography_rotate = generate_layout_array(
        input_height=size[0], input_width=size[1]
    )

    result_layout_image = generate_layout_image(
        img, typography_arr, typography_rotate, height=size[0], width=size[1]
    ).astype(np.uint8)

    result_layout_image = cv2.cvtColor(result_layout_image, cv2.COLOR_RGB2BGR)
    if request.kb:
        result_layout_image_bytes = resize_image_to_kb(
            result_layout_image, None, int(request.kb), dpi=request.dpi
        )
    else:
        result_layout_image_bytes = save_image_dpi_to_bytes(result_layout_image, None, dpi=request.dpi)
        
    result_layout_image_base64 = bytes_2_base64(result_layout_image_bytes)

    result_data = {
        "status": True,
        "image_base64": result_layout_image_base64,
    }

    return success_response(result_data)


# 透明图像添加水印接口
@router.post("/watermark")
async def watermark(request: WatermarkRequest):
    logger.info("添加水印请求")
    img = base64_2_numpy(request.input_image_base64)

    color_rgb = hex_to_rgb(request.color.lstrip("#"))
    img_with_watermark = add_watermark(
        img,
        text=request.text,
        font_size=request.size,
        opacity=request.opacity,
        angle_in_degree=request.angle,
        font_color=color_rgb,
        space=request.space,
    )

    if request.kb:
        result_image_bytes = resize_image_to_kb(img_with_watermark, None, int(request.kb), dpi=request.dpi)
    else:
        result_image_bytes = save_image_dpi_to_bytes(img_with_watermark, None, dpi=request.dpi)

    result_data = {
        "status": True,
        "image_base64": bytes_2_base64(result_image_bytes),
    }

    return success_response(result_data)


# 调整图片大小接口
@router.post("/resize")
async def set_kb(request: ResizeRequest):
    logger.info("调整图片大小请求")
    img = base64_2_numpy(request.input_image_base64)

    result_image_bytes = resize_image_to_kb(img, None, int(request.kb), dpi=request.dpi)
    result_data = {
        "status": True,
        "image_base64": bytes_2_base64(result_image_bytes),
    }
    
    return success_response(result_data)


# 证件照裁剪接口
@router.post("/crop")
async def idphoto_crop_inference(request: CropRequest):
    logger.info("证件照裁剪请求")
    img = base64_2_numpy(request.input_image_base64)

    # ------------------- 选择抠图与人脸检测模型 -------------------
    choose_handler(creator, None, request.face_detect_model)
    # 将字符串转为元组
    size = (int(request.height), int(request.width))
    try:
        result = creator(
            img,
            size=size,
            head_measure_ratio=request.head_measure_ratio,
            head_height_ratio=request.head_height_ratio,
            head_top_range=(request.top_distance_max, request.top_distance_min),
            crop_only=True,
        )
    except FaceError:
        logger.error("未检测到人脸或检测到多个人脸")
        return error_response("未检测到人脸或检测到多个人脸")

    else:
        result_image_standard_bytes = save_image_dpi_to_bytes(result.standard, None, request.dpi)
        result_data = {
            "status": True,
            "image_base64_standard": bytes_2_base64(result_image_standard_bytes),
        }

        # 如果hd为True, 则增加高清照结果（png 4通道图像）
        if request.hd:
            result_image_hd_bytes = save_image_dpi_to_bytes(result.hd, None, request.dpi)
            result_data["image_base64_hd"] = bytes_2_base64(result_image_hd_bytes)

    return success_response(result_data) 