"""
generate_dataset.py — Cleaned Hospital IT Incident Dataset Generator
Generates 500 high-quality synthetic incident records across 10 clinical IT systems.
All data is SYNTHETIC — no real patient information.
"""
import json
import csv
import random
from pathlib import Path

DATASET_DIR = Path(__file__).parent
DATASET_DIR.mkdir(parents=True, exist_ok=True)

random.seed(42)

# ─────────────────────────────────────────────────────────────────────────────
# TEMPLATES — 10 knowledge article targets with rich, varied descriptions
# ─────────────────────────────────────────────────────────────────────────────
TEMPLATES = [
    # KA-014: Restart LabSys Application Service (LabSys 5.0 - 5.5)
    {
        "target_resolution_id": "KA-014",
        "system": "LabSys",
        "version": "5.4",
        "category": "Application",
        "severity": "High",
        "descriptions": [
            "Lab results are not loading for users in ICU.",
            "Lab result viewer displays infinite loading spinner on floor 3.",
            "STAT blood work lab results hanging on render screen.",
            "LabSys viewer timeout when opening chemistry panel.",
            "Lab results failing to populate in emergency department workstation.",
            "Outpatient clinic lab result module unresponsive.",
            "Lab result viewer blank for hematology orders.",
            "LabSys web application service pool exhausted, results not displaying.",
            "Lab results not updating after analyzer completion.",
            "HL7 result queue listener frozen in LabSys application server.",
            "Clinical workstation cannot retrieve lab result data from LabSys 5.4.",
            "Lab results page unresponsive for nursing staff on 2nd floor.",
            "LabSys application service crash detected during shift change.",
            "Lab result summary screen times out after 30 seconds on ward 7.",
            "Automated lab result alerts not appearing for critical values in ICU.",
            "LabSys portal blank white screen after login for nursing staff.",
            "Lab order results queue stuck and not refreshing in LabSys 5.4.",
            "Hematology analyzer results not flowing into LabSys viewer.",
            "LabSys result panel frozen after updating from 5.3 to 5.4.",
            "Lab result notification service unresponsive — critical values not alerting."
        ]
    },
    # KA-003: Legacy LabSys 5.1 Cache Reset (LabSys 5.1 only)
    {
        "target_resolution_id": "KA-003",
        "system": "LabSys",
        "version": "5.1",
        "category": "Application",
        "severity": "Medium",
        "descriptions": [
            "Lab result screen blank on legacy workstation running LabSys 5.1.",
            "Legacy LabSys 5.1 client local cache corrupted.",
            "LabSys 5.1 client station freeze during result lookup.",
            "Legacy station lab result cache overflow in version 5.1.",
            "LabSys 5.1 client terminal displays cache read error.",
            "Legacy LabSys 5.1 workstation shows stale cached results.",
            "LabSys version 5.1 caching issue causing incorrect historic results.",
            "Outpatient terminal on version 5.1 showing blank result panel.",
            "LabSys 5.1 client cache size limit reached on shared workstation.",
            "Old ward terminal running LabSys 5.1 displays corrupted result rows."
        ]
    },
    # KA-022: LabSys Database Connection Pool Recycle (LabSys 5.0 - 5.5)
    {
        "target_resolution_id": "KA-022",
        "system": "LabSys",
        "version": "5.4",
        "category": "Database",
        "severity": "High",
        "descriptions": [
            "LabSys database query threshold exceeded 15 seconds.",
            "LabSys DB connection pool exhausted during peak shift change.",
            "Database connection timeout on LabSys clinical database server.",
            "LabSys SQL query thread pool deadlock.",
            "Lab database queries timing out for pathology lookup.",
            "LabSys DB pool starvation during morning peak — queries not completing.",
            "SQL connection timeout for LabSys database cluster during batch run.",
            "LabSys database service ORA-00020 maximum processes error at peak.",
            "Lab pathology report database connection failure during busy hours.",
            "LabSys 5.4 database pool exhausted — all 200 connections in use.",
            "Database latency above 30 seconds for LabSys result retrieval.",
            "LabSys DB read replica lagging 10 minutes — stale results displayed."
        ]
    },
    # KA-008: MedFlow Order Queue Clear & Process Recycle (MedFlow 3.0 - 3.5)
    {
        "target_resolution_id": "KA-008",
        "system": "MedFlow",
        "version": "3.2",
        "category": "Application",
        "severity": "High",
        "descriptions": [
            "Medication module timeout during order entry on floor 3.",
            "eMAR electronic medication administration record order submission frozen.",
            "Pharmacy order queue daemon unresponsive in MedFlow 3.2.",
            "Medication dispensing order queue delayed in pharmacy module.",
            "MedFlow order entry screen freeze during STAT dose entry.",
            "Pharmacy order queue listener hanging on unit dose validation.",
            "eMAR order confirmation buffer timeout.",
            "MedFlow medication administration queue backed up 200+ pending orders.",
            "Pharmacy STAT medication orders not processing through MedFlow queue.",
            "MedFlow 3.2 order processing service hung — overnight queue not cleared.",
            "Nursing eMAR administration task queue frozen during morning drug round.",
            "MedFlow dispensing cabinet sync queue timeout for floor 4 pharmacy.",
            "Medication order workflow engine stuck on verifying state in MedFlow.",
            "Pharmacy barcode scan medication administration blocked in queue."
        ]
    },
    # KA-019: PACS Image Cache Purge & DICOM Router Cycle (PACSView 4.0 - 4.5)
    {
        "target_resolution_id": "KA-019",
        "system": "PACSView",
        "version": "4.1",
        "category": "Performance",
        "severity": "Medium",
        "descriptions": [
            "PACS image loading slow in ER radiology station.",
            "CT scan images buffering slowly on PACSView radiology workstation.",
            "PACS radiology workstation DICOM cache overflow.",
            "PACSView image streaming latency high in trauma bay.",
            "Radiology PACS workstation image rendering delayed.",
            "PACS CT scan DICOM image frame drop during viewing.",
            "PACSView image loading over 90 seconds for chest X-ray in ED.",
            "PACS radiologist workstation image cache full — cannot load new series.",
            "PACSView DICOM image cache bloated causing slow rendering on reading station.",
            "Radiology overnight batch image cache not cleared — morning sessions slow.",
            "MRI series DICOM image loading lag of 3 minutes on PACSView 4.1.",
            "PACSView viewer thumbnail loading 60 seconds — radiology throughput impacted."
        ]
    },
    # KA-021: PACSView DICOM Gateway Service Restart (PACSView 4.0 - 4.5)
    {
        "target_resolution_id": "KA-021",
        "system": "PACSView",
        "version": "4.1",
        "category": "Integration",
        "severity": "High",
        "descriptions": [
            "PACS DICOM streaming gateway daemon frozen.",
            "PACSView DICOM router port unresponsive for MRI transfer.",
            "PACS DICOM gateway connection failed for radiology scanner.",
            "PACSView image ingress router socket error.",
            "DICOM gateway service crash on PACSView — CT images not received from scanner.",
            "PACSView DICOM listener port 104 not accepting new connections.",
            "Radiology modality worklist DICOM query failing — gateway offline.",
            "MRI scanner DICOM push rejected by PACSView gateway service.",
            "PACS ingress gateway daemon stopped — radiology image transfer halted.",
            "PACSView DICOM C-STORE operation failure for ultrasound study."
        ]
    },
    # KA-005: EHR Core UI Thread Recycling (EHRCore 5.8 - 6.2)
    {
        "target_resolution_id": "KA-005",
        "system": "EHRCore",
        "version": "6.0",
        "category": "UI/Application",
        "severity": "Medium",
        "descriptions": [
            "Patient registration screen freezing during intake.",
            "EHR registration module UI thread deadlock.",
            "Patient admission intake screen non-responsive.",
            "EHR Core patient chart registration session freeze.",
            "Patient demographics entry screen locked up.",
            "EHRCore 6.0 registration UI thread pool exhausted — admissions delayed.",
            "Patient admit screen hangs after entering insurance details in EHR.",
            "EHR Core chart open operation timing out for ED rapid registration.",
            "Patient registration workflow frozen at insurance verification step.",
            "EHRCore admissions screen freeze during multi-patient batch registration.",
            "EHR encounter creation screen not responding for new patient intake.",
            "EHRCore 6.0 UI freezes when selecting patient from search results list."
        ]
    },
    # KA-012: AuthGuard LDAP Gateway Synchronizer Reset (AuthGuard 2.5 - 3.0)
    {
        "target_resolution_id": "KA-012",
        "system": "AuthGuard",
        "version": "2.8",
        "category": "Authentication",
        "severity": "High",
        "descriptions": [
            "Clinical application login failure SSO auth error.",
            "AuthGuard LDAP single sign-on synchronization delay.",
            "Clinical SSO tap card login failing across nursing stations.",
            "AuthGuard directory synchronizer timeout on domain controller.",
            "Single sign-on authentication gateway rejecting clinical credentials.",
            "AuthGuard 2.8 LDAP sync delay causing 5-minute login wait at nursing station.",
            "Hospital SSO badge tap login failing for all staff in ward 5.",
            "AuthGuard LDAP directory sync lagging 20 minutes — new password not recognized.",
            "Clinical app authentication gateway returning 401 error for valid users.",
            "LDAP connection pool saturation in AuthGuard — login intermittent.",
            "AuthGuard SSO session token expiry too aggressive — re-login every 5 min.",
            "Clinical workstation smart card login rejected by AuthGuard gateway."
        ]
    },
    # KA-031: HL7 Router Queue Purge & Resend (HL7Router 3.0 - 4.0)
    {
        "target_resolution_id": "KA-031",
        "system": "HL7Router",
        "version": "3.5",
        "category": "Integration",
        "severity": "High",
        "descriptions": [
            "Interface message queue delayed HL7 lab feed.",
            "HL7 ORU_R01 lab message queue stuck in pending state.",
            "HL7 router ingress port backlogged with 5000 unparsed messages.",
            "Interface gateway message pipeline halted for lab integration.",
            "HL7 interface queue resend required for laboratory feed.",
            "HL7Router 3.5 message queue overflowing — 8000 messages pending.",
            "Lab HL7 ORU results not flowing to EHR — router queue frozen.",
            "HL7 ADT message pipeline delayed — patient admit not triggering worklists.",
            "HL7 interface engine crashed — all downstream feeds halted.",
            "HL7Router queue processing stopped — critical lab values not delivered.",
            "Outbound HL7 message queue backlog for radiology report distribution.",
            "HL7 ORM order message stuck in pending — lab not receiving orders."
        ]
    },
    # KA-002: Print Spooler Service Restart (PrintManager 1.0 - 2.0)
    {
        "target_resolution_id": "KA-002",
        "system": "PrintManager",
        "version": "1.4",
        "category": "Infrastructure",
        "severity": "Low",
        "descriptions": [
            "Printer unavailable in 4th floor nursing station.",
            "Patient wristband thermal printer offline in triage.",
            "Nursing station lab label printer spooler error.",
            "Print spooler service hung for pharmacy chart printer.",
            "Patient discharge summary printer offline in ward 3.",
            "PrintManager 1.4 spooler queue stuck with 50 pending jobs.",
            "Lab specimen barcode label printer not responding on floor 6.",
            "Thermal wristband printer driver error — print spooler crashed.",
            "Medication administration label printer offline in pharmacy.",
            "Print queue deadlock in PrintManager — nurses cannot print MAR sheet."
        ]
    }
]

