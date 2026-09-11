# Data Schema — Verified Resolution Assistant

All tables use SQLite3. Privacy classification: **Operational IT Metadata only**.

---

## Table 1: `incidents`

| Field | Type | Required | Purpose | Privacy |
|-------|------|----------|---------|---------|
| `incident_id` | TEXT PK | Yes | Unique synthetic ID (e.g. INC-301) | Operational |
| `description` | TEXT | Yes | Sanitized technical symptom | Operational (Sanitized) |
| `category` | TEXT | Yes | Technical category | Operational |
| `system` | TEXT | Yes | Clinical IT system name | Operational |
| `version` | TEXT | Yes | System software version | Operational |
| `severity` | TEXT | Yes | Critical/High/Medium/Low | Operational |
| `impact_level` | TEXT | Yes | HIGH/LOW | Operational |
| `created_at` | TEXT | Yes | ISO timestamp of creation | Operational |
| `resolved_at` | TEXT | No | ISO timestamp of resolution | Operational |
| `resolution_id` | TEXT | No | Applied knowledge article ID | Operational |
| `status` | TEXT | Yes | OPEN/RECOMMENDED/RESOLVED etc. | Operational |
| `ttr_minutes` | REAL | No | Time-to-Resolution in minutes | Operational |

---

## Table 2: `resolved_tickets`

| Field | Type | Required | Purpose | Privacy |
|-------|------|----------|---------|---------|
| `ticket_id` | TEXT PK | Yes | Unique historical ticket ID | Operational |
| `incident_summary` | TEXT | Yes | Sanitized incident description | Operational (Sanitized) |
| `system` | TEXT | Yes | Clinical system | Operational |
| `version` | TEXT | Yes | System version | Operational |
| `resolution` | TEXT | Yes | Applied resolution description | Operational |
| `successful` | INTEGER | Yes | 1=success, 0=failure | Operational |
| `resolution_time_minutes` | REAL | Yes | Minutes to resolve | Operational |
| `resolved_at` | TEXT | Yes | ISO resolution timestamp | Operational |
| `knowledge_article_id` | TEXT | No | Linked knowledge article | Operational |
| `impact_level` | TEXT | Yes | HIGH/LOW | Operational |

---

## Table 3: `knowledge_articles`

| Field | Type | Required | Purpose | Privacy |
|-------|------|----------|---------|---------|
| `article_id` | TEXT PK | Yes | Knowledge article ID (e.g. KA-014) | Operational |
| `title` | TEXT | Yes | Article title | Operational |
| `content` | TEXT | Yes | Resolution description | Operational |
| `system` | TEXT | Yes | Applicable clinical system | Operational |
| `version_from` | TEXT | Yes | Minimum compatible version | Operational |
| `version_to` | TEXT | Yes | Maximum compatible version | Operational |
| `status` | TEXT | Yes | CURRENT/RETIRED/OUTDATED | Operational |
| `last_verified` | TEXT | Yes | ISO date last validated | Operational |
| `steps` | TEXT | No | Step-by-step resolution procedure | Operational |
| `risk_level` | TEXT | Yes | HIGH/LOW — triggers human approval | Operational |

---

## Table 4: `feedback`

| Field | Type | Required | Purpose | Privacy |
|-------|------|----------|---------|---------|
| `feedback_id` | TEXT PK | Yes | Unique feedback record ID | Operational |
| `incident_id` | TEXT | Yes | Related incident | Operational |
| `recommendation_id` | TEXT | Yes | Knowledge article used | Operational |
| `accepted` | INTEGER | Yes | 1=accepted, 0=rejected | Operational |
| `successful` | INTEGER | Yes | 1=fix worked | Operational |
| `override_reason` | TEXT | No | Reason for rejection | Operational |
| `comment` | TEXT | No | Optional engineer note | Operational |
| `created_at` | TEXT | Yes | ISO timestamp | Operational |

---

## Table 5: `events`

