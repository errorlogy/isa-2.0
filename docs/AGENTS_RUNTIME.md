# Agents runtime — what runs where

**Epistemic label:** `OPERATIONAL` (adapter guidance only)

This document clarifies which tools handle **scheduled Telegram posting** vs **coding-agent customization** for the isa-2.0 repo.

---

## Summary

| Tool | Role | Runs on schedule? | RAG / images? |
|------|------|-------------------|---------------|
| **GitHub Actions + `telegram_post.py`** | Delivery pipeline | Yes (cron / dispatch) | Via external APIs (Dify, fal.ai) |
| **`.github/agents/*.agent.md`** | Copilot Coding Agent personas | No | No |
| **OpenClaw** | Self-hosted gateway (separate process) | Only if you host it | Possible, but not recommended here |

**Best practice:** the repo holds **code + GHA workflows**; Dify and fal.ai are **external services** called via GitHub Secrets.

---

## `.github/agents` — Copilot Coding Agent (not runtime)

[GitHub Copilot custom agents](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/create-custom-agents) use Markdown files with YAML frontmatter in `.github/agents/*.agent.md`.

They configure **how Copilot writes code and opens PRs** — for example:

- "When editing `telegram_post.py`, follow NEO_ERA epistemic rules"
- "Use stdlib only; no new pip dependencies"
- "Always include `INSTITUTIONAL_MODEL` disclaimer in captions"

They do **not**:

- Run on a cron schedule
- Call Dify, fal.ai, or Telegram by themselves
- Replace `neo-era-telegram.yml` or `neo-era-content-version.yml`

Optional dev agent: [`.github/agents/neo-era-telegram-dev.agent.md`](../.github/agents/neo-era-telegram-dev.agent.md)

---

## OpenClaw — separate gateway (not in-repo)

[OpenClaw](https://github.com/openclaw/openclaw) is a **self-hosted agent gateway** — a long-running process on your machine or VPS. It does **not** install into the isa-2.0 repository.

Use OpenClaw when you want a personal assistant with messaging channels (WhatsApp, Slack, etc.). It is **not recommended** for the NEO_ERA scheduled content pipeline because:

- Secrets and scheduling live outside Git audit
- Harder to reproduce dry-runs in CI
- Overlaps with GHA + Dify API for the same outcome

---

## Recommended runtime stack (content-version)

```text
GHA workflow_dispatch / cron (future)
  → scripts/telegram_post.py --mode content-version
       → Dify Workflow API (RAG + caption + image_prompt)
       → fal.ai flux/schnell (image URL)
       → Telegram sendPhoto + optional sendMessage
  → @OmegaCovenant
```

Setup: [DIFY_SETUP.md](DIFY_SETUP.md) · Bot secrets: [TELEGRAM_BOT_SETUP.md](TELEGRAM_BOT_SETUP.md)

---

*Operational guidance · INSTITUTIONAL_MODEL · not religious authority*
