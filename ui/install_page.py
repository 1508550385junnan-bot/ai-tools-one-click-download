# ui/install_page.py - 安装进度页面
# v2.0: 安装完成后自动打开命令行窗口验证版本
import os
import subprocess
import threading
import customtkinter as ctk
from config import (
    CARD_BG, TEXT_COLOR, TEXT_SECONDARY, ACCENT_COLOR,
    SUCCESS_COLOR, WARNING_COLOR, ERROR_COLOR,
    DOWNLOAD_DIR
)
from tools.registry import TOOLS
from core.downloader import Downloader
from core.installer import Installer
from core.validator import Validator


class InstallPage(ctk.CTkFrame):
    """安装进度页面"""

    def __init__(self, master, on_done=None, on_back=None):
        super().__init__(master, fg_color="transparent")
        self.on_done = on_done
        self.on_back = on_back
        self.is_running = False
        self.step_widgets = []
        self.installed_tools = []  # 记录已安装的工具，用于最后打开cmd验证
        self._build_ui()

    def _build_ui(self):
        # 标题
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))

        self.title_label = ctk.CTkLabel(
            header, text="安装进行中",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_COLOR,
        )
        self.title_label.pack(side="left")

        self.progress_bar = ctk.CTkProgressBar(
            header, width=300, height=12,
            fg_color=CARD_BG,
            progress_color=ACCENT_COLOR,
        )
        self.progress_bar.pack(side="right", padx=10)
        self.progress_bar.set(0)

        self.progress_text = ctk.CTkLabel(
            header, text="0%",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
        )
        self.progress_text.pack(side="right", padx=5)

        # 步骤列表
        self.steps_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=ACCENT_COLOR,
        )
        self.steps_frame.pack(fill="both", expand=True, padx=25, pady=10)

        # 底部按钮
        bottom = ctk.CTkFrame(self, fg_color=CARD_BG, height=50)
        bottom.pack(fill="x", padx=0, pady=0)
        bottom.pack_propagate(False)

        self.back_btn = ctk.CTkButton(
            bottom, text="← 返回",
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            text_color=ACCENT_COLOR,
            hover_color=CARD_BG,
            height=30, width=80,
            command=self._on_back,
        )
        self.back_btn.pack(side="left", padx=15)

        self.result_label = ctk.CTkLabel(
            bottom, text="",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_SECONDARY,
        )
        self.result_label.pack(side="left", padx=15)

    def start_install(self, tool_keys: list):
        """开始安装所选工具"""
        self.is_running = True
        self._clear_steps()
        self.progress_bar.set(0)
        self.progress_text.configure(text="0%")
        self.title_label.configure(text=f"正在安装 {len(tool_keys)} 个工具")

        # 记录本批次要安装的工具
        self._batch_tools = list(tool_keys)

        # 初始化步骤
        total_steps = []
        for key in tool_keys:
            tool = TOOLS[key]
            prereqs = tool.get("prerequisites", [])
            total_steps.append(f"🚀 {tool['name']}")
            if prereqs:
                for p in prereqs:
                    total_steps.append(f"  ├─ 前置: {p}")
            total_steps.append(f"  ├─ 下载 {tool['name']}")
            total_steps.append(f"  ├─ 安装 {tool['name']}")
            total_steps.append(f"  └─ 验证 {tool['name']}")

        self.total_step_count = len(total_steps)
        self._init_step_widgets(total_steps)

        # 后台执行
        thread = threading.Thread(
            target=self._run_install, args=(tool_keys,), daemon=True
        )
        thread.start()

    def _init_step_widgets(self, steps):
        for i, text in enumerate(steps):
            frame = ctk.CTkFrame(
                self.steps_frame, fg_color=CARD_BG,
                corner_radius=6,
            )
            frame.pack(fill="x", pady=2)

            ctk.CTkLabel(
                frame, text=f"{i+1:02d}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=TEXT_SECONDARY,
                width=30,
            ).pack(side="left", padx=(10, 5), pady=8)

            icon_label = ctk.CTkLabel(
                frame, text="⏳",
                font=ctk.CTkFont(size=14),
                text_color=TEXT_SECONDARY,
                width=25,
            )
            icon_label.pack(side="left", pady=8)

            text_label = ctk.CTkLabel(
                frame, text=text,
                font=ctk.CTkFont(size=13),
                text_color=TEXT_COLOR,
                anchor="w",
            )
            text_label.pack(side="left", fill="x", expand=True, padx=5, pady=8)

            detail_label = ctk.CTkLabel(
                frame, text="等待中...",
                font=ctk.CTkFont(size=11),
                text_color=TEXT_SECONDARY,
                anchor="e",
            )
            detail_label.pack(side="right", padx=10, pady=8)

            self.step_widgets.append({
                "frame": frame,
                "icon": icon_label,
                "text": text_label,
                "detail": detail_label,
            })

    def _clear_steps(self):
        for w in self.step_widgets:
            w["frame"].destroy()
        self.step_widgets = []
        self.current_step_idx = 0

    def _update_step(self, index, status, detail=""):
        if index >= len(self.step_widgets):
            return

        w = self.step_widgets[index]
        icons = {"running": "🔄", "ok": "✅", "error": "❌", "skip": "⏭️"}
        colors = {
            "running": WARNING_COLOR,
            "ok": SUCCESS_COLOR,
            "error": ERROR_COLOR,
            "skip": TEXT_SECONDARY,
        }

        w["icon"].configure(text=icons.get(status, "⏳"))
        w["detail"].configure(
            text=detail[:60] if detail else "",
            text_color=colors.get(status, TEXT_SECONDARY),
        )

        # 更新进度条
        completed = sum(
            1 for i in range(len(self.step_widgets))
            if i < index or (i == index and status == "ok")
        )
        pct = min(completed / max(self.total_step_count, 1), 1.0)
        self.progress_bar.set(pct)
        self.progress_text.configure(text=f"{int(pct*100)}%")

    def _run_install(self, tool_keys):
        """后台执行安装流程"""
        downloader = Downloader()
        installer = Installer(status_callback=self._safe_update)
        validator = Validator(status_callback=self._safe_update)

        step_idx = 0
        all_ok = True

        for tool_key in tool_keys:
            tool = TOOLS[tool_key]
            tool_name = tool["name"]

            # --- 前置环境 ---
            prereqs = tool.get("prerequisites", [])
            for prereq_key in prereqs:
                self._safe_update(f"前置环境: {prereq_key}", "running",
                                  f"检查/安装 {prereq_key}...")
                ok = installer.install_prerequisite(prereq_key)
                self._safe_update(
                    f"前置环境: {prereq_key}",
                    "ok" if ok else "error",
                    f"{'已安装' if ok else '安装失败'}",
                )
                step_idx += 1

            # --- 下载（npm/pip 类型跳过） ---
            install_type = tool.get("install", {}).get("type", "nsis")
            downloads = tool.get("downloads", [])

            if install_type not in ("npm", "pip") and downloads:
                dl = downloads[0]
                filename = dl["filename"]
                url = dl["url"]

                self._safe_update(f"下载 {tool_name}", "running",
                                  f"连接服务器...")

                def progress_cb(downloaded, total, speed):
                    if total > 0:
                        pct = downloaded / total * 100
                        mb = downloaded / 1024 / 1024
                        total_mb = total / 1024 / 1024
                        self._safe_update(
                            f"下载 {tool_name}", "running",
                            f"{pct:.0f}% | {mb:.1f}/{total_mb:.1f}MB | {speed:.0f}KB/s"
                        )
                    else:
                        mb = downloaded / 1024 / 1024
                        self._safe_update(
                            f"下载 {tool_name}", "running",
                            f"{mb:.1f}MB | {speed:.0f}KB/s"
                        )

                try:
                    downloader.download(url, filename,
                                        progress_callback=progress_cb)
                    self._safe_update(f"下载 {tool_name}", "ok",
                                      f"下载完成 ({filename})")
                except Exception as e:
                    self._safe_update(f"下载 {tool_name}", "error", str(e)[:50])
                    all_ok = False
                    step_idx += 1
                    continue

            step_idx += 1

            # --- 安装 ---
            self._safe_update(f"安装 {tool_name}", "running", "执行静默安装...")
            try:
                ok = installer.install_tool(tool_key, tool)
                if ok:
                    self._safe_update(f"安装 {tool_name}", "ok",
                                      f"{tool_name} 安装成功")
                    self.installed_tools.append(tool_key)
                else:
                    self._safe_update(f"安装 {tool_name}", "error",
                                      "安装返回失败")
                    all_ok = False
            except Exception as e:
                self._safe_update(f"安装 {tool_name}", "error", str(e)[:50])
                all_ok = False
            step_idx += 1

            # --- 验证 ---
            self._safe_update(f"验证 {tool_name}", "running", "检测版本...")
            try:
                vresult = validator.verify(tool_key, tool)
                if vresult["success"]:
                    ver = vresult.get("version", "OK")[:40]
                    self._safe_update(f"验证 {tool_name}", "ok",
                                      f"版本: {ver}")
                else:
                    self._safe_update(f"验证 {tool_name}", "warning",
                                      f"{vresult.get('error', '验证失败')[:50]}")
            except Exception as e:
                self._safe_update(f"验证 {tool_name}", "warning", str(e)[:50])
            step_idx += 1

        # 完成
        self._batch_all_ok = all_ok
        final_text = "✅ 全部安装完成!" if all_ok else "⚠️ 安装完成（部分可能失败）"
        self.after(0, lambda: self.result_label.configure(text=final_text))
        self.after(0, lambda: self.title_label.configure(text="安装完成"))
        self.is_running = False

        # 打开命令行验证窗口
        self._open_cmd_for_verification()

        # 通知完成
        if self.on_done:
            self.after(500, self.on_done)

    def _open_cmd_for_verification(self):
        """安装完成后自动打开命令行窗口，显示版本验证信息"""
        # 构建验证命令批处理脚本
        verify_cmds = []
        verify_cmds.append("@echo off")
        verify_cmds.append("title AI工具一键下载 - 版本验证")
        verify_cmds.append("echo ========================================")
        verify_cmds.append("echo   AI 工具一键下载 v2.0 - 版本验证")
        verify_cmds.append("echo   作者: 大虎子")
        verify_cmds.append("echo ========================================")
        verify_cmds.append("echo.")

        for tool_key in self.installed_tools:
            tool = TOOLS.get(tool_key, {})
            name = tool.get("name", tool_key)
            verify = tool.get("verify", {})
            command = verify.get("command")
            if command:
                verify_cmds.append(f"echo --- {name} ---")
                verify_cmds.append(f"{command} 2^>^&1")
                verify_cmds.append("echo.")
            else:
                check_paths = tool.get("install", {}).get("check_paths", [])
                if check_paths:
                    verify_cmds.append(f"echo --- {name}: 检查安装文件 ---")
                    for p in check_paths:
                        verify_cmds.append(f"if exist \"{p}\" (echo   [√] {p}) else (echo   [×] {p})")
                else:
                    verify_cmds.append(f"echo --- {name}: GUI应用，请手动验证 ---")
                verify_cmds.append("echo.")

        verify_cmds.append("echo ========================================")
        verify_cmds.append("echo   验证完成！按任意键关闭此窗口")
        verify_cmds.append("echo ========================================")
        verify_cmds.append("pause > nul")

        try:
            # 写入临时批处理文件
            bat_path = os.path.join(os.environ.get("TEMP", "."), "ai_tools_verify.bat")
            with open(bat_path, "w", encoding="gbk") as f:
                f.write("\r\n".join(verify_cmds))

            # 打开新的命令窗口执行验证
            subprocess.Popen(
                ["cmd", "/k", bat_path],
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0,
            )
        except Exception as e:
            # 如果打开cmd失败，至少尝试用start命令
            try:
                subprocess.Popen(
                    ["cmd", "/c", "start", "cmd", "/k", bat_path],
                    shell=True,
                )
            except Exception:
                pass  # 静默失败，不影响主流程

    def _safe_update(self, step_name, status, detail=""):
        """线程安全的UI更新"""
        idx = None
        for i, w in enumerate(self.step_widgets):
            widget_text = w["text"].cget("text")
            if step_name in widget_text:
                idx = i
                break

        if idx is not None:
            self.after(0, lambda: self._update_step(idx, status, detail))
        else:
            self.after(0, lambda: self._add_runtime_step(step_name, status, detail))

    def _add_runtime_step(self, step_name, status, detail):
        """动态添加运行时步骤"""
        frame = ctk.CTkFrame(
            self.steps_frame, fg_color=CARD_BG,
            corner_radius=6,
        )
        frame.pack(fill="x", pady=2)

        idx = len(self.step_widgets)
        ctk.CTkLabel(
            frame, text=f"{idx+1:02d}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_SECONDARY, width=30,
        ).pack(side="left", padx=(10, 5), pady=8)

        icon_label = ctk.CTkLabel(
            frame, text="✅" if status == "ok" else "🔄",
            font=ctk.CTkFont(size=14),
            text_color=SUCCESS_COLOR if status == "ok" else WARNING_COLOR,
            width=25,
        )
        icon_label.pack(side="left", pady=8)

        text_label = ctk.CTkLabel(
            frame, text=step_name,
            font=ctk.CTkFont(size=13),
            text_color=TEXT_COLOR, anchor="w",
        )
        text_label.pack(side="left", fill="x", expand=True, padx=5, pady=8)

        detail_label = ctk.CTkLabel(
            frame, text=detail[:60],
            font=ctk.CTkFont(size=11),
            text_color=TEXT_SECONDARY, anchor="e",
        )
        detail_label.pack(side="right", padx=10, pady=8)

        self.step_widgets.append({
            "frame": frame,
            "icon": icon_label,
            "text": text_label,
            "detail": detail_label,
        })

    def _on_back(self):
        self.is_running = False
        if self.on_back:
            self.on_back()
