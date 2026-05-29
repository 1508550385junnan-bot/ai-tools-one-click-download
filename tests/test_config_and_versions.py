import json
import os
import tempfile
import unittest
from unittest import mock
from urllib.error import HTTPError

from core.api_configurator import (
    configure_claude,
    configure_hermes,
    test_api_connection,
)
from core.downloader import Downloader
from core.installer import Installer
from core.version_utils import is_upgrade_available, normalize_version


class APIConfiguratorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_home = os.environ.get("AI_TOOLS_TEST_HOME")
        self.old_skip = os.environ.get("AI_TOOLS_SKIP_SETX")
        os.environ["AI_TOOLS_TEST_HOME"] = self.tmp.name
        os.environ["AI_TOOLS_SKIP_SETX"] = "1"

    def tearDown(self):
        if self.old_home is None:
            os.environ.pop("AI_TOOLS_TEST_HOME", None)
        else:
            os.environ["AI_TOOLS_TEST_HOME"] = self.old_home
        if self.old_skip is None:
            os.environ.pop("AI_TOOLS_SKIP_SETX", None)
        else:
            os.environ["AI_TOOLS_SKIP_SETX"] = self.old_skip
        self.tmp.cleanup()

    def test_configure_claude_writes_anthropic_compatible_settings(self):
        result = configure_claude("deepseek", "sk-test-12345678")

        self.assertTrue(result["success"], result)
        settings_path = os.path.join(self.tmp.name, ".claude", "settings.json")
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)

        self.assertEqual(settings["env"]["ANTHROPIC_BASE_URL"], "https://api.deepseek.com/anthropic")
        self.assertEqual(settings["env"]["ANTHROPIC_MODEL"], "deepseek-v4-pro[1M]")
        self.assertIn("apiKeyHelper", settings)

    def test_configure_hermes_writes_env_and_config(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML 未安装")

        result = configure_hermes("openai", "sk-test-12345678", "gpt-4o")

        self.assertTrue(result["success"], result)
        env_path = os.path.join(self.tmp.name, ".hermes", ".env")
        config_path = os.path.join(self.tmp.name, ".hermes", "config.yaml")

        with open(env_path, "r", encoding="utf-8") as f:
            self.assertIn("OPENAI_API_KEY=sk-test-12345678", f.read())
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        self.assertEqual(config["model"]["provider"], "openai-api")
        self.assertEqual(config["model"]["default"], "gpt-4o")
        self.assertEqual(config["providers"]["openai-api"]["base_url"], "https://api.openai.com/v1")

    def test_api_connection_treats_401_as_failure(self):
        error = HTTPError(
            url="https://api.openai.com/v1/chat/completions",
            code=401,
            msg="Unauthorized",
            hdrs=None,
            fp=mock.Mock(read=lambda: b'{"error":"bad key"}'),
        )
        with mock.patch("urllib.request.urlopen", side_effect=error):
            result = test_api_connection("openai", "sk-test-12345678", "gpt-4o")

        self.assertFalse(result["ok"])
        self.assertIn("认证失败", result["message"])


class VersionUtilsTests(unittest.TestCase):
    def test_numeric_version_compare(self):
        self.assertEqual(normalize_version("v3.15.0.0"), (3, 15))
        self.assertTrue(is_upgrade_available("3.9.0", "3.10.0"))
        self.assertFalse(is_upgrade_available("3.15.0.0", "3.15.0"))
        self.assertFalse(is_upgrade_available("已安装", "3.15.0"))


class InstallerBehaviorTests(unittest.TestCase):
    def test_downloader_skips_complete_existing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            import core.downloader as downloader_mod

            old_dir = downloader_mod.DOWNLOAD_DIR
            downloader_mod.DOWNLOAD_DIR = tmp
            try:
                path = os.path.join(tmp, "package.msi")
                with open(path, "wb") as f:
                    f.write(b"12345")

                head_response = mock.Mock()
                head_response.__enter__ = mock.Mock(return_value=head_response)
                head_response.__exit__ = mock.Mock(return_value=False)
                head_response.headers = {"Content-Length": "5"}

                with mock.patch("urllib.request.urlopen", return_value=head_response) as mocked:
                    result = Downloader().download("https://example.com/package.msi", "package.msi")

                self.assertEqual(result, path)
                self.assertEqual(mocked.call_count, 1)
            finally:
                downloader_mod.DOWNLOAD_DIR = old_dir

    def test_msi_reboot_required_is_success(self):
        completed = mock.Mock(returncode=3010, stdout="", stderr="")
        with mock.patch("subprocess.run", return_value=completed):
            self.assertTrue(Installer()._install_msi("package.msi", ["/quiet"]))


if __name__ == "__main__":
    unittest.main()
