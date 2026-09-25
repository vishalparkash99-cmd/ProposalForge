from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

DEFAULT_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
DEFAULT_MODELS: tuple[str, ...] = (
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-2.5-flash",
)
DEFAULT_COMPANY_CONTEXT = """We are a leading IT engineering firm specializing in Enterprise AI,
Smart Automation, Agentic Workflows, and High-Security Distributed Systems.
We have delivered 200+ enterprise-grade solutions with 99.9% reliability."""


@dataclass(frozen=True, slots=True)
class Settings:
    api_key: str | None
    base_url: str
    models: tuple[str, ...]
    company_context: str


def get_settings() -> Settings:
    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("OPENROUTER_API_KEY")
    )
    api_key = api_key.strip() if api_key else None

    base_url = (
        os.getenv("API_BASE_URL")
        or os.getenv("OPENROUTER_BASE_URL")
        or DEFAULT_API_BASE_URL
    ).strip()

    configured_models = os.getenv("MODELS", "")
    models = tuple(
        model.strip()
        for model in configured_models.split(",")
        if model.strip()
    ) or DEFAULT_MODELS

    company_context = os.getenv("COMPANY_CONTEXT", "").strip()
    if not company_context:
        company_context = DEFAULT_COMPANY_CONTEXT

    return Settings(
        api_key=api_key,
        base_url=base_url,
        models=models,
        company_context=company_context,
    )
