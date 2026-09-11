import pytest
import datetime
import uuid
from backend.seed_data import seed_database
from backend.database import get_db_connection
from backend.event_engine import process_event, get_event_audit_trail

@pytest.fixture(autouse=True)
def setup_db():
    seed_database()

def _new_incident():
    """Create a fresh test incident and return its ID."""
    from fastapi.testclient import TestClient
    from backend.main import app
    client = TestClient(app)
    r = client.post("/api/incidents", json={
        "description": "Lab results not loading for ICU users.",
        "system": "LabSys", "version": "5.4",
        "category": "Application", "severity": "High"
    })
    return r.json()["incident_id"]


def test_normal_event_sequence():
    """Normal lifecycle OPEN→RECOMMENDED→FIX_APPROVED→RESOLVED."""
    inc_id = _new_incident()
    now = datetime.datetime.now().isoformat()
    r2 = process_event(f"N-EVT-{inc_id}-2", inc_id, "RECOMMENDATION_GENERATED", now, 2)
    assert r2["status"] == "PROCESSED"
    r3 = process_event(f"N-EVT-{inc_id}-3", inc_id, "FIX_APPROVED", now, 3)
    assert r3["status"] == "PROCESSED"
    r5 = process_event(f"N-EVT-{inc_id}-5", inc_id, "INCIDENT_RESOLVED", now, 5)
    assert r5["status"] == "PROCESSED"

    conn = get_db_connection()
    row = conn.execute("SELECT status FROM incidents WHERE incident_id = ?", (inc_id,)).fetchone()
    conn.close()
    assert row["status"] == "RESOLVED"


def test_duplicate_event_is_idempotent():
    """Duplicate event_id returns DUPLICATE_IGNORED."""
    inc_id = _new_incident()
    now = datetime.datetime.now().isoformat()
    evt_id = f"DUP-EVT-{uuid.uuid4().hex[:8]}"

    r1 = process_event(evt_id, inc_id, "RECOMMENDATION_GENERATED", now, 2, "First")
    assert r1["status"] == "PROCESSED"
    r2 = process_event(evt_id, inc_id, "RECOMMENDATION_GENERATED", now, 2, "Duplicate")
    assert r2["status"] == "DUPLICATE_IGNORED"


def test_duplicate_event_does_not_change_state():
    """State is unchanged after duplicate injection."""
    inc_id = _new_incident()
    now = datetime.datetime.now().isoformat()
    evt_id = f"DUP2-EVT-{uuid.uuid4().hex[:8]}"

    process_event(evt_id, inc_id, "RECOMMENDATION_GENERATED", now, 2)
    conn = get_db_connection()
    state_after_first = conn.execute(
        "SELECT status FROM incidents WHERE incident_id=?", (inc_id,)
    ).fetchone()["status"]
    conn.close()

    process_event(evt_id, inc_id, "RECOMMENDATION_GENERATED", now, 2)  # duplicate
    conn = get_db_connection()
    state_after_dup = conn.execute(
        "SELECT status FROM incidents WHERE incident_id=?", (inc_id,)
    ).fetchone()["status"]
    conn.close()

    assert state_after_first == state_after_dup


def test_delayed_event_does_not_corrupt_state():
    """Event with old UTC timestamp but arrives late is processed safely."""
    inc_id = _new_incident()
    # Simulate a timestamp 5 minutes ago in UTC
    old_ts = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=5)).isoformat()
    r = process_event(f"DEL-EVT-{uuid.uuid4().hex[:8]}", inc_id, "RECOMMENDATION_GENERATED", old_ts, 2)
    assert r["state_changed"] is True
    assert r["is_delayed"] is True

    conn = get_db_connection()
    row = conn.execute("SELECT status FROM incidents WHERE incident_id=?", (inc_id,)).fetchone()
    conn.close()
    assert row["status"] in ["RECOMMENDED", "RESOLVED", "FIX_APPROVED", "OPEN"]


def test_out_of_order_event_does_not_regress_state():
    """
    Events arrive: OPEN → RESOLVED → then RECOMMENDATION_GENERATED (old, lower rank).
    Final state must remain RESOLVED, not regress to RECOMMENDED.
    """
    inc_id = _new_incident()
    now = datetime.datetime.now().isoformat()

    process_event(f"OOO-EVT-{inc_id}-2", inc_id, "RECOMMENDATION_GENERATED", now, 2)
    process_event(f"OOO-EVT-{inc_id}-5", inc_id, "INCIDENT_RESOLVED", now, 5)

    conn = get_db_connection()
    state_resolved = conn.execute(
        "SELECT status FROM incidents WHERE incident_id=?", (inc_id,)
    ).fetchone()["status"]
    conn.close()
    assert state_resolved == "RESOLVED"

    # Now inject a late lower-rank event — must NOT regress
    r_old = process_event(f"OOO-EVT-{inc_id}-OLD", inc_id, "RECOMMENDATION_GENERATED", now, 2)
    assert r_old["status"] in ["OUT_OF_ORDER_IGNORED", "DUPLICATE_IGNORED"]

    conn = get_db_connection()
    final_state = conn.execute(
        "SELECT status FROM incidents WHERE incident_id=?", (inc_id,)
    ).fetchone()["status"]
    conn.close()
    assert final_state == "RESOLVED"


