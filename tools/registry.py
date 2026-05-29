# tools/registry.py - 工具注册表
# v2.0: 所有工具免费，移除付费标记
import os
import sys

TOOLS = {
    "cc-switch": {
        "name": "CC Switch",
        "name_cn": "CC 切换器",
        "description": "快速切换 Claude Code 配置环境的桌面工具，\n支持多账号、多区域一键切换，告别手动改配置。",
        "icon": "🔄",
        "category": "工具",
        "latest_version": "3.15.0",
        "downloads": [
            {
                "os": "windows",
                "url": "https://github.com/farion1231/cc-switch/releases/download/v3.15.0/CC-Switch-v3.15.0-Windows.msi",
                "filename": "CC-Switch-v3.15.0-Windows.msi",
                "size_mb": 13
            }
        ],
        "install": {
            "type": "msi",
            "args": ["/quiet", "/norestart"],
            "registry_display_names": ["CC Switch", "cc-switch"],
            "check_paths": [
                os.path.expandvars("%ProgramFiles%\\CC Switch\\cc-switch.exe"),
                os.path.expandvars("%ProgramFiles(x86)%\\CC Switch\\cc-switch.exe"),
                os.path.expandvars("%LOCALAPPDATA%\\Programs\\CC Switch\\cc-switch.exe"),
                os.path.expandvars("%LOCALAPPDATA%\\Programs\\cc-switch\\cc-switch.exe"),
                os.path.expandvars("%LOCALAPPDATA%\\cc-switch\\cc-switch.exe"),
            ]
        },
        "verify": {
            "command": None,
            "method": "file_exists"
        },
        "prerequisites": []
    },

    "python": {
        "name": "Python",
        "name_cn": "Python 编程环境",
        "description": "Python 3.12 官方发行版，自动配置环境变量，\n附带 pip 包管理器，AI 开发必备基础环境。",
        "icon": "🐍",
        "category": "基础环境",
        "latest_version": "3.12.3",  # 下载链接固定为此版本
        "downloads": [
            {
                "os": "windows",
                "url": "https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe",
                "filename": "python-3.12.3-amd64.exe",
                "size_mb": 25
            }
        ],
        "install": {
            "type": "nsis",
            "args": [
                "/quiet",
                "InstallAllUsers=1",
                "PrependPath=1",
                "Include_test=0"
            ],
            "check_paths": [
                os.path.expandvars("%LOCALAPPDATA%\\Programs\\Python\\Python312\\python.exe"),
                os.path.expandvars("%ProgramFiles%\\Python312\\python.exe"),
                os.path.expandvars("C:\\Python312\\python.exe"),
            ]
        },
        "verify": {
            "command": "python --version",
            "expected": None,
            "method": "exit_code_zero"
        },
        "prerequisites": []
    },

    "vscode": {
        "name": "VS Code",
        "name_cn": "Visual Studio Code",
        "description": "微软出品的免费代码编辑器，插件生态丰富，\n支持 GitHub Copilot、AI 辅助编程，开发必备。",
        "icon": "💻",
        "category": "开发工具",
        "latest_version": None,  # 动态下载，始终为最新
        "downloads": [
            {
                "os": "windows",
                "url": "https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-user",
                "filename": "VSCodeSetup.exe",
                "size_mb": 95
            }
        ],
        "install": {
            "type": "nsis",
            "args": [
                "/VERYSILENT",
                "/SUPPRESSMSGBOXES",
                "/MERGETASKS=!runcode,addcontextmenufiles,addcontextmenufolders,addtopath"
            ],
            "check_paths": [
                os.path.expandvars("%LOCALAPPDATA%\\Programs\\Microsoft VS Code\\Code.exe"),
                os.path.expandvars("%ProgramFiles%\\Microsoft VS Code\\Code.exe"),
            ]
        },
        "verify": {
            "command": "code --version",
            "expected": None,
            "method": "exit_code_zero"
        },
        "prerequisites": []
    },

    "codex-cli": {
        "name": "Codex CLI",
        "name_cn": "OpenAI Codex CLI",
        "description": "OpenAI 官方命令行 AI 编程助手，\n终端内直接对话、生成代码、调试程序，\n支持 GPT-4o 等顶级模型。",
        "icon": "🤖",
        "category": "AI编程",
        "latest_version": None,
        "downloads": [],  # npm 安装，无需下载
        "install": {
            "type": "npm",
            "command": "npm install -g @openai/codex",
            "check_paths": [
                os.path.expandvars("%APPDATA%\\npm\\codex.cmd"),
                os.path.expandvars("%APPDATA%\\npm\\codex.ps1"),
            ]
        },
        "verify": {
            "command": "codex --version",
            "expected": None,
            "method": "exit_code_zero"
        },
        "prerequisites": ["nodejs"]
    },

    "claude-code": {
        "name": "Claude Code",
        "name_cn": "Anthropic Claude Code",
        "description": "Anthropic 官方 CLI AI 编程工具，\nClaude 大模型驱动，深度理解代码库，\n支持复杂重构和架构级开发。",
        "icon": "🧠",
        "category": "AI编程",
        "latest_version": None,
        "downloads": [],  # npm 安装，无需下载
        "install": {
            "type": "npm",
            "command": "npm install -g @anthropic-ai/claude-code",
            "check_paths": [
                os.path.expandvars("%APPDATA%\\npm\\claude.cmd"),
                os.path.expandvars("%APPDATA%\\npm\\claude.ps1"),
            ]
        },
        "verify": {
            "command": "claude --version",
            "expected": None,
            "method": "exit_code_zero"
        },
        "prerequisites": ["nodejs", "git"]
    },

    "hermes-agent": {
        "name": "Hermes Agent",
        "name_cn": "Nous Hermes Agent",
        "description": "Nous Research 出品的智能 AI Agent，\n支持多工具编排、记忆持久化、定时任务，\n可接入多种大模型后端。",
        "icon": "⚡",
        "category": "AI编程",
        "latest_version": None,
        "downloads": [],  # pip 安装，无需下载
        "install": {
            "type": "pip",
            "command": "pip install hermes-agent",
            "check_paths": [
                os.path.expandvars("%LOCALAPPDATA%\\Programs\\Python\\Python312\\Scripts\\hermes.exe"),
                os.path.expandvars("%APPDATA%\\Python\\Python312\\Scripts\\hermes.exe"),
            ]
        },
        "verify": {
            "command": "hermes version",
            "expected": None,
            "method": "exit_code_zero"
        },
        "prerequisites": ["python3", "git"]
    },
}

