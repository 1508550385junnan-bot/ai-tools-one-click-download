# core/api_configurator.py - API 模型一键配置模块
import json
import logging
import os
import shutil
import subprocess
from datetime import datetime
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


CLAUDE_MODEL_ENV_KEYS = (
    "ANTHROPIC_MODEL",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL_NAME",
    "ANTHROPIC_DEFAULT_OPUS_MODEL",
    "ANTHROPIC_DEFAULT_OPUS_MODEL_NAME",
    "ANTHROPIC_DEFAULT_SONNET_MODEL",
    "ANTHROPIC_DEFAULT_SONNET_MODEL_NAME",
)


PROVIDERS = {
    "anthropic": {
        "name": "Anthropic", "name_cn": "Anthropic", "icon": "🏛️",
        "models": ["claude-sonnet-4-5", "claude-opus-4-1", "claude-3-5-haiku-latest"],
        "base_url": "https://api.anthropic.com",
        "claude_base_url": "https://api.anthropic.com",
        "api_format": "anthropic",
        "hermes_provider": "anthropic",
        "hermes_api_key_env": "ANTHROPIC_API_KEY",
        "desc": "Claude Code 官方原生协议",
        "claude_compat": True, "hermes_compat": True,
    },
    "deepseek": {
        "name": "DeepSeek", "name_cn": "DeepSeek", "icon": "🔍",
        "models": ["deepseek-v4-pro[1M]", "deepseek-chat", "deepseek-reasoner"],
        "base_url": "https://api.deepseek.com",
        "claude_base_url": "https://api.deepseek.com/anthropic",
        "api_format": "openai",
        "hermes_provider": "deepseek",
        "hermes_api_key_env": "DEEPSEEK_API_KEY",
        "desc": "OpenAI 兼容 API；Claude Code 使用 /anthropic 端点",
        "claude_compat": True, "hermes_compat": True,
    },
    "openai": {
        "name": "OpenAI", "name_cn": "OpenAI", "icon": "🧠",
        "models": ["gpt-5.1", "gpt-5.1-mini", "gpt-4o"],
        "base_url": "https://api.openai.com/v1",
        "api_format": "openai",
        "hermes_provider": "openai-api",
        "hermes_api_key_env": "OPENAI_API_KEY",
        "desc": "OpenAI 兼容 API，适合 Hermes Agent",
        "claude_compat": False, "hermes_compat": True,
    },
    "qwen": {
        "name": "Qwen", "name_cn": "阿里通义千问", "icon": "☁️",
        "models": ["qwen-plus", "qwen-max", "qwen-turbo"],
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "api_format": "openai",
        "hermes_provider": "qwen",
        "hermes_api_key_env": "DASHSCOPE_API_KEY",
        "desc": "阿里云 DashScope OpenAI 兼容 API",
        "claude_compat": False, "hermes_compat": True,
    },
    "zhipu": {
        "name": "智谱AI", "name_cn": "智谱 GLM", "icon": "📘",
        "models": ["glm-4-plus", "glm-4-flash", "glm-4-air"],
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "api_format": "openai",
        "hermes_provider": "zhipu",
        "hermes_api_key_env": "ZHIPUAI_API_KEY",
        "desc": "智谱 OpenAI 兼容 API",
        "claude_compat": False, "hermes_compat": True,
    },
    "google": {
        "name": "Google", "name_cn": "Google Gemini", "icon": "🌐",
        "models": ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash"],
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "api_format": "openai",
        "hermes_provider": "gemini",
        "hermes_api_key_env": "GEMINI_API_KEY",
        "desc": "Gemini OpenAI 兼容端点",
        "claude_compat": False, "hermes_compat": True,
    },
    "openrouter": {
        "name": "OpenRouter", "name_cn": "OpenRouter", "icon": "🧭",
        "models": ["anthropic/claude-sonnet-4.5", "openai/gpt-5.1", "deepseek/deepseek-chat"],
        "base_url": "https://openrouter.ai/api/v1",
        "api_format": "openai",
        "hermes_provider": "openrouter",
        "hermes_api_key_env": "OPENROUTER_API_KEY",
        "desc": "多模型聚合，适合 Hermes Agent",
        "claude_compat": False, "hermes_compat": True,
    },
    "xai": {
        "name": "xAI", "name_cn": "xAI Grok", "icon": "🚀",
        "models": ["grok-4", "grok-4-mini"],
        "base_url": "https://api.x.ai/v1",
        "api_format": "openai",
        "hermes_provider": "xai",
        "hermes_api_key_env": "XAI_API_KEY",
        "desc": "xAI OpenAI 兼容 API",
        "claude_compat": False, "hermes_compat": True,
    },
    "mistral": {
        "name": "Mistral", "name_cn": "Mistral AI", "icon": "💨",
        "models": ["mistral-large-latest", "mistral-small-latest", "codestral-latest"],
        "base_url": "https://api.mistral.ai/v1",
        "api_format": "openai",
        "hermes_provider": "mistral",
        "hermes_api_key_env": "MISTRAL_API_KEY",
        "desc": "Mistral OpenAI 兼容 API",
        "claude_compat": False, "hermes_compat": True,
    },
    "minimax": {
        "name": "MiniMax", "name_cn": "MiniMax 海螺", "icon": "🐚",
        "models": ["MiniMax-M1", "abab6.5s-chat", "abab6.5g-chat"],
        "base_url": "https://api.minimax.chat/v1",
        "api_format": "openai",
        "hermes_provider": "minimax",
        "hermes_api_key_env": "MINIMAX_API_KEY",
        "desc": "MiniMax OpenAI 兼容 API",
        "claude_compat": False, "hermes_compat": True,
    },
    "hunyuan": {
        "name": "腾讯混元", "name_cn": "腾讯 Hunyuan", "icon": "💬",
        "models": ["hunyuan-turbos-latest", "hunyuan-large", "hunyuan-standard"],
        "base_url": "https://api.hunyuan.cloud.tencent.com/v1",
        "api_format": "openai",
        "hermes_provider": "hunyuan",
        "hermes_api_key_env": "HUNYUAN_API_KEY",
        "desc": "腾讯混元 OpenAI 兼容 API",
        "claude_compat": False, "hermes_compat": True,
    },
    "stepfun": {
        "name": "阶跃星辰", "name_cn": "StepFun", "icon": "⭐",
        "models": ["step-2-16k", "step-1-8k", "step-1v-8k"],
        "base_url": "https://api.stepfun.com/v1",
        "api_format": "openai",
        "hermes_provider": "stepfun",
        "hermes_api_key_env": "STEPFUN_API_KEY",
        "desc": "阶跃星辰 OpenAI 兼容 API",
        "claude_compat": False, "hermes_compat": True,
    },
    "custom": {
        "name": "自定义端点", "name_cn": "Custom Endpoint", "icon": "⚙️",
        "models": ["custom-model"],
        "base_url": "",
        "api_format": "openai",
        "hermes_provider": "custom",
        "hermes_api_key_env": "CUSTOM_API_KEY",
        "desc": "自定义 OpenAI/Anthropic 兼容网关",
        "claude_compat": True, "hermes_compat": True,
    },
}


