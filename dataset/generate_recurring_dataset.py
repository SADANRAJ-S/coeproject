import json
import csv
import random
import datetime
from pathlib import Path

DATASET_DIR = Path(__file__).parent
DATASET_DIR.mkdir(parents=True, exist_ok=True)

random.seed(42)  # Deterministic output

RECURRING_GROUPS = [
    {
        "group_id": "RG-001",
        "system": "LabSys",
        "version": "5.4",
        "category": "Application",
        "symptom": "Lab results not loading or displaying blank screen",
        "knowledge_article_id": "KA-014",
        "resolution": "Restart LabSys Application Service",
        "resolution_source": "knowledge_article",
        "baseline_ttr_range": (18, 45),   # minutes — manual search time
        "assisted_ttr_range": (8, 18),    # minutes — with assistant
        "success_rate": 0.93,
    },
    {
        "group_id": "RG-002",
        "system": "PACSView",
        "version": "4.1",
        "category": "Performance",
        "symptom": "PACS image loading slow or hanging in radiology",
        "knowledge_article_id": "KA-019",
        "resolution": "PACS Image Cache Purge and DICOM Router Cycle",
        "resolution_source": "knowledge_article",
        "baseline_ttr_range": (22, 55),
        "assisted_ttr_range": (10, 22),
        "success_rate": 0.89,
    },
    {
        "group_id": "RG-003",
        "system": "MedFlow",
        "version": "3.2",
        "category": "Application",
        "symptom": "Medication order entry frozen or queue not processing",
        "knowledge_article_id": "KA-008",
        "resolution": "MedFlow Order Queue Clear and Process Recycle",
        "resolution_source": "knowledge_article",
        "baseline_ttr_range": (20, 50),
        "assisted_ttr_range": (9, 20),
        "success_rate": 0.91,
    },
    {
        "group_id": "RG-004",
        "system": "AuthGuard",
        "version": "2.8",
        "category": "Authentication",
        "symptom": "Clinical application SSO login failure across nursing stations",
        "knowledge_article_id": "KA-012",
        "resolution": "AuthGuard LDAP Gateway Synchronizer Reset",
        "resolution_source": "knowledge_article",
        "baseline_ttr_range": (25, 60),
        "assisted_ttr_range": (12, 25),
        "success_rate": 0.88,
    },
    {
        "group_id": "RG-005",
        "system": "EHRCore",
        "version": "6.0",
        "category": "UI/Application",
        "symptom": "Patient registration screen freeze or hang during intake",
        "knowledge_article_id": "KA-005",
        "resolution": "EHR Core UI Thread Recycling",
        "resolution_source": "knowledge_article",
        "baseline_ttr_range": (15, 40),
        "assisted_ttr_range": (7, 15),
        "success_rate": 0.94,
    },
    {
        "group_id": "RG-006",
        "system": "HL7Router",
        "version": "3.5",
        "category": "Integration",
        "symptom": "HL7 message queue delayed or stuck in pending",
        "knowledge_article_id": "KA-031",
        "resolution": "HL7 Router Queue Purge and Resend",
        "resolution_source": "knowledge_article",
        "baseline_ttr_range": (30, 65),
        "assisted_ttr_range": (13, 28),
        "success_rate": 0.87,
    },
]

def generate_recurring_dataset(total=300):
    dataset = []
    inc_id = 5000
    base_date = datetime.datetime(2025, 1, 1, 8, 0, 0)

    per_group = total // len(RECURRING_GROUPS)

    for group in RECURRING_GROUPS:
        for i in range(per_group):
            inc_id += 1
            created_at = base_date + datetime.timedelta(days=random.randint(0, 200), hours=random.randint(0, 12))

            # Baseline: manual search + resolution
            baseline_ttr = round(random.uniform(*group["baseline_ttr_range"]), 1)
            baseline_resolved_at = created_at + datetime.timedelta(minutes=baseline_ttr)

            # Assisted: with retrieval assistant
            assisted_ttr = round(random.uniform(*group["assisted_ttr_range"]), 1)
            assisted_resolved_at = created_at + datetime.timedelta(minutes=assisted_ttr)

            success = 1 if random.random() < group["success_rate"] else 0
            feedback_score = round(random.uniform(0.7, 1.0) if success else random.uniform(0.2, 0.5), 2)

            dataset.append({
                "incident_id": f"RDS-{inc_id}",
                "system": group["system"],
                "system_version": group["version"],
                "category": group["category"],
                "symptom": group["symptom"],
                "created_at": created_at.isoformat(),
                "baseline_resolved_at": baseline_resolved_at.isoformat(),
                "baseline_ttr_minutes": baseline_ttr,
                "assisted_resolved_at": assisted_resolved_at.isoformat(),
                "assisted_ttr_minutes": assisted_ttr,
                "resolution": group["resolution"],
                "resolution_source": group["resolution_source"],
                "recurring_group": group["group_id"],
                "knowledge_article_id": group["knowledge_article_id"],
                "resolution_success": success,
                "feedback_score": feedback_score,
                "dataset_label": "SYNTHETIC_BENCHMARK"
            })

    random.shuffle(dataset)
    dataset = dataset[:total]

    csv_path = DATASET_DIR / "hospital_it_incidents_recurring.csv"
    json_path = DATASET_DIR / "hospital_it_incidents_recurring.json"

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(dataset[0].keys()))
        writer.writeheader()
        writer.writerows(dataset)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)

    print(f"[+] Generated {len(dataset)} recurring incident records")
    print(f"    CSV: {csv_path}")
    print(f"    JSON: {json_path}")
    return dataset

if __name__ == "__main__":
    generate_recurring_dataset()
