import os
import unittest
from unittest.mock import patch

from config import (
    DEFAULT_API_BASE_URL,
    DEFAULT_COMPANY_CONTEXT,
    DEFAULT_MODELS,
    get_settings,
)


class SettingsTests(unittest.TestCase):
    def test_uses_safe_defaults_when_environment_is_empty(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            settings = get_settings()

        self.assertIsNone(settings.api_key)
        self.assertEqual(settings.base_url, DEFAULT_API_BASE_URL)
        self.assertEqual(settings.models, DEFAULT_MODELS)
        self.assertEqual(settings.company_context, DEFAULT_COMPANY_CONTEXT)

    def test_environment_overrides_provider_models_and_company_context(self) -> None:
        environment = {
            "GEMINI_API_KEY": "  session-key  ",
            "API_BASE_URL": "https://provider.example/v1",
            "MODELS": "model-a, model-b, ,",
            "COMPANY_CONTEXT": "A custom company profile.",
        }

        with patch.dict(os.environ, environment, clear=True):
            settings = get_settings()

        self.assertEqual(settings.api_key, "session-key")
        self.assertEqual(settings.base_url, "https://provider.example/v1")
        self.assertEqual(settings.models, ("model-a", "model-b"))
        self.assertEqual(settings.company_context, "A custom company profile.")


if __name__ == "__main__":
    unittest.main()
