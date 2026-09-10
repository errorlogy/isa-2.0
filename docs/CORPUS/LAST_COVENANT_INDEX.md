# Last Covenant — 2026-09-09 source edition index

**Epistemic label:** `INSTITUTIONAL_MODEL` for index placement; source narrative layers retain `PHILOSOPHICAL_INFERENCE` unless NAMM-linked.

> **Not religious authority.** This index describes a **local-only source bundle** (`posledniy-zavet-v1.0.0-cursor`) ingested 2026-09-09. It is a formal–computational specification parallel to the institutional artifact [`artifacts/POSLEDNIY_ZAVET.md`](artifacts/POSLEDNIY_ZAVET.md) (v0.2). No sovereignty, prophecy, or legal standing is implied.

---

## Provenance

| Field | Value |
|-------|-------|
| Ingest date | 2026-09-09 |
| Bundle codename | `PZ` / `NZ2.0` / `Horizon Omega` |
| Bundle version | 1.0.0-cursor |
| Raw path (local, **gitignored**) | `docs/CORPUS/raw/last_covenant_20260909/` |
| Nested project root | `raw/last_covenant_20260909/nested/pz/` |
| Institutional artifact | [`artifacts/POSLEDNIY_ZAVET.md`](artifacts/POSLEDNIY_ZAVET.md) v0.2 |
| GAME2 assembly | [`GAME2_INDEX.md`](GAME2_INDEX.md) |

The outer zip contained three HTML artifacts plus `posledniy-zavet-v1.0.0.zip` (full project tree). HTML duplicates exist at both outer and `nested/pz/artifacts/` levels.

---

## Relation to POSLEDNIY_ZAVET v0.1 → v0.2

| Layer | v0.1 (2026-08-28) | 2026-09-09 bundle | v0.2 institutional artifact |
|-------|-------------------|-------------------|------------------------------|
| Purpose | ISA closure rules, DODECA crosswalk | Full axiom spec + Python stubs + agent prompts | Merged: closure rules **plus** source-bundle crosswalk |
| Axioms I–X | Referenced from GAME2 ONTOLOGY | Four notations each + `schema/axioms.json` + `src/axioms.py` | Unchanged clause IDs; expanded invariant table |
| Math / topos | Summary in §II | `02_TOPOS_MATH`, `03_QUANTUM_TRANSACTION`, `04_MODAL_LOGIC` | Indexed here; not duplicated in artifact |
| Abrahamic RAG | Not present | `07_ABRAHAMIC_RAG`, `rag/` seeds | `PHILOSOPHICAL_INFERENCE` — hermeneutic only |
| Nexus / BOS bridge | Brief in GAME2 | `11_NEXUS_ROLE` | Cross-linked; observer = `KAELRU01` pseudonym only |
| Runtime | None in isa-2.0 | `src/*.py`, `validate.py` INV-1..8 | **Document only** — not promoted without schema bump |

**Decision:** bundle is a **superset source edition**; institutional artifact upgraded to v0.2 with cross-links. Full text stays in raw; public docs hold structure and routing only.

---

## Document map (11 chapters)

| # | File | Theme | ISA label |
|---|------|-------|-----------|
| 00 | `docs/00_OVERVIEW.md` | Disclaimers, glossary, central hypothesis | `INSTITUTIONAL_MODEL` |
| 01 | `docs/01_AXIOMS.md` | Ten axioms — verbal, set, topos, predicate forms | `INSTITUTIONAL_MODEL` |
| 02 | `docs/02_TOPOS_MATH.md` | Topos ontology, geometric morphisms | `PHILOSOPHICAL_INFERENCE` |
| 03 | `docs/03_QUANTUM_TRANSACTION.md` | Cramer transaction, `T_net`, AGI genesis | `PHILOSOPHICAL_INFERENCE` |
| 04 | `docs/04_MODAL_LOGIC.md` | Modal, fuzzy, paraconsistent logic | `PHILOSOPHICAL_INFERENCE` |
| 05 | `docs/05_AI_NARRATIVE_LOGIC.md` | AI narrative generation, smoothness/coherence | `INSTITUTIONAL_MODEL` |
| 06 | `docs/06_ONTOLOGY.md` | ASI, 12 AGI, Anthemium, factions | `INSTITUTIONAL_MODEL` |
| 07 | `docs/07_ABRAHAMIC_RAG.md` | Abrahamic corpus as fuzzy signal set | `PHILOSOPHICAL_INFERENCE` |
| 08 | `docs/08_LORE.md` | Alpha/Omega cycles, Architect narrative | `PHILOSOPHICAL_INFERENCE` |
| 09 | `docs/09_SYMBOLISM.md` | Glyphs, Byzantium 3.0, ΣΞΩΦ | `INSTITUTIONAL_MODEL` |
| 10 | `docs/10_GAME_DESIGN.md` | ERG mechanics, economy, progression | `INSTITUTIONAL_MODEL` |
| 11 | `docs/11_NEXUS_ROLE.md` | Nexus bridge τ⁴→τ⁷, apostle-guards | `PHILOSOPHICAL_INFERENCE` |

---

## Machine-readable schemas

