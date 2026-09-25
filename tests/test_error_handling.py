from types import SimpleNamespace
from unittest.mock import Mock

import openai
import pytest

from errors import (
    InvalidAPIKeyError,
    MalformedModelResponse,
    MissingAPIKeyError,
    RateLimitError,
    RequestTimeoutError,
)
from llm_client import create_client, request_proposal


def fake_client_with_error(error: Exception) -> SimpleNamespace:
    create = Mock(side_effect=error)
    return SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create))
    )


def test_missing_api_key_has_actionable_error() -> None:
    with pytest.raises(MissingAPIKeyError) as raised:
        create_client("", "https://provider.example/v1")

    assert "No API key" in raised.value.user_message


def test_authentication_error_maps_to_invalid_key_message() -> None:
    request = SimpleNamespace()
    response = SimpleNamespace(status_code=401, headers={}, request=request)
    error = openai.AuthenticationError("provider detail", response=response, body=None)

    with pytest.raises(InvalidAPIKeyError) as raised:
        request_proposal(fake_client_with_error(error), "model", "prompt")

    assert "API key was rejected" in raised.value.user_message
    assert "provider detail" not in raised.value.user_message


def test_rate_limit_error_has_retry_guidance() -> None:
    request = SimpleNamespace()
    response = SimpleNamespace(status_code=429, headers={}, request=request)
    error = openai.RateLimitError("quota detail", response=response, body=None)

    with pytest.raises(RateLimitError) as raised:
        request_proposal(fake_client_with_error(error), "model", "prompt")

    assert "rate-limiting" in raised.value.user_message
    assert "quota detail" not in raised.value.user_message


def test_timeout_error_has_network_guidance() -> None:
    request = SimpleNamespace()
    error = openai.APITimeoutError(request)

    with pytest.raises(RequestTimeoutError) as raised:
        request_proposal(fake_client_with_error(error), "model", "prompt")

    assert "timed out" in raised.value.user_message


def test_plain_model_response_maps_to_malformed_response_error() -> None:
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(tool_calls=None))]
    )
    client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=Mock(return_value=response))
        )
    )

    with pytest.raises(MalformedModelResponse) as raised:
        request_proposal(client, "model", "prompt")

    assert "invalid proposal response" in raised.value.user_message
