# 任务计划

## 目标
修复 `C:\Users\15085\ai-tools-installer` 中 API 配置、CC Switch 安装失败、已安装检测后升级能力，并审查同范围安装器 bug。

## 阶段
| 阶段 | 内容 | 状态 |
|---|---|---|
| P1 | 读取现有结构、锁定需求、建立反馈循环 | complete |
| P2 | 网络研究 CC Switch、Claude Code/Hermes 配置、Windows MSI 安装最佳实践 | complete |
| P3 | 复现并定位 API 配置与 CC Switch 安装失败 | complete |
| P4 | 实现修复：API 配置引擎、安装/验证/版本比较 | complete |
| P5 | 增加或运行回归验证 | complete |
| P6 | 清理、审查 diff、自检交付 | complete |
| P7 | 升级版本、构建 exe、同步到 GitHub 仓库 | complete |
| P8 | 修复 Hermes、添加 OpenClaw、在线检测 AI 工具新版本 | complete |
| P9 | 升级 v2.7、测试低版本远程升级、打包并发布 GitHub | complete |
| P10 | 修复 Hermes LocalAppData Python 3.11 安装路径和输出解码误判 | complete |

## 错误记录
| 错误 | 尝试 | 处理 |
|---|---|---|
| 暂无 | - | - |
| GitHub API rate limit | 查询 CC Switch latest release API | 改用静态官方 Release URL + HEAD/本地安装验证，不依赖未认证 API |
| PowerShell Invoke-WebRequest NullReferenceException | 拉取 Claude/Hermes 文档 | 改用 Python urllib 获取文档片段 |
| 版本比较误判 | unittest 发现 `已安装` 被当成低版本 | 无法解析安装版本时不提示升级，避免误报 |

## 决策记录
| 决策 | 原因 |
|---|---|
| 使用文件化计划 | 本任务涉及多文件、多阶段调试与验证 |
| 优先建立本地可运行测试/脚本验证 | 避免只凭代码阅读判断安装器修复是否有效 |
| 发布版本定为 v2.6 | v2.5 已存在，当前修复 API 配置、CC Switch 安装、更新检测和打包发布，符合补丁/小版本升级语义 |
| 新增发布版本定为 v2.7 | 本轮新增 OpenClaw、Hermes 检测回退、在线工具更新检测和低版本升级判断，属于可发布功能更新 |
| 新增发布版本定为 v2.8 | 本轮修复 v2.7 未覆盖的 Hermes LocalAppData Python 3.11 路径和 Windows 输出解码失败，属于检测可靠性修复 |
