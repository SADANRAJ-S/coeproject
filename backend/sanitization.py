import re
from typing import Dict, Any

# Regular Expression Patterns for PHI / PII Identification
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
PHONE_PATTERN = r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
MRN_PATTERN = r'\b(?:MRN|Medical Record Number|Pat ID|Patient ID)\s*[:#-]?\s*([A-Za-z0-9-]{4,12})\b'
SSN_PATTERN = r'\b\d{3}-\d{2}-\d{4}\b'
DOB_PATTERN = r'\b(?:DOB|Date of Birth|Born)\s*[:#-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b'
PATIENT_NAME_PATTERN = r'\b(?:Patient|Pt|Name)\s*[:#-]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b'

# Free-text clinical diagnosis phrases to strip
CLINICAL_DIAGNOSIS_PHRASES = [
    r'\bdiagnosed with [^.,;]+',
    r'\bpatient presents with [^.,;]+',
    r'\bhistory of [^.,;]+',
    r'\bprescribed [^.,;]+',
    r'\bmedication dose [^.,;]+',
    r'\bblood pressure [^.,;]+',
    r'\blab specimen from [^.,;]+'
]

def sanitize_text(text: str) -> str:
    """
    Sanitize free-text incident descriptions by detecting and redacting
    unnecessary Patient Health Information (PHI) and Person Identifiable Information (PII).
    """
    if not text:
        return ""

    sanitized = text

    # 1. Redact Email Addresses
    sanitized = re.sub(EMAIL_PATTERN, "[EMAIL_REDACTED]", sanitized, flags=re.IGNORECASE)

    # 2. Redact Phone Numbers
    sanitized = re.sub(PHONE_PATTERN, "[PHONE_REDACTED]", sanitized)

    # 3. Redact Social Security Numbers (SSNs)
    sanitized = re.sub(SSN_PATTERN, "[SSN_REDACTED]", sanitized)

    # 4. Redact Medical Record Numbers (MRNs)
    sanitized = re.sub(MRN_PATTERN, "[MRN_REDACTED]", sanitized, flags=re.IGNORECASE)

    # 5. Redact Date of Birth (DOB)
    sanitized = re.sub(DOB_PATTERN, "[DOB_REDACTED]", sanitized, flags=re.IGNORECASE)

    # 6. Redact Patient Names
    sanitized = re.sub(PATIENT_NAME_PATTERN, "[PATIENT_REDACTED]", sanitized, flags=re.IGNORECASE)

    # 7. Redact free-text clinical diagnostic phrases
    for pattern in CLINICAL_DIAGNOSIS_PHRASES:
        sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)

    # Clean up redundant whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    return sanitized

def sanitize_incident_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize incoming incident payload before database persistence or embedding generation.
    Enforces operational allow-list fields only.
    """
    sanitized_description = sanitize_text(payload.get("description", ""))

    # Operational Field Allow-List
    return {
        "description": sanitized_description,
        "system": str(payload.get("system", "")).strip(),
        "version": str(payload.get("version", "")).strip(),
        "category": str(payload.get("category", "Application")).strip(),
        "severity": str(payload.get("severity", "Medium")).strip(),
        "impact_level": str(payload.get("impact_level", "LOW")).strip()
    }
