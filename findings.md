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

## 范围外问题
- 暂无。
