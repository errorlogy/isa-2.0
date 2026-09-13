# Dify setup — NEO_ERA content-version workflow

**Epistemic label:** `OPERATIONAL` (adapter contract only)

This guide configures a Dify Cloud (or self-hosted) workflow that powers `--mode content-version` in `scripts/telegram_post.py`.

Pipeline context: [NEO_ERA Telegram pipeline (umbrella draft)](https://github.com/errorlogy/ai-native-gov/blob/main/docs/integrations/NEO_ERA_TELEGRAM_PIPELINE.draft.md)

---

## Quick checklist (after you have a Dify API key)

**Fast path:** import [docs/dify/neo-era-content-workflow.dsl.yml](dify/neo-era-content-workflow.dsl.yml) (see [docs/dify/README.md](dify/README.md)) or run `python scripts/dify_bootstrap.py` with Console + Knowledge API credentials.

1. **Knowledge** → upload `docs/CORPUS/artifacts/NEO_ERA.md` (+ optional `.ru.md`)
2. **Import DSL** or build workflow manually (not Chatbot) → **Publish**
3. **API Access** → copy **App API key** (`app-…`) → GitHub secret `DIFY_API_KEY`
4. **Version history** → copy **published workflow version ID** (UUID) → GitHub secret `DIFY_WORKFLOW_ID`
5. **Test:** `gh workflow run neo-era-content-version.yml -f dry_run=true`
6. Add `FAL_KEY` (optional) → live post with `dry_run=false`

---

## 1. Create a Dify account and Workflow app

1. Sign up at [dify.ai](https://dify.ai) (Cloud) or deploy [Dify Docker](https://docs.dify.ai/en/getting-started/install-self-hosted) on a VPS.
2. **Settings → Model Provider** → add **Google Gemini** (API key from Google AI Studio). See [§ Gemini model selection](#9-gemini-model-selection-in-llm-nodes).
3. Create a new **Workflow** app (**not** Chatbot / Agent / Completion).
4. **Publish** the workflow before calling the API (draft versions are rejected).

---

## 2. Upload NEO_ERA knowledge

1. In Dify, open **Knowledge** → **Create knowledge base** (name e.g. `NEO_ERA`).
2. Upload corpus files from this repo:
   - `docs/CORPUS/artifacts/NEO_ERA.md` (**required**)
   - `docs/CORPUS/artifacts/NEO_ERA.ru.md` (optional, for `locale=ru`)
3. Chunk and embed (default settings are fine for MVP).
4. Attach the knowledge base to a **Knowledge Retrieval** node in your workflow (see [§4](#4-workflow-node-blueprint)).

---

## 3. API contract (inputs / outputs)

Variable names **must match exactly** — `scripts/telegram_post.py` passes these to `scripts/dify_client.py`.

### Inputs (Start node → user variables)

| Variable | Type | Required | Source | Description |
|----------|------|----------|--------|-------------|
| `aspect` | string | **Yes** | GHA / CLI | Wire ref e.g. `NEO_ERA:III` or Roman `III` |
| `locale` | string | **Yes** | GHA / CLI | `en` or `ru` |
| `slot_index` | string | No | GHA cron (future) | Cron slot index for rotation dedup |
| `recent_aspects` | string | No | GHA cron (future) | Comma-separated recent aspects to avoid repeats |

**Example request body** (what `dify_client.run_workflow` sends):

```json
{
  "inputs": {
    "aspect": "NEO_ERA:III",
    "locale": "en",
    "slot_index": "3",
    "recent_aspects": "NEO_ERA:I,NEO_ERA:II"
  },
  "response_mode": "blocking",
  "user": "isa-2.0-telegram"
}
```

### Outputs (End node → output variables)

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `caption_html` | string | **Yes** | HTML caption for Telegram `sendPhoto` (body only; script appends footer) |
| `image_prompt` | string | **Yes** | Text prompt for fal.ai FLUX schnell (or Dify HTTP node) |
| `aspect` | string | No | Resolved aspect (echo input or picker result) |
| `long_text` | string | No | Extended HTML for follow-up `sendMessage` if caption &gt;1024 chars |
| `image_url` | string | No | Pre-generated image URL; if empty, script calls fal.ai when `FAL_KEY` is set |

**Example blocking response** (what `extract_outputs()` reads):

```json
{
  "data": {
    "outputs": {
      "aspect": "NEO_ERA:III",
      "caption_html": "<b>NEO_ERA:III</b> — Talion ∞ …",
      "image_prompt": "Abstract geometric mirror, omega palette, no text",
      "long_text": "",
      "image_url": ""
    }
  }
}
```

### Epistemic guardrails (bake into every LLM system prompt)

1. Mandatory tone: `INSTITUTIONAL_MODEL · not religious authority`
2. **Banned:** guilty, criminal, proven, legitimate ruler, prophecy, sovereign mandate
3. **Preferred:** analytical contribution, legitimacy signals (modeled), possible / consistent with
4. Optional: Code node or regex lint before End to reject banned terms

---

## 4. Workflow node blueprint

Build this **Workflow** (not a simple chat app). Suggested node graph:

```text
┌─────────┐
│  Start  │  inputs: aspect, locale, slot_index?, recent_aspects?
└────┬────┘
     ▼
┌─────────────────────┐
│ Knowledge Retrieval │  dataset: NEO_ERA
│ query: {{aspect}}   │  top_k: 4–6
│       + {{locale}}  │
└────┬────────────────┘
     ▼
┌─────────────────────┐     (optional — skip if aspect is always NEO_ERA:I..X)
│ LLM: Aspect Picker  │  → output variable: aspect (resolved)
└────┬────────────────┘
     ▼
┌─────────────────────┐
│ LLM: Caption Writer │  → caption_html (HTML, &lt;900 chars ideal)
└────┬────────────────┘
     ▼
┌─────────────────────────┐
│ LLM: Image Prompt Writer│  → image_prompt (English, no text-in-image)
└────┬────────────────────┘
     ▼
┌─────────────────────┐     (optional)
│ LLM: Long Text      │  → long_text (extended HTML if caption too short)
└────┬────────────────┘
     ▼
┌─────────────────────┐     (optional — or leave empty; GHA calls fal.ai)
│ HTTP: fal.ai image  │  → image_url
└────┬────────────────┘
     ▼
┌─────────┐
│   End   │  publish ALL output variables listed in §3
└─────────┘
```

### Start node — declare input variables

In Dify Workflow editor → **Start** → add variables:

| Name | Type | Required |
|------|------|----------|
| `aspect` | text | yes |
| `locale` | text | yes |
| `slot_index` | text | no |
| `recent_aspects` | text | no |

### End node — declare output variables

In Dify Workflow editor → **End** → map LLM outputs:

| Output name | Source |
|-------------|--------|
| `caption_html` | Caption Writer LLM output |
| `image_prompt` | Image Prompt Writer LLM output |
| `aspect` | Start `aspect` or Aspect Picker output |
| `long_text` | Long Text LLM output (or empty string) |
| `image_url` | HTTP node output (or empty string) |

### Example system prompt (Caption Writer)

```text
You write Telegram photo captions for the NEO_ERA institutional corpus.

Epistemic rules (mandatory):
- Label: INSTITUTIONAL_MODEL · not religious authority
- Never use: guilty, criminal, proven, legitimate ruler, prophecy, sovereign mandate
- Prefer: analytical contribution, legitimacy signals (modeled), possible / consistent with
- Output valid HTML only (<b>, <i>, <code> allowed). No markdown.
- Locale: {{#locale#}} — write caption in English unless locale is "ru".
- Aspect wire ref: {{#aspect#}}
- Use retrieved context from knowledge base; do not invent axioms.

Format:
<b>NEO_ERA:X</b> — short label
<i>INSTITUTIONAL_MODEL · not religious authority</i>

2–4 sentences of analytical commentary grounded in the corpus.
Keep under 900 characters (footer is appended by the poster script).
```

### Example system prompt (Image Prompt Writer)

```text
Write a single English image-generation prompt for FLUX schnell.
Subject: symbolic illustration for {{#aspect#}} from NEO_ERA corpus.
Style: abstract geometry, topological mirror motifs, muted omega palette, institutional aesthetic.
Constraints: no text, no logos, no faces of real people, no religious iconography.
One paragraph, max 200 words.
```

### Importable DSL (preferred)

Dify supports **App DSL** import/export (YAML). This repo ships a ready-made file:

- [docs/dify/neo-era-content-workflow.dsl.yml](dify/neo-era-content-workflow.dsl.yml) — import via Studio → **Import DSL**
- [docs/dify/README.md](dify/README.md) — import steps and API limitations
- [scripts/dify_bootstrap.py](../scripts/dify_bootstrap.py) — partial automation (Knowledge API + Console import)

Replace `__NEO_ERA_DATASET_ID__` in the DSL with your knowledge base UUID before import (bootstrap script patches this automatically).

Structural reference (not importable):

```json
{
  "app_mode": "workflow",
  "inputs": ["aspect", "locale", "slot_index", "recent_aspects"],
  "outputs": ["aspect", "caption_html", "image_prompt", "long_text", "image_url"],
  "nodes": [
    {"id": "start", "type": "start"},
    {"id": "kb", "type": "knowledge-retrieval", "dataset": "NEO_ERA", "query": "{{aspect}} {{locale}}"},
    {"id": "caption", "type": "llm", "model": "gemini-2.0-flash", "output": "caption_html"},
    {"id": "image_prompt", "type": "llm", "model": "gemini-2.0-flash", "output": "image_prompt"},
    {"id": "end", "type": "end"}
  ]
}
```

---

## 5. API keys: App API key vs Workflow version ID

Dify uses **two different identifiers** — do not confuse them:

| Item | Where to find | GitHub secret | Format |
|------|---------------|---------------|--------|
| **App API key** | App → **API Access** → Create API Key | `DIFY_API_KEY` | `app-xxxxxxxx…` |
| **Workflow version ID** | App → **Publish** → **Version history** → copy icon on published row | `DIFY_WORKFLOW_ID` | UUID e.g. `7c3e33d4-2a8b-4e5f-9b1a-d3c6e8f12345` |

- The **API key** authenticates requests (`Authorization: Bearer app-…`).
- The **workflow version ID** pins a specific **published** version (draft IDs are rejected).
- **App ID** (in the URL) is **not** the same as workflow version ID. Our client uses the version ID in the path: `POST /v1/workflows/{workflow_id}/run`.
- Optional override: `DIFY_API_BASE` (default `https://api.dify.ai/v1`) for self-hosted Dify.

Both `DIFY_API_KEY` and `DIFY_WORKFLOW_ID` must be set for live Dify calls (`dify_client.configured()`).

---

## 6. GitHub secrets

| GitHub Secret | Required | Notes |
|---------------|----------|-------|
| `DIFY_API_KEY` | For live content-version | App API key from Dify (`app-…`) |
| `DIFY_WORKFLOW_ID` | For live content-version | Published workflow version UUID |
| `FAL_KEY` | Optional | fal.ai key; omit for dry-run without image |
| `TELEGRAM_BOT_TOKEN` | For live send | See [TELEGRAM_BOT_SETUP.md](TELEGRAM_BOT_SETUP.md) |
| `TELEGRAM_CHANNEL_ID` | For live send | `@OmegaCovenant` or `-100…` |

```powershell
cd C:\Users\Public\ISA_2_0
gh secret set DIFY_API_KEY --body "app-xxxxxxxx"
gh secret set DIFY_WORKFLOW_ID --body "7c3e33d4-2a8b-4e5f-9b1a-d3c6e8f12345"
gh secret set FAL_KEY --body "fal_xxxxxxxx"   # optional
```

**Never paste API keys in chat or commit them to the repo.**

---

## 7. Test locally (no Dify)

Mock payload is used when `DIFY_API_KEY` or `DIFY_WORKFLOW_ID` is unset:

```powershell
cd C:\Users\Public\ISA_2_0
python scripts/telegram_post.py --mode content-version --dry-run
python scripts/telegram_post.py --mode content-version --dry-run --aspect NEO_ERA:III
```

Expected JSON fields: `mode`, `caption_preview`, `image_prompt`, `dify_configured: false`, `fal_configured: false`.

With Dify secrets set locally:

```powershell
$env:DIFY_API_KEY = "app-..."      # set in your shell only — do not commit
$env:DIFY_WORKFLOW_ID = "uuid-..."
python scripts/telegram_post.py --mode content-version --dry-run --aspect NEO_ERA:III
```

Expected: `dify_configured: true`, real `caption_preview` from Dify.

---

## 8. Test in GitHub Actions

**Workflow file:** [neo-era-content-version.yml](https://github.com/errorlogy/isa-2.0/blob/main/.github/workflows/neo-era-content-version.yml)

**UI:** [NEO_ERA Content Version (test)](https://github.com/errorlogy/isa-2.0/actions/workflows/neo-era-content-version.yml) → **Run workflow**

### Test sequence (recommended order)

| Step | Command / action | Expect |
|------|------------------|--------|
| 1 | Mock dry-run (no Dify secrets needed) | `dify_configured: false` |
| 2 | Set `DIFY_API_KEY` + `DIFY_WORKFLOW_ID` secrets | — |
| 3 | Live Dify dry-run | `dify_configured: true`, real caption in logs |
| 4 | Add `FAL_KEY` | `fal_configured: true`, mock image URL in dry-run |
| 5 | Live post (`dry_run=false`) | `sendPhoto` to @OmegaCovenant |

### `gh workflow run` commands

```powershell
cd C:\Users\Public\ISA_2_0

# Step 1 — mock dry-run (works without any secrets)
gh workflow run neo-era-content-version.yml -f dry_run=true

# Step 3 — live Dify, still no Telegram send
gh workflow run neo-era-content-version.yml -f dry_run=true -f aspect=NEO_ERA:III -f locale=en

# Step 5 — first live post (needs all secrets: DIFY_*, FAL_KEY, TELEGRAM_*)
gh workflow run neo-era-content-version.yml -f dry_run=false -f aspect=NEO_ERA:III -f locale=en

# Watch run
gh run list --workflow=neo-era-content-version.yml --limit 3
gh run watch
```

Or use the main workflow with `mode: content-version`:

[NEO_ERA Telegram](https://github.com/errorlogy/isa-2.0/actions/workflows/neo-era-telegram.yml)

---

## 9. Gemini model selection in LLM nodes

You connected Gemini via **Settings → Model Provider → Google** in Dify. In each **LLM node**:

| Node | Recommended model | Why |
|------|-------------------|-----|
| Caption Writer | `gemini-2.0-flash` or `gemini-1.5-flash` | Fast, good HTML; captions are short |
| Image Prompt Writer | `gemini-2.0-flash` | Creative but structured output |
| Aspect Picker (optional) | `gemini-2.0-flash` | Classification / light reasoning |
| Long Text (optional) | `gemini-1.5-pro` or `gemini-2.0-flash` | Longer context if needed |

Settings per LLM node:
- **Temperature:** 0.3–0.5 (lower = more consistent epistemic tone)
- **Max tokens:** 1024 for caption, 512 for image prompt
- Enable **Knowledge** context from the retrieval node (pass `result` into user prompt)

If `gemini-2.0-flash` is unavailable in your Dify region, use `gemini-1.5-flash` — the contract is model-agnostic.

---

## 10. API reference

| Endpoint | Used by |
|----------|---------|
| `POST https://api.dify.ai/v1/workflows/{workflow_id}/run` | `scripts/dify_client.py` (when `DIFY_WORKFLOW_ID` set) |
| `POST https://fal.run/fal-ai/flux/schnell` | `scripts/telegram_post.py` when `FAL_KEY` set and no `image_url` from Dify |

Docs:
- [Dify Run Workflow by ID](https://docs.dify.ai/en/api-reference/workflow-runs/run-workflow-by-id)
- [fal.ai flux schnell](https://fal.ai/models/fal-ai/flux/schnell)

---

*Operational setup · INSTITUTIONAL_MODEL · not religious authority*
