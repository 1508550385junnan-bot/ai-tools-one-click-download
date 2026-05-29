# build.py - PyInstaller 打包脚本
# v2.0: 移除支付宝相关依赖（qrcode/pycryptodome），添加赞助图片资源
# 运行: python build.py
import subprocess
import sys
import os
from config import APP_EXE_BASENAME, APP_TITLE, APP_VERSION

def build():
    """打包为单个 EXE 文件"""
    print("=" * 60)
    print(f"  {APP_TITLE} v{APP_VERSION} - 打包构建")
    print("=" * 60)

    # PyInstaller 参数
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # 单文件
        "--windowed",                   # 无控制台窗口
        "--name", APP_EXE_BASENAME,
        "--add-data", f"config.py{os.pathsep}.",          # 配置文件
        "--add-data", f"assets{os.pathsep}assets",         # 赞助图片等资源
        "--add-data", f"tools{os.pathsep}tools",
        "--add-data", f"core{os.pathsep}core",
        "--add-data", f"ui{os.pathsep}ui",
        "--hidden-import", "customtkinter",
        "--hidden-import", "PIL",
        "--hidden-import", "PIL._tkinter_finder",
        "--hidden-import", "PIL.Image",
        "--clean",
        "--noconfirm",
        "main.py",
    ]

    print(f"\n执行命令:")
    print(" ".join(cmd))
    print()

    result = subprocess.run(cmd)
    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("  构建成功!")
        print(f"  输出: dist/{APP_EXE_BASENAME}.exe")
        print("=" * 60)
    else:
        print("\n构建失败，请检查错误信息")

if __name__ == "__main__":
    build()
