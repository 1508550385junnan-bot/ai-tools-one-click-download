# ui/main_window.py - 主窗口
# v2.2: 右上角版本+更新提醒，自动检查更新
import threading
import urllib.request
import json
import customtkinter as ctk
from config import (
    APP_TITLE, APP_VERSION, APP_AUTHOR,
    WINDOW_WIDTH, WINDOW_HEIGHT,
    THEME_COLOR, ACCENT_COLOR, TEXT_COLOR, TEXT_SECONDARY,
    SUCCESS_COLOR, WARNING_COLOR, CARD_BG,
    UPDATE_CHECK_URL,
)
from ui.select_page import ToolSelectPage
from ui.sponsor_page import SponsorPage
from ui.install_page import InstallPage


class MainWindow(ctk.CTk):
    """主窗口 - 页面路由"""

    def __init__(self, installed_versions=None):
        super().__init__()

        self.installed_versions = installed_versions or {}

        # 窗口配置
        self.title(f"{APP_TITLE} v{APP_VERSION} — {APP_AUTHOR}")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        # 居中
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - WINDOW_WIDTH) // 2
        y = (sh - WINDOW_HEIGHT) // 2
        self.geometry(f"+{x}+{y}")

        self.resizable(False, False)

        # 主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=THEME_COLOR)

        # 页面容器
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.pages = {}
        self.current_page = None
        self.selected_tools = []
        self._is_single_install = False
        self._single_tool_key = None
        self._update_available = None  # 更新信息

        self._init_pages()
        self.show_page("select")

        # 后台检查更新
        self._check_update_async()

    def _init_pages(self):
        """初始化所有页面"""
        select = ToolSelectPage(
            self.container,
            on_install=self._on_tools_selected,
            on_single_install=self._on_single_tool_click,
            installed_versions=self.installed_versions,
        )
        self.pages["select"] = select

        sponsor = SponsorPage(
            self.container,
            on_sponsor_done=self._on_sponsor_done,
            on_back=lambda: self.show_page("select"),
        )
        self.pages["sponsor"] = sponsor

        install = InstallPage(
            self.container,
            on_done=lambda: self._on_install_done(),
            on_back=lambda: self.show_page("select"),
        )
        self.pages["install"] = install

        # 在 select 页面上叠加更新栏（右上角）
        self._add_update_bar(select)

    def _add_update_bar(self, select_page):
        """在选择页右上角添加版本+更新区域"""
        bar = ctk.CTkFrame(select_page, fg_color="transparent", height=30)
        bar.place(relx=1.0, rely=0.0, x=-30, y=10, anchor="ne")

        # 版本标签
        self.version_label = ctk.CTkLabel(
            bar, text=f"v{APP_VERSION}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_SECONDARY,
        )
        self.version_label.pack(side="left", padx=(0, 5))

        # 检查更新按钮
        self.update_btn = ctk.CTkButton(
            bar, text="检查更新",
            font=ctk.CTkFont(size=10),
            fg_color="transparent",
            text_color=ACCENT_COLOR,
            hover_color=CARD_BG,
            border_width=1,
            border_color=ACCENT_COLOR,
            width=70, height=24,
            corner_radius=6,
            command=self._manual_check_update,
        )
        self.update_btn.pack(side="left")

    def _check_update_async(self):
        """后台自动检查更新"""
        if not UPDATE_CHECK_URL:
            return  # 未配置更新URL

        def _do():
            try:
                info = self._fetch_update_info()
                if info:
                    self._update_available = info
                    self.after(0, self._show_update_badge)
            except Exception:
                pass  # 静默失败，不影响主流程

        threading.Thread(target=_do, daemon=True).start()

    def _fetch_update_info(self):
        """从远程获取版本信息"""
        if not UPDATE_CHECK_URL:
            return None

        req = urllib.request.Request(UPDATE_CHECK_URL)
        req.add_header("User-Agent", f"AI-Tools-Installer/{APP_VERSION}")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                remote_ver = data.get("version", "")
                if remote_ver and remote_ver != APP_VERSION:
                    return data
        except Exception:
            pass
        return None

    def _show_update_badge(self):
        """显示更新提示"""
        if not self._update_available:
            return

        info = self._update_available
        new_ver = info.get("version", "")
        changelog = info.get("changelog", "")

        self.update_btn.configure(
            text=f"v{new_ver} 可用",
            fg_color=WARNING_COLOR,
            text_color="#0a0a1a",
            border_color=WARNING_COLOR,
        )
        self.version_label.configure(text=f"v{APP_VERSION} →", text_color=WARNING_COLOR)

        # 弹窗提示
        self._show_update_dialog(info)

    def _show_update_dialog(self, info):
        """显示更新弹窗"""
        new_ver = info.get("version", "")
        changelog = info.get("changelog", "暂无更新说明")
        download_url = info.get("download_url", "")

        dialog = ctk.CTkToplevel(self)
        dialog.title("发现新版本")
        dialog.geometry("400x280")
        dialog.resizable(False, False)
        dialog.configure(fg_color=THEME_COLOR)
        dialog.transient(self)
        dialog.grab_set()

        # 居中
        dialog.update_idletasks()
        dw = 400
        dh = 280
        sx = (self.winfo_screenwidth() - dw) // 2
        sy = (self.winfo_screenheight() - dh) // 2
        dialog.geometry(f"+{sx}+{sy}")

        ctk.CTkLabel(
            dialog, text="🎉 发现新版本",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_COLOR,
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            dialog, text=f"当前: v{APP_VERSION}  →  最新: v{new_ver}",
            font=ctk.CTkFont(size=14),
            text_color=ACCENT_COLOR,
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            dialog, text=f"更新内容:\n{changelog}",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
            justify="left",
        ).pack(pady=(0, 15))

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack()

        if download_url:
            ctk.CTkButton(
                btn_frame, text="📥 立即下载",
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=SUCCESS_COLOR,
                hover_color="#00cc66",
                text_color="#0a0a1a",
                width=140, height=36,
                corner_radius=8,
                command=lambda: self._open_download_url(download_url, dialog),
            ).pack(side="left", padx=10)
        else:
            ctk.CTkLabel(
                btn_frame, text="请访问发布页下载最新版本",
                font=ctk.CTkFont(size=12),
                text_color=TEXT_SECONDARY,
            ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame, text="稍后再说",
            font=ctk.CTkFont(size=13),
            fg_color=CARD_BG,
            hover_color="#2a2a5a",
            text_color=TEXT_SECONDARY,
            width=100, height=36,
            corner_radius=8,
            command=dialog.destroy,
        ).pack(side="left", padx=10)

    def _open_download_url(self, url, dialog):
        """打开下载链接"""
        import webbrowser
        webbrowser.open(url)
        dialog.destroy()

    def _manual_check_update(self):
        """手动检查更新"""
        if not UPDATE_CHECK_URL:
            self._show_info_dialog(
                "更新功能未配置",
                "请在 config.py 中设置 UPDATE_CHECK_URL，\n"
                "指向你的远程 version.json 文件。\n\n"
                "格式示例:\n"
                '{"version": "2.3", '
                '"download_url": "https://...", '
                '"changelog": "..."}'
            )
            return

        self.update_btn.configure(text="检查中...", state="disabled")
        self.update()

        def _do():
            try:
                info = self._fetch_update_info()
                if info and info.get("version") != APP_VERSION:
                    self._update_available = info
                    self.after(0, self._show_update_badge)
                else:
                    self.after(0, lambda: self.update_btn.configure(
                        text="检查更新", state="normal",
                        fg_color="transparent",
                        text_color=ACCENT_COLOR,
                        border_color=ACCENT_COLOR,
                    ))
                    self.after(0, lambda: self._show_info_dialog(
                        "已是最新版本",
                        f"当前版本 v{APP_VERSION} 已是最新。"
                    ))
            except Exception as e:
                self.after(0, lambda: self.update_btn.configure(
                    text="检查更新", state="normal",
                    fg_color="transparent",
                    text_color=ACCENT_COLOR,
                    border_color=ACCENT_COLOR,
                ))
                self.after(0, lambda: self._show_info_dialog(
                    "检查失败",
                    f"无法连接到更新服务器:\n{str(e)[:100]}"
                ))

        threading.Thread(target=_do, daemon=True).start()

    def _show_info_dialog(self, title, message):
        """显示信息弹窗"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("380x200")
        dialog.resizable(False, False)
        dialog.configure(fg_color=THEME_COLOR)
        dialog.transient(self)
        dialog.grab_set()

        dialog.update_idletasks()
        dw, dh = 380, 200
        sx = (self.winfo_screenwidth() - dw) // 2
        sy = (self.winfo_screenheight() - dh) // 2
        dialog.geometry(f"+{sx}+{sy}")

        ctk.CTkLabel(
            dialog, text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT_COLOR,
        ).pack(pady=(20, 10))

        ctk.CTkLabel(
            dialog, text=message,
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
            justify="left",
        ).pack(pady=(0, 15))

        ctk.CTkButton(
            dialog, text="确定",
            font=ctk.CTkFont(size=13),
            fg_color=ACCENT_COLOR,
            text_color="#0a0a1a",
            width=80, height=32,
            corner_radius=8,
            command=dialog.destroy,
        ).pack()

    # ---- 页面路由 ----

    def show_page(self, page_name: str):
        if self.current_page:
            self.current_page.pack_forget()

        page = self.pages.get(page_name)
        if page:
            page.pack(fill="both", expand=True)
            self.current_page = page

    def _on_single_tool_click(self, tool_key: str):
        self._is_single_install = True
        self._single_tool_key = tool_key
        self.show_page("sponsor")
        self.pages["sponsor"].show_for_tool(tool_key)

    def _on_tools_selected(self, tool_keys: list):
        self._is_single_install = False
        self.selected_tools = tool_keys
        self._current_install_idx = 0
        self._show_sponsor_for_next()

    def _show_sponsor_for_next(self):
        if self._current_install_idx >= len(self.selected_tools):
            self.show_page("select")
            return
        tool_key = self.selected_tools[self._current_install_idx]
        self.show_page("sponsor")
        self.pages["sponsor"].show_for_tool(tool_key)

    def _on_sponsor_done(self, tool_key: str, success: bool):
        if not success:
            self.show_page("select")
            return
        tools_to_install = [tool_key]
        if not self._is_single_install:
            self._current_install_idx += 1
        self.show_page("install")
        self.pages["install"].start_install(tools_to_install)

    def _on_install_done(self):
        installed = self.pages["install"].installed_tools
        for tool_key in installed:
            new_ver = self._detect_single_version(tool_key)
            self.installed_versions[tool_key] = new_ver
            self.pages["select"].update_tool_status(tool_key, new_ver)

        if self._is_single_install:
            self._is_single_install = False
            self.show_page("select")
        else:
            self._show_sponsor_for_next()

    def _detect_single_version(self, tool_key: str):
        from core.validator import Validator
        from tools.registry import TOOLS
        tool = TOOLS.get(tool_key)
        if not tool:
            return None
        v = Validator()
        result = v.verify(tool_key, tool)
        if result["success"]:
            return result.get("version", "已安装")
        return None

    def run(self):
        self.mainloop()
