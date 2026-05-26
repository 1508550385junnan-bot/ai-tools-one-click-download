# core/api_configurator.py - API 模型一键配置模块
# v2.5: 深入学习 CC Switch，直接修改 CLI 工具配置文件
import os
import sys
import json
import shutil
import subprocess
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ============================================================
# 13 家模型厂家
# ============================================================
PROVIDERS = {
    "anthropic": {
        "name": "Anthropic", "name_cn": "Anthropic", "icon": "🏛️",
        "models": ["claude-opus-4.7", "claude-sonnet-4.6", "claude-haiku-4.0"],
        "base_url": "https://api.anthropic.com",
        "desc": "Claude 系列，Claude Code 官方原生支持",
        "claude_compat": True, "hermes_compat": True,
    },
    "openai": {
        "name": "OpenAI", "name_cn": "OpenAI", "icon": "🧠",
        "models": ["gpt-5.1-thinking", "gpt-5.1-instant", "o5-ultra", "o5-mini", "gpt-4o-advanced"],
        "base_url": "https://api.openai.com/v1",
        "desc": "全球顶尖大模型，ChatGPT 缔造者",
        "claude_compat": False, "hermes_compat": True,
    },
    "deepseek": {
        "name": "DeepSeek", "name_cn": "DeepSeek", "icon": "🔍",
        "models": ["deepseek-chat", "deepseek-reasoner"],
        "base_url": "https://api.deepseek.com",
        "desc": "国产开源标杆，Claude Code 原生兼容（V3.2 / R1-0528）",
        "claude_compat": True, "hermes_compat": True,
    },
    "qwen": {
        "name": "Qwen", "name_cn": "阿里通义千问", "icon": "☁️",
        "models": ["qwen3-omni", "qwen3-max-ultra", "qwen3-plus-pro"],
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "desc": "阿里巴巴自研，中文能力出色",
        "claude_compat": False, "hermes_compat": True,
    },
    "zhipu": {
        "name": "智谱AI", "name_cn": "智谱 GLM", "icon": "📘",
        "models": ["glm-4.7-ultra", "glm-4-flash-pro", "glm-5-preview"],
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "desc": "清华系，Claude Code 原生兼容",
        "claude_compat": True, "hermes_compat": True,
    },
    "google": {
        "name": "Google", "name_cn": "Google Gemini", "icon": "🌐",
        "models": ["gemini-3.1-pro", "gemini-3.1-flash", "gemini-3-ultra"],
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "desc": "Google DeepMind 多模态大模型",
        "claude_compat": False, "hermes_compat": True,
    },
    "meta": {
        "name": "Meta", "name_cn": "Meta Llama", "icon": "🦙",
        "models": ["llama-4.5-maverick", "llama-4-behemoth"],
        "base_url": "https://api.llama-api.com",
        "desc": "Meta 开源大模型，生态最丰富",
        "claude_compat": False, "hermes_compat": True,
    },
    "xai": {
        "name": "xAI", "name_cn": "xAI Grok", "icon": "🚀",
        "models": ["grok-4", "grok-4-mini"],
        "base_url": "https://api.x.ai/v1",
        "desc": "马斯克旗下，实时信息大模型",
        "claude_compat": False, "hermes_compat": True,
    },
    "mistral": {
        "name": "Mistral", "name_cn": "Mistral AI", "icon": "💨",
        "models": ["mistral-large-3.5", "pixtral-large-ultra", "mistral-small-2"],
        "base_url": "https://api.mistral.ai/v1",
        "desc": "法国顶尖 AI，轻量高效开源",
        "claude_compat": False, "hermes_compat": True,
    },
    "minimax": {
        "name": "MiniMax", "name_cn": "MiniMax 海螺", "icon": "🐚",
        "models": ["abab8-chat", "abab7-ultra-chat"],
        "base_url": "https://api.minimax.chat/v1",
        "desc": "海螺AI，长文本处理能力突出",
        "claude_compat": False, "hermes_compat": True,
    },
    "hunyuan": {
        "name": "腾讯混元", "name_cn": "腾讯 Hunyuan", "icon": "💬",
        "models": ["hunyuan-pro-max", "hunyuan-turbo-ultra", "hunyuan-omni"],
        "base_url": "https://api.hunyuan.cloud.tencent.com/v1",
        "desc": "腾讯自研，微信生态深度融合",
        "claude_compat": False, "hermes_compat": True,
    },
    "stepfun": {
        "name": "阶跃星辰", "name_cn": "StepFun", "icon": "⭐",
        "models": ["step-3-ultra", "step-2-pro-32k", "step-1.5v-pro"],
        "base_url": "https://api.stepfun.com/v1",
        "desc": "前微软高管创立，多模态能力强",
        "claude_compat": False, "hermes_compat": True,
    },
    "mimo": {
        "name": "小米 MiMo", "name_cn": "小米大模型", "icon": "📱",
        "models": ["MiMo-V2-Pro", "MiMo-V2-Omni", "MiMo-V2-TTS", "MiMo-V2.5-Pro", "MiMo-V2.5"],
        "base_url": "https://api.mimo.xiaomi.com/v1",
        "desc": "小米自研，端侧+云端全场景（2026.4最新）",
        "claude_compat": False, "hermes_compat": True,
    },
}

