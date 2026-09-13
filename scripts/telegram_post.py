#!/usr/bin/env python3
"""NEO_ERA → @OmegaCovenant poster. INSTITUTIONAL_MODEL outreach only.

Modes:
  corpus          — static axiom excerpt from NEO_ERA.md (default)
  content-version — Dify workflow + optional fal.ai image → sendPhoto

Stdlib only — no pip dependencies required.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from dify_client import configured as dify_configured
from dify_client import extract_outputs, run_workflow

CLAUSE_ORDER = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
VALID_CLAUSES = set(CLAUSE_ORDER)

LABELS_EN: dict[str, str] = {
    "I": "Autopoiesis asymmetry (light over parasite)",
    "II": "True duality within light (S/F)",
    "III": "Talion ∞ (mirror collapse contour)",
    "IV": "No forgiveness of parasitic predator",
    "V": "Well (topological isolation)",
    "VI": "Guard memory (mirror lesson)",
    "VII": "Light self-sufficiency",
    "VIII": "Taboo on predator symbiosis",
    "IX": "Innocent protection (INV-8 sovereign)",
    "X": "Architect legitimization guilt",
}

MAX_LEN = 4096
CAPTION_MAX = 1024
TG_INTERVAL_S = 1.1
DEFAULT_CHANNEL = "@OmegaCovenant"
FOOTER = (
    "INSTITUTIONAL_MODEL · not religious authority · @OmegaCovenant\n"
    "https://github.com/errorlogy/isa-2.0/blob/main/docs/CORPUS/artifacts/NEO_ERA.md"
)
CONTENT_VERSION_FOOTER = (
    "INSTITUTIONAL_MODEL · not religious authority · @OmegaCovenant"
)
CORPUS_REPO_PATH = "docs/CORPUS/artifacts"
FAL_FLUX_SCHNELL = "https://fal.run/fal-ai/flux/schnell"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def rotate_clause() -> str:
    day = datetime.now(timezone.utc).timetuple().tm_yday
    return CLAUSE_ORDER[day % len(CLAUSE_ORDER)]


def rotate_aspect() -> str:
    return f"NEO_ERA:{rotate_clause()}"


def normalize_clause(clause: str | None) -> str:
    if not clause or not clause.strip():
        return rotate_clause()
    c = clause.strip().upper()
    if c not in VALID_CLAUSES:
        raise ValueError(f"Invalid clause_id '{clause}'; expected one of {CLAUSE_ORDER}")
    return c


def normalize_aspect(aspect: str | None) -> str:
    if not aspect or not aspect.strip():
        return rotate_aspect()
    raw = aspect.strip()
    if raw.upper().startswith("NEO_ERA:"):
        clause = raw.split(":", 1)[1].strip().upper()
        normalize_clause(clause)
        return f"NEO_ERA:{clause}"
    clause = normalize_clause(raw)
    return f"NEO_ERA:{clause}"


def corpus_path(locale: str, root: Path) -> Path:
    name = "NEO_ERA.ru.md" if locale == "ru" else "NEO_ERA.md"
    override = os.environ.get("NEO_ERA_CORPUS_PATH")
    if override:
        return root / override
    return root / CORPUS_REPO_PATH / name


def extract_axiom(md: str, clause_id: str) -> str:
    pattern = rf"(?ms)^###\s+Axiom\s+{clause_id}\b.*?(?=^###\s+Axiom\s+|\Z)"
    match = re.search(pattern, md)
    if match:
        return match.group(0).strip()
    return f"(axiom {clause_id} excerpt not found in corpus)"


def parse_labels_from_table(md: str) -> dict[str, str]:
    """Mirror runtime wire table labels when present."""
    labels = dict(LABELS_EN)
    for clause in CLAUSE_ORDER:
        pattern = rf"`NEO_ERA:{clause}`\s*\|\s*[^|]+\|\s*([^|]+)\|"
        m = re.search(pattern, md)
        if m:
            labels[clause] = m.group(1).strip()
    return labels


def markdown_section_to_plain(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.rstrip()
        if stripped.startswith("### "):
            stripped = stripped[4:].strip()
        elif stripped.startswith("* "):
            stripped = "• " + stripped[2:]
        elif stripped.startswith("- "):
            stripped = "• " + stripped[2:]
        lines.append(stripped)
    return "\n".join(lines).strip()


def build_message(clause: str, body_md: str, labels: dict[str, str], locale: str) -> str:
    label = labels.get(clause, "")
    body_plain = markdown_section_to_plain(body_md)
    header = (
        f"<b>NEO_ERA:{clause}</b>"
        + (f" — {html.escape(label)}" if label else "")
        + f"\n\n<i>INSTITUTIONAL_MODEL · not religious authority</i>"
        + (f" · {html.escape(locale)}" if locale != "en" else "")
        + "\n\n"
    )
    body_html = html.escape(body_plain)
    return header + body_html + "\n\n—\n" + html.escape(FOOTER)


def part_suffix(index: int, total: int) -> str:
    if total <= 1:
        return ""
    return f"\n\n— {index + 1}/{total}"


def split_message(text: str, limit: int = MAX_LEN) -> list[str]:
    if len(text) <= limit:
        return [text]

    parts: list[str] = []
    buf = ""
    for line in text.splitlines(keepends=True):
        candidate = buf + line
        if len(candidate) > limit and buf:
            parts.append(buf.rstrip("\n"))
            buf = line
        else:
            buf = candidate
    if buf:
        parts.append(buf.rstrip("\n"))

    final: list[str] = []
    for chunk in parts:
        while len(chunk) > limit:
            final.append(chunk[:limit])
            chunk = chunk[limit:]
        if chunk:
            final.append(chunk)
    return final


def truncate_caption(text: str, limit: int = CAPTION_MAX) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def idempotency_key(sha: str, clause: str, locale: str) -> str:
    return f"{sha}:{clause}:{locale}"


def content_version_key(sha: str, aspect: str, locale: str) -> str:
    return f"{sha}:content-version:{aspect}:{locale}"


def load_manifest(path: Path) -> set[str]:
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    posted = data.get("posted", [])
    return set(posted) if isinstance(posted, list) else set()


def save_manifest(path: Path, keys: set[str]) -> None:
    payload = {
        "posted": sorted(keys),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def git_sha(root: Path) -> str:
    env_sha = os.environ.get("GITHUB_SHA")
    if env_sha:
        return env_sha
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "local"


def detect_push_clauses(root: Path) -> list[str]:
    trigger = os.environ.get("TRIGGER", "")
    if trigger != "push":
        return []
    try:
        out = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD", "--", f"{CORPUS_REPO_PATH}/"],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

    if not out.strip():
        return []

    try:
        diff = subprocess.check_output(
            ["git", "diff", "HEAD~1", "HEAD", "--", f"{CORPUS_REPO_PATH}/NEO_ERA.md"],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        diff = ""

    found: list[str] = []
    for clause in CLAUSE_ORDER:
        if re.search(rf"^###\s+Axiom\s+{clause}\b", diff, re.MULTILINE):
            found.append(clause)
    return found


def _telegram_request(token: str, method: str, payload: dict[str, Any]) -> dict:
    url = f"https://api.telegram.org/bot{token}/{method}"
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def send_telegram(token: str, chat_id: str, text: str) -> dict:
    return _telegram_request(
        token,
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        },
    )


def send_photo(token: str, chat_id: str, photo: str, caption: str) -> dict:
    """Send photo via Telegram Bot API (photo = URL, file_id, or multipart-ready path)."""
    return _telegram_request(
        token,
        "sendPhoto",
        {
            "chat_id": chat_id,
            "photo": photo,
            "caption": truncate_caption(caption),
            "parse_mode": "HTML",
        },
    )


def mock_content_version(aspect: str, locale: str) -> dict[str, str]:
    clause = aspect.split(":", 1)[-1] if ":" in aspect else aspect
    label = LABELS_EN.get(clause, "analytical aspect")
    return {
        "aspect": aspect,
        "caption_html": (
            f"<b>{html.escape(aspect)}</b> — {html.escape(label)}\n\n"
            f"<i>INSTITUTIONAL_MODEL · not religious authority</i>"
            + (f" · {html.escape(locale)}" if locale != "en" else "")
            + "\n\n"
            f"Mock content-version caption for dry-run testing. "
            f"The mirror contour reflects analytical signals — not verdict."
        ),
        "image_prompt": (
            f"Abstract symbolic illustration for {aspect}: geometric light braid, "
            f"topological mirror, institutional model aesthetic, no text, muted omega palette"
        ),
        "long_text": (
            f"<b>{html.escape(aspect)}</b> — extended analytical note (mock)\n\n"
            f"This longer body would arrive as a follow-up message when Dify returns "
            f"<code>long_text</code> exceeding the 1024-character photo caption limit.\n\n"
            f"Wire label: {html.escape(label)}."
        ),
    }


def fetch_content_version(aspect: str, locale: str) -> dict[str, str]:
    if not dify_configured():
        print("Dify not configured — using mock content-version payload", file=sys.stderr)
        return mock_content_version(aspect, locale)

    api_key = os.environ["DIFY_API_KEY"]
    workflow_id = os.environ.get("DIFY_WORKFLOW_ID")
    slot_index = os.environ.get("SLOT_INDEX", "")
    recent = os.environ.get("RECENT_ASPECTS", "")

    inputs: dict[str, Any] = {
        "aspect": aspect,
        "locale": locale,
    }
    if slot_index:
        inputs["slot_index"] = slot_index
    if recent:
        inputs["recent_aspects"] = recent

    response = run_workflow(
        inputs,
        api_key=api_key,
        workflow_id=workflow_id,
    )
    outputs = extract_outputs(response)
    if not outputs:
        raise RuntimeError(f"Dify returned no outputs: {json.dumps(response)[:500]}")

    required = ("caption_html", "image_prompt")
    missing = [k for k in required if not outputs.get(k)]
    if missing:
        raise RuntimeError(f"Dify outputs missing required fields: {missing}")

    return {
        "aspect": str(outputs.get("aspect") or aspect),
        "caption_html": str(outputs["caption_html"]),
        "image_prompt": str(outputs["image_prompt"]),
        "long_text": str(outputs.get("long_text") or ""),
        "image_url": str(outputs.get("image_url") or ""),
    }


def generate_image_fal(prompt: str) -> str:
    fal_key = os.environ.get("FAL_KEY")
    if not fal_key:
        raise RuntimeError("FAL_KEY not set")

    payload = json.dumps(
        {
            "prompt": prompt,
            "image_size": "landscape_16_9",
            "num_inference_steps": 4,
            "num_images": 1,
            "enable_safety_checker": True,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        FAL_FLUX_SCHNELL,
        data=payload,
        headers={
            "Authorization": f"Key {fal_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"fal.ai HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"fal.ai network error: {exc}") from exc

    images = data.get("images") or []
    if not images or not images[0].get("url"):
        raise RuntimeError(f"fal.ai returned no image URL: {json.dumps(data)[:500]}")
    return str(images[0]["url"])


def build_content_caption(caption_html: str) -> str:
    body = caption_html.strip()
    footer = f"\n\n—\n{CONTENT_VERSION_FOOTER}"
    combined = body + footer
    return truncate_caption(combined)


def post_clause(
    clause: str,
    locale: str,
    sha: str,
    dry_run: bool,
    token: str | None,
    chat_id: str,
    manifest_path: Path,
) -> int:
    root = repo_root()
    path = corpus_path(locale, root)
    if not path.exists():
        print(f"Corpus not found: {path}", file=sys.stderr)
        return 1

    md = path.read_text(encoding="utf-8")
    labels = parse_labels_from_table(md)
    body = extract_axiom(md, clause)
    message = build_message(clause, body, labels, locale)
    parts = split_message(message)

    key = idempotency_key(sha, clause, locale)
    posted = load_manifest(manifest_path)
    if key in posted:
        print(f"skip duplicate {key}")
        return 0

    total = len(parts)
    payloads = [part + part_suffix(i, total) for i, part in enumerate(parts)]

    if dry_run or not token:
        preview = {
            "mode": "corpus",
            "idempotency_key": key,
            "clause": clause,
            "locale": locale,
            "sha": sha,
            "channel": chat_id,
            "parts": total,
            "char_lengths": [len(p) for p in payloads],
            "preview": payloads[0][:800],
        }
        print(json.dumps(preview, indent=2, ensure_ascii=False))
        if not dry_run and not token:
            print("TELEGRAM_BOT_TOKEN not set; dry-run only", file=sys.stderr)
        return 0

    if not chat_id:
        print("TELEGRAM_CHANNEL_ID required when sending", file=sys.stderr)
        return 1

    message_ids: list[int] = []
    for i, part in enumerate(payloads):
        try:
            result = send_telegram(token, chat_id, part)
            ok = result.get("ok", False)
            if not ok:
                print(json.dumps(result, indent=2), file=sys.stderr)
                return 1
            msg = (result.get("result") or {}).get("message_id")
            if msg is not None:
                message_ids.append(msg)
        except urllib.error.HTTPError as exc:
            body_err = exc.read().decode("utf-8", errors="replace")
            print(f"Telegram HTTP {exc.code}: {body_err}", file=sys.stderr)
            return 1
        except urllib.error.URLError as exc:
            print(f"Telegram network error: {exc}", file=sys.stderr)
            return 1

        if i < total - 1:
            time.sleep(TG_INTERVAL_S)

    posted.add(key)
    save_manifest(manifest_path, posted)
    print(json.dumps({"mode": "corpus", "posted": key, "parts": total, "message_ids": message_ids}, indent=2))
    return 0


def post_content_version(
    aspect: str,
    locale: str,
    sha: str,
    dry_run: bool,
    token: str | None,
    chat_id: str,
    manifest_path: Path,
) -> int:
    key = content_version_key(sha, aspect, locale)
    posted = load_manifest(manifest_path)
    if key in posted:
        print(f"skip duplicate {key}")
        return 0

    try:
        content = fetch_content_version(aspect, locale)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    aspect = content["aspect"]
    caption = build_content_caption(content["caption_html"])
    long_text = content.get("long_text", "").strip()
    image_url = content.get("image_url", "").strip()
    image_prompt = content["image_prompt"]

    fal_configured = bool(os.environ.get("FAL_KEY"))
    if not image_url and fal_configured and not dry_run:
        try:
            image_url = generate_image_fal(image_prompt)
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 1
    elif not image_url and fal_configured and dry_run:
        image_url = "https://example.com/mock-fal-image.jpg"

    preview = {
        "mode": "content-version",
        "idempotency_key": key,
        "aspect": aspect,
        "locale": locale,
        "sha": sha,
        "channel": chat_id,
        "caption_len": len(caption),
        "caption_preview": caption[:500],
        "image_prompt": image_prompt[:300],
        "image_url": image_url or None,
        "long_text_len": len(long_text),
        "dify_configured": dify_configured(),
        "fal_configured": fal_configured,
        "has_follow_up": bool(long_text),
    }

    if dry_run or not token:
        print(json.dumps(preview, indent=2, ensure_ascii=False))
        if not dry_run and not token:
            print("TELEGRAM_BOT_TOKEN not set; dry-run only", file=sys.stderr)
        return 0

    if not chat_id:
        print("TELEGRAM_CHANNEL_ID required when sending", file=sys.stderr)
        return 1

    if not image_url:
        print("No image_url from Dify and FAL_KEY not set; cannot sendPhoto", file=sys.stderr)
        return 1

    message_ids: list[int] = []
    try:
        photo_result = send_photo(token, chat_id, image_url, caption)
        if not photo_result.get("ok"):
            print(json.dumps(photo_result, indent=2), file=sys.stderr)
            return 1
        photo_msg_id = (photo_result.get("result") or {}).get("message_id")
        if photo_msg_id is not None:
            message_ids.append(photo_msg_id)
    except urllib.error.HTTPError as exc:
        body_err = exc.read().decode("utf-8", errors="replace")
        print(f"Telegram sendPhoto HTTP {exc.code}: {body_err}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"Telegram network error: {exc}", file=sys.stderr)
        return 1

    if long_text:
        time.sleep(TG_INTERVAL_S)
        follow_up = long_text
        if CONTENT_VERSION_FOOTER not in follow_up:
            follow_up = follow_up + f"\n\n—\n{CONTENT_VERSION_FOOTER}"
        parts = split_message(follow_up)
        for i, part in enumerate(parts):
            try:
                msg_result = send_telegram(token, chat_id, part + part_suffix(i, len(parts)))
                if not msg_result.get("ok"):
                    print(json.dumps(msg_result, indent=2), file=sys.stderr)
                    return 1
                msg_id = (msg_result.get("result") or {}).get("message_id")
                if msg_id is not None:
                    message_ids.append(msg_id)
            except urllib.error.HTTPError as exc:
                body_err = exc.read().decode("utf-8", errors="replace")
                print(f"Telegram HTTP {exc.code}: {body_err}", file=sys.stderr)
                return 1
            except urllib.error.URLError as exc:
                print(f"Telegram network error: {exc}", file=sys.stderr)
                return 1
            if i < len(parts) - 1:
                time.sleep(TG_INTERVAL_S)

    posted.add(key)
    save_manifest(manifest_path, posted)
    print(
        json.dumps(
            {
                "mode": "content-version",
                "posted": key,
                "aspect": aspect,
                "message_ids": message_ids,
            },
            indent=2,
        )
    )
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Post NEO_ERA content to @OmegaCovenant")
    parser.add_argument(
        "--mode",
        choices=["corpus", "content-version"],
        default=None,
        help="corpus = static axiom excerpt; content-version = Dify + fal.ai sendPhoto",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print payload without sending")
    parser.add_argument("--clause", dest="clause_id", help="Roman numeral I–X (corpus mode)")
    parser.add_argument("--aspect", help="NEO_ERA:I..X or Roman numeral (content-version mode)")
    parser.add_argument("--locale", choices=["en", "ru"], default=None, help="Corpus locale")
    return parser.parse_args(argv)


def _configure_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError, OSError):
            pass


def main(argv: list[str] | None = None) -> int:
    _configure_stdout()
    args = parse_args(argv)
    root = repo_root()

    mode = args.mode or os.environ.get("MODE", "corpus")
    dry_run = args.dry_run or os.environ.get("DRY_RUN", "false").lower() in ("1", "true", "yes")
    locale = args.locale or os.environ.get("LOCALE", "en")
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHANNEL_ID", DEFAULT_CHANNEL)
    sha = git_sha(root)
    manifest_path = root / ".telegram-post-manifest.json"

    if mode == "content-version":
        raw_aspect = args.aspect or os.environ.get("ASPECT") or ""
        aspect = normalize_aspect(raw_aspect)
        return post_content_version(aspect, locale, sha, dry_run, token, chat_id, manifest_path)

    push_clauses = detect_push_clauses(root)
    if push_clauses:
        clauses = push_clauses
    else:
        raw_clause = args.clause_id or os.environ.get("CLAUSE_ID") or ""
        clauses = [normalize_clause(raw_clause)]

    exit_code = 0
    for clause in clauses:
        code = post_clause(clause, locale, sha, dry_run, token, chat_id, manifest_path)
        if code != 0:
            exit_code = code
        if len(clauses) > 1 and not dry_run and token:
            time.sleep(TG_INTERVAL_S)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
