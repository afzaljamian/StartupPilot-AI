
import json
import joblib
import pandas as pd

from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
    balanced_accuracy_score
)


# Project paths
ROOT = Path(__file__).resolve().parents[3]

DATASET_PATH = ROOT / "datasets" / "startup data.csv"
MODEL_DIR = ROOT / "backend" / "app" / "ml" / "artifacts"

MODEL_DIR.mkdir(parents=True, exist_ok=True)


def train_models():

    print("\n========== STARTUPPILOT AI ML EVALUATION ==========\n")

    # 1. Load dataset
    df = pd.read_csv(DATASET_PATH)

    print("Original dataset shape:", df.shape)

    # 2. Remove duplicate rows
    df = df.drop_duplicates()

    # 3. Remove records without target
    df = df.dropna(subset=["status"])

    # 4. Encode target
    df["status"] = df["status"].map({
        "acquired": 1,
        "closed": 0
    })

    df = df.dropna(subset=["status"])

    y = df["status"].astype(int)

    # 5. Remove target and leakage / identifier columns
    excluded_columns = [
        "status",
        "labels",
        "closed_at",
        "last_funding_at",
        "last_funding_at",
        "age_last_funding_year",
        "age_last_milestone_year",
        "Unnamed: 0",
        "Unnamed: 6",
        "id",
        "object_id",
        "name",
        "zip_code",
        "city",
        "state_code",
        "state_code.1",
        "latitude",
        "longitude",
        "founded_at",
        "first_funding_at",
        "is_top500"
    ]

    X = df.drop(
        columns=excluded_columns,
        errors="ignore"
    )

    # 6. Remove constant columns
    X = X.loc[:, X.nunique(dropna=False) > 1]

    print("Features used:", X.columns.tolist())
    print("Number of features:", X.shape[1])

    # 7. Identify column types
    numerical_columns = X.select_dtypes(
        include=["number"]
    ).columns.tolist()

    categorical_columns = X.select_dtypes(
        exclude=["number"]
    ).columns.tolist()

    # 8. Preprocessing
    numerical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore"))
    ])

    preprocessing = ColumnTransformer([
        ("numeric", numerical_pipeline, numerical_columns),
        ("categorical", categorical_pipeline, categorical_columns)
    ])

    # 9. Stratified train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y
    )

    print("\nTraining records:", len(X_train))
    print("Testing records:", len(X_test))

    # 10. Define models
    models = {
        "Logistic Regression": LogisticRegression(
            max_iter=2000,
            class_weight="balanced"
        ),

        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            class_weight="balanced"
        ),

        "Extra Trees": ExtraTreesClassifier(
            n_estimators=200,
            random_state=42,
            class_weight="balanced"
        )
    }

    results = []
    trained_models = {}

    # 11. Train and evaluate
    for name, model in models.items():

        pipeline = Pipeline([
            ("preprocessing", preprocessing),
            ("classifier", model)
        ])

        pipeline.fit(X_train, y_train)

        predictions = pipeline.predict(X_test)
        probabilities = pipeline.predict_proba(X_test)[:, 1]

        metrics = {
            "model": name,
            "accuracy": round(
                accuracy_score(y_test, predictions), 4
            ),
            "balanced_accuracy": round(
                balanced_accuracy_score(y_test, predictions), 4
            ),
            "precision": round(
                precision_score(y_test, predictions, zero_division=0), 4
            ),
            "recall": round(
                recall_score(y_test, predictions, zero_division=0), 4
            ),
            "f1_score": round(
                f1_score(y_test, predictions, zero_division=0), 4
            ),
            "roc_auc": round(
                roc_auc_score(y_test, probabilities), 4
            ),
            "confusion_matrix": confusion_matrix(
                y_test, predictions, labels=[0, 1]
            ).tolist()
        }

        results.append(metrics)
        trained_models[name] = pipeline

        print("\nMODEL:", name)
        print(json.dumps(metrics, indent=4))

        print("\nClassification report:")
        print(classification_report(
            y_test,
            predictions,
            target_names=["closed", "acquired"],
            zero_division=0
        ))

    # 12. Select model using test F1 for this prototype.
    # Final model selection should use validation/CV, then test once.
    best = max(results, key=lambda item: item["f1_score"])

    best_name = best["model"]

    # Save model
    joblib.dump(
        trained_models[best_name],
        MODEL_DIR / "best_startup_model.joblib"
    )

    # Save actual evaluation results
    report = {
        "dataset": "Historical Startup Dataset",
        "total_records": len(df),
        "training_records": len(X_train),
        "testing_records": len(X_test),
        "target": "status",
        "target_mapping": {
            "closed": 0,
            "acquired": 1
        },
        "excluded_columns": excluded_columns,
        "feature_columns": X.columns.tolist(),
        "evaluation": "Stratified 75/25 train-test split",
        "random_state": 42,
        "best_model": best_name,
        "models": results,
        "limitations": [
            "Historical outcome classification, not guaranteed startup success prediction.",
            "Results depend on the dataset and its feature availability.",
            "Retrospective features may not be available when a new startup idea is first evaluated.",
            "Single train-test split; cross-validation is needed for stronger evidence."
        ]
    }

    with open(
        MODEL_DIR / "evaluation_results.json",
        "w"
    ) as file:
        json.dump(report, file, indent=4)

    print("\n========== FINAL MODEL COMPARISON ==========")

    print(pd.DataFrame(results).drop(
        columns=["confusion_matrix"]
    ).to_string(index=False))

    print("\nSelected model:", best_name)

    print("\nSaved model and evaluation results in:")
    print(MODEL_DIR)

    return report


if __name__ == "__main__":
    train_models()
