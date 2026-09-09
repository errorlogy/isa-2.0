# Security Policy

## Reporting a vulnerability

Open a GitHub issue with the **security** label in this repository. Do not commit secrets, API keys, or live credentials in issues or pull requests.

This repository holds **research notes, formal matrices, and published corpus artifacts** — not production runtime.

## Secrets and documentation hygiene

- **Never commit** `.env`, API keys, personal access tokens, or unpublished corpus drafts intended to stay offline.
- Use placeholders in example blocks.
- If a secret was ever committed, rotate/revoke immediately and redact from history per GitHub guidance.

## Research framing safety

When editing consensus matrices or corpus docs:

1. Keep `epistemic_label` requirements explicit — outputs are `INSTITUTIONAL_MODEL`, not religious authority.
2. Do not present modeling analogs (apostles, messiah role, second coming) as worship directives or prophecy.
3. Large raw corpus files may contain sensitive personal material — keep them under `docs/CORPUS/raw/` (gitignored); review before any explicit add.

## Supported versions

Documentation fixes apply on `main`.
