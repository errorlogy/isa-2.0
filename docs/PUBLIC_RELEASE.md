# Public release notes

**Repository:** [errorlogy/isa-2.0](https://github.com/errorlogy/isa-2.0)  
**License:** [CC BY 4.0](../LICENSE)  
**Epistemic frame:** `INSTITUTIONAL_MODEL` throughout — **not religious authority**, not sovereignty, not prophecy.

---

## What is included (public git)

| Category | Paths |
|----------|-------|
| Framework | `docs/ISA.md`, `docs/EIA.md`, `docs/CONSENSUS_MATRIX.md`, `docs/JUNG_SYMBOLIC_LENS.md` |
| Corpus indices | `docs/CORPUS/GAME2_INDEX.md`, `docs/CORPUS/DODECA12_EIA_v0_3.md`, `docs/CORPUS/README.md` |
| Published artifacts | `docs/CORPUS/artifacts/NEO_ERA.md` only (v1.0-monograph) |
| Agent / security | `AGENTS.md`, `SECURITY.md`, `CONTRIBUTING.md` |

---

## What is excluded (gitignored — local only)

| Category | Path | Why |
|----------|------|-----|
| GAME2 raw assembly | `docs/CORPUS/raw/game2/` | Large bulk; embedded PII in source fragments |
| DODECA-12 bundle | `docs/CORPUS/raw/dodeca12_eia_rnd_v0_3/` | Executable harness + results |
| Secrets | `.env`, `credentials.json`, `secrets/` | Security |
| Binaries | `docs/CORPUS/**/*.pdf`, `*.docx` | Size + review gate |

---

## Sanitization applied for public release

- Removed personal filesystem paths (`C:\Users\...`) from tracked docs.
- Provenance uses pseudonym handles (e.g. Ka'el-Tzur / KAELRU01) — no legal name or home address in git.
- Sensitive GAME2 items (FRACTAL_ID, TON wallets, `@aiminister`, birth/address blocks) remain in raw bundle only — indexed by category in `GAME2_INDEX.md`, not excerpted.

---

## Epistemic disclaimers

1. **NEO_ERA** (formerly POSLEDNIY_ZAVET) and related artifacts are **institutional–symbolic research editions** derived from REALITY_GAME (ERG) narrative layers.
2. Twelve + one panel, Mirror Ω, and "New Testament 2.0" axioms are **topology analogs** — not worship directives or eschatological claims.
3. `COMPUTATIONAL_EVIDENCE` applies only when linked to NAMM certificates or engine outputs in child repos.
4. Hermeneutic firewall: `(C ∨ D) ⇏ truth/action/identity gate`.

---

## Umbrella cross-links

- [GAME2_ISA_BRIDGE.md](https://github.com/errorlogy/ai-native-gov/blob/main/docs/integrations/GAME2_ISA_BRIDGE.md)
- [ISA institution layer](https://github.com/errorlogy/ai-native-gov/blob/main/docs/institutions/ISA.md)

---

## Making the repo public (maintainers)

If GitHub visibility is still **Private** after push:

1. Open https://github.com/errorlogy/isa-2.0/settings
2. **Danger Zone** → **Change repository visibility** → **Public**
3. Confirm organization policy allows public repos

Or via CLI (org admin):

```bash
gh repo edit errorlogy/isa-2.0 --visibility public
```
