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

    # Table 6: events
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        event_id TEXT PRIMARY KEY,
        incident_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        event_timestamp TEXT NOT NULL,
        sequence_number INTEGER NOT NULL,
        processed_at TEXT NOT NULL,
        status TEXT NOT NULL,
        details TEXT
    );
    """)

    # Table 7: risk_register
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS risk_register (
        risk_id INTEGER PRIMARY KEY AUTOINCREMENT,
        risk TEXT NOT NULL,
        impact TEXT NOT NULL,
        likelihood TEXT NOT NULL,
        mitigation TEXT NOT NULL,
        status TEXT NOT NULL
    );
    """)

    # Table 8: stakeholder_feedback
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stakeholder_feedback (
        feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        rating INTEGER NOT NULL,
        comment TEXT NOT NULL,
        stakeholder_role TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized at", DB_PATH)
