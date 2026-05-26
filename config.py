# config.py - 全局配置
# ============================================================
# 作者: 大虎子 | 版本: 2.2
# ============================================================

# --- 赞助页面配置 ---
# 赞助图片（打包时自动嵌入EXE，运行时从assets目录加载）
SPONSOR_IMAGE = "assets/sponsor.jpg"

# 赞助页面文案
SPONSOR_TEXT = "创作不易，随缘赞助"
SPONSOR_HEART = "❤️"

# 赞助按钮文字
SPONSOR_BUTTON_TEXT = "已赞助，继续下载"

# --- 版本更新检查 ---
# 远程版本信息 JSON URL（留空则不检查更新）
# 格式: {"version": "2.2", "download_url": "https://xxx.com/AI工具一键下载.exe", "changelog": "更新内容..."}
# 你可以把 version.json 放在 GitHub Releases 或你自己的服务器上
UPDATE_CHECK_URL = "https://raw.githubusercontent.com/1508550385junnan-bot/ai-tools-one-click-download/main/version.json"

# --- 下载相关 ---
DOWNLOAD_DIR = "./downloads"       # 安装包下载目录
MAX_RETRIES = 3                    # 下载最大重试次数
CHUNK_SIZE = 8192                  # 下载分块大小

# --- UI相关 ---
APP_TITLE = "AI 工具一键下载"
APP_VERSION = "2.3"
APP_AUTHOR = "大虎子"
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 680
THEME_COLOR = "#1a1a2e"            # 主背景色（深蓝黑）
ACCENT_COLOR = "#00d4ff"           # 强调色（科技蓝）
SUCCESS_COLOR = "#00ff88"          # 成功绿
WARNING_COLOR = "#ffaa00"          # 警告橙
ERROR_COLOR = "#ff4444"            # 错误红
CARD_BG = "#16213e"                # 卡片背景
TEXT_COLOR = "#e0e0e0"             # 主文字色
TEXT_SECONDARY = "#8899aa"         # 次要文字色
