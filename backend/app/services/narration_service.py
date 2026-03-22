"""
Narration Service – LLM invocation and JSON response parsing.

Extracts the narration generation and parsing logic that was previously
inlined in the interactions endpoint.
"""

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.core.llm_client import LLMClient


@dataclass
class NarrationResult:
    """Structured result from LLM narration parsing."""

    narration: str = ""
    suggested_actions: List[str] = field(default_factory=list)
    event: Optional[str] = None
    enemy_name: Optional[str] = None
    rewards: Dict[str, Any] = field(default_factory=dict)
    parse_error: bool = False


async def generate_narration(system_prompt: str, user_message: str, llm_client: LLMClient) -> str:
    """
    Call the LLM and return the raw response string.

    Raises on critical LLM failure (caller should handle).
    """
    return await llm_client.generate(
        system_prompt=system_prompt,
        user_message=user_message,
    )


def parse_llm_response(raw_response: str) -> NarrationResult:
    """
    Parse the raw LLM response (expected JSON) into a NarrationResult.

    Handles common LLM errors such as trailing commas, nested "response"
    wrappers, and missing JSON blocks.
    """
    result = NarrationResult()

    try:
        json_match = re.search(r"\{.*\}", raw_response, re.DOTALL)
        if json_match:
            response_data = _parse_json_block(json_match.group(0))

            result.narration = _extract_narration(response_data) or raw_response
            result.suggested_actions = _extract_field(response_data, "suggested_actions") or []
            result.event = _extract_field(response_data, "event")
            result.enemy_name = _extract_field(response_data, "enemy")
            result.rewards = _extract_field(response_data, "rewards") or {}
        else:
            # Fallback: try to extract narration from non-JSON text
            result.narration = _extract_narration_fallback(raw_response)
            result.suggested_actions = ["Attacca", "Difenditi"]
    except Exception as e:
        print(f"⚠️ JSON Parsing Error: {e}")
        result.narration = raw_response
        result.parse_error = True

    return result


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_json_block(json_str: str) -> dict:
    """Attempt to parse a JSON string with progressive cleanup."""
    # First attempt: clean trailing commas
    cleaned = re.sub(r",\s*\}", "}", json_str)
    cleaned = re.sub(r",\s*\]", "]", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Second attempt: collapse whitespace
    collapsed = json_str.replace("\n", " ").replace("\r", " ")
    return json.loads(collapsed)


def _extract_narration(data: dict) -> Optional[str]:
    """Robustly extract the narration text from a parsed JSON dict."""
    if not isinstance(data, dict):
        return None

    # Check for nested "response" wrapper
    if "response" in data:
        res = data["response"]
        if isinstance(res, str):
            return res
        if isinstance(res, dict):
            nested = _extract_narration(res)
            if nested:
                return nested

    # Priority keys
    for key in ("narration", "message", "description", "text", "content"):
        if key in data and data[key] and isinstance(data[key], str):
            return data[key]

    # Fallback: check nested dicts for a message/narration field
    # e.g. {"action": {"message": "..."}}
    for key, value in data.items():
        if isinstance(value, dict):
            for inner_key in ("message", "narration", "text", "description", "content"):
                inner_val = value.get(inner_key)
                if inner_val and isinstance(inner_val, str):
                    return inner_val

    return None


def _extract_field(data: dict, field_name: str) -> Any:
    """Extract a field from the top level or nested 'response' wrapper."""
    value = data.get(field_name)
    if value is None and isinstance(data.get("response"), dict):
        value = data["response"].get(field_name)
    return value


def _extract_narration_fallback(raw: str) -> str:
    """Try to extract narration from text that looks JSON-ish but didn't parse."""
    if '"narration":' in raw:
        match = re.search(r'"narration":\s*"([^"]*)"', raw)
        if match:
            return match.group(1)
    return raw
