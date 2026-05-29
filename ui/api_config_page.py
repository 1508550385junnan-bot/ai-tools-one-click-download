# ui/api_config_page.py - API 模型一键配置页面
# v2.4: 支持 Claude Code / Hermes Agent 配置主流模型厂家 API
import threading
import customtkinter as ctk
from config import (
    CARD_BG, TEXT_COLOR, TEXT_SECONDARY, ACCENT_COLOR,
    SUCCESS_COLOR, WARNING_COLOR, ERROR_COLOR, THEME_COLOR,
)
from core.api_configurator import PROVIDERS, SUPPORTED_APPS, try_configure, test_api_connection


class APIConfigPage(ctk.CTkFrame):
    """API 模型配置页面"""

    def __init__(self, master, on_back=None):
        super().__init__(master, fg_color="transparent")
        self.on_back = on_back
        self.selected_app = None     # claude-code / hermes-agent
        self.selected_provider = None
        self.selected_model = None
        self._build_ui()

    def _build_ui(self):
        # 标题栏
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))

        self.back_btn = ctk.CTkButton(
            header, text="← 返回",
            font=ctk.CTkFont(size=12),
            fg_color="transparent", text_color=ACCENT_COLOR,
            hover_color=CARD_BG, width=80, height=30,
            command=self._on_back,
        )
        self.back_btn.pack(side="left")

        ctk.CTkLabel(
            header, text="API 模型一键配置",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_COLOR,
        ).pack(side="left", padx=20)

        # 主内容（可滚动）
        scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=ACCENT_COLOR,
        )
        scroll.pack(fill="both", expand=True, padx=25, pady=10)

        # === 步骤1: 选择程序 ===
        ctk.CTkLabel(
            scroll, text="▎步骤 1: 选择要配置的程序",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=ACCENT_COLOR,
        ).pack(anchor="w", pady=(10, 8))

        app_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        app_frame.pack(fill="x")

        self.app_buttons = {}
        for app_key, app in SUPPORTED_APPS.items():
            card = ctk.CTkFrame(
                app_frame, fg_color=CARD_BG,
                corner_radius=10, border_width=1, border_color="#2a2a4a",
            )
            card.pack(side="left", padx=5, pady=5, fill="x", expand=True)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(padx=15, pady=12, fill="x")

            ctk.CTkLabel(
                inner, text=f"{app['icon']} {app['name']}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=TEXT_COLOR if app["configurable"] else TEXT_SECONDARY,
            ).pack(anchor="w")

            ctk.CTkLabel(
                inner, text=app["hint"],
                font=ctk.CTkFont(size=11),
                text_color=TEXT_SECONDARY,
            ).pack(anchor="w", pady=(2, 8))

            if app["configurable"]:
                btn = ctk.CTkButton(
                    inner, text="选择",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    fg_color=CARD_BG, text_color=ACCENT_COLOR,
                    border_width=1, border_color=ACCENT_COLOR,
                    hover_color="#2a2a5a", height=30, width=80,
                    corner_radius=6,
                    command=lambda k=app_key: self._select_app(k),
                )
            else:
                btn = ctk.CTkButton(
                    inner, text="不支持",
                    font=ctk.CTkFont(size=12),
                    fg_color="transparent", text_color=TEXT_SECONDARY,
                    border_width=1, border_color="#3a3a5a",
                    hover_color=CARD_BG, height=30, width=80,
                    corner_radius=6, state="disabled",
                )
            btn.pack()
            self.app_buttons[app_key] = (card, btn)

        # === 步骤2: 选择模型厂家 ===
        ctk.CTkLabel(
            scroll, text="▎步骤 2: 选择模型厂家",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=ACCENT_COLOR,
        ).pack(anchor="w", pady=(25, 8))

        self.providers_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.providers_frame.pack(fill="x")

        self.provider_buttons = {}
        for i, (prov_key, prov) in enumerate(PROVIDERS.items()):
            row_frame = ctk.CTkFrame(self.providers_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)

            card = ctk.CTkFrame(
                row_frame, fg_color=CARD_BG,
                corner_radius=8, border_width=1, border_color="#2a2a4a",
            )
            card.pack(fill="x")

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(padx=15, pady=10, fill="x")

            ctk.CTkLabel(
                inner, text=f"{prov['icon']}  {prov['name']}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=TEXT_COLOR,
            ).pack(side="left")

            ctk.CTkLabel(
                inner, text=prov["desc"],
                font=ctk.CTkFont(size=11),
                text_color=TEXT_SECONDARY,
            ).pack(side="left", padx=15)

            btn = ctk.CTkButton(
                inner, text="选择此厂家",
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=CARD_BG, text_color=ACCENT_COLOR,
                border_width=1, border_color=ACCENT_COLOR,
                hover_color="#2a2a5a", height=30, width=90,
                corner_radius=6,
                command=lambda k=prov_key: self._select_provider(k),
            )
            btn.pack(side="right")
            self.provider_buttons[prov_key] = (card, btn)

        # 兼容性警告（当选择 Claude Code + 非 Anthropic 厂家时显示）
        self.compat_warning = ctk.CTkLabel(
            scroll, text="",
            font=ctk.CTkFont(size=12),
            text_color=WARNING_COLOR,
            justify="left",
        )

        # === 步骤3: 输入模型、Base URL、API Key ===
        ctk.CTkLabel(
            scroll, text="▎步骤 3: 确认模型、Base URL 并一键配置",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=ACCENT_COLOR,
        ).pack(anchor="w", pady=(25, 8))

        key_frame = ctk.CTkFrame(scroll, fg_color=CARD_BG, corner_radius=10)
        key_frame.pack(fill="x", pady=(0, 15))

        key_inner = ctk.CTkFrame(key_frame, fg_color="transparent")
        key_inner.pack(padx=20, pady=15, fill="x")

        ctk.CTkLabel(
            key_inner, text="模型:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_COLOR,
        ).pack(anchor="w")

        self.model_menu = ctk.CTkOptionMenu(
            key_inner, values=["请先选择厂家"],
            font=ctk.CTkFont(size=13),
            fg_color="#0d1b2a",
            button_color=ACCENT_COLOR,
            button_hover_color="#0099cc",
            text_color=TEXT_COLOR,
            height=36,
            command=self._select_model,
        )
        self.model_menu.pack(fill="x", pady=(8, 12))
        self.model_menu.set("请先选择厂家")

        ctk.CTkLabel(
            key_inner, text="Base URL:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_COLOR,
        ).pack(anchor="w")

        self.base_url_entry = ctk.CTkEntry(
            key_inner, font=ctk.CTkFont(size=13),
            fg_color="#0d1b2a", text_color=TEXT_COLOR,
            border_color=ACCENT_COLOR, border_width=1,
            height=38, placeholder_text="https://api.example.com/v1",
        )
        self.base_url_entry.pack(fill="x", pady=(8, 12))

        ctk.CTkLabel(
            key_inner, text="API Key:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_COLOR,
        ).pack(anchor="w")

        self.api_key_entry = ctk.CTkEntry(
            key_inner, font=ctk.CTkFont(size=13),
            fg_color="#0d1b2a", text_color=TEXT_COLOR,
            border_color=ACCENT_COLOR, border_width=1,
            height=38, placeholder_text="sk-... 或您的 API Key",
            show="*",  # 密码模式
        )
        self.api_key_entry.pack(fill="x", pady=(8, 12))

        # 配置按钮
        self.config_btn = ctk.CTkButton(
            key_inner, text="⚡ 一键配置",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=SUCCESS_COLOR, hover_color="#00cc66",
            text_color="#0a0a1a", height=46,
            corner_radius=10,
            command=self._on_configure,
        )
        self.config_btn.pack(fill="x", pady=(5, 0))

        # === 状态显示 ===
        self.status_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.status_frame.pack(fill="x", pady=(0, 20))

        self.status_label = ctk.CTkLabel(
            self.status_frame, text="",
            font=ctk.CTkFont(size=13), text_color=TEXT_SECONDARY,
            justify="left",
        )
        self.status_label.pack(anchor="w")

    def _select_app(self, app_key):
        """选择要配置的程序"""
        for key, (card, btn) in self.app_buttons.items():
            card.configure(border_color="#2a2a4a")
            if SUPPORTED_APPS[key]["configurable"]:
                btn.configure(fg_color=CARD_BG, text_color=ACCENT_COLOR)

        card, btn = self.app_buttons[app_key]
        card.configure(border_color=ACCENT_COLOR)
        btn.configure(fg_color=ACCENT_COLOR, text_color="#0a0a1a")
        self.selected_app = app_key

        # Claude Code 选择时 — 提示 relay
        if app_key == "claude-code":
            if "anthropic" in self.provider_buttons:
                card, btn = self.provider_buttons["anthropic"]
                card.configure(border_color=SUCCESS_COLOR, border_width=2)

            self.compat_warning.configure(
                text="💡 Anthropic 官方：开箱即用。\n"
                     "   其他厂家：需通过 API 中继服务（OpenRouter/SiliconFlow 等）转发。\n"
                     "   环境变量和配置文件会自动设置。",
            )
            self.compat_warning.pack(anchor="w", pady=(10, 0))
        else:
            if "anthropic" in self.provider_buttons:
                card, btn = self.provider_buttons["anthropic"]
                card.configure(border_color="#2a2a4a", border_width=1)
            self.compat_warning.pack_forget()

    def _select_provider(self, prov_key):
        """选择模型厂家"""
        for key, (card, btn) in self.provider_buttons.items():
            card.configure(border_color="#2a2a4a")
            btn.configure(fg_color=CARD_BG, text_color=ACCENT_COLOR)

        card, btn = self.provider_buttons[prov_key]
        card.configure(border_color=ACCENT_COLOR)
        btn.configure(fg_color=ACCENT_COLOR, text_color="#0a0a1a")
        self.selected_provider = prov_key
        provider = PROVIDERS[prov_key]
        models = provider.get("models", ["custom-model"])
        self.selected_model = models[0]
        self.model_menu.configure(values=models)
        self.model_menu.set(models[0])

        if self.selected_app == "claude-code":
            base_url = provider.get("claude_base_url") or provider.get("base_url") or ""
        else:
            base_url = provider.get("base_url") or ""
        self.base_url_entry.delete(0, "end")
        self.base_url_entry.insert(0, base_url)
        self.update()

        # Claude Code + 非 Anthropic → relay 提示
        if self.selected_app == "claude-code" and prov_key != "anthropic":
            if provider["claude_compat"]:
                # 已验证有 Anthropic 端点
                self.compat_warning.configure(
                    text=f"✅ {provider['name']} 已验证支持 Anthropic 格式。\n"
                         f"   可直接用于 Claude Code，无需 relay。",
                )
            else:
                self.compat_warning.configure(
                    text=f"💡 {provider['name']} 需 API 中继服务转发。\n"
                         f"   BASE_URL 已设为 {provider['base_url']}\n"
                         "   若直连不通，请填入 relay 服务地址。",
                )
                self.compat_warning.pack(anchor="w", pady=(10, 0))

    def _select_model(self, model):
        """选择模型"""
        self.selected_model = model

    def _on_configure(self):
        """执行配置"""
        if not self.selected_app:
            self._show_status("请先选择要配置的程序（步骤1）", WARNING_COLOR)
            return
        if not self.selected_provider:
            self._show_status("请先选择模型厂家（步骤2）", WARNING_COLOR)
            return

        api_key = self.api_key_entry.get().strip()
        if not api_key:
            self._show_status("请输入 API Key（步骤3）", WARNING_COLOR)
            return

        model = self.selected_model
        base_url = self.base_url_entry.get().strip()

        self.config_btn.configure(state="disabled", text="配置中...")
        self._show_status("正在配置，请稍候...", WARNING_COLOR)

        def _do():
            result = try_configure(self.selected_app, self.selected_provider, api_key, model, base_url)
            self.after(0, lambda: self._on_result(result))

        threading.Thread(target=_do, daemon=True).start()

    def _on_result(self, result):
        """配置结果处理"""
        self.config_btn.configure(state="normal", text="⚡ 一键配置")
        if result["success"]:
            self._show_status(result["message"], SUCCESS_COLOR)
            # 自动测试连接
            self._run_api_test()
        else:
            self._show_status(f"配置失败: {result.get('error', '未知错误')}", ERROR_COLOR)

    def _run_api_test(self):
        """后台测试 API 连接"""
        api_key = self.api_key_entry.get().strip()
        model = self.selected_model
        base_url = self.base_url_entry.get().strip()
        prov_key = self.selected_provider

        self._show_status(
            self.status_label.cget("text") + "\n\n🔍 正在测试 API 连接...",
            WARNING_COLOR
        )

        def _do():
            result = test_api_connection(prov_key, api_key, model, base_url)
            self.after(0, lambda: self._on_test_result(result))

        threading.Thread(target=_do, daemon=True).start()

    def _on_test_result(self, result):
        """API 测试结果显示"""
        prev = self.status_label.cget("text").split("\n\n🔍")[0]
        if result["ok"]:
            self._show_status(
                f"{prev}\n\n✅ API 测试通过: {result['message']}",
                SUCCESS_COLOR
            )
        else:
            self._show_status(
                f"{prev}\n\n❌ API 测试失败: {result['message']}\n"
                f"请检查 API Key 和网络后重新配置",
                ERROR_COLOR
            )

    def _show_status(self, text, color):
        self.status_label.configure(text=text, text_color=color)

    def _on_back(self):
        if self.on_back:
            self.on_back()
