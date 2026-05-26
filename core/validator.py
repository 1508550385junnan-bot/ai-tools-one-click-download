# core/validator.py - 版本验证模块
import os
import sys
import subprocess
import logging

logger = logging.getLogger(__name__)


def _get_windows_file_version(filepath: str) -> str | None:
    """通过 Windows API 获取 exe/dll 文件的版本号。失败返回 None。"""
    if sys.platform != "win32":
        return None
    try:
        import ctypes
        from ctypes import wintypes

        ver = ctypes.windll.version

        # 获取版本信息大小
        size = ver.GetFileVersionInfoSizeW(filepath, None)
        if not size:
            return None

        # 读取版本信息
        buf = ctypes.create_string_buffer(size)
        if not ver.GetFileVersionInfoW(filepath, 0, size, buf):
            return None

        # 查询根版本块
        ptr = ctypes.c_void_p()
        ptr_size = wintypes.UINT()
        if not ver.VerQueryValueW(buf, "\\", ctypes.byref(ptr), ctypes.byref(ptr_size)):
            return None

        if ptr_size.value < 52:
            return None

        # 解析 VS_FIXEDFILEINFO
        class VS_FIXEDFILEINFO(ctypes.Structure):
            _fields_ = [
                ("dwSignature", wintypes.DWORD),
                ("dwStrucVersion", wintypes.DWORD),
                ("dwFileVersionMS", wintypes.DWORD),
                ("dwFileVersionLS", wintypes.DWORD),
                ("dwProductVersionMS", wintypes.DWORD),
                ("dwProductVersionLS", wintypes.DWORD),
                ("dwFileFlagsMask", wintypes.DWORD),
                ("dwFileFlags", wintypes.DWORD),
                ("dwFileOS", wintypes.DWORD),
                ("dwFileType", wintypes.DWORD),
                ("dwFileSubtype", wintypes.DWORD),
                ("dwFileDateMS", wintypes.DWORD),
                ("dwFileDateLS", wintypes.DWORD),
            ]

        info = ctypes.cast(ptr, ctypes.POINTER(VS_FIXEDFILEINFO)).contents
        major = info.dwFileVersionMS >> 16
        minor = info.dwFileVersionMS & 0xFFFF
        build = info.dwFileVersionLS >> 16
        rev = info.dwFileVersionLS & 0xFFFF

        return f"{major}.{minor}.{build}.{rev}"
    except Exception as e:
        logger.debug(f"获取文件版本失败: {e}")
        return None


