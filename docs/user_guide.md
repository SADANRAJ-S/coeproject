# User Guide — Verified Resolution Assistant
# For: Hospital IT Support Engineers (24/7 Operations)

---

## Overview

The **Verified Resolution Assistant** helps hospital IT engineers resolve recurring clinical system incidents faster by retrieving relevant, version-compatible, evidence-backed resolutions and requiring explicit human approval before high-impact actions.

**This is a decision-support system.** It does not automatically execute fixes.

---

## Step-by-Step: Resolving an Incident

### Step 1 — Create Incident

1. Open the application at `http://localhost:8000`.
2. Click **New Incident** in the navigation.
3. Enter:
   - **System**: Which clinical system is affected (e.g. LabSys, PACSView, MedFlow).
   - **Version**: The active software version (e.g. 5.4).
   - **Category**: Application / Database / Authentication / Infrastructure.
   - **Severity**: Critical / High / Medium / Low.
   - **Description**: Describe the technical symptom (no patient names or MRNs needed).
4. Click **Create Incident**.

> **Note**: The system automatically redacts any accidental PHI/PII from the description before saving.

---

### Step 2 — Enter Technical Symptoms

Describe what you observe technically:

- **Good**: "Lab result viewer displays infinite spinner on floor 3 ICU workstation."
- **Avoid**: "Patient John Smith MRN 12345 cannot see their results." (PHI — will be auto-redacted)

---

### Step 3 — Sanitization (Automatic)

The system silently scans the description and removes:
- Patient names, MRN numbers, email addresses, phone numbers, SSNs, date-of-birth.
- Clinical diagnosis phrases.

You will see the sanitized description on screen before submission.

---

### Step 4 — Search Verified Resolutions

1. With the incident open, click **Find Verified Resolutions**.
2. The system runs the full retrieval pipeline:
   - Semantic vector similarity search.
   - System compatibility check.
   - Version compatibility check.
   - Knowledge article freshness check.
   - Historical success rate calculation.
3. Results display in two sections:
   - **SECTION A — VERIFIED RECOMMENDATIONS**: Passes all checks. Shows score breakdown.
   - **SECTION B — REJECTED CANDIDATES**: Failed one or more checks, with exact reason.

---

### Step 5 — Review Evidence

Click **View Evidence** on any Verified Recommendation to see:

- Semantic Similarity score (0–100%).
- System compatibility status.
- Version compatibility range.
- Historical Success Rate (% of past incidents resolved with this fix).
- Knowledge Article Freshness (days since last verification).
- Resolution Recency score.
- Feedback Score (average engineer acceptance rate).
- Step-by-step resolution procedure.
- List of similar historical resolved tickets (ticket ID, resolved in N minutes).
- All verification rules passed (R1–R5).

---

### Step 6 — Check Compatibility

The evidence panel explicitly shows:
- Whether the resolution applies to your current system version.
- The valid version range for this resolution.
- Whether the knowledge article is current or retired.

If a resolution is shown in **SECTION B**, it must NOT be applied — it failed a hard filter.

---

### Step 7 — Confirm High-Impact Action

If the recommended resolution has `impact_level = HIGH`, the system will:
1. Display a **HIGH-IMPACT ACTION — Human Approval Required** banner.
2. Show the specific steps that are high-risk (e.g. "Restart LabSys Application Service").
3. Require you to click **Approve** or **Reject / Override**.

**Never approve a high-impact action without reading the steps carefully.**

---

### Step 8 — Apply Fix

After approval:
1. The system records your approval decision in the `feedback` table.
2. The event engine logs the `FIX_APPROVED` → `FIX_APPLIED` → `INCIDENT_RESOLVED` state transitions.
3. Apply the fix to the actual clinical system following the steps shown.

---

### Step 9 — Record Outcome

1. Return to the application and confirm whether the fix worked.
2. If successful: incident is marked **RESOLVED** with TTR calculated automatically.
3. If unsuccessful: click **Reject / Override**, select a reason, and re-search for an alternative.

---

### Step 10 — Review MTTR Analytics

Visit the **MTTR Analytics** tab to see:
- Your team's average Time-to-Resolution.
- Comparison to the baseline (manual search) process.
- Percentage improvement from assistant-aided workflow.

---

### Step 11 — Provide Feedback

After resolution, rate the recommendation:
- Was the suggested fix correct?
- Was the evidence clear?
- Did the confirmation workflow feel safe?

Feedback updates the recommendation scoring for future incidents.

---

## Quick Reference

| Action | Navigation |
|--------|-----------|
| Create incident | New Incident tab |
| Find recommendations | Incident → Find Verified Resolutions |
| View evidence | Recommendation → View Evidence |
| Approve/Reject action | Recommendation → Approve / Reject |
| View MTTR analytics | MTTR Analytics tab |
| Inject event (testing) | Event Reliability Simulator tab |
| Review data privacy | Privacy Governance tab |
| View risks | Risk Register tab |

---

## Important Safety Rules

1. **Never approve a high-impact action without reading the steps.**
2. **Never use SECTION B rejected candidates as resolutions.**
3. **Never enter patient names or MRNs** in the description — the system sanitizes but description accuracy matters.
4. **Always record override reasons** — this improves future recommendations.
5. **Contact the senior IT lead** if no valid recommendation exists (all candidates blocked).