SUPPORTED_APPS = {
    "claude-code": {"name": "Claude Code", "icon": "🧠", "configurable": True,
                    "hint": "需要 Anthropic 协议；DeepSeek 使用 /anthropic 或自定义中继。"},
    "hermes-agent": {"name": "Hermes Agent", "icon": "⚡", "configurable": True,
                     "hint": "写入 ~/.hermes/.env 和 config.yaml。"},
    "codex-cli": {"name": "Codex CLI", "icon": "🤖", "configurable": False,
                  "hint": "当前安装器不改写 Codex CLI 认证。"},
}


def _home_dir() -> str:
    return os.environ.get("AI_TOOLS_TEST_HOME") or os.path.expanduser("~")


def _backup_file(path: str) -> str | None:
    if not os.path.exists(path):
        return None
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    bak = f"{path}.bak-{ts}"
    shutil.copy2(path, bak)
    return bak


def _atomic_write_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


def _read_json(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception as e:
        raise ValueError(f"JSON 解析失败: {e}") from e


def _write_json(path: str, data: dict) -> None:
    _atomic_write_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def _quote_powershell_single(value: str) -> str:
    return value.replace("'", "''")


def _write_env_vars(vars_dict: dict) -> dict:
    results = {}
    skip_setx = os.environ.get("AI_TOOLS_SKIP_SETX") == "1"
    for name, value in vars_dict.items():
        value = str(value)
        os.environ[name] = value
        if skip_setx:
            results[name] = True
            continue
        try:
            r = subprocess.run(
                ["setx", name, value],
                capture_output=True, text=True, timeout=10,
            )
            results[name] = r.returncode == 0
            if r.returncode != 0:
                logger.warning("setx %s 失败: %s", name, (r.stderr or r.stdout)[:200])
        except Exception as e:
            results[name] = False
            logger.error("setx %s 异常: %s", name, e)
    return results


def _merge_dotenv(path: str, values: dict) -> None:
    existing = []
    seen = set()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            existing = f.read().splitlines()

    lines = []
    for line in existing:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in line:
            lines.append(line)
            continue
        key = line.split("=", 1)[0].strip()
        if key in values:
            lines.append(f"{key}={values[key]}")
            seen.add(key)
        else:
            lines.append(line)

    for key, value in values.items():
        if key not in seen:
            lines.append(f"{key}={value}")

    _backup_file(path)
    _atomic_write_text(path, "\n".join(lines).rstrip() + "\n")


def _parse_yaml(path: str) -> dict:
    try:
        import yaml
    except ImportError as e:
        raise RuntimeError("缺少 PyYAML，无法写入 Hermes config.yaml") from e
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data if isinstance(data, dict) else {}


def _write_yaml(path: str, data: dict) -> None:
    try:
        import yaml
    except ImportError as e:
        raise RuntimeError("缺少 PyYAML，无法写入 Hermes config.yaml") from e
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
    os.replace(tmp, path)


def _provider_base(provider: dict, app_key: str, override_base_url: str | None) -> str:
    base_url = (override_base_url or "").strip()
    if base_url:
        return base_url.rstrip("/")
    if app_key == "claude-code":
        return (provider.get("claude_base_url") or provider.get("base_url") or "").rstrip("/")
    return (provider.get("base_url") or "").rstrip("/")


def configure_claude(provider_key: str, api_key: str, model: str | None = None,
                     base_url: str | None = None) -> dict:
    provider = PROVIDERS.get(provider_key)
    if not provider:
        return {"success": False, "error": "未知厂家"}
    if not model:
        model = provider["models"][0]

    endpoint = _provider_base(provider, "claude-code", base_url)
    if not endpoint:
        return {"success": False, "error": "Claude Code 配置缺少 Base URL"}
    if not provider.get("claude_compat") and not base_url:
        return {
            "success": False,
            "error": f"{provider['name']} 不是 Anthropic 协议端点。请填写 Anthropic 兼容中继 Base URL。",
        }

    env_vars = {
        "ANTHROPIC_API_KEY": api_key,
        "ANTHROPIC_AUTH_TOKEN": api_key,
        "ANTHROPIC_BASE_URL": endpoint,
    }
    for key in CLAUDE_MODEL_ENV_KEYS:
        env_vars[key] = model

    claude_dir = os.path.join(_home_dir(), ".claude")
    settings_path = os.path.join(claude_dir, "settings.json")
    try:
        os.makedirs(claude_dir, exist_ok=True)
        settings = _read_json(settings_path)
        _backup_file(settings_path)
        settings.setdefault("env", {})
        settings["env"].update(env_vars)
        settings["apiKeyHelper"] = (
            "powershell -NoProfile -Command "
            f"\"Write-Output '{_quote_powershell_single(api_key)}'\""
        )
        _write_json(settings_path, settings)
    except Exception as e:
        return {"success": False, "error": f"Claude settings.json 写入失败: {e}"}

    env_results = _write_env_vars(env_vars)
    failed = [key for key, ok in env_results.items() if not ok]
    messages = [
        "✅ Claude Code 配置已写入",
        f"   配置文件: {settings_path}",
        f"   Base URL: {endpoint}",
        f"   模型: {model}",
    ]
    if failed:
        messages.append(f"⚠️ setx 持久化失败: {', '.join(failed)}；settings.json 已生效，重开 Claude Code 后使用。")
    else:
        messages.append("✅ 环境变量已持久化，新终端自动生效")
    logger.info("Claude Code 配置成功: provider=%s model=%s base=%s", provider_key, model, endpoint)
    return {"success": True, "message": "\n".join(messages)}


def configure_hermes(provider_key: str, api_key: str, model: str | None = None,
                     base_url: str | None = None) -> dict:
    provider = PROVIDERS.get(provider_key)
    if not provider:
        return {"success": False, "error": "未知厂家"}
    if not model:
        model = provider["models"][0]

    endpoint = _provider_base(provider, "hermes-agent", base_url)
    if not endpoint:
        return {"success": False, "error": "Hermes 配置缺少 Base URL"}

    hermes_dir = os.path.join(_home_dir(), ".hermes")
    env_path = os.path.join(hermes_dir, ".env")
    config_path = os.path.join(hermes_dir, "config.yaml")
    provider_id = provider.get("hermes_provider", provider_key)
    api_key_env = provider.get("hermes_api_key_env", f"{provider_key.upper()}_API_KEY")

    try:
        os.makedirs(hermes_dir, exist_ok=True)
        dotenv_values = {api_key_env: api_key}
        if provider_id == "openai-api" or provider_key == "custom":
            dotenv_values["OPENAI_BASE_URL"] = endpoint
        _merge_dotenv(env_path, dotenv_values)

        config = _parse_yaml(config_path)
        _backup_file(config_path)
        config.setdefault("model", {})
        config["model"]["provider"] = provider_id
        config["model"]["default"] = model

        providers = config.setdefault("providers", {})
        if not isinstance(providers, dict):
            providers = {}
            config["providers"] = providers
        providers[provider_id] = {
            "base_url": endpoint,
            "api_key_env": api_key_env,
            "models": list(provider.get("models", [model])),
        }

        custom_providers = config.get("custom_providers")
        if not isinstance(custom_providers, list):
            custom_providers = []
        custom_entry = {
            "name": provider_id,
            "base_url": endpoint,
            "api_key_env": api_key_env,
            "protocol": "messages" if provider.get("api_format") == "anthropic" else "chat_completions",
            "models": {m: {"context_length": 131072} for m in provider.get("models", [model])},
        }
        custom_providers = [
            item for item in custom_providers
            if not (isinstance(item, dict) and item.get("name") == provider_id)
        ]
        custom_providers.append(custom_entry)
        config["custom_providers"] = custom_providers
        _write_yaml(config_path, config)
    except Exception as e:
        return {"success": False, "error": f"Hermes 配置写入失败: {e}"}

    env_results = _write_env_vars({api_key_env: api_key})
    failed = [key for key, ok in env_results.items() if not ok]
    messages = [
        "✅ Hermes Agent 配置已写入",
        f"   .env: {env_path}",
        f"   config.yaml: {config_path}",
        f"   provider: {provider_id}",
        f"   Base URL: {endpoint}",
        f"   模型: {model}",
    ]
    if failed:
        messages.append(f"⚠️ setx 持久化失败: {', '.join(failed)}；Hermes 会从 ~/.hermes/.env 读取。")
    logger.info("Hermes Agent 配置成功: provider=%s model=%s base=%s", provider_id, model, endpoint)
    return {"success": True, "message": "\n".join(messages)}


def _validate_input(app_key: str, provider_key: str, api_key: str,
                    model: str | None = None, base_url: str | None = None) -> str | None:
    if app_key not in SUPPORTED_APPS:
        return f"不支持的程序: {app_key}"
    if not SUPPORTED_APPS[app_key]["configurable"]:
        return f"{SUPPORTED_APPS[app_key]['name']} 不支持在此页面配置"
    if provider_key not in PROVIDERS:
        return f"未知厂家: {provider_key}"
    if not api_key or len(api_key.strip()) < 8:
        return "API Key 太短（至少8个字符）"
    if len(api_key.strip()) > 500:
        return f"API Key 过长（{len(api_key.strip())}字符），请检查是否粘贴了文件内容"
    if model is not None and not model.strip():
        return "模型名称不能为空"
    if base_url is not None and base_url.strip() and not base_url.strip().startswith(("http://", "https://")):
        return "Base URL 必须以 http:// 或 https:// 开头"
    return None


def _build_test_request(provider: dict, api_key: str, model: str, base_url: str):
    import urllib.request

    api_format = provider.get("api_format", "openai")
    base = base_url.rstrip("/") + "/"
    if api_format == "anthropic" or "/anthropic" in base_url:
        url = urljoin(base, "v1/messages")
        payload = {
            "model": model,
            "max_tokens": 1,
            "messages": [{"role": "user", "content": "hi"}],
        }
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Authorization": f"Bearer {api_key}",
        }
    else:
        url = urljoin(base, "chat/completions")
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 1,
        }
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = json.dumps(payload).encode("utf-8")
    return urllib.request.Request(url, data=body, headers=headers, method="POST")


