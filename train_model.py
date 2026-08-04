"""
Trains ML models on the extracted URL features to classify phishing vs
legitimate websites. Compares Logistic Regression, Random Forest, and
Gradient Boosting; saves the best-performing model to disk.
"""

import csv
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

from feature_extraction import extract_features, FEATURE_NAMES


def load_dataset(path="data/urls_dataset.csv"):
    urls, labels = [], []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            urls.append(row["url"])
            labels.append(int(row["label"]))
    return urls, labels


def build_feature_matrix(urls):
    rows = [extract_features(u) for u in urls]
    return pd.DataFrame(rows, columns=FEATURE_NAMES)


def main():
    print("Loading dataset...")
    urls, labels = load_dataset()
    X = build_feature_matrix(urls)
    y = labels
    print(f"Dataset shape: {X.shape}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Random Forest": RandomForestClassifier(n_estimators=200, random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(random_state=42),
    }

    results = {}
    best_model_name, best_model, best_f1 = None, None, -1

    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)

        acc = accuracy_score(y_test, preds)
        prec = precision_score(y_test, preds)
        rec = recall_score(y_test, preds)
        f1 = f1_score(y_test, preds)
        cm = confusion_matrix(y_test, preds)

        results[name] = {"accuracy": acc, "precision": prec, "recall": rec, "f1": f1, "cm": cm}

        print(f"\n{name}")
        print(f"  Accuracy : {acc:.4f}")
        print(f"  Precision: {prec:.4f}")
        print(f"  Recall   : {rec:.4f}")
        print(f"  F1-score : {f1:.4f}")
        print(f"  Confusion Matrix:\n{cm}")

        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_model = model

    print(f"\n>>> Best model: {best_model_name} (F1={best_f1:.4f})")

    # Save best model + feature names + metrics for the report
    joblib.dump(best_model, "model/phishing_model.pkl")
    joblib.dump(FEATURE_NAMES, "model/feature_names.pkl")

    with open("model/results_summary.txt", "w") as f:
        f.write(f"Best model: {best_model_name}\n\n")
        for name, r in results.items():
            f.write(f"{name}:\n")
            f.write(f"  Accuracy : {r['accuracy']:.4f}\n")
            f.write(f"  Precision: {r['precision']:.4f}\n")
            f.write(f"  Recall   : {r['recall']:.4f}\n")
            f.write(f"  F1-score : {r['f1']:.4f}\n")
            f.write(f"  Confusion Matrix:\n{r['cm']}\n\n")

    print("Model saved to model/phishing_model.pkl")

    # Feature importance (if available) - useful for the presentation
    if hasattr(best_model, "feature_importances_"):
        importances = sorted(
            zip(FEATURE_NAMES, best_model.feature_importances_),
            key=lambda x: x[1], reverse=True
        )
        print("\nTop 10 important features:")
        for name, imp in importances[:10]:
            print(f"  {name}: {imp:.4f}")


if __name__ == "__main__":
    main()
