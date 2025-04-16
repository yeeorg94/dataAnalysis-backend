from fastapi import APIRouter, HTTPException, Response
from typing import Optional
from pydantic import BaseModel
import requests
from src.app.test.index import Test
from src.utils import get_system_logger
import httpx
from fastapi.responses import StreamingResponse
import io

# 获取应用日志器
logger = get_system_logger()

# 创建路由器
router = APIRouter(
    prefix="/system",
    tags=["system"],
    responses={404: {"description": "Not found"}},
)

# 定义请求参数模型
class SystemParams(BaseModel):
    url: str
    filename: Optional[str] = None  # 可选的文件名参数

# 无前缀的POST端点
@router.post("/get_file_stream")
async def process_get_file_stream(params: SystemParams):
    """
    将文件的url转换成流返回
    
    参数:
    - url: 文件链接
    - filename: 可选的文件名，用于设置Content-Disposition header
    """
    logger.info(f"处理文件流请求 (POST): {params.url}")
    try:
        async with httpx.AsyncClient() as client:
            # 使用stream=True来支持大文件流式传输
            response = await client.get(params.url, follow_redirects=True)
            response.raise_for_status()  # 确保请求成功
            
            # 获取内容类型
            content_type = response.headers.get("content-type", "application/octet-stream")
            
            # 处理文件名
            filename = params.filename
            if not filename:
                # 尝试从URL或响应头获取文件名
                cd_header = response.headers.get("content-disposition", "")
                if "filename=" in cd_header:
                    filename = cd_header.split("filename=")[1].strip('"\'')
                else:
                    # 从URL路径获取文件名
                    filename = params.url.split("/")[-1].split("?")[0] or "downloaded_file"
            
            # 设置响应头
            headers = {
                "Content-Disposition": f"attachment; filename={filename}"
            }
            
            # 返回流式响应
            return StreamingResponse(
                io.BytesIO(response.content), 
                media_type=content_type,
                headers=headers
            )
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=e.response.status_code, detail=f"远程服务器错误: {str(e)}")
    except Exception as e:
        logger.error(f"处理文件流请求出错: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/image_proxy")
async def process_image_proxy(url: str):
    """
    处理图片代理请求 设置referer为weibo.com 返回图片信息供前端展示
    
    参数:
    - url: 图片链接
    """
    try:
        headers = {
            'Referer': 'https://weibo.com',  # 设置合法的Referer
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers, stream=True)
        return Response(response.content)
    
    except Exception as e:
        logger.error(f"处理图片代理请求出错: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))