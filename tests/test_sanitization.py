import pytest
from backend.sanitization import sanitize_text, sanitize_incident_payload

def test_email_redaction():
    text = "Lab results failing. Contact technician at john.doe@hospital.org for updates."
    sanitized = sanitize_text(text)
    assert "john.doe@hospital.org" not in sanitized
    assert "[EMAIL_REDACTED]" in sanitized
    assert "Lab results failing" in sanitized

def test_phone_redaction():
    text = "PACS viewer freeze reported by phone 555-123-4567 in radiology."
    sanitized = sanitize_text(text)
    assert "555-123-4567" not in sanitized
    assert "[PHONE_REDACTED]" in sanitized

def test_mrn_redaction():
    text = "EHR screen frozen for MRN: 12345678 on 3rd floor workstation."
    sanitized = sanitize_text(text)
    assert "12345678" not in sanitized
    assert "[MRN_REDACTED]" in sanitized

def test_patient_name_redaction():
    text = "Patient John Smith chart failed to open in EHR Core."
    sanitized = sanitize_text(text)
    assert "John Smith" not in sanitized
    assert "[PATIENT_REDACTED]" in sanitized

def test_clinical_text_exclusion():
    text = "Lab results not loading. Patient presents with acute hypertension diagnosed with cardiac arrest."
    sanitized = sanitize_text(text)
    assert "acute hypertension" not in sanitized
    assert "Lab results not loading" in sanitized

def test_operational_fields_preserved():
    raw_payload = {
        "description": "Patient John Doe MRN 998877 reported Lab results are not loading. Contact tech@hospital.com.",
        "system": "LabSys",
        "version": "5.4",
        "category": "Application",
        "severity": "High",
        "impact_level": "HIGH"
    }
    clean = sanitize_incident_payload(raw_payload)
    assert clean["system"] == "LabSys"
    assert clean["version"] == "5.4"
    assert clean["category"] == "Application"
    assert clean["severity"] == "High"
    assert "MRN" not in clean["description"] or "[MRN_REDACTED]" in clean["description"]
    assert "tech@hospital.com" not in clean["description"]
