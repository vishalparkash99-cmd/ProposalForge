from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from errors import MalformedModelResponse

SUBMIT_PROPOSAL_TOOL_NAME = "submit_proposal"

PROPOSAL_SECTIONS: tuple[tuple[str, str], ...] = (
    ("executive_summary", "Problem Breakdown & Executive Summary"),
    ("proposed_solution", "Proposed Solution & AI Agent Architecture"),
    ("pilot_roadmap", "4-Week Pilot Roadmap & Key Deliverables"),
    ("why_our_company", "Why Our Company"),
    ("next_steps", "Next Steps"),
)

PROPOSAL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        field: {
            "type": "string",
            "minLength": 1,
            "description": f"Write the {label} section as complete B2B proposal prose.",
        }
        for field, label in PROPOSAL_SECTIONS
    },
    "required": [field for field, _ in PROPOSAL_SECTIONS],
    "additionalProperties": False,
}

PROPOSAL_TOOL: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": SUBMIT_PROPOSAL_TOOL_NAME,
        "description": (
            "Submit a complete enterprise proposal with one field for each required section."
        ),
        "parameters": PROPOSAL_SCHEMA,
        "strict": True,
    },
}

PROPOSAL_TOOL_CHOICE: dict[str, Any] = {
    "type": "function",
    "function": {"name": SUBMIT_PROPOSAL_TOOL_NAME},
}


@dataclass(frozen=True, slots=True)
class Proposal:
    executive_summary: str
    proposed_solution: str
    pilot_roadmap: str
    why_our_company: str
    next_steps: str

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> Proposal:
        if not isinstance(payload, Mapping):
            raise MalformedModelResponse("Proposal payload must be a JSON object.")

        expected_fields = {field for field, _ in PROPOSAL_SECTIONS}
        actual_fields = set(payload)
        missing_fields = expected_fields - actual_fields
        unexpected_fields = actual_fields - expected_fields
        if missing_fields or unexpected_fields:
            details: list[str] = []
            if missing_fields:
                details.append(f"missing fields: {', '.join(sorted(missing_fields))}")
            if unexpected_fields:
                details.append(f"unexpected fields: {', '.join(sorted(unexpected_fields))}")
            raise MalformedModelResponse("Proposal schema mismatch (" + "; ".join(details) + ").")

        values: dict[str, str] = {}
        for field, _ in PROPOSAL_SECTIONS:
            value = payload[field]
            if not isinstance(value, str) or not value.strip():
                raise MalformedModelResponse(
                    f"Proposal field {field!r} must be a non-empty string."
                )
            values[field] = value.strip()
        return cls(**values)

    def to_dict(self) -> dict[str, str]:
        return {field: getattr(self, field) for field, _ in PROPOSAL_SECTIONS}

    def to_text(self) -> str:
        return "\n\n".join(
            f"{label}\n{getattr(self, field)}"
            for field, label in PROPOSAL_SECTIONS
        )


def _read_attribute(value: Any, name: str, default: Any = None) -> Any:
    if isinstance(value, Mapping):
        return value.get(name, default)
    return getattr(value, name, default)


def _tool_call_arguments(raw_arguments: Any) -> Mapping[str, Any]:
    if isinstance(raw_arguments, Mapping):
        return raw_arguments
    if not isinstance(raw_arguments, str) or not raw_arguments.strip():
        raise MalformedModelResponse(
            f"{SUBMIT_PROPOSAL_TOOL_NAME} returned no JSON arguments."
        )
    try:
        payload = json.loads(raw_arguments)
    except json.JSONDecodeError as error:
        raise MalformedModelResponse(
            f"{SUBMIT_PROPOSAL_TOOL_NAME} returned invalid JSON arguments."
        ) from error
    if not isinstance(payload, Mapping):
        raise MalformedModelResponse(
            f"{SUBMIT_PROPOSAL_TOOL_NAME} arguments must be a JSON object."
        )
    return payload


def parse_proposal_response(response: Any) -> Proposal:
    choices = _read_attribute(response, "choices", ())
    if not isinstance(choices, Sequence) or isinstance(choices, (str, bytes)):
        raise MalformedModelResponse("Model response did not contain any choices.")
    if not choices:
        raise MalformedModelResponse("Model response did not contain any choices.")

    message = _read_attribute(choices[0], "message")
    tool_calls = _read_attribute(message, "tool_calls")
    if not isinstance(tool_calls, Sequence) or isinstance(tool_calls, (str, bytes)):
        raise MalformedModelResponse(
            f"Model response did not call {SUBMIT_PROPOSAL_TOOL_NAME}."
        )

    for tool_call in tool_calls:
        function = _read_attribute(tool_call, "function")
        if _read_attribute(function, "name") != SUBMIT_PROPOSAL_TOOL_NAME:
            continue
        arguments = _read_attribute(function, "arguments")
        return Proposal.from_dict(_tool_call_arguments(arguments))

    raise MalformedModelResponse(
        f"Model response did not call {SUBMIT_PROPOSAL_TOOL_NAME}."
    )
