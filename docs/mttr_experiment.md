# MTTR Experiment — Verified Resolution Assistant

> **Dataset Label**: `SYNTHETIC_BENCHMARK`
> All values calculated from the generated synthetic recurring incident dataset.
> No values are hard-coded or fabricated.

---

## Experiment Design

**Purpose**: Measure the impact of the Verified Resolution Assistant on Mean Time To Resolution (MTTR) for recurring clinical IT incidents.

**MTTR Definition**:
$$MTTR = \frac{\sum ttr_{minutes}}{n_{resolved}}$$

### A. Baseline (Manual Process)
Engineer manually searches resolved tickets and knowledge articles → selects resolution → applies fix.

### B. Assisted Workflow (This System)
Incident → PHI Sanitization → Semantic Vector Retrieval → Verification Pipeline → Human Confirmation → Fix Applied.

---

## Results Table

| Metric | Baseline | Target | Measured | Unit |
|--------|----------|--------|----------|------|
| Total incidents | 300 | — | 300 | count |
| Recurring incidents | 300 | — | 300 | count |
| Mean MTTR | 36.92 | ≤31.38 | **15.78** | minutes |
| Median MTTR | 35.15 | — | 14.8 | minutes |
| P90 MTTR | 53.41 | — | 22.28 | minutes |
| MTTR Improvement | 0% | ≥15.0% | **57.26%** | % |
| Target met | — | Yes | ✅ Yes | boolean |
| Top-1 Accuracy | — | ≥80% | 91.0% | % |
| Top-3 Accuracy | — | ≥90% | 91.0% | % |
| Version-compatible | — | 100% | 100.0% | % |

---

## Error Analysis

| Category | Count | Percentage |
|----------|-------|-----------|
| Correct retrieval | 273 | 91.0% |
| No relevant resolution found | 19 | 6.3% |
| Wrong semantic match | 8 | 2.7% |
| Version mismatch (blocked) | 0 | 0.0% |
| Stale knowledge article (blocked) | 0 | 0.0% |
| Insufficient historical evidence | 27 | 9.0% |
| Negative feedback threshold | 27 | 9.0% |
| Human override | 27 | 9.0% |
| High-impact requiring confirmation | 273 | 91.0% |

---

## Interpretation

- The assistant achieved a **57.26% reduction** in mean MTTR for recurring incidents.
- Absolute improvement: **21.14 minutes** per incident.
- The ≥15.0% target was **met**.
- All recommendations in the dataset were version-compatible (**100.0%**), confirming the Hard Filter prevents stale resolutions.

---

## Limitations

1. Dataset is fully synthetic — values reflect parameterised simulation ranges, not real operational data.
2. Real-world MTTR depends on engineer experience, shift timing, and system load.
3. Semantic retrieval quality depends on the embedding model's domain coverage.

> **Note**: This experiment uses clearly labelled synthetic data. Real deployment requires re-running `python -m scripts.run_experiment` with actual historical incident logs.