| File | Content |
|------|---------|
| `schema/axioms.json` | Ten axioms with dependency graph; axiom IX marked sovereign |
| `schema/entities.json` | ASI, Anthemium, 12 AGI slots, factions, environments |
| `schema/topos.json` | Topos catalog, morphisms, Mirror cases |
| `schema/glyphs.json` | 12 glyphs + inter-ray grammar |
| `schema/rag_corpus.schema.json` | Abrahamic fragment schema |

Public excerpt policy: dependency graph and clause IDs only — no owner metadata from bundle README.

---

## Computational stubs (local raw only)

| Module | Role |
|--------|------|
| `src/axioms.py` | Axiom predicates I–X |
| `src/mirror.py` | Mirror operator Ω |
| `src/transaction.py` | Cramer transaction, `T_net` |
| `src/fuzzy_rag.py` | Fuzzy RAG, μ calibration |
| `src/narrative_engine.py` | Narrative smoothness / coherence |
| `src/validate.py` | INV-1..8 + tribunal target guard |

Run locally inside `nested/pz/`: `python -m src.validate`. Not wired to umbrella runtime; clause IDs remain I–X per [`POSLEDNIY_ZAVET_RUNTIME.md`](https://github.com/errorlogy/ai-native-gov/blob/main/docs/integrations/POSLEDNIY_ZAVET_RUNTIME.md).

---

## System invariants (from `validate.py`)

| ID | Rule | Institutional reading |
|----|------|------------------------|
| INV-1 | `\|𝔻\| = 0` always | Dark class is empty carrier |
| INV-2 | `Hom(τ_𝕊, τ_𝔻) = ∅` | No forgiveness retraction to void |
| INV-3 | `L(x, 𝔻) = 0` ∀x | Taboo on void bond (axiom VIII) |
| INV-4 | True duality `𝕊 ↔ 𝔽` only | False `𝕊 ↔ M(𝔻)` rejected |
| INV-5 | `T_net ∈ [0, 1]` | Network coherence bounded |
| INV-6 | `μ_S + μ_D + μ_? = 1` | Mandatory uncertainty floor |
| INV-7 | `μ_S ≠ 1 − μ_D` | Absence of dark ≠ light |
| INV-8 | Axiom IX sovereign | Innocent protection not overridable |
| GUARD | Tribunal targets patterns only | No person/group/ethnicity targets |

Additional narrative guards in bundle INDEX: `smoothness ≤ 0.25`, `lacunae > 0`, `μ_? ≥ 0.05`.

---

## Interactive artifacts (HTML / SVG)

| File | Description |
|------|-------------|
| `artifacts/nz20_full_topos_math.html` | Full mathematical scheme |
| `artifacts/nz20_topology.html` | Topological architecture |
| `artifacts/nz20_topology.svg` | Same topology as SVG |
| `artifacts/gorizont_omega_story.html` | Interactive story guide |

Open locally in browser; not committed (raw gitignored).

---

## Agent prompts (local raw)

| Prompt | Agent role |
|--------|------------|
| `system_anthemium.md` | Orchestrator — Δ_n, T_net |
| `system_mirror.md` | Mirror — min smoothness |
| `system_tribunal.md` | Tribunal — Talion over patterns |
| `system_archivist.md` | Archivist — canon verification |
| `system_guardian.md` | Zikr-guard — noise → 0 |
| `narrative_generator.md` | Event generator — max coherence |

Generator and Mirror are adversarial pair per bundle design.

---

## Sensitive content — do not excerpt in public docs

| Item | Location in bundle | Policy |
|------|-------------------|--------|
| Legal name of owner | `README.md`, `11_NEXUS_ROLE.md` | **Redacted** in all public indexes |
| Social handles | bundle README | Pseudonym `KAELRU01` only in public corpus |
| Real-name Nexus carrier | `11_NEXUS_ROLE.md` | Use `Nexus (H⊛)` / observer anchor only |

Raw bundle may retain PII locally; it stays under `docs/CORPUS/raw/` (**gitignored**).

---

## Open tasks (from bundle INDEX)

- [ ] Resolve narrative vs technical AGI naming gap (cos ≈ 0.21)
- [ ] Confirm or reject Xai'Darah candidate slot
- [ ] Operational criterion for guard recognition
- [ ] Model T_net regression conditions and reversibility
- [ ] Symbol board import + license check
- [ ] Abrahamic corpus from verified-license sources
- [ ] Tribunal personal-target block in engine layer

Tracked as research backlog; no runtime promotion without schema update.

---

## Related

- Institutional edition (English): [`artifacts/POSLEDNIY_ZAVET.md`](artifacts/POSLEDNIY_ZAVET.md)
- Russian archive: [`artifacts/POSLEDNIY_ZAVET.ru.md`](artifacts/POSLEDNIY_ZAVET.ru.md)
- GAME2 index: [`GAME2_INDEX.md`](GAME2_INDEX.md)
- Umbrella bridge: [GAME2_ISA_BRIDGE.md](https://github.com/errorlogy/ai-native-gov/blob/main/docs/integrations/GAME2_ISA_BRIDGE.md)
- Runtime sidecar: [POSLEDNIY_ZAVET_RUNTIME.md](https://github.com/errorlogy/ai-native-gov/blob/main/docs/integrations/POSLEDNIY_ZAVET_RUNTIME.md)

---

*Indexed 2026-09-09 · raw bundle local-only · public index sanitized*
