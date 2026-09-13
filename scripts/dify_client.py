#!/usr/bin/env python3
"""Minimal Dify Workflow API client (stdlib only)."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

DEFAULT_BASE = "https://api.dify.ai/v1"


def _api_base() -> str:
    return os.environ.get("DIFY_API_BASE", DEFAULT_BASE).rstrip("/")


def run_workflow(
    inputs: dict[str, Any],
    *,
    api_key: str,
    workflow_id: str | None = None,
    user: str = "isa-2.0-telegram",
    response_mode: str = "blocking",
    timeout: int = 120,
) -> dict[str, Any]:
    """Run a published Dify workflow and return parsed JSON."""
    base = _api_base()
    if workflow_id:
        url = f"{base}/workflows/{workflow_id}/run"
    else:
        url = f"{base}/workflows/run"

    payload = json.dumps(
        {
            "inputs": inputs,
            "response_mode": response_mode,
            "user": user,
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Dify HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Dify network error: {exc}") from exc


def extract_outputs(response: dict[str, Any]) -> dict[str, Any]:
    """Pull workflow output variables from a blocking response."""
    data = response.get("data") or {}
    outputs = data.get("outputs")
    if isinstance(outputs, dict):
        return outputs
    return {}


def configured() -> bool:
    return bool(os.environ.get("DIFY_API_KEY") and os.environ.get("DIFY_WORKFLOW_ID"))