# 前置环境定义
PREREQUISITES = {
    "nodejs": {
        "name": "Node.js",
        "description": "JavaScript 运行时环境（Codex CLI、Claude Code 等工具依赖）",
        "download_url": "https://nodejs.org/dist/v20.12.2/node-v20.12.2-x64.msi",
        "filename": "node-v20.12.2-x64.msi",
        "install_type": "msi",
        "install_args": ["/quiet", "/norestart"],
        "verify_command": "node --version",
        "check_paths": [
            os.path.expandvars("%ProgramFiles%\\nodejs\\node.exe"),
            os.path.expandvars("%ProgramFiles(x86)%\\nodejs\\node.exe"),
        ]
    },
    "git": {
        "name": "Git",
        "description": "版本控制系统（Claude Code、Hermes Agent 等工具依赖）",
        "download_url": "https://github.com/git-for-windows/git/releases/download/v2.44.0.windows.1/Git-2.44.0-64-bit.exe",
        "filename": "Git-2.44.0-64-bit.exe",
        "install_type": "nsis",
        "install_args": ["/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/NOCANCEL",
                         "/CLOSEAPPLICATIONS", "/RESTARTAPPLICATIONS"],
        "verify_command": "git --version",
        "check_paths": [
            os.path.expandvars("%ProgramFiles%\\Git\\bin\\git.exe"),
            os.path.expandvars("%ProgramFiles(x86)%\\Git\\bin\\git.exe"),
        ]
    },
    "python3": {
        "name": "Python 3",
        "description": "Python 运行环境（Hermes Agent 等工具依赖）",
        "download_url": "https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe",
        "filename": "python-3.12.3-amd64.exe",
        "install_type": "nsis",
        "install_args": ["/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_test=0"],
        "verify_command": "python --version",
        "check_paths": [
            os.path.expandvars("%LOCALAPPDATA%\\Programs\\Python\\Python312\\python.exe"),
            os.path.expandvars("%ProgramFiles%\\Python312\\python.exe"),
        ]
    }
}
