# Dify setup — NEO_ERA content-version workflow

**Epistemic label:** `OPERATIONAL` (adapter contract only)

This guide configures a Dify Cloud (or self-hosted) workflow that powers `--mode content-version` in `scripts/telegram_post.py`.

Pipeline context: [NEO_ERA Telegram pipeline (umbrella draft)](https://github.com/errorlogy/ai-native-gov/blob/main/docs/integrations/NEO_ERA_TELEGRAM_PIPELINE.draft.md)

---

## 1. Create a Dify account

1. Sign up at [dify.ai](https://dify.ai) (Cloud) or deploy [Dify Docker](https://docs.dify.ai/en/getting-started/install-self-hosted) on a VPS.
2. Create a new **Workflow** app (not Chatbot).
3. Publish the workflow before calling the API.

---

## 2. Upload NEO_ERA knowledge

1. In Dify, open **Knowledge** → **Create knowledge base**.
2. Upload corpus files from this repo:
   - `docs/CORPUS/artifacts/NEO_ERA.md`
   - `docs/CORPUS/artifacts/NEO_ERA.ru.md` (optional)
   - Selected KLS excerpts if needed
3. Chunk and embed (default settings are fine for MVP).
4. Attach the knowledge base to a **Knowledge Retrieval** node in your workflow.

---

## 3. Workflow contract (inputs / outputs)

The isa-2.0 poster expects this API contract. Variable names must match exactly.

### Inputs (from `telegram_post.py`)

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `aspect` | string | Yes | Wire ref e.g. `NEO_ERA:III` or clause hint |
| `locale` | string | Yes | `en` or `ru` |
| `slot_index` | string | No | Cron slot index (for rotation dedup) |
| `recent_aspects` | string | No | Comma-separated recent aspects to avoid repeats |

### Outputs (workflow end node)

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `aspect` | string | No | Resolved aspect (echo or picker result) |
| `caption_html` | string | **Yes** | HTML caption for `sendPhoto` (body only; script appends footer) |
| `image_prompt` | string | **Yes** | Text prompt for fal.ai FLUX schnell |
| `long_text` | string | No | Extended HTML for follow-up `sendMessage` if &gt;1024 caption |
| `image_url` | string | No | Pre-generated image URL; if empty, script calls fal.ai when `FAL_KEY` is set |

### Epistemic guardrails (bake into system prompt)

1. Mandatory tone: `INSTITUTIONAL_MODEL · not religious authority`
2. **Banned:** guilty, criminal, proven, legitimate ruler, prophecy, sovereign mandate
3. **Preferred:** analytical contribution, legitimacy signals (modeled), possible / consistent with
4. Optional: LLM compliance node or regex lint before output

---

## 4. Example workflow shape

```text
Start
  → Knowledge Retrieval (NEO_ERA corpus, query = aspect + locale)
  → LLM: Aspect Picker (if aspect is vague)
  → LLM: Caption Writer → caption_html
  → LLM: Image Prompt Writer → image_prompt
  → LLM: Long Text (optional) → long_text
End (publish outputs)
```

You may generate `image_url` inside Dify via an HTTP node to fal.ai, or leave it empty and let the GitHub Action call fal.ai.

---

## 5. API keys and workflow ID

1. In Dify app → **API Access** → create an API key.
2. Copy the **Workflow ID** from the published workflow (or use the app API key with `/workflows/run`).

| GitHub Secret | Required | Notes |
|---------------|----------|-------|
| `DIFY_API_KEY` | For live content-version | App API key from Dify |
| `DIFY_WORKFLOW_ID` | For live content-version | Published workflow UUID |
| `FAL_KEY` | Optional | fal.ai key; omit for dry-run without image |
| `TELEGRAM_BOT_TOKEN` | For live send | See [TELEGRAM_BOT_SETUP.md](TELEGRAM_BOT_SETUP.md) |
| `TELEGRAM_CHANNEL_ID` | For live send | `@OmegaCovenant` or `-100…` |

```powershell
cd C:\Users\Public\ISA_2_0
gh secret set DIFY_API_KEY --body "app-xxxxxxxx"
gh secret set DIFY_WORKFLOW_ID --body "workflow-uuid-here"
gh secret set FAL_KEY --body "fal_xxxxxxxx"   # optional
```

---

## 6. Test locally (no Dify)

Mock payload is used when `DIFY_API_KEY` or `DIFY_WORKFLOW_ID` is unset:

```powershell
cd C:\Users\Public\ISA_2_0
python scripts/telegram_post.py --mode content-version --dry-run
python scripts/telegram_post.py --mode content-version --dry-run --aspect NEO_ERA:III
```

Expected JSON fields: `mode`, `caption_preview`, `image_prompt`, `dify_configured: false`, `fal_configured: false`.

---

## 7. Test in GitHub Actions

1. [NEO_ERA Content Version (test)](https://github.com/errorlogy/isa-2.0/actions/workflows/neo-era-content-version.yml) → **Run workflow**
2. `dry_run: true` first (works without Dify/FAL secrets — mock data).
3. Add Dify secrets → `dry_run: true` again to validate live Dify JSON in logs.
4. Add `FAL_KEY` + Telegram secrets → `dry_run: false` for first live `sendPhoto`.

Or use the main workflow with `mode: content-version`:

[NEO_ERA Telegram](https://github.com/errorlogy/isa-2.0/actions/workflows/neo-era-telegram.yml)

---

## 8. API reference

- Dify: `POST https://api.dify.ai/v1/workflows/{workflow_id}/run`
- Client: `scripts/dify_client.py`
- fal.ai: `POST https://fal.run/fal-ai/flux/schnell` (see [fal.ai flux schnell](https://fal.ai/models/fal-ai/flux/schnell))

---

*Operational setup · INSTITUTIONAL_MODEL · not religious authority*
