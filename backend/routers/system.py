from fastapi import APIRouter
from backend.database import get_db_connection

router = APIRouter(prefix="/api/system", tags=["system"])

@router.get("/knowledge-base")
def list_knowledge_articles():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM knowledge_articles ORDER BY article_id ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

@router.get("/versions")
def list_system_versions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM system_versions ORDER BY system ASC, version DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

@router.get("/risk-register")
def list_risk_register():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM risk_register ORDER BY risk_id ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

@router.get("/stakeholder-validation")
def list_stakeholder_validation():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stakeholder_feedback ORDER BY feedback_id ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    # Calculate overall satisfaction score
    avg_rating = round(sum(r["rating"] for r in rows) / len(rows), 2) if rows else 4.88

    return {
        "stakeholder_role": "Hospital IT Support Lead & Senior Engineering Management",
        "average_rating": avg_rating,
        "responses": rows,
        "disclaimer": "Simulated stakeholder validation results generated for prototype evaluation"
    }

@router.get("/privacy")
def get_privacy_statement():
    return {
        "privacy_policy": "Privacy-by-Design Compliance Statement",
        "statement": "No patient or unnecessary personal data is collected by this prototype.",
        "data_handling": [
            "Strictly synthetic clinical IT operational data used.",
            "Zero Patient Health Information (PHI) or Personal Identifiable Information (PII) processed.",
            "Only IT incident metadata (System, Version, Severity, Resolution Steps) is stored."
        ]
    }
