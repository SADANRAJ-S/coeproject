import pytest
import os
import joblib
from pathlib import Path
from dataset.generate_dataset import generate_cleaned_dataset, DATASET_DIR
from scripts.train_model import train_and_evaluate_model, MODEL_PATH
from backend.retrieval_engine import rank_recommendations

def test_dataset_generation():
    """Test clean dataset generation."""
    dataset = generate_cleaned_dataset(total_count=100)
    assert len(dataset) == 100
    assert (DATASET_DIR / "hospital_it_incidents_clean.csv").exists()
    assert (DATASET_DIR / "hospital_it_incidents_clean.json").exists()

def test_model_training_and_persistence():
    """Test model training pipeline and joblib artifact persistence."""
    metrics = train_and_evaluate_model()
    assert metrics["accuracy"] >= 85.0, "Model accuracy should be at least 85%"
    assert metrics["f1_score"] >= 85.0
    assert MODEL_PATH.exists(), "Joblib model artifact must be created"

    # Test loading persistent model
    pipeline = joblib.load(MODEL_PATH)
    assert pipeline is not None
    preds = pipeline.predict(["Lab results not loading in ICU [SYSTEM: LabSys]"])
    assert preds[0] == "KA-014"

def test_ml_retrieval_integration():
    """Test inference integration inside retrieval engine."""
    res = rank_recommendations("Lab results are not loading for users.", "LabSys", "5.4")
    verified = res.get("verified_recommendations", [])
    assert len(verified) > 0
    top_rec = verified[0]
    assert top_rec["recommendation_id"] == "KA-014"
    assert top_rec["relevance_score"] >= 50.0
