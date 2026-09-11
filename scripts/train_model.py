"""
train_model.py — Hospital IT Resolution Assistant Model Training Pipeline
Trains a TF-IDF + Logistic Regression classifier on the cleaned incident dataset.
Uses 5-fold stratified cross-validation for reliable evaluation.
"""
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score, cross_val_predict
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support
from dataset.generate_dataset import generate_cleaned_dataset

BASE_DIR = Path(__file__).parent.parent
DATASET_PATH = BASE_DIR / "dataset" / "hospital_it_incidents_clean.csv"
MODEL_DIR = BASE_DIR / "backend" / "model_artifacts"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / "resolution_model.joblib"


def train_and_evaluate_model(total_count: int = 500):
    print("=" * 70)
    print("  Hospital IT Resolution Assistant — ML Model Training Pipeline")
    print("=" * 70)

    # Step 1: Generate fresh dataset
    print("\n[1] Generating cleaned dataset...")
    generate_cleaned_dataset(total_count=total_count)

    # Step 2: Load dataset
    df = pd.read_csv(DATASET_PATH)
    print(f"\n[2] Loaded dataset: {len(df)} records, "
          f"{df['target_resolution_id'].nunique()} resolution classes.")
    print(f"    Classes: {sorted(df['target_resolution_id'].unique())}")

    # Step 3: Feature engineering
    # Combine description + system + category for richer features
    X = (
        df["description"] + " [SYSTEM: " + df["system"] + "]"
        + " [CAT: " + df["category"] + "]"
    )
    y = df["target_resolution_id"]

    # Step 4: Build pipeline with tuned hyperparameters
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 3),        # unigram + bigram + trigram
            sublinear_tf=True,
            stop_words="english",
            max_features=5000,         # increased vocab
            min_df=2,                  # ignore very rare terms
            analyzer="word"
        )),
        ("classifier", LogisticRegression(
            C=5.0,
            max_iter=2000,
            solver="lbfgs",
            class_weight="balanced"
        ))
    ])

    # Step 5: 5-fold stratified cross-validation
    print("\n[3] Running 5-fold stratified cross-validation...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(pipeline, X, y, cv=cv, scoring="accuracy")

    print(f"    Fold Accuracy Scores : {[round(s*100, 2) for s in cv_scores]}")
    print(f"    Mean CV Accuracy     : {np.mean(cv_scores)*100:.2f}% "
          f"(+/- {np.std(cv_scores)*100:.2f}%)")

    # Step 6: Detailed per-class metrics from CV predictions
    y_pred = cross_val_predict(pipeline, X, y, cv=cv)
    acc = accuracy_score(y, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y, y_pred, average="weighted")

    print(f"\n[4] Weighted Metrics (CV predictions):")
    print(f"    Accuracy  : {acc*100:.2f}%")
    print(f"    Precision : {precision*100:.2f}%")
    print(f"    Recall    : {recall*100:.2f}%")
    print(f"    F1-Score  : {f1*100:.2f}%")

    print("\n[5] Classification Report per Knowledge Article:")
    print(classification_report(y, y_pred))

    # Step 7: Train final model on full dataset
    print("[6] Training final model on full dataset...")
    pipeline.fit(X, y)

    # Step 8: Save joblib artifact
    joblib.dump(pipeline, MODEL_PATH)
    print(f"[7] Model saved: {MODEL_PATH}")
    print("=" * 70)

    return {
        "accuracy": round(acc * 100, 2),
        "f1_score": round(f1 * 100, 2),
        "precision": round(precision * 100, 2),
        "recall": round(recall * 100, 2),
        "cv_mean_accuracy": round(float(np.mean(cv_scores)) * 100, 2),
        "cv_std_accuracy": round(float(np.std(cv_scores)) * 100, 2),
        "dataset_records": len(df),
        "classes_count": df["target_resolution_id"].nunique()
    }


if __name__ == "__main__":
    metrics = train_and_evaluate_model()
    print(f"\nFinal Model Metrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v}")