SUPPORTED_APPS = {
    "claude-code": {"name": "Claude Code", "icon": "🧠", "configurable": True,
                    "hint": "仅 Anthropic 官方。其他厂家需 API 中继。"},
    "hermes-agent": {"name": "Hermes Agent", "icon": "⚡", "configurable": True,
                     "hint": "支持所有 OpenAI 兼容 API。"},
    "codex-cli": {"name": "Codex CLI", "icon": "🤖", "configurable": False,
                  "hint": "仅支持 OpenAI 官方 API。"},
}

# ============================================================
# 核心：按 CC Switch 方式修改配置文件
# ============================================================

def _backup_file(path: str):
    """备份文件为 .bak"""
    if os.path.exists(path):
        bak = path + ".bak"
        shutil.copy2(path, bak)
        return bak
    return None


def _write_env_vars(vars_dict: dict) -> dict:
    """通过 setx 写入环境变量。返回 {name: success}"""
    results = {}
    for name, value in vars_dict.items():
        try:
            r = subprocess.run(
                ["setx", name, str(value)],
                capture_output=True, text=True, timeout=10,
            )
            results[name] = r.returncode == 0
            logger.info(f"setx {name}: {'OK' if r.returncode == 0 else 'FAIL'}")
        except Exception as e:
            results[name] = False
            logger.error(f"setx {name} 异常: {e}")
    return results


def _try_parse_yaml(path: str) -> dict | None:
    """尝试解析 YAML 文件"""
    try:
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        return None
    except Exception:
        return None


def _try_write_yaml(path: str, data: dict) -> bool:
    """尝试写入 YAML 文件"""
    try:
        import yaml
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        return True
    except Exception as e:
        logger.error(f"写入 YAML 失败: {e}")
        return False


