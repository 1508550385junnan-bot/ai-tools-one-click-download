# core/downloader.py - 下载模块
# 支持进度回调、断点续传（HTTP Range）、自动重试
import os
import time
import logging
import urllib.request
import urllib.error
from config import DOWNLOAD_DIR, MAX_RETRIES, CHUNK_SIZE

logger = logging.getLogger(__name__)


class Downloader:
    """文件下载器，带进度回调和重试机制"""

    def __init__(self):
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    def download(self, url: str, filename: str,
                 progress_callback=None,
                 retries: int = MAX_RETRIES) -> str:
        """
        下载文件
        progress_callback(downloaded_bytes, total_bytes, speed_kbps)
        返回: 下载完成后的本地文件路径
        """
        dest = os.path.join(DOWNLOAD_DIR, filename)

        for attempt in range(1, retries + 1):
            try:
                logger.info(f"下载 {filename} (第{attempt}次尝试)...")
                return self._do_download(url, dest, progress_callback)
            except Exception as e:
                logger.warning(f"下载失败 (第{attempt}次): {e}")
                if attempt < retries:
                    wait = 2 ** attempt
                    logger.info(f"等待 {wait}s 后重试...")
                    time.sleep(wait)
                else:
                    raise RuntimeError(
                        f"下载 {filename} 失败（已重试{retries}次）: {e}"
                    )

    def _do_download(self, url: str, dest: str,
                     progress_callback=None) -> str:
        """执行单次下载"""
        # 获取文件大小
        req = urllib.request.Request(url, method="HEAD")
        req.add_header("User-Agent", "AI-Tools-Installer/1.0")
        total_size = 0

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                total_size = int(resp.headers.get("Content-Length", 0))
        except Exception:
            total_size = 0  # 无法获取大小则未知

        # 检查已有部分下载（断点续传）
        existing_size = 0
        if os.path.exists(dest):
            existing_size = os.path.getsize(dest)
            if total_size > 0 and existing_size >= total_size:
                logger.info(f"文件已存在且大小完整，跳过下载: {dest}")
                if progress_callback:
                    progress_callback(existing_size, total_size, 0)
                return dest

        # 下载
        get_req = urllib.request.Request(url)
        get_req.add_header("User-Agent", "AI-Tools-Installer/1.0")

        if existing_size > 0 and total_size > 0:
            get_req.add_header("Range", f"bytes={existing_size}-")
            mode = "ab"
        else:
            existing_size = 0
            mode = "wb"

        start_time = time.time()
        downloaded = existing_size
        last_callback = 0

        try:
            resp_ctx = urllib.request.urlopen(get_req, timeout=300)
        except urllib.error.HTTPError as e:
            if e.code == 416 and os.path.exists(dest):
                actual_size = os.path.getsize(dest)
                if total_size == 0 or actual_size >= total_size:
                    logger.info(f"服务器返回416，已有文件视为完整: {dest}")
                    if progress_callback:
                        progress_callback(actual_size, max(total_size, actual_size), 0)
                    return dest
            raise

        with resp_ctx as resp:
            with open(dest, mode) as f:
                while True:
                    chunk = resp.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)

                    # 进度回调（最多每秒一次，避免UI卡顿）
                    now = time.time()
                    if progress_callback and (now - last_callback > 0.3):
                        elapsed = now - start_time
                        if elapsed > 0:
                            speed = (downloaded - existing_size) / elapsed / 1024
                        else:
                            speed = 0
                        progress_callback(downloaded, total_size, speed)
                        last_callback = now

        # 最终回调
        elapsed = time.time() - start_time
        speed = (downloaded - existing_size) / max(elapsed, 0.1) / 1024
        if progress_callback:
            progress_callback(downloaded, max(total_size, downloaded), speed)

        # 验证文件完整性
        actual_size = os.path.getsize(dest)
        if total_size > 0 and actual_size < total_size * 0.95:
            raise RuntimeError(
                f"文件大小不匹配: 预期 {total_size}, 实际 {actual_size}"
            )

        logger.info(f"下载完成: {dest} ({actual_size/1024/1024:.1f}MB)")
        return dest
