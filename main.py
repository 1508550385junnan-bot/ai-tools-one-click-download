# main.py - AI工具一键下载入口
"""
============================================================
  AI 工具一键下载
  一键安装 CC Switch、Python、VS Code、
  Codex CLI、Claude Code、Hermes Agent
============================================================

使用方式:
  1. 直接运行本程序
  2. 打包为 EXE: python build.py

特性:
  - 启动时自动检测已安装版本（Splash 加载界面）
  - 卡片按钮显示版本号
  - 右上角版本更新提醒
  - 全自动启动，无需任何用户操作
============================================================
"""
import sys
import os
import logging
import threading

# 设置日志
log_dir = os.path.join(os.path.expanduser("~"), ".ai-tools-installer")
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(
            os.path.join(log_dir, "installer.log"),
            encoding="utf-8",
        ),
    ],
)

logger = logging.getLogger("main")


def check_admin():
    """检查是否有管理员权限"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


def request_admin():
    """请求管理员权限（重新启动自身）"""
    if not check_admin():
        logger.info("需要管理员权限，正在重新启动...")
        try:
            import ctypes
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable,
                " ".join(sys.argv), None, 1
            )
            sys.exit(0)
        except Exception as e:
            logger.error(f"请求管理员权限失败: {e}")
            logger.warning("将在无管理员权限下运行，部分安装可能失败")


def check_dependencies_silent():
    """静默检查运行依赖（不弹交互），返回缺失列表"""
    missing = []
    try:
        import customtkinter
    except ImportError:
        missing.append("customtkinter")
    try:
        from PIL import Image
    except ImportError:
        missing.append("Pillow")
    return missing


def _clean_version(version_str: str, tool_key: str) -> str:
    """清理版本号，提取有用部分"""
    if not version_str:
        return "已安装"

    import re
    v = version_str.strip()

    # Python: "Python 3.11.9" → "3.11.9"
    if tool_key == "python":
        m = re.search(r'(\d+\.\d+\.\d+)', v)
        if m:
            return m.group(1)

    # Hermes: "Hermes Agent v0.14.0 (2026.5.16)" → "0.14.0"
    if tool_key == "hermes-agent":
        m = re.search(r'v?(\d+\.\d+\.\d+)', v)
        if m:
            return m.group(1)

    # Claude: "2.1.150 (Claude Code)" → "2.1.150"
    if tool_key == "claude-code":
        m = re.search(r'(\d+\.\d+\.\d+)', v)
        if m:
            return m.group(1)

    # Codex CLI: 同样提取版本号
    if tool_key == "codex-cli":
        m = re.search(r'(\d+\.\d+\.\d+)', v)
        if m:
            return m.group(1)

    # Windows PE 文件版本: "3.15.0.0" → "3.15.0"
    m = re.match(r'^(\d+\.\d+\.\d+)\.0$', v)
    if m:
        return m.group(1)

    # 通用：如果字符串中有版本号模式，提取出来
    m = re.search(r'(\d+\.\d+(?:\.\d+)?)', v)
    if m and len(m.group(1)) > 2:
        return m.group(1)

    v = v.split('\n')[0].strip()
    if len(v) > 40:
        v = v[:37] + "..."
    return v


def detect_installed_versions(splash_callback=None):
    """
    检测所有工具是否已安装及版本号
    splash_callback(tool_key, status, version) - 更新加载界面
    """
    from tools.registry import TOOLS
    from core.validator import Validator

    validator = Validator()
    versions = {}

    for tool_key, tool in TOOLS.items():
        name = tool["name"]
        try:
            result = validator.verify(tool_key, tool)
            if result["success"]:
                ver = result.get("version", "已安装")
                ver_clean = _clean_version(ver, tool_key)
                versions[tool_key] = ver_clean
                logger.info(f"检测到已安装: {name} = {ver_clean}")
                if splash_callback:
                    splash_callback(tool_key, "ok", ver_clean)
            else:
                versions[tool_key] = None
                error = result.get("error", "未安装")
                logger.info(f"未检测到: {name} - {error}")
                if splash_callback:
                    splash_callback(tool_key, "not_found", error)
        except Exception as e:
            versions[tool_key] = None
            logger.warning(f"检测 {name} 失败: {e}")
            if splash_callback:
                splash_callback(tool_key, "error", str(e))

    return versions


def show_splash_and_init():
    """显示加载界面，执行检测，然后启动主窗口"""
    import customtkinter as ctk
    from PIL import Image
    from config import (
        APP_TITLE, APP_VERSION, APP_AUTHOR,
        THEME_COLOR, ACCENT_COLOR, TEXT_COLOR, TEXT_SECONDARY,
        SUCCESS_COLOR, WARNING_COLOR, ERROR_COLOR, CARD_BG,
    )

    # 创建加载窗口
    splash = ctk.CTk()
    splash.title(f"{APP_TITLE} v{APP_VERSION}")
    splash.geometry("520x480")
    splash.resizable(False, False)
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    splash.configure(fg_color=THEME_COLOR)

    # 居中
    splash.update_idletasks()
    sw = splash.winfo_screenwidth()
    sh = splash.winfo_screenheight()
    splash.geometry(f"+{(sw-520)//2}+{(sh-480)//2}")

    # 标题
    ctk.CTkLabel(
        splash, text=f"{APP_TITLE}",
        font=ctk.CTkFont(size=24, weight="bold"),
        text_color=TEXT_COLOR,
    ).pack(pady=(40, 5))

    ctk.CTkLabel(
        splash, text=f"v{APP_VERSION} | {APP_AUTHOR}",
        font=ctk.CTkFont(size=13),
        text_color=TEXT_SECONDARY,
    ).pack(pady=(0, 20))

    # 加载提示
    status_label = ctk.CTkLabel(
        splash, text="🔄 正在初始化...",
        font=ctk.CTkFont(size=14),
        text_color=ACCENT_COLOR,
    )
    status_label.pack(pady=(0, 15))

    # 检测列表区域
    list_frame = ctk.CTkScrollableFrame(
        splash, fg_color=CARD_BG,
        corner_radius=8,
        width=440, height=220,
    )
    list_frame.pack(pady=(0, 15), padx=40)
    list_frame.pack_propagate(False)

    # 进度条
    progress = ctk.CTkProgressBar(
        splash, width=400, height=8,
        fg_color=CARD_BG, progress_color=ACCENT_COLOR,
    )
    progress.pack(pady=(0, 10))
    progress.set(0)

    progress_text = ctk.CTkLabel(
        splash, text="0 / 6",
        font=ctk.CTkFont(size=12),
        text_color=TEXT_SECONDARY,
    )
    progress_text.pack()

    # 检测条目
    item_labels = {}
    from tools.registry import TOOLS
    total = len(TOOLS)
    completed = [0]

    for i, (tool_key, tool) in enumerate(TOOLS.items()):
        row = ctk.CTkFrame(list_frame, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=3)

        icon = ctk.CTkLabel(
            row, text="⏳",
            font=ctk.CTkFont(size=13), width=25,
            text_color=TEXT_SECONDARY,
        )
        icon.pack(side="left")

        name = ctk.CTkLabel(
            row, text=f"{tool['name']}",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_COLOR, anchor="w",
        )
        name.pack(side="left", fill="x", expand=True)

        detail = ctk.CTkLabel(
            row, text="检测中...",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY, anchor="e",
        )
        detail.pack(side="right")
        item_labels[tool_key] = (icon, detail)

    splash.update()

    # 完成后的回调
    init_done = threading.Event()
    detected_versions = {}

    def on_progress(tool_key, status, info):
        if tool_key in item_labels:
            icon_lbl, detail_lbl = item_labels[tool_key]
            if status == "ok":
                icon_lbl.configure(text="✅", text_color=SUCCESS_COLOR)
                detail_lbl.configure(text=info, text_color=SUCCESS_COLOR)
            elif status == "not_found":
                icon_lbl.configure(text="❌", text_color=ERROR_COLOR)
                detail_lbl.configure(text=info, text_color=ERROR_COLOR)
            else:
                icon_lbl.configure(text="⚠️", text_color=WARNING_COLOR)
                detail_lbl.configure(text=info, text_color=WARNING_COLOR)

        completed[0] += 1
        pct = completed[0] / total
        progress.set(pct)
        progress_text.configure(text=f"{completed[0]} / {total}")
        splash.update()

    def do_detect():
        nonlocal detected_versions
        status_label.configure(text="🔍 正在检测已安装工具版本...")
        splash.update()
        detected_versions = detect_installed_versions(splash_callback=on_progress)

        status_label.configure(text="✅ 检测完成，正在启动...")
        splash.update()

        # 短暂延迟让用户看到完成状态
        import time
        time.sleep(0.5)

        init_done.set()

    # 后台执行检测
    thread = threading.Thread(target=do_detect, daemon=True)
    thread.start()

    # 轮询等待完成，完成后退出 mainloop 再启动主窗口
    def check_and_quit():
        if init_done.is_set():
            splash.quit()  # 退出 mainloop，不直接 destroy
        else:
            splash.after(100, check_and_quit)

    splash.after(100, check_and_quit)
    splash.mainloop()
    splash.destroy()

    # splash 的 mainloop 已退出，现在安全启动主窗口
    from ui.main_window import MainWindow
    logger.info(f"启动{APP_TITLE} v{APP_VERSION}")
    app = MainWindow(installed_versions=detected_versions)
    app.run()


def main():
    """主入口"""
    from config import APP_TITLE, APP_VERSION

    logger.info("=" * 50)
    logger.info(f"{APP_TITLE} v{APP_VERSION} 启动")
    
    # 检查管理员权限
    request_admin()

    # 静默检查依赖
    missing = check_dependencies_silent()
    if missing:
        # 缺少依赖 → 尝试自动安装
        logger.warning(f"缺少依赖: {missing}")
        try:
            import subprocess
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install"] + missing,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            logger.info("依赖自动安装完成")
        except Exception as e:
            logger.error(f"依赖安装失败: {e}")
            # 显示错误对话框
            try:
                import tkinter.messagebox as mb
                mb.showerror(
                    "依赖缺失",
                    f"缺少必要组件: {', '.join(missing)}\n\n"
                    f"请手动运行:\n"
                    f"pip install {' '.join(missing)}"
                )
            except:
                print(f"缺少依赖: {missing}")
                print(f"请运行: pip install {' '.join(missing)}")
            sys.exit(1)

    # 显示加载界面并启动
    show_splash_and_init()


if __name__ == "__main__":
    main()
