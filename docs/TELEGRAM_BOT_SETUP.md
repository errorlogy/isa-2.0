# Telegram bot setup — NEO_ERA → @OmegaCovenant

**Epistemic label:** `OPERATIONAL` (adapter only) · not religious authority

This guide configures the GitHub Actions workflow that posts `NEO_ERA:I..X` axiom excerpts from the isa-2.0 corpus to [@OmegaCovenant](https://t.me/OmegaCovenant).

Pipeline design (umbrella): [NEO_ERA_TELEGRAM_PIPELINE.draft.md](https://github.com/errorlogy/ai-native-gov/blob/main/docs/integrations/NEO_ERA_TELEGRAM_PIPELINE.draft.md)

---

## 1. Create the bot (@BotFather)

1. Open Telegram and start [@BotFather](https://t.me/BotFather).
2. Send `/newbot`.
3. Choose a display name (e.g. `Omega Covenant Poster`).
4. Choose a username ending in `bot` (e.g. `omega_covenant_poster_bot`).
5. BotFather replies with an HTTP API **token** like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`.
6. Copy the token — you will store it only in GitHub Secrets (never commit it).

Optional BotFather commands:

```
/setdescription — NEO_ERA institutional outreach (INSTITUTIONAL_MODEL)
/setabouttext — Posts axiom excerpts from errorlogy/isa-2.0. Not religious authority.
```

---

## 2. Add the bot to @OmegaCovenant

1. Open [@OmegaCovenant](https://t.me/OmegaCovenant) as a channel administrator.
2. **Administrators** → **Add administrator**.
3. Search for your bot username and add it.
4. Enable at minimum:
   - **Post messages**
   - **Edit messages** (optional, for future edits)

---

## 3. Resolve channel ID

GitHub secret `TELEGRAM_CHANNEL_ID` can be:

| Value | Notes |
|-------|-------|
| `@OmegaCovenant` | Public username (default in script) |
| `-100xxxxxxxxxx` | Numeric supergroup/channel ID (more reliable in some setups) |

To obtain the numeric ID:

1. Forward any post from @OmegaCovenant to [@userinfobot](https://t.me/userinfobot) or [@getidsbot](https://t.me/getidsbot), **or**
2. Post a test message with the bot, then call `https://api.telegram.org/bot<TOKEN>/getUpdates`.

---

## 4. GitHub repository secrets

Repository: [errorlogy/isa-2.0](https://github.com/errorlogy/isa-2.0)

| Secret | Required | Value |
|--------|----------|-------|
| `TELEGRAM_BOT_TOKEN` | Yes | Token from @BotFather |
| `TELEGRAM_CHANNEL_ID` | Recommended | `@OmegaCovenant` or numeric `-100…` |

### Via GitHub UI

**Settings** → **Secrets and variables** → **Actions** → **New repository secret**

### Via CLI (authenticated `gh`)

```powershell
cd C:\Users\Public\ISA_2_0
gh secret set TELEGRAM_BOT_TOKEN --body "PASTE_TOKEN_FROM_BOTFATHER"
gh secret set TELEGRAM_CHANNEL_ID --body "@OmegaCovenant"
```

---

## 5. First run — dry run

1. Open [Actions → NEO_ERA Telegram](https://github.com/errorlogy/isa-2.0/actions/workflows/neo-era-telegram.yml).
2. **Run workflow** → branch `main`.
3. Set inputs:
   - `dry_run`: **true**
   - `clause_id`: `I`
   - `locale`: `en`
4. Inspect the job log — JSON preview with `idempotency_key`, `parts`, and `preview` text.
5. Confirm disclaimer line: `INSTITUTIONAL_MODEL · not religious authority`.

---

## 6. First live post

1. **Run workflow** again with `dry_run`: **false**, `clause_id`: `I`.
2. Verify the message appears on [@OmegaCovenant](https://t.me/OmegaCovenant).

---

## 7. Local dry-run (no token)

```powershell
cd C:\Users\Public\ISA_2_0
python scripts/telegram_post.py --dry-run --clause I
```

Stdlib only — no `pip install` required.

Environment variables (optional):

| Variable | Default | Purpose |
|----------|---------|---------|
| `TELEGRAM_BOT_TOKEN` | — | Bot API token |
| `TELEGRAM_CHANNEL_ID` | `@OmegaCovenant` | Target channel |
| `DRY_RUN` | `false` | `true` to skip send |
| `CLAUSE_ID` | day rotation | Roman I–X |
| `LOCALE` | `en` | `en` or `ru` |
| `GITHUB_SHA` | `git rev-parse HEAD` | Idempotency key component |

---

## 8. Workflow triggers

| Trigger | Behavior |
|---------|----------|
| `schedule` | Daily 09:00 UTC — rotates axiom by day-of-year |
| `workflow_dispatch` | Manual clause / locale / dry_run |
| `push` | On `docs/CORPUS/artifacts/NEO_ERA*.md` change — posts touched axioms |
| `repository_dispatch` | `neo-era-post` with optional `clause_id`, `locale`, `sha`, `dry_run` |

---

## Security

- Never commit the bot token to the corpus or umbrella repos.
- Use `dry_run: true` for all manual validation before the first live send.
- Posts are labeled `INSTITUTIONAL_MODEL` — not religious authority.

---

*Operational setup · INSTITUTIONAL_MODEL · not religious authority*
