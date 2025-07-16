from fastapi import APIRouter, HTTPException, Query, Response
from typing import Optional
import logging
import asyncio
import io
import traceback
import re
import tempfile
import os
import subprocess
import shutil
import sys
import shlex

# 获取应用日志器
logger = logging.getLogger("app")

# 创建路由
router = APIRouter(
    prefix="/youtube",
    tags=["youtube"],
    responses={404: {"description": "Not found dep"}},
)

@router.get("")
async def download_youtube_video(
    url: str = Query(..., description="YouTube视频URL"),
    quality: Optional[str] = Query("best", description="视频质量: best, worst 或具体分辨率(如720)")
):
    """
    下载YouTube视频并以流的形式返回
    """
    try:
        # 记录请求信息
        logger.info(f"开始处理视频下载请求: {url}, 质量: {quality}")
        
        # 创建异步任务下载视频
        result = await asyncio.to_thread(_download_video, url, quality)
        
        if not result or not result.get("success"):
            error_message = result.get("error", "未知错误") if result else "下载失败"
            logger.error(f"下载失败: {error_message}")
            raise HTTPException(status_code=500, detail=f"下载失败: {error_message}")
        
        # 获取视频内容
        video_content = result["content"]
        filename = result["filename"]
        
        # 处理文件名中的特殊字符
        sanitized_filename = re.sub(r'[^\w\s.-]', '', filename)
        if not sanitized_filename.endswith('.mp4'):
            sanitized_filename += '.mp4'
        
        # 设置响应头
        headers = {
            "Content-Disposition": f"attachment; filename=\"{sanitized_filename}\"",
            "Content-Type": "video/mp4"
        }
        
        logger.info(f"视频下载成功: {sanitized_filename}, 大小: {len(video_content) / (1024*1024):.2f} MB")
        
        # 返回视频流
        return Response(
            content=video_content,
            media_type="video/mp4",
            headers=headers
        )
    except Exception as e:
        error_detail = str(e)
        stack_trace = traceback.format_exc()
        logger.error(f"下载YouTube视频失败: {error_detail}\n{stack_trace}")
        raise HTTPException(status_code=500, detail=f"下载失败: {error_detail}")

def _download_video(url: str, quality: str) -> dict:
    """
    使用yt-dlp下载YouTube视频
    """
    try:
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "video.mp4")
            
            # 根据质量参数设置yt-dlp格式选项
            if quality == "best":
                format_option = "best[ext=mp4]/best"
            elif quality == "worst":
                format_option = "worst[ext=mp4]/worst"
            else:
                # 尝试获取特定分辨率
                format_option = f"best[height<={quality}][ext=mp4]/best[height<={quality}]"
            
            # 使用Python可执行文件路径调用yt-dlp模块，而不是依赖命令行工具
            python_executable = sys.executable
            
            # 构建命令
            command = [
                python_executable,
                "-m", "yt_dlp",
                "-f", format_option,
                "-o", output_path,
                "--no-playlist",
                "--no-warnings",
                url
            ]
            
            logger.info(f"执行命令: {' '.join([shlex.quote(str(arg)) for arg in command])}")
            
            # 执行命令
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 获取命令输出
            stdout, stderr = process.communicate()
            
            # 检查命令是否成功
            if process.returncode != 0:
                logger.error(f"yt-dlp命令失败: {stderr}")
                return {
                    "success": False,
                    "error": f"下载命令失败: {stderr}"
                }
            
            # 检查文件是否存在
            if not os.path.exists(output_path):
                logger.error(f"下载后文件不存在: {output_path}")
                return {
                    "success": False,
                    "error": "下载后文件不存在"
                }
            
            # 读取文件内容
            with open(output_path, "rb") as f:
                video_content = f.read()
            
            # 获取文件名
            filename = os.path.basename(output_path)
            if "video.mp4" in filename:
                # 如果是默认文件名，尝试从stdout获取更好的名称
                match = re.search(r'Destination:\s+(.+?\.mp4)', stdout)
                if match:
                    filename = os.path.basename(match.group(1))
                else:
                    # 从URL中提取视频ID作为文件名
                    video_id = url.split("/")[-1].split("?")[0]
                    filename = f"{video_id}.mp4"
            
            logger.info(f"视频已下载到临时文件: {output_path}, 大小: {len(video_content) / (1024*1024):.2f} MB")
            
            return {
                "success": True,
                "content": video_content,
                "filename": filename
            }
    except Exception as e:
        logger.error(f"下载YouTube视频错误: {str(e)}\n{traceback.format_exc()}")
        return {
            "success": False,
            "error": str(e)
        } 