import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "hospital_it.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Drop and recreate all tables to enforce latest schema
    tables_to_drop = [
        "event_audit", "override_logs", "experiment_results",
        "stakeholder_feedback", "risk_register", "feedback",
        "events", "system_versions", "resolved_tickets",
        "knowledge_articles", "incidents"
    ]
    for tbl in tables_to_drop:
        cursor.execute(f"DROP TABLE IF EXISTS {tbl}")

    # Table 1: incidents
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS incidents (
        incident_id TEXT PRIMARY KEY,
        description TEXT NOT NULL,
        category TEXT NOT NULL,
        system TEXT NOT NULL,
        version TEXT NOT NULL,
        severity TEXT NOT NULL,
        impact_level TEXT NOT NULL,
        created_at TEXT NOT NULL,
        resolved_at TEXT,
        resolution_id TEXT,
        status TEXT NOT NULL,
        ttr_minutes REAL
    );
    """)

    # Table 2: resolved_tickets
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resolved_tickets (
        ticket_id TEXT PRIMARY KEY,
        incident_summary TEXT NOT NULL,
        system TEXT NOT NULL,
        version TEXT NOT NULL,
        resolution TEXT NOT NULL,
        successful INTEGER NOT NULL,
        resolution_time_minutes REAL NOT NULL,
        resolved_at TEXT NOT NULL,
        knowledge_article_id TEXT,
        impact_level TEXT NOT NULL DEFAULT 'LOW'
    );
    """)

    # Table 3: knowledge_articles
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS knowledge_articles (
        article_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        system TEXT NOT NULL,
        version_from TEXT NOT NULL,
        version_to TEXT NOT NULL,
        status TEXT NOT NULL,
        last_verified TEXT NOT NULL,
        steps TEXT,
        risk_level TEXT NOT NULL DEFAULT 'LOW'
    );
    """)

    # Table 4: feedback
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        feedback_id TEXT PRIMARY KEY,
        incident_id TEXT NOT NULL,
        recommendation_id TEXT NOT NULL,
        accepted INTEGER NOT NULL,
        successful INTEGER NOT NULL,
        override_reason TEXT,
        comment TEXT,
        created_at TEXT NOT NULL
    );
    """)

    # Table 5: system_versions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_versions (
        system TEXT NOT NULL,
        version TEXT NOT NULL,
        status TEXT NOT NULL,
        release_date TEXT NOT NULL,
        PRIMARY KEY (system, version)
    );
    """)

    # Table 6: events (enhanced with payload and received_at)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        event_id TEXT PRIMARY KEY,
        incident_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        event_timestamp TEXT NOT NULL,
        sequence_number INTEGER NOT NULL,
        payload TEXT,
        received_at TEXT NOT NULL,
        processed_at TEXT NOT NULL,
        status TEXT NOT NULL,
        details TEXT
    );
    """)

    # Table 7: event_audit — full state transition audit trail
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS event_audit (
        audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id TEXT NOT NULL,
        incident_id TEXT NOT NULL,
        previous_state TEXT,
        new_state TEXT,
        event_type TEXT NOT NULL,
        event_timestamp TEXT NOT NULL,
        received_at TEXT NOT NULL,
        processing_status TEXT NOT NULL,
        reason TEXT,
        recorded_at TEXT NOT NULL
    );
    """)

    # Table 8: override_logs — human override decisions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS override_logs (
        override_id TEXT PRIMARY KEY,
        incident_id TEXT NOT NULL,
        recommendation_id TEXT NOT NULL,
        decision TEXT NOT NULL,
        override_reason TEXT,
        override_comment TEXT,
        operator_id TEXT,
        timestamp TEXT NOT NULL
    );
    """)

    # Table 9: experiment_results — MTTR experiment output
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS experiment_results (
        result_id INTEGER PRIMARY KEY AUTOINCREMENT,
        experiment_name TEXT NOT NULL,
        metric_name TEXT NOT NULL,
        baseline_value REAL,
        target_value REAL,
        measured_value REAL,
        unit TEXT,
        dataset_label TEXT NOT NULL,
        recorded_at TEXT NOT NULL
    );
    """)

    # Table 10: stakeholder_feedback
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stakeholder_feedback (
        feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        rating INTEGER NOT NULL,
        comment TEXT NOT NULL,
        stakeholder_role TEXT NOT NULL,
        recorded_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Table 11: risk_register
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS risk_register (
        risk_id INTEGER PRIMARY KEY AUTOINCREMENT,
        risk TEXT NOT NULL,
        likelihood TEXT NOT NULL,
        impact TEXT NOT NULL,
        mitigation TEXT NOT NULL,
        owner TEXT,
        status TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized at", DB_PATH)
