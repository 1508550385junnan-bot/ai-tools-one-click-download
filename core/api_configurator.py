# core/api_configurator.py - API 模型一键配置模块
# v2.4: 支持 Claude Code / Hermes Agent 配置主流模型厂家 API
import os
import subprocess
import logging

logger = logging.getLogger(__name__)

# 8 大主流模型厂家
PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "name_cn": "OpenAI",
        "icon": "🧠",
        "models": ["gpt-4o", "gpt-4.1", "o4-mini"],
        "base_url": "https://api.openai.com/v1",
        "desc": "GPT-4o / GPT-4.1 / o4-mini",
    },
    "anthropic": {
        "name": "Anthropic",
        "name_cn": "Anthropic",
        "icon": "🏛️",
        "models": ["claude-sonnet-4-20250514", "claude-opus-4-20250514", "claude-haiku-3.5"],
        "base_url": "https://api.anthropic.com",
        "desc": "Claude Sonnet 4 / Opus 4 / Haiku 3.5",
    },
    "google": {
        "name": "Google",
        "name_cn": "Google Gemini",
        "icon": "🌐",
        "models": ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite"],
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "desc": "Gemini 2.5 Pro / Flash",
    },
    "deepseek": {
        "name": "DeepSeek",
        "name_cn": "DeepSeek",
        "icon": "🔍",
        "models": ["deepseek-chat", "deepseek-reasoner"],
        "base_url": "https://api.deepseek.com",
        "desc": "DeepSeek-V3 / R1 推理模型",
    },
    "meta": {
        "name": "Meta",
        "name_cn": "Meta Llama",
        "icon": "🦙",
        "models": ["llama-4-maverick", "llama-4-scout"],
        "base_url": "https://api.llama-api.com",
        "desc": "Llama 4 Maverick / Scout",
    },
    "xai": {
        "name": "xAI",
        "name_cn": "xAI Grok",
        "icon": "🚀",
        "models": ["grok-3", "grok-3-mini"],
        "base_url": "https://api.x.ai/v1",
        "desc": "Grok-3 / Grok-3-mini",
    },
    "mistral": {
        "name": "Mistral",
        "name_cn": "Mistral AI",
        "icon": "💨",
        "models": ["mistral-large-latest", "mistral-small-latest", "codestral-latest"],
        "base_url": "https://api.mistral.ai/v1",
        "desc": "Mistral Large / Small / Codestral",
    },
    "qwen": {
        "name": "Qwen",
        "name_cn": "阿里通义千问",
        "icon": "☁️",
        "models": ["qwen-max", "qwen-plus", "qwen-turbo"],
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "desc": "通义千问 Max / Plus / Turbo",
    },
}

# 哪些程序支持配置
SUPPORTED_APPS = {
    "claude-code": {
        "name": "Claude Code",
        "icon": "🧠",
        "configurable": True,
        "hint": "支持配置第三方 API Key 和地址",
    },
    "hermes-agent": {
        "name": "Hermes Agent",
        "icon": "⚡",
        "configurable": True,
        "hint": "支持配置多 Provider",
    },
    "codex-cli": {
        "name": "Codex CLI",
        "icon": "🤖",
        "configurable": False,
        "hint": "仅支持 OpenAI API，无法配置第三方",
    },
}


def configure_claude(provider_key: str, api_key: str, model: str = None) -> dict:
    """
    配置 Claude Code 使用指定厂家的 API。
    Claude Code 通过环境变量 ANTHROPIC_BASE_URL 和 ANTHROPIC_API_KEY 配置。
    """
    provider = PROVIDERS.get(provider_key)
    if not provider:
        return {"success": False, "error": f"未知厂家: {provider_key}"}

    if not model:
        model = provider["models"][0]

    try:
        # 方法1：设置用户环境变量（当前用户永久生效）
        # 用 setx 命令设置用户环境变量
        results = []

        # 设置 API Key
        r1 = subprocess.run(
            ["setx", "ANTHROPIC_API_KEY", api_key],
            capture_output=True, text=True, timeout=10,
        )
        results.append(("ANTHROPIC_API_KEY", r1.returncode == 0))

        # 设置 API Base URL（如果不是 Anthropic 官方）
        if provider_key != "anthropic":
            r2 = subprocess.run(
                ["setx", "ANTHROPIC_BASE_URL", provider["base_url"]],
                capture_output=True, text=True, timeout=10,
            )
            results.append(("ANTHROPIC_BASE_URL", r2.returncode == 0))

        # 设置默认模型
        r3 = subprocess.run(
            ["setx", "ANTHROPIC_DEFAULT_MODEL", model],
            capture_output=True, text=True, timeout=10,
        )
        results.append(("ANTHROPIC_DEFAULT_MODEL", r3.returncode == 0))

        all_ok = all(r[1] for r in results)
        if all_ok:
            logger.info(f"Claude Code 配置成功: provider={provider_key}, model={model}")
            return {
                "success": True,
                "message": f"已配置 Claude Code 使用 {provider['name']}\n模型: {model}\n请重新打开终端生效",
                "details": results,
            }
        else:
            failed = [r[0] for r in results if not r[1]]
            return {
                "success": False,
                "error": f"部分环境变量设置失败: {', '.join(failed)}",
            }
    except Exception as e:
        logger.error(f"Claude Code 配置失败: {e}")
        return {"success": False, "error": str(e)}


