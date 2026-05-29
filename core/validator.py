# core/validator.py - 版本验证模块
import os
import sys
import subprocess
import logging
import shlex

logger = logging.getLogger(__name__)


def _get_windows_file_version(filepath: str) -> str | None:
    """通过 Windows API 获取 exe/dll 文件的版本号。失败返回 None。"""
    if sys.platform != "win32":
        return None
    try:
        import ctypes
        from ctypes import wintypes

        ver = ctypes.windll.version
        size = ver.GetFileVersionInfoSizeW(filepath, None)
        if not size:
            return None

        buf = ctypes.create_string_buffer(size)
        if not ver.GetFileVersionInfoW(filepath, 0, size, buf):
            return None

        ptr = ctypes.c_void_p()
        ptr_size = wintypes.UINT()
        if not ver.VerQueryValueW(buf, "\\", ctypes.byref(ptr), ctypes.byref(ptr_size)):
            return None
        if ptr_size.value < 52:
            return None

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

def _find_windows_uninstall_entry(display_names: list[str]) -> dict | None:
    """从 Windows 卸载注册表中查找安装记录。"""
    if sys.platform != "win32" or not display_names:
        return None
    try:
        import winreg
    except ImportError:
        return None

    roots = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]
    wanted = [name.lower() for name in display_names]
    for root, subkey in roots:
        try:
            with winreg.OpenKey(root, subkey) as parent:
                for i in range(winreg.QueryInfoKey(parent)[0]):
                    child_name = winreg.EnumKey(parent, i)
                    try:
                        with winreg.OpenKey(parent, child_name) as child:
                            display = _reg_value(child, "DisplayName")
                            if not display or display.lower() not in wanted:
                                continue
                            return {
                                "display_name": display,
                                "version": _reg_value(child, "DisplayVersion"),
                                "install_location": _reg_value(child, "InstallLocation"),
                            }
                    except OSError:
                        continue
        except OSError:
            continue
    return None


def _reg_value(key, name: str) -> str | None:
    try:
        value, _ = __import__("winreg").QueryValueEx(key, name)
        return str(value) if value else None
    except OSError:
        return None


def _existing_paths(paths: list[str]) -> list[str]:
    found = []
    for path in paths:
        expanded = os.path.expandvars(path)
        if os.path.exists(expanded):
            found.append(expanded)
    return found


def _command_with_executable(command: str, executable: str) -> str:
    parts = shlex.split(command, posix=False)
    args = parts[1:] if len(parts) > 1 else []
    quoted_exe = subprocess.list2cmdline([executable])
    quoted_args = subprocess.list2cmdline(args) if args else ""
    return f"{quoted_exe} {quoted_args}".strip()


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
        install_config = tool_info.get("install", {})
        check_paths = install_config.get("check_paths", [])

        # 方法1: 文件存在性检查
        if method == "file_exists" or not command:
            self.callback(f"验证 {tool_info['name']}", "running", "检查安装文件...")
            reg_entry = _find_windows_uninstall_entry(install_config.get("registry_display_names", []))
            if reg_entry:
                install_location = reg_entry.get("install_location")
                exe_path = None
                if install_location:
                    candidate = os.path.join(os.path.expandvars(install_location), "cc-switch.exe")
                    if os.path.exists(candidate):
                        exe_path = candidate
                version_str = reg_entry.get("version") or (
                    _get_windows_file_version(exe_path) if exe_path else None
                ) or "已安装"
                self.callback(f"验证 {tool_info['name']}", "ok",
                              f"注册表: {reg_entry['display_name']} (v{version_str})")
                return {
                    "success": True,
                    "version": version_str,
                    "error": None,
                    "method": "registry",
                }
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
            return self._run_version_command(tool_info["name"], command, check_paths)

        # 方法3: 包含特定版本号
        elif method == "version_contains":
            expected = verify_config.get("expected", "")
            self.callback(f"验证 {tool_info['name']}", "running",
                          f"执行: {command}")
            try:
                result = subprocess.run(
                    command, shell=True,
                    capture_output=True, text=True, timeout=30,
                    env={**os.environ, "PATH": self._get_extended_path(check_paths)}
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

    def _run_version_command(self, tool_name: str, command: str, check_paths: list[str]) -> dict:
        commands = [command]
        for executable in _existing_paths(check_paths):
            fallback = _command_with_executable(command, executable)
            if fallback not in commands:
                commands.append(fallback)

        last_output = None
        last_error = None
        for candidate in commands:
            try:
                result = subprocess.run(
                    candidate, shell=True,
                    capture_output=True, text=True, timeout=30,
                    env={**os.environ, "PATH": self._get_extended_path(check_paths)}
                )
                version_output = result.stdout.strip() or result.stderr.strip()
                last_output = version_output
                if result.returncode == 0:
                    self.callback(f"验证 {tool_name}", "ok",
                                  f"版本: {version_output[:60]}")
                    return {
                        "success": True,
                        "version": version_output or "已安装",
                        "error": None,
                        "method": "exit_code_zero",
                    }
                last_error = f"exit code {result.returncode}"
            except FileNotFoundError:
                last_error = "命令未找到（PATH未生效？）"
            except Exception as e:
                last_error = str(e)

        self.callback(f"验证 {tool_name}", "error",
                      f"命令返回失败: {(last_output or last_error or '')[:60]}")
        return {
            "success": False,
            "version": last_output,
            "error": last_error,
            "method": "exit_code_zero",
        }

    @staticmethod
    def _get_extended_path(check_paths: list[str] | None = None) -> str:
        """扩展PATH，包含常见安装路径"""
        paths = [os.environ.get("PATH", "")]
        extras = [
            os.path.expandvars("%ProgramFiles%\\nodejs"),
            os.path.expandvars("%ProgramFiles(x86)%\\nodejs"),
            os.path.expandvars("%APPDATA%\\npm"),
            os.path.expandvars("%LOCALAPPDATA%\\Programs\\Python\\Python312"),
            os.path.expandvars("%LOCALAPPDATA%\\Programs\\Python\\Python312\\Scripts"),
            os.path.expandvars("%APPDATA%\\Python\\Python313\\Scripts"),
            os.path.expandvars("%APPDATA%\\Python\\Python312\\Scripts"),
            os.path.expandvars("%APPDATA%\\Python\\Python311\\Scripts"),
            os.path.expandvars("%APPDATA%\\Python\\Python310\\Scripts"),
            os.path.expandvars("%ProgramFiles%\\Python312"),
            os.path.expandvars("%ProgramFiles%\\Python312\\Scripts"),
            os.path.expandvars("%ProgramFiles%\\Git\\bin"),
            os.path.expandvars("%ProgramFiles%\\Git\\cmd"),
            os.path.expandvars("%LOCALAPPDATA%\\Programs\\Microsoft VS Code\\bin"),
        ]
        for path in check_paths or []:
            expanded = os.path.expandvars(path)
            parent = os.path.dirname(expanded)
            if parent:
                extras.append(parent)
        for p in extras:
            if os.path.isdir(p):
                paths.append(p)
        return ";".join(paths)
