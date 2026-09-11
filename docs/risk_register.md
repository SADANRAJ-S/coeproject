# Risk Register — Verified Resolution Assistant

> Last updated: 2026-09-11
> Owner: Hospital IT Operations Team

---

| ID | Risk | Likelihood | Impact | Mitigation | Owner | Status |
|----|------|-----------|--------|-----------|-------|--------|
| R-01 | Wrong recommendation causes engineer to apply incorrect fix | Medium | High | Semantic + version + system hard filters; human confirmation required for HIGH-impact actions; evidence panel shows reasoning | IT Lead | Mitigated |
| R-02 | Outdated resolution recommended (stale knowledge article) | Medium | High | `article.status` filter blocks RETIRED/OUTDATED articles; `last_verified` freshness scoring devalues stale articles | IT Lead | Mitigated |
| R-03 | Version mismatch — fix valid for v5.1 applied to v5.4 system | Medium | High | Hard filter: `version_from <= incident.version <= version_to`; mismatches rejected and shown in Section B | IT Lead | Mitigated |
| R-04 | PHI/PII leakage — patient data enters incident description | Low | Critical | Mandatory sanitization pipeline (email, phone, MRN, name, SSN, diagnosis redacted) before any write or embedding; tested in `test_sanitization.py` | Privacy Lead | Mitigated |
| R-05 | Duplicate event corrupts incident state | Low | Medium | Idempotency registry: `event_id` unique in `events` table; DUPLICATE_IGNORED status returned; state unchanged | Dev Team | Mitigated |
| R-06 | Out-of-order event regresses resolved incident to open | Low | High | Sequence buffer: incoming lifecycle rank compared to current state rank; lower-rank events that would regress state are OUT_OF_ORDER_IGNORED | Dev Team | Mitigated |
| R-07 | Delayed event overwrites current state | Low | Medium | `received_at` vs `event_timestamp` differentiated; delayed events processed only if they advance lifecycle | Dev Team | Mitigated |
| R-08 | False semantic match — unrelated resolution surfaces as top result | Medium | Medium | Cosine similarity threshold ≥0.25 required; system hard filter eliminates cross-system false positives | Dev Team | Mitigated |
| R-09 | High-impact clinical system action auto-executes without confirmation | Low | Critical | HIGH-impact recommendations require `requires_human_confirmation=True`; UI enforces confirmation modal; backend blocks APPROVE if system mismatch | IT Lead | Mitigated |
| R-10 | Embedding model unavailable (no internet / model not downloaded) | Medium | Low | Graceful fallback to TF-IDF cosine similarity if SentenceTransformer fails; no external API dependency | Dev Team | Mitigated |
| R-11 | Data quality problem — seed data incorrectly maps systems | Low | Medium | `seed_data.py` strictly maps incidents to correct system knowledge articles; `test_retrieval.py` TEST 1 catches cross-system mapping errors | Dev Team | Mitigated |