def test_api_connection(provider_key: str, api_key: str, model: str | None = None,
                        base_url: str | None = None) -> dict:
    import time
    import urllib.error
    import urllib.request

    provider = PROVIDERS.get(provider_key)
    if not provider:
        return {"ok": False, "message": "未知厂家"}
    if not model:
        model = provider["models"][0]
    endpoint = _provider_base(provider, "hermes-agent", base_url)
    if not endpoint:
        return {"ok": False, "message": "Base URL 为空"}

    start = time.time()
    try:
        req = _build_test_request(provider, api_key, model, endpoint)
        with urllib.request.urlopen(req, timeout=15):
            elapsed = int((time.time() - start) * 1000)
            return {"ok": True, "message": f"连接成功 ({elapsed}ms)", "latency_ms": elapsed}
    except urllib.error.HTTPError as e:
        elapsed = int((time.time() - start) * 1000)
        body = e.read().decode("utf-8", errors="ignore")[:240]
        if e.code in (401, 403):
            return {"ok": False, "message": f"认证失败 HTTP {e.code}: 请检查 API Key", "latency_ms": elapsed}
        if e.code == 404:
            return {"ok": False, "message": "端点不存在 HTTP 404，请检查 Base URL/协议", "latency_ms": elapsed}
        if e.code in (400, 422):
            return {"ok": False, "message": f"请求格式或模型不支持 HTTP {e.code}: {body}", "latency_ms": elapsed}
        return {"ok": False, "message": f"HTTP {e.code}: {body}", "latency_ms": elapsed}
    except Exception as e:
        msg = str(e)
        if "getaddrinfo" in msg.lower():
            return {"ok": False, "message": "域名解析失败，请检查 Base URL"}
        if "timeout" in msg.lower() or "timed out" in msg.lower():
            return {"ok": False, "message": "连接超时"}
        return {"ok": False, "message": f"连接失败: {msg[:120]}"}


def try_configure(app_key: str, provider_key: str, api_key: str,
                  model: str | None = None, base_url: str | None = None) -> dict:
    err = _validate_input(app_key, provider_key, api_key, model, base_url)
    if err:
        return {"success": False, "error": err}
    api_key = api_key.strip()
    model = model.strip() if model else None
    base_url = base_url.strip() if base_url else None
    if app_key == "claude-code":
        return configure_claude(provider_key, api_key, model, base_url)
    if app_key == "hermes-agent":
        return configure_hermes(provider_key, api_key, model, base_url)
    if app_key == "codex-cli":
        return {"success": False, "error": "Codex CLI 当前不支持在此页面配置"}
    return {"success": False, "error": "不支持的程序"}
