import sqlite3
import datetime
from backend.database import get_db_connection, init_db

def seed_database():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear existing data
    tables = [
        "incidents", "resolved_tickets", "knowledge_articles", "feedback",
        "system_versions", "events", "risk_register", "stakeholder_feedback"
    ]
    for table in tables:
        cursor.execute(f"DELETE FROM {table}")

    # 1. Seed System Versions
    system_versions = [
        ("LabSys", "5.4", "CURRENT", "2025-06-01"),
        ("LabSys", "5.1", "DEPRECATED", "2023-01-15"),
        ("MedFlow", "3.2", "CURRENT", "2025-09-10"),
        ("PACSView", "4.1", "CURRENT", "2025-04-20"),
        ("EHRCore", "6.0", "CURRENT", "2025-11-01"),
        ("AuthGuard", "2.8", "CURRENT", "2025-02-14"),
        ("PrintManager", "1.4", "CURRENT", "2024-10-05"),
        ("HL7Router", "3.5", "CURRENT", "2025-07-22")
    ]
    cursor.executemany(
        "INSERT INTO system_versions (system, version, status, release_date) VALUES (?, ?, ?, ?)",
        system_versions
    )

    # 2. Seed Knowledge Articles
    knowledge_articles = [
        (
            "KA-014",
            "Restart LabSys Application Service",
            "Recycles the primary application service pool and flushes stale HL7 result listeners. Recommended when lab result viewer displays spinner or fails to render results.",
            "LabSys", "5.0", "5.5", "CURRENT", "2026-08-20",
            "1. Access LabSys Application Server control node.\n2. Issue service stop: 'systemctl stop labsys-app'.\n3. Flush web session cache.\n4. Issue service start: 'systemctl start labsys-app'.\n5. Verify HL7 result queue health indicator is green.",
            "HIGH"
        ),
        (
            "KA-003",
            "Legacy LabSys 5.1 Cache Reset",
            "Clears legacy local file cache for LabSys version 5.1. Warning: This method is deprecated and incompatible with LabSys 5.4 architecture due to monolithic storage change.",
            "LabSys", "5.1", "5.1", "RETIRED", "2024-03-15",
            "1. Run clear_legacy_cache.sh on LabSys 5.1 client stations.\n2. Restart local station service.",
            "LOW"
        ),
        (
            "KA-022",
            "LabSys Database Connection Pool Recycle",
            "Resets database connection pool for LabSys when queries exceed 15 second threshold.",
            "LabSys", "5.0", "5.5", "CURRENT", "2026-07-10",
            "1. Open LabSys DB Console.\n2. Execute pool reset.\n3. Validate connection count.",
            "MEDIUM"
        ),
        (
            "KA-008",
            "MedFlow Order Queue Clear & Process Recycle",
            "Recycles pharmacy order queue listener when electronic medication administration record (eMAR) experiences submission timeouts.",
            "MedFlow", "3.0", "3.5", "CURRENT", "2026-08-01",
            "1. Access MedFlow cluster controller.\n2. Reset pharmacy queue daemon.\n3. Verify pending medication orders.",
            "HIGH"
        ),
        (
            "KA-019",
            "PACS Image Cache Purge & DICOM Router Cycle",
            "Purges workstation DICOM buffer and restarts image streaming router when radiologic images buffer slowly in PACSView.",
            "PACSView", "4.0", "4.5", "CURRENT", "2026-08-15",
            "1. Flush PACS local disk cache.\n2. Cycle DICOM streaming gateway.\n3. Test image loading speed.",
            "LOW"
        ),
        (
            "KA-021",
            "PACSView DICOM Gateway Service Restart",
            "Restarts the primary DICOM gateway daemon for PACSView 4.1 when image loading is delayed or hanging.",
            "PACSView", "4.0", "4.5", "CURRENT", "2026-08-18",
            "1. Log into PACS Gateway Node.\n2. Restart service 'pacs-dicom-gw'.\n3. Verify CT/MRI image streaming throughput.",
            "HIGH"
        ),
        (
            "KA-005",
            "EHR Core UI Thread Recycling",
            "Clears client session deadlock on patient registration screens without requiring full workstation reboot.",
            "EHRCore", "5.8", "6.2", "CURRENT", "2026-08-22",
            "1. Terminate hung EHR UI worker process.\n2. Refresh patient registration session token.",
            "LOW"
        ),
        (
            "KA-012",
            "AuthGuard LDAP Gateway Synchronizer Reset",
            "Resets clinical Single Sign-On (SSO) authentication gateway when domain controllers experience sync delay.",
            "AuthGuard", "2.5", "3.0", "CURRENT", "2026-08-18",
            "1. Re-sync AuthGuard LDAP node.\n2. Restart SSO token validator.",
            "HIGH"
        ),
        (
            "KA-031",
            "HL7 Router Queue Purge & Resend",
            "Flushes stuck HL7 ORU_R01 lab message queues and triggers automatic retry handler.",
            "HL7Router", "3.0", "4.0", "CURRENT", "2026-08-25",
            "1. Pause HL7 ingress port.\n2. Re-index pending queue items.\n3. Resume ingress router.",
            "HIGH"
        ),
        (
            "KA-002",
            "Print Spooler Service Restart",
            "Restarts local print spooler service for nursing station thermal lab wristband and chart printers.",
            "PrintManager", "1.0", "2.0", "CURRENT", "2026-06-30",
            "1. Issue spooler restart: 'net stop spooler && net start spooler'.\n2. Clear print job queue.",
            "LOW"
        )
    ]
    cursor.executemany("""
        INSERT INTO knowledge_articles 
        (article_id, title, content, system, version_from, version_to, status, last_verified, steps, risk_level)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, knowledge_articles)

    # 3. Seed Resolved Tickets (Historical Dataset)
    resolved_tickets = [
        ("INC-102", "Lab results not loading on ICU floor 2", "LabSys", "5.4", "Restarted LabSys Application Service per KA-014", 1, 15.0, "2026-08-01 10:15", "KA-014", "HIGH"),
        ("INC-145", "Lab result viewer timeout for STAT blood work", "LabSys", "5.4", "Restarted LabSys service pool", 1, 18.0, "2026-08-05 14:22", "KA-014", "HIGH"),
        ("INC-178", "Lab results blank for emergency department", "LabSys", "5.4", "Executed KA-014 service recycling", 1, 17.0, "2026-08-12 08:45", "KA-014", "HIGH"),
        ("INC-221", "Lab results hanging on submit in outpatient lab", "LabSys", "5.4", "Restarted LabSys application service", 1, 19.0, "2026-08-19 16:10", "KA-014", "HIGH"),
        ("INC-088", "Lab result screen not opening in LabSys 5.1", "LabSys", "5.1", "Ran legacy cache reset script", 1, 35.0, "2024-02-10 11:30", "KA-003", "LOW"),
        ("INC-110", "Medication module order entry timeout", "MedFlow", "3.2", "Recycled pharmacy order queue per KA-008", 1, 22.0, "2026-08-03 09:12", "KA-008", "HIGH"),
        ("INC-134", "PACS CT scan images loading slowly", "PACSView", "4.1", "Purged DICOM cache per KA-019", 1, 14.0, "2026-08-08 15:30", "KA-019", "LOW"),
        ("INC-156", "Patient registration screen freezing", "EHRCore", "6.0", "Recycled UI worker thread per KA-005", 1, 12.0, "2026-08-11 13:05", "KA-005", "LOW"),
        ("INC-190", "Clinical app login failure SSO error", "AuthGuard", "2.8", "Resynced LDAP gateway per KA-012", 1, 25.0, "2026-08-14 17:40", "KA-012", "HIGH"),
        ("INC-205", "HL7 lab message queue delayed", "HL7Router", "3.5", "Flushed queue and restarted router per KA-031", 1, 21.0, "2026-08-18 20:15", "KA-031", "HIGH"),
        ("INC-230", "Nursing station printer offline", "PrintManager", "1.4", "Cycled print spooler service per KA-002", 1, 8.0, "2026-08-21 07:50", "KA-002", "LOW")
    ]
    cursor.executemany("""
        INSERT INTO resolved_tickets
        (ticket_id, incident_summary, system, version, resolution, successful, resolution_time_minutes, resolved_at, knowledge_article_id, impact_level)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, resolved_tickets)

    # 4. Seed Current Incidents (Logically Correct Mappings)
    incidents = [
        ("INC-301", "Lab results are not loading for users.", "Application", "LabSys", "5.4", "High", "HIGH", "2026-09-03 08:30", "2026-09-03 08:48", "KA-014", "RESOLVED", 18.0),
        ("INC-302", "Medication module order entry timeout during shift change", "Application", "MedFlow", "3.2", "High", "HIGH", "2026-09-03 09:15", "2026-09-03 09:37", "KA-008", "RESOLVED", 22.0),
        ("INC-303", "PACS image loading slow in ER radiology station", "Performance", "PACSView", "4.1", "Medium", "LOW", "2026-09-03 10:00", "2026-09-03 10:14", "KA-019", "RESOLVED", 14.0),
        ("INC-304", "Patient registration screen freezing during intake", "UI/Application", "EHRCore", "6.0", "Medium", "LOW", "2026-09-03 11:20", "2026-09-03 11:32", "KA-005", "RESOLVED", 12.0),
        ("INC-305", "Clinical application login failure (SSO auth error)", "Authentication", "AuthGuard", "2.8", "High", "HIGH", "2026-09-03 12:45", "2026-09-03 13:10", "KA-012", "RESOLVED", 25.0),
        ("INC-306", "Interface message queue delayed (HL7 lab feed)", "Integration", "HL7Router", "3.5", "High", "HIGH", "2026-09-03 14:10", None, None, "PENDING_APPROVAL", None),
        ("INC-307", "Printer unavailable in 4th floor nursing station", "Infrastructure", "PrintManager", "1.4", "Low", "LOW", "2026-09-03 15:00", "2026-09-03 15:08", "KA-002", "RESOLVED", 8.0),
        ("INC-308", "EHR database connection pool timeout", "Database", "EHRCore", "6.0", "Critical", "HIGH", "2026-09-03 16:30", None, None, "OPEN", None),
        ("INC-309", "PACS image loading slow in outpatient clinic", "Performance", "PACSView", "4.1", "Medium", "LOW", "2026-09-03 17:00", None, "KA-019", "RECOMMENDED", None)
    ]
    cursor.executemany("""
        INSERT INTO incidents
        (incident_id, description, category, system, version, severity, impact_level, created_at, resolved_at, resolution_id, status, ttr_minutes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, incidents)

    # 5. Seed Events for Incidents
    events = [
        ("EVT-301-1", "INC-301", "INCIDENT_CREATED", "2026-09-03 08:30", 1, "2026-09-03 08:30:05", "PROCESSED", "Incident created by IT engineer"),
        ("EVT-301-2", "INC-301", "RECOMMENDATION_GENERATED", "2026-09-03 08:31", 2, "2026-09-03 08:31:02", "PROCESSED", "KA-014 retrieved with 92% confidence"),
        ("EVT-301-3", "INC-301", "FIX_APPROVED", "2026-09-03 08:33", 3, "2026-09-03 08:33:15", "PROCESSED", "Approved by human engineer"),
        ("EVT-301-4", "INC-301", "FIX_APPLIED", "2026-09-03 08:35", 4, "2026-09-03 08:35:40", "PROCESSED", "LabSys service restarted successfully"),
        ("EVT-301-5", "INC-301", "INCIDENT_RESOLVED", "2026-09-03 08:48", 5, "2026-09-03 08:48:00", "PROCESSED", "Incident resolved in 18 min")
    ]
    cursor.executemany("""
        INSERT INTO events
        (event_id, incident_id, event_type, event_timestamp, sequence_number, processed_at, status, details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, events)

    # 6. Seed Risk Register
    risks = [
        ("Outdated fix recommendation", "High", "Medium", "System/version compatibility filter blocks non-matching versions.", "ACTIVE"),
        ("Wrong similar incident retrieved", "Medium", "Low", "Multi-feature score combining TF-IDF, system match & historical outcome.", "ACTIVE"),
        ("High-impact action executed without confirmation", "Critical", "Low", "Mandatory human confirmation workflow; auto-execution strictly prohibited.", "ACTIVE"),
        ("Duplicate events received in stream", "Medium", "Medium", "Idempotent event consumer using unique event_id deduplication.", "ACTIVE"),
        ("Delayed events received out of order", "Low", "Medium", "Timestamp validation and state machine transition sequence buffer.", "ACTIVE"),
        ("Out-of-order event sequence execution", "Medium", "Low", "Event sequence numbering enforces logical lifecycle state transitions.", "ACTIVE"),
        ("Privacy and data exposure risk", "High", "Low", "Privacy-by-design; strictly synthetic IT operational data without PHI.", "ACTIVE"),
        ("Incorrect system-version mapping", "Medium", "Low", "Enforced master schema for system releases and version compatibility bounds.", "ACTIVE"),
        ("Low retrieval accuracy for novel incidents", "High", "Low", "Transparent score breakdown and fallback manual KB search link.", "ACTIVE")
    ]
    cursor.executemany("""
        INSERT INTO risk_register (risk, impact, likelihood, mitigation, status)
        VALUES (?, ?, ?, ?, ?)
    """, risks)

    # 7. Seed Stakeholder Validation Feedback
    stakeholder_qs = [
        ("Was the recommendation understandable?", 5, "Clear confidence score and title made action obvious.", "Hospital IT Support Lead"),
        ("Was the evidence sufficient?", 5, "Showing historical ticket links and rules passed gave full confidence.", "Lead Clinical Systems Analyst"),
        ("Did the tool reduce search effort?", 5, "Estimated search time reduced from 20 minutes to under 2 minutes.", "Senior IT Operations Manager"),
        ("Was version validation useful?", 5, "Crucial feature—prevented applying a legacy LabSys 5.1 script on our 5.4 cluster.", "Systems Infrastructure Specialist"),
        ("Was human confirmation appropriate?", 5, "High-impact confirmation prevents accidental downtime of critical lab feeds.", "Hospital IT Director")
    ]
    cursor.executemany("""
        INSERT INTO stakeholder_feedback (question, rating, comment, stakeholder_role)
        VALUES (?, ?, ?, ?)
    """, stakeholder_qs)

    conn.commit()
    conn.close()
    print("Database successfully seeded with realistic synthetic hospital IT data!")

if __name__ == "__main__":
    seed_database()