def configure_claude(provider_key: str, api_key: str, model: str = None) -> dict:
    """
    配置 Claude Code — 参考 CC Switch
    允许配置所有厂家（通过 relay 中继服务接入）
    1. 设置环境变量 ANTHROPIC_AUTH_TOKEN / ANTHROPIC_API_KEY / ANTHROPIC_BASE_URL
    2. 修改 Claude Code 配置文件 settings.json
    3. 非 Anthropic 厂家提示使用 relay 服务
    """
    provider = PROVIDERS.get(provider_key)
    if not provider:
        return {"success": False, "error": "未知厂家"}
    if not model:
        model = provider["models"][0]

    messages = []

    # 1. 设置环境变量（CC Switch 风格）
    env_vars = {
        "ANTHROPIC_AUTH_TOKEN": api_key,
        "ANTHROPIC_API_KEY": api_key,
        "ANTHROPIC_BASE_URL": provider["base_url"],
    }
    env_results = _write_env_vars(env_vars)
    if all(env_results.values()):
        messages.append("✅ 环境变量已设置")
        messages.append(f"   ANTHROPIC_AUTH_TOKEN=***")
        messages.append(f"   ANTHROPIC_BASE_URL={provider['base_url']}")
    else:
        failed = [k for k, v in env_results.items() if not v]
        messages.append(f"⚠️ 部分环境变量失败: {failed}")

    # 2. 修改 settings.json
    claude_dir = os.path.join(os.path.expanduser("~"), ".claude")
    settings_path = os.path.join(claude_dir, "settings.json")
    os.makedirs(claude_dir, exist_ok=True)

    try:
        _backup_file(settings_path)
        if os.path.exists(settings_path):
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
        else:
            settings = {}

        settings["apiKeyHelper"] = None
        if "env" not in settings:
            settings["env"] = {}
        settings["env"]["ANTHROPIC_AUTH_TOKEN"] = api_key
        settings["env"]["ANTHROPIC_BASE_URL"] = provider["base_url"]

        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        messages.append(f"✅ settings.json 已更新")
    except Exception as e:
        messages.append(f"⚠️ settings.json 更新失败: {e}")

    # 3. 非 Anthropic 厂家提示
    if not provider["claude_compat"]:
        messages.append("")
        messages.append("⚠️ 该厂家使用 OpenAI 格式 API，Claude Code 需要 Anthropic 格式。")
        messages.append("   请使用 API 中继服务（如 CC Switch 管理的 relay）转发请求。")
        messages.append("   常用 relay: OpenRouter / SiliconFlow / Shengsuanyun / AIGoCode")

    messages.append(f"\n📋 厂家: {provider['name']} | 模型: {model}")
    messages.append("⚠️ 请重新打开终端使环境变量生效")

    return {"success": True, "message": "\n".join(messages)}


def configure_hermes(provider_key: str, api_key: str, model: str = None) -> dict:
    """
    配置 Hermes Agent — 参考 CC Switch hermes_config.rs
    1. 设置环境变量 OPENAI_API_KEY + OPENAI_BASE_URL
    2. 修改 ~/.hermes/config.yaml 的 custom_providers
    """
    provider = PROVIDERS.get(provider_key)
    if not provider:
        return {"success": False, "error": "未知厂家"}
    if not model:
        model = provider["models"][0]

    messages = []
    all_ok = True

    # 1. 环境变量
    env_vars = {
        "OPENAI_API_KEY": api_key,
        "OPENAI_BASE_URL": provider["base_url"],
    }
    env_results = _write_env_vars(env_vars)
    if all(env_results.values()):
        messages.append("✅ 环境变量已设置（OPENAI_API_KEY, OPENAI_BASE_URL）")
    else:
        failed = [k for k, v in env_results.items() if not v]
        messages.append(f"⚠️ 部分环境变量失败: {failed}")
        all_ok = False

    # 2. 修改 config.yaml
    hermes_dir = os.path.join(os.path.expanduser("~"), ".hermes")
    config_path = os.path.join(hermes_dir, "config.yaml")

    try:
        import yaml
    except ImportError:
        messages.append("\n⚠️ 未安装 pyyaml，跳过 config.yaml 修改")
        messages.append(f"📋 请手动编辑 {config_path}:\n"
                        f"  custom_providers:\n"
                        f"    - name: {provider['name']}\n"
                        f"      base_url: {provider['base_url']}\n"
                        f"      api_key_env: OPENAI_API_KEY\n"
                        f"      protocol: chat_completions\n"
                        f"      models:\n"
                        f"        - id: {model}")
        return {"success": True, "message": "\n".join(messages)}

    os.makedirs(hermes_dir, exist_ok=True)
    _backup_file(config_path)

    config = _try_parse_yaml(config_path) or {}
    if config is None:
        config = {}

    # 构建 custom_providers（参考 CC Switch 的 Hermes 配置结构）
    custom_providers = config.get("custom_providers", [])
    if custom_providers is None:
        custom_providers = []

    # 构建 provider entry
    provider_entry = {
        "name": provider["name"],
        "base_url": provider["base_url"],
        "api_key_env": "OPENAI_API_KEY",
        "protocol": "chat_completions",
        "models": {},
    }
    for m in provider["models"]:
        provider_entry["models"][f"{provider_key}/{m}"] = {"context_length": 131072}

    # 替换或新增
    replaced = False
    for i, cp in enumerate(custom_providers):
        if isinstance(cp, dict) and cp.get("name") == provider["name"]:
            custom_providers[i] = provider_entry
            replaced = True
            break
    if not replaced:
        custom_providers.append(provider_entry)

    config["custom_providers"] = custom_providers

    # 设置默认模型
    if "model" not in config:
        config["model"] = {}
    config["model"]["default"] = f"{provider_key}/{model}"

    if _try_write_yaml(config_path, config):
        messages.append(f"✅ Hermes config.yaml 已更新 ({config_path})")
        messages.append(f"   已添加 custom_provider: {provider['name']}")
        messages.append(f"   默认模型: {provider_key}/{model}")
    else:
        messages.append(f"⚠️ config.yaml 写入失败")

    messages.append("\n⚠️ 请重新打开终端使环境变量生效")
    return {"success": True, "message": "\n".join(messages)}


