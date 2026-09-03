import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score, cross_val_predict
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support

BASE_DIR = Path(__file__).parent.parent
DATASET_PATH = BASE_DIR / "dataset" / "hospital_it_incidents_clean.csv"
MODEL_DIR = BASE_DIR / "backend" / "model_artifacts"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / "resolution_model.joblib"

def train_and_evaluate_model():
    print("=" * 70)
    print(" Hospital IT Resolution Assistant - ML Model Training Pipeline")
    print("=" * 70)

    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Cleaned dataset not found at {DATASET_PATH}. Run dataset/generate_dataset.py first.")

    df = pd.read_csv(DATASET_PATH)
    print(f"[+] Loaded cleaned dataset: {len(df)} records across {df['target_resolution_id'].nunique()} resolution classes.")

    # Combine description with system for training features
    X = df["description"] + " [SYSTEM: " + df["system"] + "]"
    y = df["target_resolution_id"]

    # Build Machine Learning Pipeline
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            stop_words="english",
            max_features=2500
        )),
        ("classifier", LogisticRegression(
            C=1.0,
            max_iter=1000,
            solver="lbfgs"
        ))
    ])

    # 5-Fold Stratified Cross Validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(pipeline, X, y, cv=cv, scoring="accuracy")

    print("\n[+] 5-Fold Cross-Validation Evaluation Results:")
    print(f"    - Fold Accuracy Scores: {[round(s, 4) for s in cv_scores]}")
    print(f"    - Mean Accuracy:        {np.mean(cv_scores) * 100:.2f}% (±{np.std(cv_scores) * 100:.2f}%)")

    # Predict via CV to get detailed classification metrics
    y_pred = cross_val_predict(pipeline, X, y, cv=cv)
    acc = accuracy_score(y, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y, y_pred, average="weighted")

    print("\n[+] Detailed Metrics:")
    print(f"    - Overall Accuracy:  {acc * 100:.2f}%")
    print(f"    - Precision:         {precision * 100:.2f}%")
    print(f"    - Recall:            {recall * 100:.2f}%")
    print(f"    - F1-Score:          {f1 * 100:.2f}%")

    print("\n[+] Classification Report per Knowledge Article:")
    print(classification_report(y, y_pred))

    # Train final pipeline on full dataset
    pipeline.fit(X, y)

    # Save model artifacts using joblib
    joblib.dump(pipeline, MODEL_PATH)
    print(f"[+] Model successfully trained & saved to: {MODEL_PATH}")
    print("=" * 70)

    return {
        "accuracy": round(acc * 100, 2),
        "f1_score": round(f1 * 100, 2),
        "precision": round(precision * 100, 2),
        "recall": round(recall * 100, 2),
        "dataset_records": len(df),
        "classes_count": df["target_resolution_id"].nunique()
    }

if __name__ == "__main__":
    train_and_evaluate_model()
