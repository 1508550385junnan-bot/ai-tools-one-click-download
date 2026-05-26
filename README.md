# AI 工具一键下载 v2.1

**作者: 大虎子 | 版本: 2.1**

一键安装 CC Switch、Python、VS Code、Codex CLI、Claude Code、Hermes Agent 的 Windows 桌面程序。

---

## 一、执行摘要

面向不会配置开发环境的小白用户（或懒得手动的老手），打开程序 → 自动检测已安装版本 → 勾选工具或点击右侧按钮 → 查看赞助图 → 点击继续 → 等待自动完成，安装完成后自动弹出命令行窗口验证版本。

**v2.1 新特性：**
- 启动时自动检测每个工具的安装状态和版本号
- 卡片右侧按钮：未安装显示"安装"，最新版显示"已安装 ✓"，旧版显示"升级到 vX.X.X"
- 支持单工具一键安装和批量安装两种模式
- 无需 Python 环境：打包后的 EXE 自带 Python 解释器

## 二、前置条件

| 条件 | 要求 | 说明 |
|------|------|------|
| 操作系统 | Windows 10/11 (64位) | Win7 未测试 |
| 网络 | 稳定互联网连接 | 下载安装包需要 |
| 磁盘空间 | ≥ 5GB 可用空间 | 含安装包缓存 |
| 权限 | 建议管理员权限 | 部分工具需要 |
| Python | 3.10+ (仅打包需要) | **最终用户不需要 Python 环境** |

## 三、快速开始

### 3.1 直接使用 EXE（推荐）

1. 双击 `AI工具一键下载.exe`
2. 程序自动检测已安装工具的版本（约 3 秒）
3. 点击工具卡片右侧的"安装"按钮（或勾选多个后点"批量安装"）
4. 查看赞助图片，点击"已赞助，继续下载"
5. 等待进度条走完，看到 ✅ 即完成
6. 自动弹出命令行窗口，显示已安装工具的版本信息

### 3.2 从源码运行

```bash
pip install -r requirements.txt
python main.py
```

### 3.3 打包为 EXE

```bash
python build.py
# 输出: dist/AI工具一键下载.exe  (约 25MB，自带 Python 运行时)
```

## 四、支持的 6 个工具（全部免费）

| 工具 | 简介 | 最新版本 |
|------|------|----------|
| CC Switch | Claude Code 配置切换工具 | GitHub Latest |
| Python 3.12 | Python 官方 + pip + 环境变量 | 3.12.3 |
| VS Code | 微软代码编辑器 | 自动最新 |
| Codex CLI | OpenAI Codex 命令行 AI | GitHub Latest |
| Claude Code | Anthropic Claude Code CLI | GitHub Latest |
| Hermes Agent | Nous Research Hermes Agent | GitHub Latest |

## 五、卡片按钮状态说明

| 状态 | 按钮显示 | 颜色 | 说明 |
|------|----------|------|------|
| 未安装 | `安装` | 蓝色 | 点击直接安装该工具 |
| 已安装(最新) | `已安装 ✓` | 绿色 | 不可点击 |
| 已安装(旧版) | `升级到 vX.X.X` | 橙色 | 点击安装最新版 |

## 六、赞助说明

打开工具后会展示赞助图片 + "创作不易，随缘赞助 ❤️"文案。点击"已赞助，继续下载"即可直接下载安装，无需实际支付。

## 七、安装流程详解

```
用户选择工具
    │
    ├─ 点击右侧按钮（单工具）
    └─ 勾选+批量安装（多工具）
            │
            ▼
    显示赞助图片 ──→ 用户点击"已赞助，继续下载"
                          │
                          ▼
    ① 检查前置环境 (Node.js / Git / Python)
    ② 下载安装包 (显示百分比+速度)
    ③ 静默安装 (/S 或 /quiet 模式)
    ④ 版本验证 (执行 --version / 检查文件)
    ⑤ 显示结果 ✅ 或 ❌
    ⑥ 自动打开命令行窗口验证版本
```

## 八、前置环境自动安装

| 工具 | 需要的环境 | 自动处理 |
|------|-----------|----------|
| Codex CLI | Node.js | 自动下载安装 Node.js 20.x |
| Claude Code | Node.js + Git | 自动安装两者 |
| Hermes Agent | Python 3 + Git | 优先检测已有安装 |

## 九、关于 EXE 独立运行

打包后的 EXE 使用 PyInstaller `--onefile` 模式，将 Python 解释器、所有依赖（customtkinter、Pillow）和赞助图片全部嵌入单个文件。在 **没有安装 Python 的 Windows 电脑上也能直接运行**。

## 十、项目结构

```
ai-tools-installer/
├── main.py              # 入口（启动时版本检测）
├── config.py            # 全局配置
├── build.py             # PyInstaller打包脚本
├── requirements.txt     # Python依赖（3个包）
├── README.md            # 本文档
├── ui/
│   ├── main_window.py   # 主窗口+页面路由
│   ├── select_page.py   # 工具选择（版本状态+按钮）
│   ├── sponsor_page.py  # 赞助页（图片+文案）
│   └── install_page.py  # 安装进度+自动cmd验证
├── core/
│   ├── downloader.py    # 下载器（重试+断点续传）
│   ├── installer.py     # 安装器（NSIS/MSI/npm/pip）
│   └── validator.py     # 版本验证
├── tools/
│   └── registry.py      # 工具注册表（含 latest_version）
└── assets/
    └── sponsor.jpg      # 赞助图片
```

---

## 自检清单

| 检查项 | 标准值 | 检查方法 | 优先级 |
|--------|--------|----------|--------|
| Python依赖 | customtkinter/Pillow 已安装 | `pip list \| grep -E "customtkinter\|Pillow"` | 必须 |
| 赞助图片 | assets/sponsor.jpg 存在 | `ls -la assets/sponsor.jpg` | 必须 |
| 版本检测 | 启动时显示6行检测结果 | 运行 main.py 观察控制台 | 必须 |
| 卡片按钮 | 未安装/已安装/升级 三种状态 | 运行 main.py 观察UI | 必须 |
| 单工具安装 | 点击卡片按钮→赞助页→安装 | 观察流程 | 必须 |
| 批量安装 | 勾选→批量安装→逐个赞助→安装 | 观察流程 | 必须 |
| 赞助页 | 显示图片+文案+按钮 | 观察UI | 必须 |
| 自动cmd | 安装后弹出命令行窗口 | 观察是否弹出 | 必须 |
| EXE打包 | dist/AI工具一键下载.exe 存在 | `python build.py` | 必须 |
| EXE独立运行 | 无Python环境可启动 | 复制到其他Win10机器测试 | 建议 |
| 杀软误报 | Windows Defender不拦截 | 右键扫描 | 建议 |
