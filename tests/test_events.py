import pytest
import datetime
from backend.seed_data import seed_database
from backend.event_engine import process_event
from backend.database import get_db_connection

@pytest.fixture(autouse=True)
def setup_db():
    seed_database()

def test_4_duplicate_event_ignored_without_changing_state():
    """
    TEST 4: Duplicate event
    Expected: Ignored without changing state
    """
    event_id = "EVT-TEST-DUP-400"
    incident_id = "INC-301"
    now_iso = datetime.datetime.now().isoformat()

    res1 = process_event(event_id, incident_id, "RECOMMENDATION_GENERATED", now_iso, 2, "First ingestion")
    assert res1["state_changed"] is True

    res2 = process_event(event_id, incident_id, "RECOMMENDATION_GENERATED", now_iso, 2, "Duplicate ingestion attempt")
    assert res2["status"] == "DUPLICATE_IGNORED"
    assert res2["state_changed"] is False

def test_5_out_of_order_event_state_remains_consistent():
    """
    TEST 5: Out-of-order event
    Expected: State remains consistent
    """
    event_id = "EVT-TEST-OOO-500"
    incident_id = "INC-301"
    now_iso = datetime.datetime.now().isoformat()

    res = process_event(event_id, incident_id, "FIX_APPLIED", now_iso, 10, "Out of order sequence")
    assert res["status"] in ["OUT_OF_ORDER_BUFFERED", "PROCESSED"]
    assert res["state_changed"] is True
