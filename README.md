<p align="center">
  <img src="https://img.shields.io/github/v/release/1508550385junnan-bot/ai-tools-one-click-download?color=00d4ff&label=version" alt="version">
  <img src="https://img.shields.io/badge/platform-Windows%2010%2B-lightgrey" alt="platform">
  <img src="https://img.shields.io/badge/size-19MB-blue" alt="size">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="license">
  <img src="https://img.shields.io/github/stars/1508550385junnan-bot/ai-tools-one-click-download?style=social" alt="stars">
</p>

<h1 align="center">🤖 AI 工具一键下载</h1>
<p align="center"><b>面向小白的 AI 开发环境全家桶 —— 双击安装，告别命令行</b></p>

<p align="center">
  <a href="#-为什么需要这个工具">为什么</a> •
  <a href="#-一键安装的工具">安装什么</a> •
  <a href="#-快速开始">快速开始</a> •
  <a href="#-api-模型一键配置">API配置</a> •
  <a href="#-在线升级">在线升级</a>
</p>

---

## 🤔 为什么需要这个工具？

| 😫 没有这个工具 | 😎 有了这个工具 |
|---------------|---------------|
| 手动下载 Python / VS Code / Node.js / Git | 勾选 → 一键全自动安装 |
| 百度搜"Claude Code 怎么装"，看5篇教程 | 点一下，3分钟装好 |
| 配置 API Key 要改 config.yaml、改 env、改 settings.json | 选厂家 → 输 Key → 一键完成 |
| 装完不知道怎么验证 | 自动弹出命令行显示版本号 |
| 软件更新要重新下载重新装 | 启动时自动检测，弹窗提醒升级 |

**你只需要会双击 exe，剩下的交给它。**

---

## 📦 一键安装的工具

| 工具 | 简介 | 安装方式 |
|------|------|----------|
| 🐍 **Python 3.12** | 编程语言 + pip 包管理 | 静默安装，自动配环境变量 |
| 💻 **VS Code** | 微软代码编辑器 | 静默安装 + 右键菜单 |
| 🧠 **Claude Code** | Anthropic 官方 CLI AI 编程 | npm 一键安装 |
| 🤖 **Codex CLI** | OpenAI 命令行 AI | npm 一键安装 |
| ⚡ **Hermes Agent** | Nous Research AI Agent | pip 一键安装 |
| 🔄 **CC Switch** | Claude Code 配置管理 | MSI 静默安装 |

---

## ⚡ 快速开始

### 方式一：下载 EXE（推荐）

从 [Releases](https://github.com/1508550385junnan-bot/ai-tools-one-click-download/releases/latest) 下载 `AI工具一键下载.exe`，双击运行。

**无需安装 Python，无需任何环境，19MB 单文件，双击即用。**

### 方式二：从源码运行

```bash
git clone https://github.com/1508550385junnan-bot/ai-tools-one-click-download.git
cd ai-tools-one-click-download
pip install -r requirements.txt
python main.py
```

---

## 🎯 特性

### 🚀 全自动 Splash 启动
双击后自动检测已安装工具的版本号，3秒出结果，零交互。

### 📊 版本状态一目了然
每个工具卡片显示：
- 🔵 `安装` — 未安装，点击即装
- 🟢 `v3.15.0 ✓` — 已安装最新版
- 🟠 `升级 v3.12.3` — 有新版本可升级

### 🎨 赞助友好
安装前展示赞助图片，点击"已赞助，继续下载"即可继续，无需实际支付。

### 🖥️ 安装后自动验证
安装完成后自动弹出命令行窗口，显示每个工具的版本号，确认安装成功。

---

## 🔌 API 模型一键配置

支持 **Claude Code** 和 **Hermes Agent** 一键配置 API，覆盖 **13 家主流模型厂家**：

| 国际大厂 | 国内大厂 |
|----------|----------|
| OpenAI / Anthropic / Google / Meta / xAI / Mistral | DeepSeek / 阿里 Qwen / 智谱 GLM / MiniMax / 腾讯混元 / 阶跃星辰 / 小米 MiMo |

### 三步完成配置

```
选程序 → 选厂家 → 输入 API Key → 一键配置
```

- **DeepSeek + Claude Code 直连**（已验证 Anthropic 兼容端点）
- **智谱 GLM + Claude Code 直连**
- 自动写入 `settings.json` 和 `config.yaml`
- 配置后自动测试 API 连通性

---

## 🔄 在线升级

启动时自动检查 GitHub Release，发现新版本弹窗提醒：

- 右上角显示当前版本号
- 检测到新版本按钮变橙色
- 一键跳转下载页面

---

## 📁 项目结构

```
ai-tools-one-click-download/
├── main.py                 # 入口（Splash + 版本检测）
├── config.py               # 全局配置
├── build.py                # PyInstaller 打包脚本
├── ui/
│   ├── select_page.py      # 工具选择（版本状态卡片）
│   ├── sponsor_page.py     # 赞助页面
│   ├── install_page.py     # 安装进度 + 自动 cmd 验证
│   ├── api_config_page.py  # API 模型配置页面
│   └── main_window.py      # 主窗口 + 更新检查
├── core/
│   ├── api_configurator.py # API 配置引擎（13 家厂家）
│   ├── installer.py        # NSIS/MSI/npm/pip 安装器
│   ├── downloader.py       # 下载器（断点续传+重试）
│   └── validator.py        # 版本验证（PE 文件版本读取）
└── tools/
    └── registry.py         # 工具注册表
```

---

## 🔧 技术栈

- **UI**: CustomTkinter（暗色科技风）
- **打包**: PyInstaller（单文件 EXE，自带 Python 运行时）
- **API 检测**: Windows API（PE 文件版本读取）
- **在线升级**: GitHub Release API
- **配置管理**: 直接读写 Claude Code / Hermes Agent 配置文件

---

## 🤝 贡献

欢迎提 Issue 和 PR！如果你想添加新的工具或模型厂家：

- 工具：编辑 `tools/registry.py`
- 模型厂家：编辑 `core/api_configurator.py` 的 `PROVIDERS` 字典

---

## 📄 License

MIT © 大虎子

---

<p align="center">
  <b>如果这个工具帮到了你，请给个 ⭐ Star 支持一下！</b>
</p>
