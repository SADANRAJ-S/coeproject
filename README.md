# Verified Resolution Assistant 🏥

> **Evidence-backed resolution retrieval for 24/7 clinical IT support teams.**

The **Verified Resolution Assistant** is a full-stack, evidence-backed decision-support system designed for hospital IT support engineers to solve recurring clinical-system IT incidents faster (e.g. LabSys, PACS, Medication Module, EHR).

---

## 🌟 Key Capabilities & Features

1. **Decision-Support Guardrail**: High-impact recommendations (e.g., service restarts, DB pool flushes) NEVER auto-execute. They display an explicit warning (`⚠️ HIGH-IMPACT ACTION`) and require human approval.
2. **Transparent 5-Part Scoring Engine**:
   $$\text{Relevance Score} = 0.50 \cdot \text{Similarity} + 0.20 \cdot \text{VersionCompat} + 0.15 \cdot \text{SuccessRate} + 0.10 \cdot \text{KnowledgeFreshness} + 0.05 \cdot \text{Recency}$$
3. **Version & Currentness Verification**: Outdated resolutions (e.g., LabSys 5.1 fixes when running LabSys 5.4) are automatically detected and flagged:
   `⚠️ Outdated Resolution — Not Recommended: This resolution was validated only for version 5.1. Current system version is 5.4.`
4. **Evidence Panel**: Provides transparent breakdown of passed rules, historical ticket resolution times, knowledge article verification dates, and scoring math.
5. **Override Reason Logging**: When an engineer rejects a recommendation, an interactive modal captures structured override reasons (e.g., Version mismatch, Fix already attempted) for machine learning feedback.
6. **Incident Lifecycle & Dynamic TTR**: Tracks complete timeline: `Created → Retrieved → Recommended → Approved → Applied → Resolved`, dynamically computing Time to Resolution (TTR).
7. **Event Reliability Engine**: Idempotent event consumer handling duplicate, delayed, and out-of-order network events without state corruption.
8. **Privacy-by-Design**: Operates strictly on synthetic IT operational metadata. Zero patient health information (PHI) or personal data is collected or stored.

---

## 🏗️ System Architecture

```
+-------------------------------------------------------------------------------+
|                       React + Tailwind CSS Frontend                           |
|  - Enterprise Hospital IT Console & 10-Section Navigation Sidebar             |
|  - Incident Entry Wizard & Preset Mandatory Scenario Trigger                  |
|  - Candidate Resolutions List, Compatibility Badges, & Evidence Modal         |
|  - High-Impact Action Safety Confirmation & Override Reason Capture Modal      |
|  - Incident Timeline, TTR Analytics, & Experiment Benchmarks                  |
|  - Interactive Event Reliability Fault Injector (Duplicate/Delayed/OOO)        |
|  - Risk Register, Stakeholder Validation, & IT Engineer User Guide            |
+-------------------------------------------------------------------------------+
                                      | REST API (JSON)
                                      v
+-------------------------------------------------------------------------------+
|                             FastAPI Backend (Python 3.13)                      |
|  - Retrieval Engine (TF-IDF + Cosine / Jaccard + Multi-Factor Scoring)         |
|  - Version Matcher & Outdated Fix Filter Guard                                |
|  - Idempotent Event Stream Engine & Sequence Buffer                           |
|  - SQLite Database Connection Handler & Seed Data Generator                   |
+-------------------------------------------------------------------------------+
                                      | SQLite3
                                      v
+-------------------------------------------------------------------------------+
|                             SQLite Database (hospital_it.db)                 |
|  Tables: incidents, resolved_tickets, knowledge_articles, feedback,           |
|          system_versions, events, risk_register, stakeholder_feedback          |
+-------------------------------------------------------------------------------+
```

---

## 🚀 Quickstart & Setup Guide

### Prerequisites
- Python 3.10+ (Tested on Python 3.13.7)
- Standard web browser (Chrome, Edge, Firefox)

