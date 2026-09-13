# Dify automation — NEO_ERA content-version

**Epistemic label:** `OPERATIONAL`

Importable workflow DSL and a bootstrap script for `scripts/telegram_post.py --mode content-version`.

Full contract: [DIFY_SETUP.md](../DIFY_SETUP.md)

---

## What Dify supports

| Method | Creates workflow | Uploads knowledge | Runs workflow |
|--------|------------------|-------------------|---------------|
| **UI → Import DSL** (YAML) | Yes | No (metadata only) | After publish |
| **Console API** (`/console/api/apps/imports`) | Yes | No | After publish |
| **Knowledge API** (`POST /v1/datasets`, upload file) | No | Yes | — |
| **App API** (`app-…` key, `dify_client.py`) | No | No | Yes (published version) |

There is **no official Dify CLI** for workflow import. Use UI import or `scripts/dify_bootstrap.py`.

---

## Option A — One-click UI import (recommended first try)

1. **Knowledge** → create `NEO_ERA` → upload `docs/CORPUS/artifacts/NEO_ERA.md` (+ optional `.ru.md`).
2. Copy the knowledge base **UUID** from the URL or settings.
3. Open `neo-era-content-workflow.dsl.yml` → replace `__NEO_ERA_DATASET_ID__` with that UUID.
4. Dify Studio → **Import DSL** → select the YAML file.
5. **Settings → Model Provider → Google Gemini** (if not already).
6. Open each LLM node → confirm model (`gemini-2.0-flash` or `gemini-1.5-flash`).
7. **Publish** → **API Access** → create App API key → `DIFY_API_KEY`.
8. **Version history** → copy published version UUID → `DIFY_WORKFLOW_ID`.

Test:

```powershell
cd C:\Users\Public\ISA_2_0
$env:DIFY_API_KEY = "app-..."       # shell only — never commit
$env:DIFY_WORKFLOW_ID = "uuid-..."
python scripts/telegram_post.py --mode content-version --dry-run --aspect NEO_ERA:III
```

---

## Option B — Bootstrap script (partial automation)

```powershell
cd C:\Users\Public\ISA_2_0

# Console login (for DSL import) — NOT the app- API key
$env:DIFY_CONSOLE_EMAIL = "you@example.com"
$env:DIFY_CONSOLE_PASSWORD = "..."    # or use DIFY_CONSOLE_ACCESS_TOKEN

# Knowledge API key (Knowledge → API Access) — may differ from app- key
$env:DIFY_DATASET_API_KEY = "dataset-..."

python scripts/dify_bootstrap.py
```

The script will attempt to:

1. Create `NEO_ERA` knowledge base and upload corpus files.
2. Patch `__NEO_ERA_DATASET_ID__` in the DSL.
3. Import the workflow via Console API.

You still **manually**: confirm import in UI (if prompted), assign Gemini on LLM nodes, **Publish**, copy `DIFY_API_KEY` + `DIFY_WORKFLOW_ID`.

See `python scripts/dify_bootstrap.py --help` for flags and limitations.

---

## Files

| File | Purpose |
|------|---------|
| [neo-era-content-workflow.dsl.yml](neo-era-content-workflow.dsl.yml) | Importable workflow matching I/O contract |
| [../DIFY_SETUP.md](../DIFY_SETUP.md) | Full setup, prompts, GitHub secrets |
| [../../scripts/dify_bootstrap.py](../../scripts/dify_bootstrap.py) | API bootstrap helper |
| [../../scripts/dify_client.py](../../scripts/dify_client.py) | Runtime workflow runner |

---

*Operational setup · INSTITUTIONAL_MODEL · not religious authority*
