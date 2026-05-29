<p align="center">
  <img src="https://img.shields.io/github/v/release/1508550385junnan-bot/ai-tools-one-click-download?color=00d4ff&label=version" alt="version">
  <img src="https://img.shields.io/badge/platform-Windows%2010%2B-lightgrey" alt="platform">
  <img src="https://img.shields.io/badge/size-19MB-blue" alt="size">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="license">
  <img src="https://img.shields.io/github/downloads/1508550385junnan-bot/ai-tools-one-click-download/total" alt="downloads">
  <img src="https://img.shields.io/github/stars/1508550385junnan-bot/ai-tools-one-click-download?style=social" alt="stars">
</p>

<h1 align="center">🤖 AI 工具一键下载 / AI Tools One-Click Installer</h1>
<p align="center">
  <b>双击 EXE，3 分钟搭好 AI 编程环境。零终端、零教程、零痛苦。</b><br>
  <sub>Your AI dev environment, one double-click away. No terminal. No tutorials. No pain.</sub>
</p>

<p align="center">
  <a href="#-the-problem--the-solution">Why</a> •
  <a href="#-tools-installed">Tools</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-api-model-config">API Config</a> •
  <a href="#-auto-update">Auto Update</a>
</p>

---

## 💡 The Problem & The Solution

Setting up an AI development environment on Windows sucks. You need Python, VS Code, Node.js, Git, Claude Code, Codex CLI, Hermes Agent... Each one has its own installer, its own quirks, its own StackOverflow rabbit hole.

**This tool reduces hours of setup to 3 clicks.**

| 😫 Without This Tool | 😎 With This Tool |
|---------------------|-------------------|
| Google "how to install Claude Code" → 5 tabs open | Click → 3 minutes → Done |
| Manually download Python / Node.js / Git one by one | Check boxes → One-click install all |
| Edit config.yaml, settings.json, env vars by hand | Pick provider → Paste key → Done |
| "Did it actually install? How do I verify?" | Auto-opens terminal with version output |
| Re-download everything when new version drops | Auto-detects updates, one-click upgrade |

**If you can double-click an .exe, you can set up your AI dev environment.**

---

## 📦 Tools Installed

| Tool | What It Is | Install Method |
|------|-----------|---------------|
| 🐍 **Python 3.12** | Programming language + pip | Silent install, auto PATH |
| 💻 **VS Code** | Microsoft code editor | Silent install + context menu |
| 🧠 **Claude Code** | Anthropic's CLI AI coding tool | npm one-liner |
| 🤖 **Codex CLI** | OpenAI's CLI AI assistant | npm one-liner |
| ⚡ **Hermes Agent** | Nous Research AI agent | pip one-liner |
| 🔄 **CC Switch** | Claude Code config manager | MSI silent install |

---

## ⚡ Quick Start

### Option 1: Download EXE (Recommended)

Grab `AI工具一键下载.exe` from [Releases](https://github.com/1508550385junnan-bot/ai-tools-one-click-download/releases/latest) and double-click.

**No Python required. No dependencies. 19MB single file. Just works.**

### Option 2: Run from Source

```bash
git clone https://github.com/1508550385junnan-bot/ai-tools-one-click-download.git
cd ai-tools-one-click-download
pip install -r requirements.txt
python main.py
```

---

## ✨ Features

### 🚀 Zero-Interaction Splash Screen
Launch → auto-detect all installed tool versions → main window ready in 3 seconds. No prompts, no "press Y to continue", just smooth.

### 📊 Version Status at a Glance
Each tool card shows real-time status:
- 🔵 `Install` — Not installed, click to install
- 🟢 `v3.15.0 ✓` — Already up-to-date
- 🟠 `Upgrade to v3.12.3` — Newer version available

### 🎨 Friendly Sponsor Page
See a sponsor image before installation, click "Sponsored, Continue" to proceed. No actual payment required. Just an appreciation nudge.

### 🖥️ Auto Verification Terminal
Installation complete → a terminal window pops up automatically showing version numbers of everything you just installed.

### 🎯 Smart Version Detection
Reads PE file version info via Windows API for GUI tools (like CC Switch). Uses `--version` for CLI tools. No more "is it actually installed?" guessing.

---

## 🔌 API Model One-Click Config

Configure **Claude Code** and **Hermes Agent** with **13 major model providers** in 3 steps:

| International | China / Asia |
|--------------|-------------|
| OpenAI / Anthropic / Google / Meta / xAI / Mistral | DeepSeek / Alibaba Qwen / Zhipu GLM / MiniMax / Tencent Hunyuan / StepFun / Xiaomi MiMo |

### How it works

```
Pick App → Pick Provider → Paste API Key → One Click
```

- **DeepSeek → Claude Code: Direct connection** (verified Anthropic-compatible endpoint)
- **Zhipu GLM → Claude Code: Direct connection**
- Auto-writes `settings.json` and `config.yaml` (learned from CC Switch source)
- Auto-tests API connectivity after configuration
- Warns when a relay/proxy service is needed

---

## 🔄 Auto Update

Checks GitHub Releases on startup. New version detected? Orange badge + popup. One click to download.

```
[v2.5] [Check Update]  →  [v2.6 Available] [Check Update]
```

---

## 🏗️ Architecture

```
ai-tools-one-click-download/
├── main.py                 # Entry (Splash + version detection)
├── config.py               # Global config
├── build.py                # PyInstaller packager
├── ui/
│   ├── select_page.py      # Tool selection (version cards)
│   ├── sponsor_page.py     # Sponsor page
│   ├── install_page.py     # Install progress + auto cmd verify
│   ├── api_config_page.py  # API model config UI
│   └── main_window.py      # Main window + update checker
├── core/
│   ├── api_configurator.py # API config engine (13 providers)
│   ├── installer.py        # NSIS/MSI/npm/pip installer
│   ├── downloader.py       # Resumable downloader with retry
│   └── validator.py        # Version validation (PE file reader)
└── tools/
    └── registry.py         # Tool registry
```

---

## 🔧 Tech Stack

- **UI**: CustomTkinter (dark cyber-theme)
- **Packaging**: PyInstaller (single EXE, embedded Python runtime)
- **Version Detection**: Windows API via ctypes (PE file version info)
- **Auto Update**: GitHub Releases API polling
- **Config Management**: Direct read/write of Claude Code & Hermes Agent config files

---

## 🤝 Contributing

PRs welcome! To add a new tool or model provider:

- **New tool** → Edit `tools/registry.py`
- **New provider** → Edit `PROVIDERS` dict in `core/api_configurator.py`

Run `python build.py` to repackage.

---

## 📄 License

MIT © 大虎子 (DaHuzi)

---

<p align="center">
  <b>⭐ If this saved you from 10 StackOverflow tabs, drop a star!</b>
  <br><br>
  <a href="https://github.com/1508550385junnan-bot/ai-tools-one-click-download">
    <img src="https://img.shields.io/github/stars/1508550385junnan-bot/ai-tools-one-click-download?style=social" alt="star this repo">
  </a>
</p>
