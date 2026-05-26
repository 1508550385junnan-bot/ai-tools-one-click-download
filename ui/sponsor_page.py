# ui/sponsor_page.py - 赞助页面
# v2.0: 替换支付宝支付，改为展示赞助图片+文案，点击按钮后继续
import os
import sys
import customtkinter as ctk
from PIL import Image
from config import (
    CARD_BG, TEXT_COLOR, TEXT_SECONDARY, ACCENT_COLOR,
    SUCCESS_COLOR, SPONSOR_IMAGE, SPONSOR_TEXT, SPONSOR_HEART,
    SPONSOR_BUTTON_TEXT,
)


def _get_sponsor_image_path() -> str:
    """获取赞助图片路径（兼容开发环境和 PyInstaller 打包环境）"""
    # PyInstaller 打包后的路径
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
        path = os.path.join(base, "assets", "sponsor.jpg")
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base, "assets", "sponsor.jpg")

    # 回退：尝试相对于当前工作目录
    if not os.path.exists(path):
        path = os.path.join(os.getcwd(), "assets", "sponsor.jpg")

    return path


class SponsorPage(ctk.CTkFrame):
    """赞助页面 — 展示图片 + 文案 + 按钮"""

    def __init__(self, master, on_sponsor_done=None, on_back=None):
        super().__init__(master, fg_color="transparent")
        self.on_sponsor_done = on_sponsor_done
        self.on_back = on_back
        self.current_tool = None
        self.ctk_image = None  # 保持引用防止垃圾回收
        self._build_ui()

    def _build_ui(self):
        # 标题栏
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))

        self.back_btn = ctk.CTkButton(
            header, text="← 返回选择",
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            text_color=ACCENT_COLOR,
            hover_color=CARD_BG,
            width=100, height=30,
            command=self._on_back,
        )
        self.back_btn.pack(side="left")

        self.title_label = ctk.CTkLabel(
            header, text="即将开始下载",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_COLOR,
        )
        self.title_label.pack(side="left", padx=20)

        # 主内容区
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=10)

        # 赞助图片
        self.image_label = ctk.CTkLabel(
            content, text="",
            text_color=TEXT_COLOR,
        )
        self.image_label.pack(pady=(0, 10))

        # 赞助文案
        self.text_label = ctk.CTkLabel(
            content,
            text=f"{SPONSOR_TEXT} {SPONSOR_HEART}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_COLOR,
        )
        self.text_label.pack(pady=(0, 20))

        # "已赞助，继续下载" 按钮
        self.sponsor_btn = ctk.CTkButton(
            content,
            text=SPONSOR_BUTTON_TEXT,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=SUCCESS_COLOR,
            hover_color="#00cc66",
            text_color="#0a0a1a",
            height=50, width=240,
            corner_radius=10,
            command=self._on_sponsor_click,
        )
        self.sponsor_btn.pack(pady=10)

        # 底部提示
        self.hint_label = ctk.CTkLabel(
            content,
            text="点击上方按钮即可继续下载安装，无需实际支付",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
        )
        self.hint_label.pack(pady=(5, 0))

    def show_for_tool(self, tool_key: str):
        """为指定工具显示赞助页面"""
        from tools.registry import TOOLS
        self.current_tool = tool_key
        tool = TOOLS.get(tool_key, {"name": tool_key})
        self.title_label.configure(text=f"准备安装 {tool['name']}")

        # 加载赞助图片
        self._load_sponsor_image()

    def _load_sponsor_image(self):
        """加载赞助图片并显示"""
        try:
            img_path = _get_sponsor_image_path()
            if os.path.exists(img_path):
                pil_image = Image.open(img_path)
                # 限制最大尺寸 (宽度不超过500，高度按比例)
                max_w, max_h = 500, 350
                w, h = pil_image.size
                scale = min(max_w / w, max_h / h, 1.0)
                new_w, new_h = int(w * scale), int(h * scale)
                pil_image = pil_image.resize((new_w, new_h), Image.LANCZOS)

                ctk_image = ctk.CTkImage(
                    light_image=pil_image,
                    dark_image=pil_image,
                    size=(new_w, new_h),
                )
                self.ctk_image = ctk_image  # 保持引用
                self.image_label.configure(image=ctk_image, text="")
            else:
                self.image_label.configure(
                    text="📷 赞助图片未找到\n请将图片放入 assets/sponsor.jpg",
                    font=ctk.CTkFont(size=14),
                    text_color=TEXT_SECONDARY,
                )
        except Exception as e:
            self.image_label.configure(
                text=f"⚠️ 图片加载失败\n{str(e)[:80]}",
                font=ctk.CTkFont(size=13),
                text_color=TEXT_SECONDARY,
            )

    def _on_sponsor_click(self):
        """用户点击'已赞助，继续下载'"""
        if self.on_sponsor_done and self.current_tool:
            self.on_sponsor_done(self.current_tool, True)

    def _on_back(self):
        if self.on_back:
            self.on_back()