### 1. Clone & Navigate to Repository
```bash
cd "c:\New folder\coe project"
```

### 2. Run the Application
Start the FastAPI server and seed the SQLite database automatically:
```bash
python run.py
```
*Outputs:*
```text
======================================================================
 Verified Resolution Assistant - 24/7 Hospital IT Support Team
======================================================================
[+] Database verified at: hospital_it.db
[+] Starting FastAPI server on http://127.0.0.1:8000 ...
======================================================================
```

Open your browser and navigate to:
👉 **`http://localhost:8000`**

---

## 🧪 Automated Testing

Execute the complete unit and integration test suite using `pytest`:
```bash
python -m pytest -v
```

### Included Automated Test Coverage:
- `tests/test_retrieval.py`: Retrieval scoring formula, version range matching, and outdated fix rejection (LabSys 5.1 vs 5.4).
- `tests/test_events.py`: Idempotent duplicate event rejection, delayed event handling, and out-of-order event sequence buffer.
- `tests/test_workflow.py`: End-to-end incident creation, high-impact confirmation flow, override logging, and dynamic TTR computation.

---

## 📋 Mandatory Demo Scenario Walkthrough (Section 23)

To test the core workflow specified in Section 23 of the requirements:

1. Click **Run Mandatory Demo (LabSys 5.4)** in the top navigation bar or go to **New Incident** and select **LabSys 5.4 (Mandatory Demo)**.
2. Form Parameters:
   - Incident Description: `"Lab results are not loading for users."`
   - System: `LabSys`
   - Version: `5.4`
3. Click **Find Verified Resolution**.
4. Observe Results:
   - Candidate #1: **Restart LabSys Application Service** (`KA-014`) retrieved with ~92% relevance score. Badged as `✓ Current & Compatible`. Marked as **HIGH IMPACT** requiring human confirmation.
   - Candidate #2: **Legacy LabSys 5.1 Cache Reset** (`KA-003`) retrieved but flagged with `⚠️ Outdated Resolution — Not Recommended: This resolution was validated only for version 5.1. Current system version is 5.4.`
5. Click **View Evidence** on Candidate #1 to inspect the rules passed, historical ticket logs (`INC-102`, `INC-145`, `INC-178`, `INC-221`), knowledge article details, and scoring math.
6. Click **Approve Fix** to execute human confirmation. Observe state transition to `RESOLVED` and calculated Time to Resolution (18 minutes).

---

## 🛡️ Event Reliability Simulator (Section 14)

Navigate to the **Event Reliability Demo** sidebar item:
- **Inject Duplicate Event**: Sends event `EVT-103-DUP` twice. The idempotent processor safely ignores the duplicate (`DUPLICATE_IGNORED`) without corrupting incident state.
- **Inject Delayed Event**: Sends a historical event arriving late. Processed safely (`DELAYED_EVENT_PROCESSED`).
- **Inject Out-of-Order Event**: Sends `FIX_APPLIED` before `FIX_APPROVED`. Sequence buffer aligns event (`OUT_OF_ORDER_BUFFERED`).

---

## 📊 Analytics & Experiment Benchmarks

- **Baseline TTR**: 42.0 minutes (Manual historical lookup)
- **Target TTR**: 30.0 minutes
- **Measured Prototype TTR**: ~18.0 - 27.0 minutes
- **Dynamic TTR Improvement**: **+35.7%**
- Includes Top-1 (88.5%), Top-3 (96.0%), and Current-Version (99.2%) retrieval accuracy metrics and Error Analysis table.

---

## 🔒 Privacy-by-Design Compliance Statement

> **"No patient or unnecessary personal data is collected by this prototype."**
> 
> This application uses strictly synthetic clinical IT operational data (systems, versions, error messages, KB articles, and resolution steps). Zero Patient Health Information (PHI) or Personally Identifiable Information (PII) is processed or stored.
