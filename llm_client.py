from __future__ import annotations

from typing import Any

import openai
from openai import OpenAI

from errors import (
    ConfigurationError,
    InvalidAPIKeyError,
    MalformedModelResponse,
    MissingAPIKeyError,
    ProposalGenerationError,
    ProviderConnectionError,
    RateLimitError,
    RequestTimeoutError,
)
from proposal_schema import (
    PROPOSAL_TOOL,
    PROPOSAL_TOOL_CHOICE,
    Proposal,
    parse_proposal_response,
)


def create_client(api_key: str | None, base_url: str) -> OpenAI:
    if not api_key or not api_key.strip():
        raise MissingAPIKeyError()
    if not base_url.strip():
        raise ConfigurationError()

    try:
        return OpenAI(api_key=api_key.strip(), base_url=base_url.strip())
    except openai.AuthenticationError as error:
        raise InvalidAPIKeyError() from error
    except (openai.OpenAIError, ValueError) as error:
        raise ConfigurationError() from error


def request_proposal(
    client: OpenAI,
    model: str,
    prompt: str,
    temperature: float = 0.7,
) -> Proposal:
    try:
        response: Any = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            tools=[PROPOSAL_TOOL],
            tool_choice=PROPOSAL_TOOL_CHOICE,
        )
    except openai.AuthenticationError as error:
        raise InvalidAPIKeyError() from error
    except openai.PermissionDeniedError as error:
        raise InvalidAPIKeyError() from error
    except openai.RateLimitError as error:
        raise RateLimitError() from error
    except openai.APITimeoutError as error:
        raise RequestTimeoutError() from error
    except (TimeoutError, openai.APIConnectionError) as error:
        raise ProviderConnectionError() from error
    except openai.OpenAIError as error:
        raise ProposalGenerationError() from error

    try:
        return parse_proposal_response(response)
    except MalformedModelResponse:
        raise
    except Exception as error:
        raise MalformedModelResponse() from error