def _validate_input(app_key: str, provider_key: str, api_key: str) -> str | None:
    if app_key not in SUPPORTED_APPS:
        return f"不支持的程序: {app_key}"
    if not SUPPORTED_APPS[app_key]["configurable"]:
        return f"{SUPPORTED_APPS[app_key]['name']} 不支持配置第三方 API"
    if provider_key not in PROVIDERS:
        return f"未知厂家: {provider_key}"
    if not api_key or len(api_key.strip()) < 8:
        return "API Key 太短（至少8个字符）"
    if len(api_key.strip()) > 500:
        return f"API Key 过长（{len(api_key.strip())}字符），请检查是否粘贴了文件内容"
    return None


def test_api_connection(provider_key: str, api_key: str, model: str = None) -> dict:
    """测试 API 连接。发送最小请求验证连通性。"""
    import urllib.request
    import time

    provider = PROVIDERS.get(provider_key)
    if not provider or not provider.get("base_url"):
        return {"ok": False, "message": "厂家信息不完整"}
    if not model:
        model = provider["models"][0]

    base = provider["base_url"].rstrip("/")
    try:
        start = time.time()
        url = f"{base}/chat/completions"
        body = json.dumps({
            "model": model, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 1,
        }).encode("utf-8")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")

        import urllib.error
        with urllib.request.urlopen(req, timeout=10) as resp:
            elapsed = int((time.time() - start) * 1000)
            return {"ok": True, "message": f"连接成功 ({elapsed}ms)", "latency_ms": elapsed}
    except urllib.error.HTTPError as e:
        elapsed = int((time.time() - start) * 1000)
        if e.code in (401, 403):
            return {"ok": True, "message": f"API 端点可达 (认证格式正确, {elapsed}ms)", "latency_ms": elapsed}
        body = e.read().decode("utf-8", errors="ignore")[:200]
        return {"ok": False, "message": f"HTTP {e.code}", "latency_ms": elapsed}
    except Exception as e:
        msg = str(e)
        if "getaddrinfo" in msg.lower():
            return {"ok": False, "message": "域名解析失败，请检查 Base URL"}
        if "timeout" in msg.lower():
            return {"ok": False, "message": "连接超时"}
        return {"ok": False, "message": f"连接失败: {msg[:80]}"}


def try_configure(app_key: str, provider_key: str, api_key: str, model: str = None) -> dict:
    err = _validate_input(app_key, provider_key, api_key)
    if err:
        return {"success": False, "error": err}
    if app_key == "claude-code":
        return configure_claude(provider_key, api_key, model)
    elif app_key == "hermes-agent":
        return configure_hermes(provider_key, api_key, model)
    elif app_key == "codex-cli":
        return {"success": False, "error": "Codex CLI 仅支持 OpenAI 官方"}
    return {"success": False, "error": "不支持的程序"}
