from __future__ import annotations


class ProposalGenerationError(Exception):
    user_message = "The proposal could not be generated. Try again or check your provider settings."

    def __init__(
        self,
        detail: str | None = None,
        *,
        user_message: str | None = None,
    ) -> None:
        self.user_message = user_message or self.user_message
        super().__init__(detail or self.user_message)


class MissingAPIKeyError(ProposalGenerationError):
    user_message = "No API key is available. Add one in .env, Streamlit secrets, or the session-only field."


class InvalidAPIKeyError(ProposalGenerationError):
    user_message = "The API key was rejected. Check the key and its provider permissions, then try again."


class RateLimitError(ProposalGenerationError):
    user_message = (
        "The model provider is rate-limiting requests. Wait briefly, reduce request frequency, "
        "or try another model."
    )


class RequestTimeoutError(ProposalGenerationError):
    user_message = "The model request timed out. Check the network and try again."


class ProviderConnectionError(ProposalGenerationError):
    user_message = "The model provider could not be reached. Check the API base URL and network, then try again."


class ConfigurationError(ProposalGenerationError):
    user_message = "The provider configuration is invalid. Check the API base URL and model settings."


class MalformedModelResponse(ProposalGenerationError):
    user_message = "The model returned an invalid proposal response. Try again; the proposal schema was not satisfied."

    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail)