def configure_hermes(provider_key: str, api_key: str, model: str = None) -> dict:
    """
    配置 Hermes Agent 使用指定厂家的 API。
    Hermes Agent 通过 hermes config set 命令配置。
    """
    provider = PROVIDERS.get(provider_key)
    if not provider:
        return {"success": False, "error": f"未知厂家: {provider_key}"}

    if not model:
        model = provider["models"][0]

    try:
        results = []

        # 检查 hermes 是否可用
        check = subprocess.run(
            ["hermes", "version"], capture_output=True, text=True, timeout=10,
        )
        if check.returncode != 0:
            return {
                "success": False,
                "error": "Hermes Agent 未安装或不在 PATH 中。请先安装 Hermes Agent。",
            }

        # 设置 provider
        # 将 provider_key 映射为 hermes 支持的 provider 名称
        hermes_provider_map = {
            "openai": "openai",
            "anthropic": "anthropic",
            "google": "google",
            "deepseek": "openai",       # DeepSeek 兼容 OpenAI 格式
            "meta": "openai",            # Llama API 兼容 OpenAI 格式
            "xai": "openai",             # xAI 兼容 OpenAI 格式
            "mistral": "openai",         # Mistral 兼容 OpenAI 格式
            "qwen": "openai",            # Qwen 兼容 OpenAI 格式
        }

        h_provider = hermes_provider_map.get(provider_key, "custom")

        # 设置 API key（通过环境变量或 config）
        # 大多数 provider 通过 OPENAI_API_KEY 环境变量
        env_var_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "google": "GOOGLE_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
            "meta": "LLAMA_API_KEY",
            "xai": "XAI_API_KEY",
            "mistral": "MISTRAL_API_KEY",
            "qwen": "DASHSCOPE_API_KEY",
        }
        env_var = env_var_map.get(provider_key, "OPENAI_API_KEY")

        # 设置环境变量
        r1 = subprocess.run(
            ["setx", env_var, api_key],
            capture_output=True, text=True, timeout=10,
        )
        results.append((f"{env_var} 环境变量", r1.returncode == 0))

        # 如果 provider 不是标准后端，配置自定义 base_url
        if provider_key not in ("openai", "anthropic", "google"):
            # 设置自定义 endpoint 环境变量
            r2 = subprocess.run(
                ["setx", "OPENAI_BASE_URL", provider["base_url"]],
                capture_output=True, text=True, timeout=10,
            )
            results.append(("OPENAI_BASE_URL 环境变量", r2.returncode == 0))

        all_ok = all(r[1] for r in results)
        if all_ok:
            logger.info(f"Hermes Agent 配置成功: provider={provider_key}, model={model}")
            return {
                "success": True,
                "message": (
                    f"已配置 Hermes Agent 使用 {provider['name']}\n"
                    f"模型: {model}\n"
                    f"请运行以下命令完成配置:\n"
                    f"  hermes config set provider custom\n"
                    f"  hermes config set model custom/{model}\n"
                    f"环境变量已设置，请重新打开终端生效"
                ),
                "details": results,
            }
        else:
            failed = [r[0] for r in results if not r[1]]
            return {
                "success": False,
                "error": f"部分设置失败: {', '.join(failed)}",
            }
    except Exception as e:
        logger.error(f"Hermes Agent 配置失败: {e}")
        return {"success": False, "error": str(e)}


def try_configure(app_key: str, provider_key: str, api_key: str, model: str = None) -> dict:
    """
    统一的配置入口。
    返回 {"success": bool, "message": str, "error": str}
    """
    if app_key == "claude-code":
        return configure_claude(provider_key, api_key, model)
    elif app_key == "hermes-agent":
        return configure_hermes(provider_key, api_key, model)
    elif app_key == "codex-cli":
        return {"success": False, "error": "Codex CLI 仅支持 OpenAI 官方 API，无法配置第三方模型"}
    else:
        return {"success": False, "error": f"不支持的程序: {app_key}"}
