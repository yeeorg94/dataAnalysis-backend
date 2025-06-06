from fastapi import APIRouter, HTTPException, Response, Query
from typing import Optional
from pydantic import BaseModel
import requests
from src.app.test.index import Test
from src.utils import get_global_logger, config
import httpx
from fastapi.responses import StreamingResponse
import io
import ipaddress
from urllib.parse import urlparse

# 获取应用日志器
logger = get_global_logger()

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
        # 获取原始响应的内容类型
        content_type = response.headers.get('Content-Type')
        
        # 构建响应时传递原始内容类型
        return Response(
            content=response.content,
            media_type=content_type
        )
    
    except Exception as e:
        logger.error(f"处理图片代理请求出错: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/proxy")
def proxy_download(url: str = Query(..., description="目标资源 URL")):
    try:
        # 设置更符合抖音要求的请求头
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-TW,zh;q=0.9,ja;q=0.8,ko;q=0.7,zh-CN;q=0.6,en-GB;q=0.5,en;q=0.4,en-US;q=0.3",
            "Host": "sns-video-qc.xhscdn.com",
            "Proxy-Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Referer": "https://www.duoleta.com/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0"
        }

        logger.info(f"请求URL: {url}")
        logger.info(f"请求头: {headers}")

        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)

        # 记录响应详情
        logger.info(f"响应状态码: {response.status_code}")
        logger.info(f"响应头: {response.headers}")
        logger.info(f"响应内容前100字节: {response.text[:100]}")

        if response.status_code != 200:
            logger.error(f"请求失败: {response.text}")
            raise HTTPException(status_code=response.status_code, detail=f"Failed to fetch resource: {response.text}")

        content_type = response.headers.get("Content-Type", "application/octet-stream")

        return StreamingResponse(
            content=response.iter_content(chunk_size=1024),
            media_type=content_type,
            headers={"Content-Type": content_type}
        )

    except Exception as e:
        error_msg = f"Request failed: {str(e)}"
        logger.error(f"请求失败: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
