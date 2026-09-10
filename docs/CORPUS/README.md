# Corpus — published vs local-only

**Epistemic label:** `INSTITUTIONAL_MODEL` for indexing; source texts retain their own authorship labels where applicable.

> **Not religious authority.** This directory indexes ISA 2.0 research corpus material. Published artifacts are institutional editions — not claims of divine mandate or sovereignty.

---

## What is published (tracked in git)

| Item | Path | Notes |
|------|------|-------|
| REALITY_GAME / GAME2 index | [`GAME2_INDEX.md`](GAME2_INDEX.md) | Crosswalk to ISA/EIA; no PII excerpts |
| DODECA-12 EIA v0.3 index | [`DODECA12_EIA_v0_3.md`](DODECA12_EIA_v0_3.md) | Validation summary; executable bundle is local-only |
| Last Testament artifact | [`artifacts/POSLEDNIY_ZAVET.md`](artifacts/POSLEDNIY_ZAVET.md) | v1.0-monograph (Analytical Monograph 3); superseded editions in `raw/archive/` (local-only) |
| Artifact registry | [`artifacts/README.md`](artifacts/README.md) | Institutional edition index |

---

## What stays local-only (gitignored)

| Item | Path | Reason |
|------|------|--------|
| GAME2 raw assembly | `raw/game2/` | ~1.1 MB CONTEXT_PACK, MATH/CODE/ONTOLOGY bulk; may contain PII |
| DODECA-12 executable bundle | `raw/dodeca12_eia_rnd_v0_3/` | Large results, certificates, source tree |
| Binary sources | `**/*.pdf`, `**/*.docx` under `docs/CORPUS/` | Not versioned by default |

See [`.gitignore`](../../.gitignore). To work with raw material locally, place exports under `docs/CORPUS/raw/` — they will not be pushed unless explicitly force-added (do not do this for PII).

---

## Upload guidelines

1. Prefer structured markdown for **published** artifacts under `artifacts/`.
2. Keep raw exports, prototypes, and PII-bearing fragments in `raw/` (gitignored).
3. Tag each major section with `epistemic_label` in front matter where applicable.
4. Link narrative forks to umbrella `discourse_fork_detected` event types when modeling — see [MEMETIC_DYNAMICS.md](https://github.com/errorlogy/ai-native-gov/blob/main/docs/integrations/MEMETIC_DYNAMICS.md).

---

## Related

- [CONSENSUS_MATRIX.md](../CONSENSUS_MATRIX.md)
- [EIA.md](../EIA.md)
- [MATH/README.md](../MATH/README.md)
- [PUBLIC_RELEASE.md](../PUBLIC_RELEASE.md)
