# core/latest_versions.py - 在线工具版本检测
import json
import logging
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


def _read_json(url: str, timeout: int = 8) -> dict:
    req = urllib.request.Request(url, headers={
        "User-Agent": "AI-Tools-Installer/latest-version-check",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _clean_tag(value: str | None) -> str | None:
    if not value:
        return None
    match = re.search(r"v?(\d+(?:\.\d+){1,3})", str(value))
    if match:
        return match.group(1)
    return str(value).strip() or None


def resolve_latest_version(tool_info: dict, timeout: int = 8) -> str | None:
    """按工具 registry 中的 latest 配置获取远程最新版本。失败时返回静态 latest_version。"""
    static_version = tool_info.get("latest_version")
    latest = tool_info.get("latest") or {}
    source_type = latest.get("type")

    try:
        if source_type == "npm":
            package = latest["package"]
            data = _read_json(f"https://registry.npmjs.org/{package}/latest", timeout)
            return _clean_tag(data.get("version")) or static_version

        if source_type == "pypi":
            package = latest["package"]
            data = _read_json(f"https://pypi.org/pypi/{package}/json", timeout)
            return _clean_tag(data.get("info", {}).get("version")) or static_version

        if source_type == "github_release":
            repo = latest["repo"]
            data = _read_json(f"https://api.github.com/repos/{repo}/releases/latest", timeout)
            return _clean_tag(data.get("tag_name") or data.get("name")) or static_version
    except Exception as e:
        logger.info("获取远程版本失败: %s (%s)", tool_info.get("name"), e)

    return static_version


def resolve_latest_versions(tools: dict, timeout: int = 8, max_workers: int = 5) -> dict:
    """并发查询所有配置了 latest 的工具，返回 {tool_key: version}。"""
    result = {}
    candidates = {
        key: tool for key, tool in tools.items()
        if tool.get("latest") or tool.get("latest_version")
    }
    if not candidates:
        return result

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(resolve_latest_version, tool, timeout): key
            for key, tool in candidates.items()
        }
        for future in as_completed(future_map):
            key = future_map[future]
            try:
                version = future.result()
            except Exception as e:
                logger.info("工具版本检测异常: %s (%s)", key, e)
                version = None
            if version:
                result[key] = version
    return result
