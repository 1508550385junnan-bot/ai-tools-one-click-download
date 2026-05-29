# 发现记录

## 代码发现
- 项目是 Python + customtkinter 桌面安装器。
- API 配置核心在 `core/api_configurator.py`。
- CC Switch 安装配置在 `tools/registry.py`，安装执行在 `core/installer.py`，检测在 `core/validator.py`。
- 选择页已有安装/升级状态入口，但需要审查版本比较与安装后刷新。
- 复现到 API 测试 bug：Anthropic/Claude 协议被错误打到 `/chat/completions`，DeepSeek Claude Code 配置也缺少 `/anthropic` 端点和模型环境变量。
- 复现到 API 测试误判：OpenAI 兼容接口返回 401/403 时旧逻辑会显示“端点可达/认证格式正确”，实际应判定为认证失败。
- CC Switch 官方 MSI 文件已完整存在于 `downloads`，旧下载器在已有完整文件时仍尝试 Range 续传，弱网下会反复失败。
- MSI 安装返回码 3010/1641 表示成功但需要重启，旧逻辑只认 0，可能误报安装失败。
- CC Switch GUI 文件可能没有可读 PE 版本，注册表 `DisplayVersion` 更可靠。
- 旧版本比较只做字符串相等，`3.9.0` 与 `3.10.0` 等场景会误判。
- 打包前复测发现 `requirements.txt` 的中文注释会触发 Windows pip 按 GBK 解码失败，导致 `pip install -r requirements.txt` 阻断；发布依赖清单应保持 ASCII 或显式兼容编码。

## 外部研究
- CC Switch 官方 GitHub Release v3.15.0：仓库约 83.3k star；Windows 推荐资产是 `CC-Switch-v3.15.0-Windows.msi`，说明为 MSI 安装器并支持 auto-update。来源：https://github.com/farion1231/cc-switch/releases/tag/v3.15.0
- Claude Code 官方设置文档：用户级配置在 `~/.claude/settings.json`，Windows 对应 `%USERPROFILE%\.claude`；`env` 字段会应用到每次 Claude Code 会话。来源：https://code.claude.com/docs/en/settings
- Claude Code 官方环境变量文档：`ANTHROPIC_API_KEY`、`ANTHROPIC_AUTH_TOKEN`、`ANTHROPIC_BASE_URL` 分别控制 API Key、自定义 Authorization、代理/网关端点。来源：https://code.claude.com/docs/en/env-vars
- Hermes Agent 官方文档：所有配置存储在 `~/.hermes/`，`config.yaml` 是模型、provider、base_url 的真相源；旧的 `OPENAI_BASE_URL` 和 `LLM_MODEL` 环境变量已移除。来源：https://hermes-agent.nousresearch.com/docs/integrations/providers
- GitHub Releases API 访问被当前出口 IP 限流，不能作为安装器运行时唯一依赖；代码应支持静态 URL，并在下载失败时给出明确 HTTP 错误。
- PyInstaller 官方文档：Windows GUI 单文件应用可使用 `--onefile --windowed`，资源通过 `--add-data` 纳入，间接依赖可用 `--hidden-import` 显式声明。来源：https://pyinstaller.org/en/stable/usage.html
- GitHub CLI Release 文档：Release 可附加本地构建产物作为 asset；本机未安装 `gh`，发布产物上传需要改用已有 git 凭据之外的 Release 上传方式或后续安装/配置 `gh`。来源：https://cli.github.com/manual/gh_release_create
- GitHub Release assets 官方文档：上传资产时 GitHub 会重命名包含特殊字符、非字母数字字符或首尾句点的文件名，最终应以 List release assets 返回的文件名为准；因此发布资产名改为 ASCII 的 `AI.exe`。来源：https://docs.github.com/en/rest/releases/assets
- OpenClaw 官网 `https://openclaw.ai/` 指向 OpenClaw 工具；npm 注册信息确认包名为 `openclaw`，bin 命令为 `openclaw`，当前版本 `2026.5.27`，仓库为 `https://github.com/openclaw/openclaw`。本次采用 `npm install -g openclaw`，因为它与官方站点/npm 元数据一致，且符合现有 npm 工具安装模式。来源：https://openclaw.ai/ 与 https://www.npmjs.com/package/openclaw
- `@openai/codex` npm 当前版本为 `0.135.0`，bin 命令为 `codex`；适合用 npm registry `/latest` 做最新版本检测。来源：https://www.npmjs.com/package/@openai/codex
- `@anthropic-ai/claude-code` npm 当前版本为 `2.1.156`，bin 命令为 `claude`；适合用 npm registry `/latest` 做最新版本检测。来源：https://www.npmjs.com/package/@anthropic-ai/claude-code
- `hermes-agent` PyPI 当前版本为 `0.15.2`；适合用 PyPI JSON API 做最新版本检测。来源：https://pypi.org/project/hermes-agent/
- Hermes 误判根因：验证器只执行 `hermes version`，如果 pip 安装路径未进入当前进程 PATH，即使 `%APPDATA%\Python\Python3xx\Scripts\hermes.exe/cmd` 存在也会显示未安装。应把 check_paths 目录加入 PATH，并在命令失败时用实际脚本路径重试。

## 范围外问题
- 暂无。

## v2.8 Hermes 补充发现
- 本机 Hermes 实际安装路径为 `%LOCALAPPDATA%\Programs\Python\Python311\Scripts\hermes.exe`，v2.7 只覆盖了 `%APPDATA%\Python\Python311\Scripts` 和 `%LOCALAPPDATA%\Programs\Python\Python312\Scripts` 等路径，遗漏 LocalAppData Python 3.11 Scripts。
- `python -m pip show hermes-agent` 和 `py -m pip show hermes-agent` 会查询当前默认 Python，不一定等于 Hermes 所在 Python；本机需要使用 `%LOCALAPPDATA%\Programs\Python\Python311\python.exe -m pip show hermes-agent` 才能看到 `0.14.0`。
- `hermes version` 输出包含特殊符号，Windows 默认 GBK 解码会触发 `UnicodeDecodeError`，导致验证器把已安装误判为未安装；子进程读取需要固定 UTF-8 并用替换策略处理异常字符。