def test_same_timestamp_events_are_deterministic():
    """Two events with same timestamp use sequence_number for deterministic ordering."""
    inc_id = _new_incident()
    ts = datetime.datetime.now().isoformat()
    evt_a = f"STS-A-{uuid.uuid4().hex[:6]}"
    evt_b = f"STS-B-{uuid.uuid4().hex[:6]}"

    r_a = process_event(evt_a, inc_id, "RECOMMENDATION_GENERATED", ts, 2)
    r_b = process_event(evt_b, inc_id, "FIX_APPROVED", ts, 3)

    assert r_a["status"] == "PROCESSED"
    assert r_b["status"] == "PROCESSED"

    conn = get_db_connection()
    final = conn.execute(
        "SELECT status FROM incidents WHERE incident_id=?", (inc_id,)
    ).fetchone()["status"]
    conn.close()
    assert final == "FIX_APPROVED"


def test_mixed_event_stream_recovers_correctly():
    """
    Inject a mixed stream: normal → duplicate → delayed → out-of-order → resolve.
    Final state must be RESOLVED.
    """
    inc_id = _new_incident()
    now = datetime.datetime.now().isoformat()
    old_ts = (datetime.datetime.now() - datetime.timedelta(minutes=10)).isoformat()
    dup_id = f"MIXED-DUP-{uuid.uuid4().hex[:6]}"

    process_event(f"MIXED-2-{uuid.uuid4().hex[:6]}", inc_id, "RECOMMENDATION_GENERATED", now, 2)
    process_event(dup_id, inc_id, "FIX_APPROVED", now, 3)
    process_event(dup_id, inc_id, "FIX_APPROVED", now, 3)      # duplicate
    process_event(f"MIXED-DEL-{uuid.uuid4().hex[:6]}", inc_id, "FIX_APPROVED", old_ts, 3)  # delayed
    process_event(f"MIXED-5-{uuid.uuid4().hex[:6]}", inc_id, "INCIDENT_RESOLVED", now, 5)

    conn = get_db_connection()
    final = conn.execute(
        "SELECT status FROM incidents WHERE incident_id=?", (inc_id,)
    ).fetchone()["status"]
    conn.close()
    assert final == "RESOLVED"


def test_processed_event_registry_is_persistent():
    """After duplicate, the events table still contains exactly one record for that event_id."""
    inc_id = _new_incident()
    now = datetime.datetime.now().isoformat()
    evt_id = f"PERSIST-{uuid.uuid4().hex[:8]}"

    process_event(evt_id, inc_id, "RECOMMENDATION_GENERATED", now, 2)
    process_event(evt_id, inc_id, "RECOMMENDATION_GENERATED", now, 2)  # duplicate

    conn = get_db_connection()
    count = conn.execute(
        "SELECT COUNT(*) as cnt FROM events WHERE event_id=?", (evt_id,)
    ).fetchone()["cnt"]
    conn.close()
    assert count == 1  # Only one record, duplicate rejected


def test_final_state_is_correct_after_fault_injection():
    """
    After injecting duplicate + out-of-order events, final state is RESOLVED.
    Audit trail contains all events (including ignored ones).
    """
    inc_id = _new_incident()
    now = datetime.datetime.now().isoformat()
    dup_id = f"FAULT-DUP-{uuid.uuid4().hex[:6]}"

    process_event(f"FAULT-2-{uuid.uuid4().hex[:6]}", inc_id, "RECOMMENDATION_GENERATED", now, 2)
    process_event(dup_id, inc_id, "FIX_APPROVED", now, 3)
    process_event(dup_id, inc_id, "FIX_APPROVED", now, 3)  # duplicate
    process_event(f"FAULT-OLD-{uuid.uuid4().hex[:6]}", inc_id, "RECOMMENDATION_GENERATED", now, 2)  # OOO
    process_event(f"FAULT-5-{uuid.uuid4().hex[:6]}", inc_id, "INCIDENT_RESOLVED", now, 5)

    conn = get_db_connection()
    final = conn.execute(
        "SELECT status FROM incidents WHERE incident_id=?", (inc_id,)
    ).fetchone()["status"]
    conn.close()
    assert final == "RESOLVED"

    audit = get_event_audit_trail(inc_id)
    statuses = [a["processing_status"] for a in audit]
    assert "DUPLICATE_IGNORED" in statuses
