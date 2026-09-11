# Stakeholder Validation — Verified Resolution Assistant

> **IMPORTANT**: This validation was conducted as a **synthetic prototype walkthrough**.
> No real hospital stakeholders were interviewed. Scenarios and feedback are simulated.
> Label: `SYNTHETIC_PROTOTYPE_VALIDATION`

---

## Validation Design

| Attribute | Value |
|-----------|-------|
| Type | Synthetic prototype walkthrough |
| Participants | 3 simulated role types |
| Scenarios | 4 clinical IT incident scenarios |
| Method | Structured 5-question feedback form |
| Data collected | Role type only — no names, no contact info |

---

## Participant Profiles

| ID | Role | Scenario |
|----|------|---------|
| P-01 | Synthetic: Senior IT Support Engineer | Scenario A — LabSys 5.4 application failure |
| P-02 | Synthetic: IT Manager (Shift Lead) | Scenario B — PACSView system mismatch demo |
| P-03 | Synthetic: IT Quality Assurance Analyst | Scenario C — High-impact confirmation workflow |

---

## Evaluation Scenarios

### Scenario A — Valid Retrieval (LabSys 5.4)
**Task**: Create a LabSys 5.4 incident for "Lab results not loading", retrieve recommendations, review evidence, approve.
**Expected**: KA-014 surfaces as top verified recommendation with ≥80% relevance.

### Scenario B — System Mismatch Demo (PACSView / LabSys)
**Task**: Create a PACSView 4.1 incident, observe that LabSys resolutions appear in SECTION B (BLOCKED).
**Expected**: KA-014 (LabSys) appears in Rejected Candidates with "System mismatch" reason.

### Scenario C — High-Impact Confirmation
**Task**: Approve a HIGH-impact recommendation; verify the confirmation modal appears.
**Expected**: System requires explicit [Approve] click; no auto-execution occurs.

### Scenario D — Override Workflow
**Task**: Reject a recommendation, provide override reason, verify it is stored.
**Expected**: Override reason persists in database; feedback updates recommendation score.

---

## Feedback Results (Synthetic — Prototype Walkthrough)

> All ratings are **simulated responses** based on system design review. Not real user data.

| Question | P-01 (IT Engineer) | P-02 (IT Manager) | P-03 (QA Analyst) | Note |
|---------|------|------|------|------|
| Ease of use (1-5) | 4 | 4 | 3 | Simulated |
| Trust in recommendation (1-5) | 4 | 5 | 4 | Simulated |
| Evidence clarity (1-5) | 5 | 4 | 5 | Simulated |
| Safety of human confirmation (1-5) | 5 | 5 | 5 | Simulated |
| Perceived usefulness (1-5) | 5 | 4 | 4 | Simulated |

### Simulated Comments

- **P-01**: *"The evidence panel showing historical resolved tickets is very useful for building confidence in the fix."*
- **P-02**: *"The system mismatch rejection in Section B clearly explains why LabSys fixes cannot be applied to PACSView incidents."*
- **P-03**: *"Excellent that high-impact actions require explicit approval. This would meet our clinical system change management policy."*

---

## Identified Limitations

1. No real hospital IT engineers or clinical system managers participated.
2. Real validation would require IRB/governance approval and anonymised operational incident logs.
3. Semantic similarity quality is model-dependent; real evaluation requires domain expert review.
4. MTTR values are from synthetic benchmark data, not live hospital operational data.

---

## Recommendations for Real Validation

1. Conduct structured walkthroughs with 5–10 hospital IT support engineers.
2. Use realistic (sanitised) historical incident scenarios from the target hospital.
3. Measure actual time-on-task for recommendation review and approval.
4. Collect feedback via the in-app stakeholder form (anonymous, no PII).
