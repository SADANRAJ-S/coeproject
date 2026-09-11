# Verified Resolution Assistant — Architecture

## System Overview

The **Verified Resolution Assistant** is a full-stack decision-support application for 24/7 hospital IT operations teams. It retrieves, verifies, and presents evidence-backed resolutions for recurring clinical system incidents, requiring explicit human confirmation before any high-impact action.

---

## Component Architecture Diagram

```
+==============================================================================+
|                       BROWSER — React 18 + Tailwind CSS                      |
|  Tabs: Incidents | Recommendations | Evidence | MTTR Analytics |              |
|        Event Simulator | Privacy Governance | Risk Register | User Guide      |
+==============================================================================+
                            |  HTTP REST (FastAPI)
+==============================================================================+
|                     FastAPI Application (backend/main.py)                    |
|  Routers: /api/incidents, /api/retrieval, /api/recommendations,              |
|           /api/events, /api/analytics, /api/system, /api/ml                  |
+==============================================================================+
        |                 |                  |                 |
        v                 v                  v                 v
+---------------+ +------------------+ +-----------+ +------------------+
| Sanitization  | | Semantic Vector  | | Event     | | MTTR Experiment  |
| Layer         | | Retrieval Engine | | Engine    | | Engine           |
| (sanitize     | | (semantic_       | | (event_   | | (scripts/run_    |
|  ation.py)    | |  retrieval.py +  | |  engine.  | |  experiment.py)  |
|               | |  retrieval_      | |  py)      | |                  |
|  - Email      | |  engine.py)      | |           | | - Baseline MTTR  |
|  - Phone      | |                  | | - Idem-   | | - Assisted MTTR  |
|  - MRN        | | - SentenceTrans- | |   potency | | - Error analysis |
|  - Patient    | |   former embed.  | | - OOO     | | - CSV/JSON/MD    |
|    Name       | | - Cosine sim.    | |   safety  | |   reports        |
|  - SSN / DOB  | | - Hard Filters   | | - Audit   | +------------------+
|  - Clinical   | | - 5-part score   | |   trail   |
|    Diagnosis  | +------------------+ +-----------+
+---------------+
                            |
                    +-------+-------+
                    |               |
              +-----+-----+   +-----+------+
              | SQLite3   |   | model_art- |
              | (hospital_|   | ifacts/    |
              |  it.db)   |   | resolution_|
              |           |   | model.job- |
              | Tables:   |   | lib        |
              | - incidents|  +------------+
              | - knowledge|
              |   _articles|
              | - resolved_|
              |   tickets  |
              | - events   |
              | - event_   |
              |   audit    |
              | - feedback |
              | - override_|
              |   logs     |
              | - experiment|
              |   _results  |
              +-----------+
```

---

## Module Descriptions

| Module | Path | Purpose |
|--------|------|---------|
| Sanitization | `backend/sanitization.py` | Detects and redacts PHI/PII (MRN, email, phone, name, SSN, diagnosis) before any database write or embedding |
| Semantic Retrieval | `backend/semantic_retrieval.py` | Dense vector embeddings via `sentence-transformers` (all-MiniLM-L6-v2), cosine similarity computation |
| Retrieval Engine | `backend/retrieval_engine.py` | Multi-stage verification pipeline: sanitize → embed → system hard filter → version filter → freshness → evidence scoring |
| Event Engine | `backend/event_engine.py` | Idempotent event processor: duplicate detection, out-of-order safety, delayed event differentiation, state audit trail |
| Database | `backend/database.py` | SQLite initialization, 11 tables including `event_audit` and `experiment_results` |
| MTTR Experiment | `scripts/run_experiment.py` | Reproducible synthetic benchmark computing real MTTR reduction |
| Seed Data | `backend/seed_data.py` | Synthetic hospital IT incident knowledge base with 10 knowledge articles and 50+ resolved tickets |

---

## Data Flow — Incident Resolution Request

```
1. Engineer enters incident description (system, version, symptom)
   |
2. PHI/PII Sanitization Gate (backend/sanitization.py)
   → Email, Phone, MRN, Patient Name, SSN, Clinical Diagnosis stripped
   |
3. Semantic Vector Embedding (backend/semantic_retrieval.py)
   → SentenceTransformer encodes sanitized description
   → Cosine similarity computed against knowledge article corpus
   |
4. Verification Pipeline (backend/retrieval_engine.py)
   → HARD FILTER: incident.system == resolution.system
   → HARD FILTER: version_from <= incident.version <= version_to
   → HARD FILTER: article.status in [CURRENT, SUPPORTED]
   → SOFT FILTER: semantic_similarity >= 0.25
   → SOFT FILTER: feedback_score >= 0.40
   |
5. 5-Part Transparent Score:
   Score = 0.50 * SemanticSim + 0.20 * VersionCompat
         + 0.15 * SuccessRate + 0.10 * Freshness + 0.05 * Recency
   |
6. Human Review — Evidence Panel displays all 5 score components
   |
7. HIGH-IMPACT ACTION: Human Confirmation Required
   → [Approve] or [Reject + Override Reason]
   |
8. Event Engine logs transition: OPEN → RECOMMENDED → FIX_APPROVED → RESOLVED
   → Full audit trail written to event_audit table
   |
9. TTR calculated: resolved_at - created_at (minutes)
```
