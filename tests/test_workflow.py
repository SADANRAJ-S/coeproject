import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.seed_data import seed_database
from backend.database import get_db_connection

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    seed_database()

def test_6_high_impact_recommendation_requires_human_confirmation():
    """
    TEST 6: High-impact recommendation
    Expected: Human confirmation required
    """
    inc_res = client.post("/api/incidents", json={
        "description": "Lab results are not loading for users.",
        "system": "LabSys",
        "version": "5.4",
        "category": "Application",
        "severity": "High",
        "impact_level": "HIGH"
    })
    incident_id = inc_res.json()["incident_id"]

    rec_res = client.post("/api/retrieval/recommend", json={"incident_id": incident_id})
    rec_data = rec_res.json()
    verified = rec_data.get("verified_recommendations", [])
    assert len(verified) > 0
    top_rec = verified[0]
    assert top_rec["impact_level"] == "HIGH"
    assert top_rec["requires_human_confirmation"] is True

def test_7_rejected_recommendation_stores_override_reason():
    """
    TEST 7: Rejected recommendation
    Expected: Override reason stored in database
    """
    inc_res = client.post("/api/incidents", json={
        "description": "PACS image loading slow",
        "system": "PACSView",
        "version": "4.1",
        "category": "Performance",
        "severity": "Medium"
    })
    incident_id = inc_res.json()["incident_id"]

    reject_res = client.post(
        f"/api/recommendations/KA-019/confirm?incident_id={incident_id}",
        json={
            "action": "REJECT",
            "recommendation_id": "KA-019",
            "override_reason": "Version mismatch",
            "override_comment": "Tested manual cache clearing."
        }
    )
    assert reject_res.status_code == 200
    data = reject_res.json()
    assert data["status"] == "REJECTED"
    assert data["override_reason"] == "Version mismatch"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM feedback WHERE incident_id = ?", (incident_id,))
    fb = cursor.fetchone()
    conn.close()
    assert fb is not None
    assert fb["override_reason"] == "Version mismatch"

def test_8_resolved_incident_ttr_calculated_correctly():
    """
    TEST 8: Resolved incident
    Expected: TTR calculated correctly
    """
    inc_res = client.post("/api/incidents", json={
        "description": "Lab results are not loading.",
        "system": "LabSys",
        "version": "5.4",
        "category": "Application",
        "severity": "High"
    })
    incident_id = inc_res.json()["incident_id"]

    approve_res = client.post(
        f"/api/recommendations/KA-014/confirm?incident_id={incident_id}",
        json={"action": "APPROVE", "recommendation_id": "KA-014"}
    )
    assert approve_res.status_code == 200
    data = approve_res.json()
    assert data["status"] == "APPROVED"
    assert data["incident_status"] == "RESOLVED"
    assert data["ttr_minutes"] > 0
