#!/usr/bin/env python3
"""Bootstrap NEO_ERA Dify workflow via Dify APIs (stdlib only).

Automates what is possible without browser UI:
  - Create knowledge base + upload NEO_ERA corpus (Knowledge API)
  - Import workflow DSL (Console API)

Still requires manual UI steps: Gemini provider, Publish, App API key,
published workflow version UUID → DIFY_WORKFLOW_ID.

Environment (set locally — never commit or paste in chat):
  DIFY_CONSOLE_EMAIL + DIFY_CONSOLE_PASSWORD   Console login (DSL import)
  DIFY_CONSOLE_ACCESS_TOKEN                    Alternative to email/password
  DIFY_DATASET_API_KEY                         Knowledge API key (dataset-…)
  DIFY_API_BASE                                Default https://api.dify.ai/v1
  DIFY_CONSOLE_BASE                            Default https://cloud.dify.ai/console/api

Note: DIFY_API_KEY (app-…) is for *running* workflows only — not for bootstrap.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

DEFAULT_API_BASE = "https://api.dify.ai/v1"
DEFAULT_CONSOLE_BASE = "https://cloud.dify.ai/console/api"
DSL_PATH = Path(__file__).resolve().parents[1] / "docs" / "dify" / "neo-era-content-workflow.dsl.yml"
CORPUS_DIR = Path(__file__).resolve().parents[1] / "docs" / "CORPUS" / "artifacts"
DATASET_PLACEHOLDER = "__NEO_ERA_DATASET_ID__"


def _api_base() -> str:
    return os.environ.get("DIFY_API_BASE", DEFAULT_API_BASE).rstrip("/")


def _console_base() -> str:
    return os.environ.get("DIFY_CONSOLE_BASE", DEFAULT_CONSOLE_BASE).rstrip("/")


def _request_json(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    data: bytes | None = None,
    timeout: int = 120,
) -> tuple[int, Any]:
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed: Any = json.loads(body) if body else {"raw": body}
        except json.JSONDecodeError:
            parsed = {"raw": body}
        return exc.code, parsed


def console_access_token() -> str:
    token = os.environ.get("DIFY_CONSOLE_ACCESS_TOKEN", "").strip()
    if token:
        return token

    email = os.environ.get("DIFY_CONSOLE_EMAIL", "").strip()
    password = os.environ.get("DIFY_CONSOLE_PASSWORD", "")
    if not email or not password:
        raise RuntimeError(
            "Set DIFY_CONSOLE_ACCESS_TOKEN or DIFY_CONSOLE_EMAIL + DIFY_CONSOLE_PASSWORD "
            "for DSL import (Console API). DIFY_API_KEY (app-…) cannot import workflows."
        )

    payload = json.dumps(
        {
            "email": email,
            "password": password,
            "remember_me": True,
        }
    ).encode("utf-8")
    status, body = _request_json(
        f"{_console_base()}/login",
        method="POST",
        headers={"Content-Type": "application/json"},
        data=payload,
    )
    if status != 200:
        raise RuntimeError(f"Console login failed HTTP {status}: {body}")

    data = body.get("data") if isinstance(body, dict) else None
    access = (data or body).get("access_token") if isinstance(data or body, dict) else None
    if not access:
        raise RuntimeError(f"Console login returned no access_token: {body}")
    return str(access)


def create_dataset(api_key: str, name: str = "NEO_ERA") -> str:
    payload = json.dumps(
        {
            "name": name,
            "description": "NEO_ERA institutional corpus for Telegram content-version",
            "indexing_technique": "high_quality",
        }
    ).encode("utf-8")
    status, body = _request_json(
        f"{_api_base()}/datasets",
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=payload,
    )
    if status not in (200, 201):
        raise RuntimeError(f"Create dataset failed HTTP {status}: {body}")
    dataset_id = body.get("id") if isinstance(body, dict) else None
    if not dataset_id:
        raise RuntimeError(f"Create dataset returned no id: {body}")
    return str(dataset_id)


def upload_document_by_file(api_key: str, dataset_id: str, file_path: Path) -> None:
    if not file_path.is_file():
        raise FileNotFoundError(file_path)

    data_json = json.dumps(
        {
            "indexing_technique": "high_quality",
            "process_rule": {"mode": "automatic"},
        }
    )
    mime = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    file_bytes = file_path.read_bytes()

    boundary = f"----difybootstrap{uuid.uuid4().hex}"
    body_parts: list[bytes] = []

    def add_field(name: str, value: str, content_type: str = "text/plain") -> None:
        body_parts.append(f"--{boundary}\r\n".encode())
        body_parts.append(
            f'Content-Disposition: form-data; name="{name}"\r\n'
            f"Content-Type: {content_type}\r\n\r\n".encode()
        )
        body_parts.append(value.encode("utf-8"))
        body_parts.append(b"\r\n")

    add_field("data", data_json, "text/plain")
    body_parts.append(f"--{boundary}\r\n".encode())
    body_parts.append(
        f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"\r\n'
        f"Content-Type: {mime}\r\n\r\n".encode()
    )
    body_parts.append(file_bytes)
    body_parts.append(b"\r\n")
    body_parts.append(f"--{boundary}--\r\n".encode())
    payload = b"".join(body_parts)

    status, resp = _request_json(
        f"{_api_base()}/datasets/{dataset_id}/document/create-by-file",
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        data=payload,
    )
    if status not in (200, 201):
        raise RuntimeError(f"Upload {file_path.name} failed HTTP {status}: {resp}")
    print(f"  uploaded: {file_path.name}", file=sys.stderr)


def load_dsl(dataset_id: str, dsl_path: Path) -> str:
    text = dsl_path.read_text(encoding="utf-8")
    if DATASET_PLACEHOLDER not in text:
        print(f"Warning: placeholder {DATASET_PLACEHOLDER} not found in DSL", file=sys.stderr)
    return text.replace(DATASET_PLACEHOLDER, dataset_id)


def import_dsl(access_token: str, yaml_content: str, *, app_name: str | None = None) -> dict[str, Any]:
    body_obj: dict[str, Any] = {
        "mode": "yaml-content",
        "yaml_content": yaml_content,
    }
    if app_name:
        body_obj["name"] = app_name
    payload = json.dumps(body_obj).encode("utf-8")
    status, body = _request_json(
        f"{_console_base()}/apps/imports",
        method="POST",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        data=payload,
    )
    if status not in (200, 201, 202):
        raise RuntimeError(f"DSL import failed HTTP {status}: {body}")
    if not isinstance(body, dict):
        raise RuntimeError(f"Unexpected import response: {body}")
    return body


def confirm_import(access_token: str, import_id: str) -> dict[str, Any]:
    status, body = _request_json(
        f"{_console_base()}/apps/imports/{import_id}/confirm",
        method="POST",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        data=b"{}",
    )
    if status not in (200, 201):
        raise RuntimeError(f"Import confirm failed HTTP {status}: {body}")
    return body if isinstance(body, dict) else {"raw": body}


def print_manual_steps(dataset_id: str | None, import_result: dict[str, Any] | None) -> None:
    print("\n--- Manual steps (UI) ---", file=sys.stderr)
    if dataset_id:
        print(f"  Knowledge base ID: {dataset_id}", file=sys.stderr)
    if import_result:
        app_id = import_result.get("app_id") or (import_result.get("data") or {}).get("app_id")
        if app_id:
            print(f"  Imported app ID: {app_id}", file=sys.stderr)
    print("  1. Dify → Settings → Model Provider → Google Gemini", file=sys.stderr)
    print("  2. Open workflow → verify LLM nodes use Gemini", file=sys.stderr)
    print("  3. Publish workflow", file=sys.stderr)
    print("  4. API Access → create App API key → GitHub secret DIFY_API_KEY", file=sys.stderr)
    print("  5. Version history → copy published UUID → GitHub secret DIFY_WORKFLOW_ID", file=sys.stderr)
    print("  6. Test: python scripts/telegram_post.py --mode content-version --dry-run", file=sys.stderr)
    print("\nSee docs/dify/README.md and docs/DIFY_SETUP.md", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap NEO_ERA Dify workflow via APIs")
    parser.add_argument(
        "--dsl",
        type=Path,
        default=DSL_PATH,
        help=f"DSL YAML path (default: {DSL_PATH})",
    )
    parser.add_argument(
        "--dataset-id",
        help="Existing NEO_ERA knowledge base UUID (skip create/upload)",
    )
    parser.add_argument(
        "--skip-knowledge",
        action="store_true",
        help="Skip knowledge base create/upload",
    )
    parser.add_argument(
        "--skip-import",
        action="store_true",
        help="Skip DSL import (only knowledge)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned actions without API calls",
    )
    args = parser.parse_args()

    dataset_id = args.dataset_id
    import_result: dict[str, Any] | None = None

    if args.dry_run:
        print("Dry run — would:", file=sys.stderr)
        if not args.skip_knowledge and not dataset_id:
            print("  create NEO_ERA dataset + upload corpus", file=sys.stderr)
        print(f"  import DSL from {args.dsl}", file=sys.stderr)
        print_manual_steps(dataset_id, None)
        return 0

    # --- Knowledge ---
    if not args.skip_knowledge and not dataset_id:
        kb_key = os.environ.get("DIFY_DATASET_API_KEY", "").strip()
        if not kb_key:
            print(
                "Skipping knowledge: set DIFY_DATASET_API_KEY (Knowledge → API Access) "
                "or pass --dataset-id / --skip-knowledge",
                file=sys.stderr,
            )
        else:
            print("Creating knowledge base NEO_ERA…", file=sys.stderr)
            dataset_id = create_dataset(kb_key)
            for name in ("NEO_ERA.md", "NEO_ERA.ru.md"):
                path = CORPUS_DIR / name
                if path.is_file():
                    upload_document_by_file(kb_key, dataset_id, path)
            print(f"Knowledge base ready: {dataset_id}", file=sys.stderr)

    if not dataset_id and not args.skip_import:
        print(
            "Error: no dataset ID for DSL (create knowledge or pass --dataset-id)",
            file=sys.stderr,
        )
        return 1

    # --- DSL import ---
    if not args.skip_import:
        if not args.dsl.is_file():
            print(f"DSL not found: {args.dsl}", file=sys.stderr)
            return 1
        yaml_content = load_dsl(dataset_id or DATASET_PLACEHOLDER, args.dsl)
        print("Importing workflow DSL via Console API…", file=sys.stderr)
        token = console_access_token()
        import_result = import_dsl(token, yaml_content)

        status = import_result.get("status") or (import_result.get("data") or {}).get("status")
        import_id = import_result.get("id") or (import_result.get("data") or {}).get("id")
        if status == "pending" and import_id:
            print(f"Import pending confirmation — confirming {import_id}…", file=sys.stderr)
            import_result = confirm_import(token, str(import_id))

        print(f"Import result: {json.dumps(import_result, indent=2)[:2000]}", file=sys.stderr)

    print_manual_steps(dataset_id, import_result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
