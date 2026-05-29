# core/version_utils.py - 版本号比较工具
import re


def normalize_version(value: str | None) -> tuple:
    if not value:
        return ()
    parts = re.findall(r"\d+", str(value))
    if not parts:
        return ()
    numbers = [int(p) for p in parts[:4]]
    while numbers and numbers[-1] == 0:
        numbers.pop()
    return tuple(numbers)


def is_upgrade_available(installed_version: str | None, latest_version: str | None) -> bool:
    if not installed_version or not latest_version:
        return False
    installed = normalize_version(installed_version)
    latest = normalize_version(latest_version)
    if not installed:
        return False
    if not latest:
        return str(installed_version).strip() != str(latest_version).strip()
    max_len = max(len(installed), len(latest))
    installed += (0,) * (max_len - len(installed))
    latest += (0,) * (max_len - len(latest))
    return installed < latest
