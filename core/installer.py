# core/installer.py - 安装模块
# 支持 NSIS(/S)、MSI(/quiet)、npm install、pip install、exe 等多种安装方式
import os
import subprocess
import logging
import time
import glob
from config import DOWNLOAD_DIR

logger = logging.getLogger(__name__)


class Installer:
    """工具安装器，处理静默安装和环境配置"""

    def __init__(self, status_callback=None):
        """
        status_callback(step_name, status, detail)
        status: "running" | "ok" | "error" | "skip"
        """
        self.callback = status_callback or (lambda *a: None)

    def install_tool(self, tool_key: str, tool_info: dict) -> bool:
        """安装单个工具（含前置环境）"""
        tool_name = tool_info.get("name", tool_key)

        # Step 1: 检查前置环境
        prerequisites = tool_info.get("prerequisites", [])
        if prerequisites:
            self.callback("检查前置环境", "running",
                          f"需要 {len(prerequisites)} 个依赖: {', '.join(prerequisites)}")
            for prereq_key in prerequisites:
                self._install_prerequisite(prereq_key)
            self.callback("检查前置环境", "ok", "所有依赖就绪")

        # Step 2: 获取安装配置
        install_config = tool_info.get("install", {})
        install_type = install_config.get("type", "nsis")

        # npm/pip 类型不需要下载文件，直接安装
        if install_type in ("npm", "pip"):
            self.callback(f"安装 {tool_name}", "running",
                          f"正在安装 {tool_name}...")

            if install_type == "npm":
                success = self._install_npm(install_config.get("command", ""))
            else:
                success = self._install_pip(install_config.get("command", ""))

            if success:
                self.callback(f"安装 {tool_name}", "ok",
                              f"{tool_name} 安装成功，正在等待系统注册...")
                time.sleep(3)
            else:
                self.callback(f"安装 {tool_name}", "error",
                              f"{tool_name} 安装失败，请查看日志")
            return success

        # 其他类型需要下载文件
        downloads = tool_info.get("downloads", [])
        if not downloads:
            self.callback("下载", "error", "无下载地址")
            return False

        dl = downloads[0]
        filename = dl["filename"]
        installer_path = os.path.abspath(os.path.join(DOWNLOAD_DIR, filename))

        if not os.path.exists(installer_path):
            self.callback("下载安装包", "error",
                          f"未找到 {filename}，请先下载")
            return False

        # Step 3: 安装
        self.callback(f"安装 {tool_name}", "running",
                      f"正在静默安装 {tool_name}...")

        if install_type == "nsis":
            success = self._install_nsis(installer_path,
                                         install_config.get("args", ["/S"]))
        elif install_type == "msi":
            success = self._install_msi(installer_path,
                                        install_config.get("args", ["/quiet", "/norestart"]))
        else:
            success = self._install_exe(installer_path, install_config.get("args", []))

        logger.info(f"安装 {tool_name}: {'成功' if success else '失败'} (type={install_type})")
        if success:
            self.callback(f"安装 {tool_name}", "ok",
                          f"{tool_name} 安装成功，正在等待系统注册...")
            time.sleep(3)
        else:
            self.callback(f"安装 {tool_name}", "error",
                          f"{tool_name} 安装失败，请查看日志")
        return success

    def install_prerequisite(self, prereq_key: str) -> bool:
        """安装单个前置环境"""
        return self._install_prerequisite(prereq_key)

    def _install_prerequisite(self, prereq_key: str) -> bool:
        """安装前置环境"""
        from tools.registry import PREREQUISITES
        prereq = PREREQUISITES.get(prereq_key)
        if not prereq:
            self.callback("前置环境", "error", f"未知依赖: {prereq_key}")
            return False

        prereq_name = prereq["name"]

        # 先检查是否已安装
        if self._check_installed(prereq.get("check_paths", [])):
            self.callback(f"前置: {prereq_name}", "skip", "已安装，跳过")
            return True

        # 检查命令是否可用
        verify_cmd = prereq.get("verify_command")
        if verify_cmd:
            try:
                result = subprocess.run(
                    verify_cmd, shell=True,
                    capture_output=True, timeout=10
                )
                if result.returncode == 0:
                    self.callback(f"前置: {prereq_name}", "skip", "已安装，跳过")
                    return True
            except Exception:
                pass

        # 下载并安装
        dl_url = prereq["download_url"]
        filename = prereq["filename"]
        dest = os.path.join(DOWNLOAD_DIR, filename)

        if not os.path.exists(dest):
            self.callback(f"前置: {prereq_name}", "running", f"正在下载 {prereq_name}...")
            from core.downloader import Downloader
            dler = Downloader()
            try:
                dler.download(dl_url, filename)
            except Exception as e:
                self.callback(f"前置: {prereq_name}", "error", str(e))
                return False

        # 安装
        install_type = prereq.get("install_type", "nsis")
        install_args = prereq.get("install_args", [])
        self.callback(f"前置: {prereq_name}", "running", f"正在安装 {prereq_name}...")

        if install_type == "msi":
            success = self._install_msi(dest, install_args)
        else:
            success = self._install_nsis(dest, install_args)

        if success:
            self.callback(f"前置: {prereq_name}", "ok", f"{prereq_name} 安装完成")
            time.sleep(2)
            return True
        else:
            self.callback(f"前置: {prereq_name}", "error", f"{prereq_name} 安装失败")
            return False

    def _install_nsis(self, path: str, args: list) -> bool:
        """NSIS/Inno 安装包静默安装"""
        try:
            cmd = [path] + args
            self._log_cmd(cmd)
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=600
            )
            ok = result.returncode == 0
            if not ok:
                logger.error(f"NSIS安装失败 (exit={result.returncode}): stderr={result.stderr[:200]}")
            return ok
        except subprocess.TimeoutExpired:
            logger.error(f"安装超时: {path}")
            return False
        except Exception as e:
            logger.error(f"安装异常: {e}")
            return False

    def _install_msi(self, path: str, args: list) -> bool:
        """MSI 安装包静默安装（通过 msiexec）"""
        try:
            cmd = ["msiexec", "/i", path] + args
            self._log_cmd(cmd)
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=600
            )
            ok = result.returncode in (0, 1641, 3010)
            if not ok:
                logger.error(f"MSI安装失败 (exit={result.returncode}): stdout={result.stdout[:200]}, stderr={result.stderr[:200]}")
            elif result.returncode in (1641, 3010):
                logger.info(f"MSI安装成功但需要重启 (exit={result.returncode})")
            return ok
        except subprocess.TimeoutExpired:
            logger.error(f"MSI安装超时: {path}")
            return False
        except Exception as e:
            logger.error(f"MSI安装异常: {e}")
            return False

    def _install_npm(self, command: str) -> bool:
        """通过 npm install -g 安装"""
        try:
            self._log_cmd(command)
            from core.validator import Validator
            result = subprocess.run(
                command, shell=True,
                capture_output=True, text=True, timeout=300,
                env={**os.environ, "PATH": Validator._get_extended_path()}
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"npm安装异常: {e}")
            return False

    def _install_pip(self, command: str) -> bool:
        """通过 pip install 安装"""
        try:
            self._log_cmd(command)
            from core.validator import Validator
            result = subprocess.run(
                command, shell=True,
                capture_output=True, text=True, timeout=300,
                env={**os.environ, "PATH": Validator._get_extended_path()}
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"pip安装异常: {e}")
            return False

    def _install_exe(self, path: str, args: list) -> bool:
        """通用 exe 安装"""
        try:
            cmd = [path] + args
            self._log_cmd(cmd)
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=600
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"exe安装异常: {e}")
            return False

    @staticmethod
    def _check_installed(check_paths: list) -> bool:
        """检查文件是否存在"""
        for p in check_paths:
            expanded = os.path.expandvars(p)
            matches = glob.glob(expanded) if glob.has_magic(expanded) else [expanded]
            if any(os.path.exists(path) for path in matches):
                return True
        return False

    @staticmethod
    def _log_cmd(cmd):
        cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd
        logger.info(f"执行: {cmd_str}")
