# Privacy and Data Sanitization Policy

## 🔒 Privacy-by-Design Overview
The **Verified Resolution Assistant** operates strictly on synthetic clinical IT operational data. In accordance with healthcare data governance and HIPAA Security Rule principles, Patient Health Information (PHI) and Person Identifiable Information (PII) are **never** stored, indexed, or passed to vector search embeddings.

---

## 🛠️ Automated Sanitization Pipeline

Every incoming incident passes through an automated sanitization gate (`backend/sanitization.py`) BEFORE database persistence or vector embedding generation.

```
Incoming Incident Payload
           │
           ▼
[Regex & Pattern Identification]
           │
           ├── Email Redaction (-> [EMAIL_REDACTED])
           ├── Phone Redaction (-> [PHONE_REDACTED])
           ├── MRN Redaction (-> [MRN_REDACTED])
           ├── Patient Name Redaction (-> [PATIENT_REDACTED])
           ├── SSN & DOB Redaction (-> [SSN_REDACTED] / [DOB_REDACTED])
           └── Clinical Diagnosis Free-Text Stripping
           │
           ▼
[Operational Field Allow-List Validation]
           │
           ▼
Database & Vector Embedding Storage
```

---

## 📋 Operational Allow-List Fields

Only technical IT incident metadata required for resolution retrieval is retained:

| Field Name | Type | Description | Privacy Status |
| :--- | :--- | :--- | :--- |
| `incident_id` | String | Unique synthetic incident identifier (e.g. `INC-301`) | **Approved IT Metadata** |
| `system` | String | Target clinical system (e.g. `LabSys`, `PACSView`) | **Approved IT Metadata** |
| `version` | String | Active system software version (e.g. `5.4`) | **Approved IT Metadata** |
| `category` | String | Technical category (e.g. `Application`, `Database`) | **Approved IT Metadata** |
| `severity` | String | Technical severity (`Critical`, `High`, `Medium`, `Low`) | **Approved IT Metadata** |
| `description` | String | Technical symptom description (sanitized) | **Sanitized IT Symptom** |

---

## 🧪 Verification & Automated Test Coverage

The sanitization pipeline is validated by `tests/test_sanitization.py` covering:
- `test_email_redaction()`
- `test_phone_redaction()`
- `test_mrn_redaction()`
- `test_patient_name_redaction()`
- `test_clinical_text_exclusion()`
- `test_operational_fields_preserved()`
