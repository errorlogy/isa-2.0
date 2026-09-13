#!/usr/bin/env python3
"""NEO_ERA → @OmegaCovenant poster. INSTITUTIONAL_MODEL outreach only.

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
TG_INTERVAL_S = 1.1
DEFAULT_CHANNEL = "@OmegaCovenant"
FOOTER = (
    "INSTITUTIONAL_MODEL · not religious authority · @OmegaCovenant\n"
    "https://github.com/errorlogy/isa-2.0/blob/main/docs/CORPUS/artifacts/NEO_ERA.md"
)
CORPUS_REPO_PATH = "docs/CORPUS/artifacts"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def rotate_clause() -> str:
    day = datetime.now(timezone.utc).timetuple().tm_yday
    return CLAUSE_ORDER[day % len(CLAUSE_ORDER)]


def normalize_clause(clause: str | None) -> str:
    if not clause or not clause.strip():
        return rotate_clause()
    c = clause.strip().upper()
    if c not in VALID_CLAUSES:
        raise ValueError(f"Invalid clause_id '{clause}'; expected one of {CLAUSE_ORDER}")
    return c


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

    # Hard-split any chunk still over limit (no newlines).
    final: list[str] = []
    for chunk in parts:
        while len(chunk) > limit:
            final.append(chunk[:limit])
            chunk = chunk[limit:]
        if chunk:
            final.append(chunk)
    return final


def idempotency_key(sha: str, clause: str, locale: str) -> str:
    return f"{sha}:{clause}:{locale}"


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


def send_telegram(token: str, chat_id: str, text: str) -> dict:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps(
        {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


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

    for i, part in enumerate(payloads):
        try:
            result = send_telegram(token, chat_id, part)
            ok = result.get("ok", False)
            if not ok:
                print(json.dumps(result, indent=2), file=sys.stderr)
                return 1
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            print(f"Telegram HTTP {exc.code}: {body}", file=sys.stderr)
            return 1
        except urllib.error.URLError as exc:
            print(f"Telegram network error: {exc}", file=sys.stderr)
            return 1

        if i < total - 1:
            time.sleep(TG_INTERVAL_S)

    posted.add(key)
    save_manifest(manifest_path, posted)
    print(json.dumps({"posted": key, "parts": total}, indent=2))
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Post NEO_ERA axiom to @OmegaCovenant")
    parser.add_argument("--dry-run", action="store_true", help="Print payload without sending")
    parser.add_argument("--clause", dest="clause_id", help="Roman numeral I–X")
    parser.add_argument("--locale", choices=["en", "ru"], default=None, help="Corpus locale")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = repo_root()

    dry_run = args.dry_run or os.environ.get("DRY_RUN", "false").lower() in ("1", "true", "yes")
    locale = args.locale or os.environ.get("LOCALE", "en")
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHANNEL_ID", DEFAULT_CHANNEL)
    sha = git_sha(root)
    manifest_path = root / ".telegram-post-manifest.json"

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
