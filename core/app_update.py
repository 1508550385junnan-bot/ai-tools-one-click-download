# core/app_update.py - 应用自身更新判断
from core.version_utils import is_upgrade_available


def normalize_update_info(data: dict, current_version: str) -> dict | None:
    """远端版本高于当前版本时返回更新信息；相同、更低或格式错误时返回 None。"""
    if not isinstance(data, dict):
        return None
    remote_version = str(data.get("version", "")).strip()
    if not remote_version:
        return None
    if not is_upgrade_available(current_version, remote_version):
        return None
    return data
