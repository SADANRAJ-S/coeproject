import pytest
from backend.seed_data import seed_database
from backend.retrieval_engine import rank_recommendations, compare_versions, is_version_in_range

@pytest.fixture(autouse=True)
def setup_db():
    seed_database()

def test_version_helpers():
    assert compare_versions("5.4", "5.1") == 1
    assert compare_versions("5.1", "5.4") == -1
    assert compare_versions("5.4", "5.4") == 0
    assert is_version_in_range("5.4", "5.0", "5.5") is True
    assert is_version_in_range("5.4", "5.1", "5.1") is False

def test_1_pacsview_incident_labsys_resolution_blocked_system_mismatch():
    """
    TEST 1: PACSView incident + LabSys resolution
    Expected: BLOCKED - System mismatch
    """
    res = rank_recommendations("PACS image loading slow", "PACSView", "4.1")
    verified = res.get("verified_recommendations", [])
    rejected = res.get("rejected_candidates", [])

    # Ensure LabSys resolutions (e.g. KA-014) are NOT in verified recommendations
    labsys_verified = [r for r in verified if r["recommendation_id"] == "KA-014"]
    assert len(labsys_verified) == 0, "LabSys resolution MUST NOT be in verified recommendations for a PACSView incident"

    # Ensure LabSys resolutions appear in rejected_candidates with System Mismatch reason
    labsys_rejected = next((r for r in rejected if r["recommendation_id"] == "KA-014"), None)
    assert labsys_rejected is not None, "KA-014 (LabSys) must be present in rejected candidates"
    assert labsys_rejected["status"] == "BLOCKED"
    assert labsys_rejected["recommendable"] is False
    assert "System mismatch" in labsys_rejected["reason"]
    assert labsys_rejected["verification_rule"] == "incident.system === resolution.system"

def test_2_labsys_54_incident_retired_version51_resolution_blocked():
    """
    TEST 2: LabSys 5.4 incident + LabSys 5.1 retired resolution (KA-003)
    Expected: BLOCKED - Version/currentness failure
    """
    res = rank_recommendations("Lab result screen blank", "LabSys", "5.4")
    verified = res.get("verified_recommendations", [])
    rejected = res.get("rejected_candidates", [])

    ka003_verified = [r for r in verified if r["recommendation_id"] == "KA-003"]
    assert len(ka003_verified) == 0, "KA-003 (LabSys 5.1 / Retired) must NOT be recommended for LabSys 5.4"

    ka003_rejected = next((r for r in rejected if r["recommendation_id"] == "KA-003"), None)
    assert ka003_rejected is not None, "KA-003 must be in rejected candidates"
    assert ka003_rejected["status"] == "BLOCKED"
    assert ka003_rejected["recommendable"] is False
    assert ("Version incompatibility" in ka003_rejected["reason"] or "retired" in ka003_rejected["reason"].lower())

def test_3_labsys_54_incident_valid_resolution():
    """
    TEST 3: LabSys 5.4 incident + current LabSys 5.4 resolution (KA-014)
    Expected: VALID recommendation
    """
    res = rank_recommendations("Lab results are not loading for users.", "LabSys", "5.4")
    verified = res.get("verified_recommendations", [])
    
    assert len(verified) > 0, "Verified recommendations should not be empty for LabSys 5.4"
    top_rec = verified[0]
    assert top_rec["recommendation_id"] == "KA-014"
    assert top_rec["system_compatibility"] is True
    assert top_rec["version_compatibility"] is True
    assert top_rec["status"] == "VERIFIED"
    assert top_rec["recommendable"] is True
    assert top_rec["relevance_score"] >= 70.0