class Validator:
    """安装后版本验证"""

    def __init__(self, status_callback=None):
        self.callback = status_callback or (lambda *a: None)

    def verify(self, tool_key: str, tool_info: dict) -> dict:
        """
        验证工具是否安装成功
        返回: {"success": bool, "version": str, "error": str, "method": str}
        """
        verify_config = tool_info.get("verify", {})
        method = verify_config.get("method", "exit_code_zero")
        command = verify_config.get("command")
        check_paths = tool_info.get("install", {}).get("check_paths", [])

        # 方法1: 文件存在性检查
        if method == "file_exists" or not command:
            self.callback(f"验证 {tool_info['name']}", "running", "检查安装文件...")
            for p in check_paths:
                expanded = os.path.expandvars(p)
                if os.path.exists(expanded):
                    # 尝试获取文件版本号
                    file_ver = _get_windows_file_version(expanded)
                    version_str = file_ver if file_ver else "已安装"
                    self.callback(f"验证 {tool_info['name']}", "ok",
                                  f"找到: {expanded}" + (f" (v{file_ver})" if file_ver else ""))
                    return {
                        "success": True,
                        "version": version_str,
                        "error": None,
                        "method": "file_exists",
                    }
            self.callback(f"验证 {tool_info['name']}", "error", "未找到安装文件")
            return {
                "success": False,
                "version": None,
                "error": "未检测到安装文件",
                "method": "file_exists",
            }

        # 方法2: 执行 --version 命令
        elif method == "exit_code_zero":
            self.callback(f"验证 {tool_info['name']}", "running",
                          f"执行: {command}")
            try:
                result = subprocess.run(
                    command, shell=True,
                    capture_output=True, text=True, timeout=30,
                    env={**os.environ, "PATH": self._get_extended_path()}
                )
                version_output = (
                    result.stdout.strip() or result.stderr.strip()
                )

                if result.returncode == 0:
                    self.callback(f"验证 {tool_info['name']}", "ok",
                                  f"版本: {version_output[:60]}")
                    return {
                        "success": True,
                        "version": version_output,
                        "error": None,
                        "method": "exit_code_zero",
                    }
                else:
                    self.callback(f"验证 {tool_info['name']}", "error",
                                  f"命令返回失败: {version_output[:60]}")
                    return {
                        "success": False,
                        "version": version_output,
                        "error": f"exit code {result.returncode}",
                        "method": "exit_code_zero",
                    }
            except FileNotFoundError:
                self.callback(f"验证 {tool_info['name']}", "error",
                              "命令未找到，可能需要重启终端")
                return {
                    "success": False,
                    "version": None,
                    "error": "命令未找到（PATH未生效？）",
                    "method": "exit_code_zero",
                }
            except Exception as e:
                self.callback(f"验证 {tool_info['name']}", "error", str(e))
                return {
                    "success": False,
                    "version": None,
                    "error": str(e),
                    "method": "exit_code_zero",
                }

        # 方法3: 包含特定版本号
        elif method == "version_contains":
            expected = verify_config.get("expected", "")
            self.callback(f"验证 {tool_info['name']}", "running",
                          f"执行: {command}")
            try:
                result = subprocess.run(
                    command, shell=True,
                    capture_output=True, text=True, timeout=30,
                    env={**os.environ, "PATH": self._get_extended_path()}
                )
                version_output = (
                    result.stdout.strip() or result.stderr.strip()
                )
                if expected in version_output:
                    self.callback(f"验证 {tool_info['name']}", "ok",
                                  f"版本匹配: {version_output[:60]}")
                    return {
                        "success": True,
                        "version": version_output,
                        "error": None,
                        "method": "version_contains",
                    }
                else:
                    self.callback(f"验证 {tool_info['name']}", "error",
                                  f"预期含 '{expected}'，实际: {version_output[:60]}")
                    return {
                        "success": False,
                        "version": version_output,
                        "error": f"版本不匹配（预期含: {expected}）",
                        "method": "version_contains",
                    }
            except Exception as e:
                return {
                    "success": False, "version": None,
                    "error": str(e), "method": "version_contains",
                }

        return {"success": False, "version": None, "error": "未知验证方法", "method": method}

    @staticmethod
    def _get_extended_path() -> str:
        """扩展PATH，包含常见安装路径"""
        paths = [os.environ.get("PATH", "")]
        extras = [
            os.path.expandvars("%ProgramFiles%\\nodejs"),
            os.path.expandvars("%ProgramFiles(x86)%\\nodejs"),
            os.path.expandvars("%APPDATA%\\npm"),
            os.path.expandvars("%LOCALAPPDATA%\\Programs\\Python\\Python312"),
            os.path.expandvars("%LOCALAPPDATA%\\Programs\\Python\\Python312\\Scripts"),
            os.path.expandvars("%ProgramFiles%\\Python312"),
            os.path.expandvars("%ProgramFiles%\\Python312\\Scripts"),
            os.path.expandvars("%ProgramFiles%\\Git\\bin"),
            os.path.expandvars("%ProgramFiles%\\Git\\cmd"),
            os.path.expandvars("%LOCALAPPDATA%\\Programs\\Microsoft VS Code\\bin"),
        ]
        for p in extras:
            if os.path.isdir(p):
                paths.append(p)
        return ";".join(paths)
