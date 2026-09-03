import json
import csv
import random
import os
from pathlib import Path

DATASET_DIR = Path(__file__).parent
DATASET_DIR.mkdir(parents=True, exist_ok=True)

# Templates for synthetic clinical IT incident generation
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
            "HL7 result queue listener frozen in LabSys application server."
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
            "LabSys 5.1 client terminal displays cache read error."
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
            "Lab database queries timing out for pathology lookup."
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
            "eMAR order confirmation buffer timeout."
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
            "PACS CT scan DICOM image frame drop during viewing."
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
            "PACSView image ingress router socket error."
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
            "Patient demographics entry screen locked up."
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
            "Single sign-on authentication gateway rejecting clinical credentials."
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
            "HL7 interface queue resend required for laboratory feed."
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
            "Print spooler service hung for pharmacy chart printer."
        ]
    }
]

def generate_cleaned_dataset(total_count=250):
    dataset = []
    
    # Variations of symptoms to augment dataset
    prefix_variations = [
        "", "Urgent: ", "Clinical Alert: ", "Reported by Nursing: ", 
        "Shift A Ticket: ", "Recurring issue: ", "STAT: "
    ]
    suffix_variations = [
        "", " Affecting patient care.", " Please resolve immediately.", 
        " Needs immediate IT response.", " Workstation reboot did not fix."
    ]

    count_per_template = (total_count // len(TEMPLATES)) + 1
    
    inc_id = 1000
    for template in TEMPLATES:
        descs = template["descriptions"]
        for _ in range(count_per_template):
            base_desc = random.choice(descs)
            prefix = random.choice(prefix_variations)
            suffix = random.choice(suffix_variations)
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
                "is_successful": 1
            })

    random.shuffle(dataset)
    dataset = dataset[:total_count]

    # Save to CSV
    csv_path = DATASET_DIR / "hospital_it_incidents_clean.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "incident_id", "description", "system", "version", "category", "severity", "target_resolution_id", "is_successful"
        ])
        writer.writeheader()
        writer.writerows(dataset)

    # Save to JSON
    json_path = DATASET_DIR / "hospital_it_incidents_clean.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)

    print(f"[+] Successfully generated cleaned dataset with {len(dataset)} records!")
    print(f"    - CSV Path: {csv_path}")
    print(f"    - JSON Path: {json_path}")
    return dataset

if __name__ == "__main__":
    generate_cleaned_dataset()
