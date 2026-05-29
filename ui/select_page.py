# ui/select_page.py - 工具选择页面
# v2.2: 已安装按钮显示版本号，卡片显示详细版本信息
import customtkinter as ctk
from config import (
    CARD_BG, TEXT_COLOR, TEXT_SECONDARY, ACCENT_COLOR,
    SUCCESS_COLOR, WARNING_COLOR,
)
from tools.registry import TOOLS
from core.version_utils import is_upgrade_available


class ToolSelectPage(ctk.CTkFrame):
    """工具选择页面"""

    def __init__(self, master, on_install=None, on_single_install=None,
                 installed_versions=None):
        super().__init__(master, fg_color="transparent")
        self.on_install = on_install
        self.on_single_install = on_single_install
        self.installed_versions = installed_versions or {}
        self.latest_versions = {}
        self.tool_vars = {}
        self.tool_buttons = {}
        self.tool_desc_labels = {}
        self._build_ui()

    def _build_ui(self):
        # 标题
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))

        ctk.CTkLabel(
            header, text="选择要安装的工具",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_COLOR,
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text=f"共 {len(TOOLS)} 个工具 | 右侧按钮可一键安装",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
        ).pack(side="left", padx=15)

        # 工具卡片滚动区
        scroll_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=ACCENT_COLOR,
            scrollbar_button_hover_color="#0099cc",
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # 按分类分组
        categories = {}
        for key, tool in TOOLS.items():
            cat = tool.get("category", "其他")
            categories.setdefault(cat, []).append((key, tool))

        for cat, tools in categories.items():
            self._add_category_header(scroll_frame, cat)
            for tool_key, tool in tools:
                self._add_tool_card(scroll_frame, tool_key, tool)

        # 底部操作栏
        bottom = ctk.CTkFrame(self, fg_color=CARD_BG, height=60)
        bottom.pack(fill="x", padx=0, pady=0)
        bottom.pack_propagate(False)

        count_frame = ctk.CTkFrame(bottom, fg_color="transparent")
        count_frame.pack(side="left", padx=20)

        self.count_label = ctk.CTkLabel(
            count_frame, text="已选 0 个工具",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=ACCENT_COLOR,
        )
        self.count_label.pack(side="left")

        # 全选/取消
        self.select_all_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            count_frame, text="全选",
            variable=self.select_all_var,
            command=self._toggle_all,
            checkbox_width=18, checkbox_height=18,
            fg_color=ACCENT_COLOR,
            text_color=TEXT_COLOR,
            font=ctk.CTkFont(size=12),
        ).pack(side="left", padx=20)

        # 批量安装
        install_btn = ctk.CTkButton(
            bottom, text="批量安装",
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=ACCENT_COLOR,
            hover_color="#0099cc",
            text_color="#0a0a1a",
            height=40, width=160,
            corner_radius=8,
            command=self._on_install_click,
        )
        install_btn.pack(side="right", padx=20)

        from config import APP_VERSION
        ctk.CTkLabel(
            bottom, text=f"作者: 大虎子 | v{APP_VERSION}",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_SECONDARY,
        ).pack(side="right", padx=10)

    def _add_category_header(self, parent, cat_name):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=(12, 2))
        ctk.CTkLabel(
            frame, text=f"▎{cat_name}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=ACCENT_COLOR,
        ).pack(anchor="w")

    def _get_tool_status(self, tool_key, tool):
        """判断工具状态：'not_installed' / 'installed_latest' / 'upgrade_available'"""
        installed_ver = self.installed_versions.get(tool_key)
        if installed_ver is None:
            return "not_installed", None

        latest_ver = self._get_latest_version(tool_key, tool)
        if latest_ver is None:
            return "installed_latest", installed_ver

        if is_upgrade_available(installed_ver, latest_ver):
            return "upgrade_available", installed_ver
        else:
            return "installed_latest", installed_ver

    def _add_tool_card(self, parent, tool_key, tool):
        """添加工具卡片（v2.2: 按钮显示版本号）"""
        status, installed_ver = self._get_tool_status(tool_key, tool)
        latest_ver = self._get_latest_version(tool_key, tool)

        card = ctk.CTkFrame(
            parent, fg_color=CARD_BG,
            corner_radius=10, border_width=1,
            border_color="#2a2a4a",
        )
        card.pack(fill="x", padx=10, pady=4)

        # 左侧: 图标+勾选
        left = ctk.CTkFrame(card, fg_color="transparent")
        left.pack(side="left", padx=(12, 8), pady=10)

        ctk.CTkLabel(
            left, text=tool.get("icon", "📦"),
            font=ctk.CTkFont(size=28),
        ).pack()

        var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            left, text="",
            variable=var,
            command=lambda k=tool_key: self._on_toggle(k),
            checkbox_width=20, checkbox_height=20,
            fg_color=ACCENT_COLOR,
            hover_color="#0099cc",
        ).pack(pady=(5, 0))
        self.tool_vars[tool_key] = var

        # 中间: 名称+描述+版本状态
        mid = ctk.CTkFrame(card, fg_color="transparent")
        mid.pack(side="left", fill="both", expand=True, padx=8, pady=10)

        name_text = f"{tool['name']} ({tool['name_cn']})" if tool.get("name_cn") else tool['name']
        ctk.CTkLabel(
            mid, text=name_text,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TEXT_COLOR,
        ).pack(anchor="w")

        # 描述 + 版本状态
        desc_text = self._build_description(tool_key, tool, status, installed_ver)
        desc_label = ctk.CTkLabel(
            mid, text=desc_text,
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
            justify="left",
        )
        desc_label.pack(anchor="w", pady=(4, 0))
        self.tool_desc_labels[tool_key] = desc_label

        # 右侧: 按钮（带版本号）
        right = ctk.CTkFrame(card, fg_color="transparent")
        right.pack(side="right", padx=15, pady=10)

        if status == "not_installed":
            btn_text = "安装"
            btn_color = ACCENT_COLOR
            btn_hover = "#0099cc"
            btn_state = "normal"
            btn_width = 80
        elif status == "installed_latest":
            ver_short = installed_ver[:15] if installed_ver and len(installed_ver) > 15 else installed_ver
            btn_text = f"v{ver_short} ✓"
            btn_color = SUCCESS_COLOR
            btn_hover = SUCCESS_COLOR
            btn_state = "disabled"
            btn_width = 130
        else:  # upgrade_available
            btn_text = f"升级 v{latest_ver}"
            btn_color = WARNING_COLOR
            btn_hover = "#cc8800"
            btn_state = "normal"
            btn_width = 130

        action_btn = ctk.CTkButton(
            right, text=btn_text,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=btn_color,
            hover_color=btn_hover,
            text_color="#0a0a1a",
            height=34, width=btn_width,
            corner_radius=8,
            state=btn_state,
            command=lambda k=tool_key, s=status: self._on_tool_action(k, s),
        )
        action_btn.pack()
        self.tool_buttons[tool_key] = action_btn

    def _get_latest_version(self, tool_key, tool):
        return self.latest_versions.get(tool_key) or tool.get("latest_version")

    def _build_description(self, tool_key, tool, status, installed_ver):
        latest_ver = self._get_latest_version(tool_key, tool)
        desc_text = tool["description"]
        if status == "installed_latest":
            if latest_ver:
                desc_text += f"\n✅ 已安装最新版: {installed_ver}"
            else:
                desc_text += f"\n✅ 已安装: {installed_ver}"
        elif status == "upgrade_available":
            desc_text += f"\n⚠️ 当前: {installed_ver} → 可升级: {latest_ver}"
        elif latest_ver:
            desc_text += f"\n最新版本: {latest_ver}"
        return desc_text

    def _on_tool_action(self, tool_key, status):
        """点击卡片右侧按钮"""
        if status in ("not_installed", "upgrade_available"):
            if self.on_single_install:
                self.on_single_install(tool_key)

    def _on_toggle(self, tool_key):
        self._update_count()

    def _toggle_all(self):
        state = self.select_all_var.get()
        for var in self.tool_vars.values():
            var.set(state)
        self._update_count()

    def _update_count(self):
        count = sum(1 for v in self.tool_vars.values() if v.get())
        self.count_label.configure(text=f"已选 {count} 个工具")

    def _on_install_click(self):
        selected = [k for k, v in self.tool_vars.items() if v.get()]
        if not selected:
            return
        if self.on_install:
            self.on_install(selected)

    def get_selected_tools(self) -> list:
        return [k for k, v in self.tool_vars.items() if v.get()]

    def update_tool_status(self, tool_key, installed_version):
        """安装完成后刷新单个工具的状态"""
        self.installed_versions[tool_key] = installed_version
        self._refresh_tool_status(tool_key)

    def apply_latest_versions(self, latest_versions: dict):
        """后台联网获取到最新版本后刷新卡片升级状态。"""
        self.latest_versions.update({k: v for k, v in latest_versions.items() if v})
        for tool_key in self.latest_versions:
            self._refresh_tool_status(tool_key)

    def _refresh_tool_status(self, tool_key):
        tool = TOOLS.get(tool_key)
        if not tool or tool_key not in self.tool_buttons:
            return

        status, ver = self._get_tool_status(tool_key, tool)
        latest_ver = self._get_latest_version(tool_key, tool)
        btn = self.tool_buttons[tool_key]

        if status == "not_installed":
            btn.configure(text="安装", fg_color=ACCENT_COLOR,
                          hover_color="#0099cc", state="normal",
                          command=lambda k=tool_key, s=status: self._on_tool_action(k, s))
        elif status == "installed_latest":
            ver_short = ver[:15] if ver and len(ver) > 15 else ver
            btn.configure(text=f"v{ver_short} ✓", fg_color=SUCCESS_COLOR,
                          hover_color=SUCCESS_COLOR, state="disabled",
                          command=lambda k=tool_key, s=status: self._on_tool_action(k, s))
        else:
            btn.configure(text=f"升级 v{latest_ver}",
                          fg_color=WARNING_COLOR,
                          hover_color="#cc8800", state="normal",
                          command=lambda k=tool_key, s=status: self._on_tool_action(k, s))
        if tool_key in self.tool_desc_labels:
            self.tool_desc_labels[tool_key].configure(
                text=self._build_description(tool_key, tool, status, ver)
            )