| Field | Type | Required | Purpose | Privacy |
|-------|------|----------|---------|---------|
| `event_id` | TEXT PK | Yes | Unique event ID (idempotency key) | Operational |
| `incident_id` | TEXT | Yes | Parent incident | Operational |
| `event_type` | TEXT | Yes | INCIDENT_CREATED/RECOMMENDATION_GENERATED/etc. | Operational |
| `event_timestamp` | TEXT | Yes | When event occurred (ISO) | Operational |
| `sequence_number` | INTEGER | Yes | Deterministic ordering key | Operational |
| `payload` | TEXT | No | Optional event payload JSON | Operational |
| `received_at` | TEXT | Yes | When event arrived at engine | Operational |
| `processed_at` | TEXT | Yes | When event was processed | Operational |
| `status` | TEXT | Yes | PROCESSED/DUPLICATE_IGNORED/OUT_OF_ORDER_IGNORED | Operational |
| `details` | TEXT | No | Human-readable description | Operational |

---

## Table 6: `event_audit`

Full state transition audit trail — every processing decision recorded.

| Field | Type | Required | Purpose | Privacy |
|-------|------|----------|---------|---------|
| `audit_id` | INTEGER PK | Yes | Auto-increment audit record | Operational |
| `event_id` | TEXT | Yes | Associated event | Operational |
| `incident_id` | TEXT | Yes | Associated incident | Operational |
| `previous_state` | TEXT | Yes | State before this event | Operational |
| `new_state` | TEXT | Yes | State after this event | Operational |
| `event_type` | TEXT | Yes | Event type | Operational |
| `event_timestamp` | TEXT | Yes | Event time | Operational |
| `received_at` | TEXT | Yes | Arrival time at engine | Operational |
| `processing_status` | TEXT | Yes | PROCESSED/DUPLICATE_IGNORED etc. | Operational |
| `reason` | TEXT | No | Human-readable processing reason | Operational |
| `recorded_at` | TEXT | Yes | When audit record was written | Operational |

---

## Table 7: `override_logs`

| Field | Type | Required | Purpose | Privacy |
|-------|------|----------|---------|---------|
| `override_id` | TEXT PK | Yes | Unique override record | Operational |
| `incident_id` | TEXT | Yes | Parent incident | Operational |
| `recommendation_id` | TEXT | Yes | Rejected recommendation | Operational |
| `decision` | TEXT | Yes | APPROVE/REJECT | Operational |
| `override_reason` | TEXT | No | Engineer's stated reason | Operational |
| `override_comment` | TEXT | No | Additional notes | Operational |
| `operator_id` | TEXT | No | Anonymous operator reference | Operational |
| `timestamp` | TEXT | Yes | ISO decision timestamp | Operational |

---

## Table 8: `experiment_results`

| Field | Type | Required | Purpose | Privacy |
|-------|------|----------|---------|---------|
| `result_id` | INTEGER PK | Yes | Auto-increment | Operational |
| `experiment_name` | TEXT | Yes | Experiment identifier | Operational |
| `metric_name` | TEXT | Yes | Metric label | Operational |
| `baseline_value` | REAL | No | Baseline measurement | Operational |
| `target_value` | REAL | No | Target threshold | Operational |
| `measured_value` | REAL | No | Actual measurement | Operational |
| `unit` | TEXT | No | minutes / % / count | Operational |
| `dataset_label` | TEXT | Yes | SYNTHETIC_BENCHMARK | Operational |
| `recorded_at` | TEXT | Yes | ISO timestamp | Operational |

---

## Table 9: `stakeholder_feedback`

Anonymous prototype walkthrough ratings (no PII collected).

| Field | Type | Required | Purpose | Privacy |
|-------|------|----------|---------|---------|
| `feedback_id` | INTEGER PK | Yes | Auto-increment | Operational |
| `question` | TEXT | Yes | Evaluation question | Operational |
| `rating` | INTEGER | Yes | 1-5 Likert scale | Operational |
| `comment` | TEXT | Yes | Optional text feedback | Operational |
| `stakeholder_role` | TEXT | Yes | Role type only (no name) | Operational |
| `recorded_at` | TEXT | No | ISO timestamp | Operational |

---

> **Privacy Classification Note**: No PHI, PII, patient identifiers, MRNs, patient names, clinical diagnoses, or medical record data are stored in any table. All `description` and `incident_summary` fields are passed through the sanitization pipeline before persistence.
