"""
conftest.py — Pytest session-level setup.
Deletes and recreates the hospital_it.db with the latest schema before any tests run.
"""
import pytest
from pathlib import Path


def pytest_sessionstart(session):
    """Called once before the test session starts. Force fresh DB schema."""
    db_path = Path(__file__).parent / "hospital_it.db"
    if db_path.exists():
        db_path.unlink()
        print(f"\n[conftest] Deleted stale DB at {db_path}")

    # Reinitialise with latest schema and seed data
    from backend.database import init_db
    init_db()
    print("[conftest] Database reinitialised with latest schema.")