# ─────────────────────────────────────────────────────────────────────────────
# AUGMENTATION — prefix/suffix variations to increase lexical diversity
# ─────────────────────────────────────────────────────────────────────────────
PREFIXES = [
    "", "Urgent: ", "Clinical Alert: ", "Reported by Nursing: ",
    "Shift A Ticket: ", "Recurring issue: ", "STAT: ",
    "Critical: ", "Escalated: ", "Morning handover: ",
    "Night shift report: ", "IT Help Desk: ", "Ward 3 reporting: ",
    "ED Nursing: ", "Pharmacy calling: ", "Radiology team: ",
]

SUFFIXES = [
    "", " Affecting patient care.", " Please resolve immediately.",
    " Needs immediate IT response.", " Workstation reboot did not fix.",
    " Affecting multiple users.", " On-call engineer notified.",
    " Issue persisting for 2 hours.", " All staff affected.",
    " First reported at shift change.", " Ongoing since 06:00.",
    " Intermittent since yesterday.", " No recent system changes.",
    " Recurring for third time this week.", " Second report from same ward.",
]


def generate_cleaned_dataset(total_count: int = 500) -> list:
    """
    Generate a high-quality cleaned hospital IT incident dataset.

    Args:
        total_count: Total number of records to generate (default: 500)

    Returns:
        List of incident record dicts
    """
    dataset = []
    count_per_template = max(1, (total_count // len(TEMPLATES)) + 1)
    inc_id = 1000

    for template in TEMPLATES:
        descs = template["descriptions"]
        for _ in range(count_per_template):
            base_desc = random.choice(descs)
            prefix = random.choice(PREFIXES)
            suffix = random.choice(SUFFIXES)
            full_desc = f"{prefix}{base_desc}{suffix}".strip()

            inc_id += 1
            dataset.append({
                "incident_id": f"DS-{inc_id}",
                "description": full_desc,
                "system": template["system"],
                "version": template["version"],
                "category": template["category"],
                "severity": template["severity"],
                "target_resolution_id": template["target_resolution_id"],
                "is_successful": 1,
                "dataset_label": "SYNTHETIC_BENCHMARK"
            })

    random.shuffle(dataset)
    dataset = dataset[:total_count]

    # Save to CSV
    csv_path = DATASET_DIR / "hospital_it_incidents_clean.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(dataset[0].keys()))
        writer.writeheader()
        writer.writerows(dataset)

    # Save to JSON
    json_path = DATASET_DIR / "hospital_it_incidents_clean.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)

    # Class distribution
    class_dist = {}
    for row in dataset:
        k = row["target_resolution_id"]
        class_dist[k] = class_dist.get(k, 0) + 1

    print(f"[+] Generated cleaned dataset: {len(dataset)} records, {len(class_dist)} classes")
    print("    Class distribution:")
    for k, v in sorted(class_dist.items()):
        print(f"      {k}: {v} records")
    print(f"    CSV:  {csv_path}")
    print(f"    JSON: {json_path}")

    return dataset


if __name__ == "__main__":
    generate_cleaned_dataset(total_count=500)
