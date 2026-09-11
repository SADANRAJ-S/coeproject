# Verified Resolution Assistant

> **Hospital IT 24/7 Decision-Support System**
> Semantic retrieval of verified, version-compatible, evidence-backed resolutions for recurring clinical IT incidents.

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/SADANRAJ-S/coeproject.git
cd coeproject

# 2. Create virtual environment (Windows)
python -m venv .venv
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the application
python run.py

# 5. Open in browser
# http://localhost:8000
```

---

## Run Tests

```bash
python -m pytest -v
```

Expected: **All tests pass** (26 tests across 5 test files).

---

## Run MTTR Experiment

```bash
python -m scripts.run_experiment
```

Outputs:
- `results/mttr_results.csv`
- `results/mttr_report.json`
- `docs/mttr_experiment.md`

---

## Project Structure

```
coeproject/
  backend/
    main.py                  # FastAPI app entry point
    database.py              # SQLite schema (11 tables)
    sanitization.py          # PHI/PII redaction pipeline
    semantic_retrieval.py    # SentenceTransformer vector embeddings
    retrieval_engine.py      # Multi-stage verification pipeline
    event_engine.py          # Idempotent event processor + audit trail
    seed_data.py             # Synthetic knowledge base seeding
    models.py                # Pydantic request models
    model_artifacts/         # Trained joblib ML classifier
    routers/
      incidents.py           # Incident CRUD + dashboard KPIs
      recommendations.py     # Retrieval + confirmation endpoints
      events.py              # Event injection API
      analytics.py           # MTTR analytics
      ml.py                  # ML training + metrics endpoints
      system.py              # System version management
  dataset/
    generate_dataset.py             # 250-record clean dataset
    generate_recurring_dataset.py   # 300-record recurring MTTR dataset
    hospital_it_incidents_clean.csv
    hospital_it_incidents_recurring.csv
  scripts/
    train_model.py           # ML model training pipeline
    run_experiment.py        # Reproducible MTTR experiment
  tests/
    test_sanitization.py     # PHI/PII redaction tests (6)
    test_events.py           # Event engine reliability tests (9)
    test_retrieval.py        # Semantic retrieval + verification tests (5)
    test_workflow.py         # End-to-end workflow tests (3)
    test_model.py            # ML model training and inference tests (3)
  results/
    mttr_results.csv
    mttr_report.json
  docs/
    architecture.md
    data_schema.md
    risk_register.md
    user_guide.md
    stakeholder_validation.md
    privacy_and_data_sanitization.md
    mttr_experiment.md
    final_evaluation_report.md
  static/js/app.js           # React 18 single-page application
  templates/index.html       # HTML shell (Tailwind + FontAwesome)
  run.py                     # Server launcher
  requirements.txt
```

---

## Key Features

| Feature | Status |
|---------|--------|
| Semantic vector search (sentence-transformers) | Implemented |
| PHI/PII sanitization pipeline | Implemented |
| Hard system + version compatibility filters | Implemented |
| Idempotent event engine (duplicate/OOO/delayed) | Implemented |
| Full state audit trail (event_audit table) | Implemented |
| Human-in-the-loop for HIGH-impact actions | Implemented |
| Override reason logging | Implemented |
| Reproducible MTTR experiment | Implemented |
| 26 automated passing tests | Implemented |

---

## Note on Data

All data is **100% synthetic**. No real patient data, PHI, or hospital operational data is used or stored. The MTTR values are calculated from the synthetic benchmark dataset (`dataset/hospital_it_incidents_recurring.json`) and clearly labelled as `SYNTHETIC_BENCHMARK`.
