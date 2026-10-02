from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "outputs"
SEED = 42
TEST_FRACTION = 0.20
SOURCE_SHEET = "Original dataset"


def auc_roc(y: np.ndarray, score: np.ndarray) -> float:
    order = np.argsort(score, kind="mergesort")
    ranks = np.empty(len(score), dtype=float)
    sorted_score = score[order]
    i = 0
    while i < len(order):
        j = i + 1
        while j < len(order) and sorted_score[j] == sorted_score[i]:
            j += 1
        ranks[order[i:j]] = (i + 1 + j) / 2
        i = j
    pos = int(y.sum())
    neg = len(y) - pos
    if pos == 0 or neg == 0:
        return float("nan")
    return float((ranks[y == 1].sum() - pos * (pos + 1) / 2) / (pos * neg))


def stratified_indices(y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(SEED)
    train_parts, test_parts = [], []
    for label in np.unique(y):
        idx = np.flatnonzero(y == label)
        rng.shuffle(idx)
        n_test = max(1, int(round(len(idx) * TEST_FRACTION)))
        test_parts.append(idx[:n_test])
        train_parts.append(idx[n_test:])
    train = np.concatenate(train_parts)
    test = np.concatenate(test_parts)
    rng.shuffle(train)
    rng.shuffle(test)
    return train, test


def average_precision(y: np.ndarray, score: np.ndarray) -> float:
    order = np.argsort(-score, kind="mergesort")
    ranked = y[order]
    positives = int(ranked.sum())
    if positives == 0:
        return float("nan")
    precision_at = np.cumsum(ranked) / (np.arange(len(ranked)) + 1)
    return float((precision_at * ranked).sum() / positives)


def metrics(y: np.ndarray, pred: np.ndarray, prob: np.ndarray) -> dict:
    tp = int(((y == 1) & (pred == 1)).sum())
    tn = int(((y == 0) & (pred == 0)).sum())
    fp = int(((y == 0) & (pred == 1)).sum())
    fn = int(((y == 1) & (pred == 0)).sum())
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {
        "n": int(len(y)), "threshold": 0.5,
        "accuracy": float((pred == y).mean()), "precision_churn": precision,
        "recall_churn": recall,
        "f1_churn": 2 * precision * recall / (precision + recall) if precision + recall else 0.0,
        "roc_auc": auc_roc(y, prob), "average_precision": average_precision(y, prob), "confusion_matrix": {"tn": tn, "fp": fp, "fn": fn, "tp": tp},
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    parser = argparse.ArgumentParser(description="Rebuild a held-out churn evaluation")
    parser.add_argument("--source", type=Path, default=ROOT / "data" / "dataset of marketing management lab.xlsx", help="Path to the authorized source workbook")
    parser.add_argument("--sheet", default=SOURCE_SHEET, help="Worksheet containing the source observations")
    args = parser.parse_args()
    source = args.source
    sheet = args.sheet
    if not source.exists():
        raise FileNotFoundError(f"Dataset workbook not found: {source}")
    df = pd.read_excel(source, sheet_name=sheet)
    if "Churn" not in df.columns or "CustomerID" not in df.columns:
        raise ValueError("Expected CustomerID and Churn columns in E Comm sheet")
    if df["CustomerID"].duplicated().any():
        raise ValueError("CustomerID is not unique; inspect source before modeling")

    y = pd.to_numeric(df["Churn"], errors="raise").astype(int).to_numpy()
    if set(np.unique(y)) != {0, 1}:
        raise ValueError("Expected a binary Churn target encoded 0/1")
    excluded = [c for c in ["CustomerID", "Churnclass", "Pred:Churnclass", "Pred:Conf.Churnclass"] if c in df.columns]
    feature_cols = [c for c in df.columns if c not in excluded + ["Churn"]]
    train_idx, test_idx = stratified_indices(y)
    train_raw = df.iloc[train_idx][feature_cols].copy()
    test_raw = df.iloc[test_idx][feature_cols].copy()
    y_train, y_test = y[train_idx], y[test_idx]

    numeric = [c for c in feature_cols if pd.api.types.is_numeric_dtype(train_raw[c])]
    categorical = [c for c in feature_cols if c not in numeric]
    medians = train_raw[numeric].median()
    train_raw[numeric] = train_raw[numeric].fillna(medians)
    test_raw[numeric] = test_raw[numeric].fillna(medians)
    modes = {c: (train_raw[c].mode(dropna=True).iloc[0] if not train_raw[c].mode(dropna=True).empty else "__MISSING__") for c in categorical}
    for c in categorical:
        train_raw[c] = train_raw[c].fillna(modes[c]).astype(str)
        test_raw[c] = test_raw[c].fillna(modes[c]).astype(str)
    train_encoded = pd.get_dummies(train_raw, columns=categorical, dtype=float)
    test_encoded = pd.get_dummies(test_raw, columns=categorical, dtype=float).reindex(columns=train_encoded.columns, fill_value=0.0)
    means = train_encoded.mean()
    scales = train_encoded.std(ddof=0).replace(0, 1.0)
    X_train = ((train_encoded - means) / scales).to_numpy(dtype=float)
    X_test = ((test_encoded - means) / scales).to_numpy(dtype=float)

    # L2-regularized binary logistic regression, optimized with full-batch gradient descent.
    weights = np.zeros(X_train.shape[1], dtype=float)
    intercept = 0.0
    learning_rate, l2, steps = 0.15, 0.02, 4000
    for _ in range(steps):
        logits = np.clip(X_train @ weights + intercept, -30, 30)
        probs = 1.0 / (1.0 + np.exp(-logits))
        grad_w = (X_train.T @ (probs - y_train)) / len(y_train) + l2 * weights
        grad_b = float((probs - y_train).mean())
        weights -= learning_rate * grad_w
        intercept -= learning_rate * grad_b

    test_prob = 1.0 / (1.0 + np.exp(-np.clip(X_test @ weights + intercept, -30, 30)))
    test_pred = (test_prob >= 0.5).astype(int)
    majority = int(np.bincount(y_train).argmax())
    baseline_pred = np.full(len(y_test), majority, dtype=int)
    baseline_prob = np.full(len(y_test), float(y_train.mean()))

    threshold_rows = []
    for threshold in [0.20, 0.30, 0.40, 0.50, 0.60]:
        m = metrics(y_test, (test_prob >= threshold).astype(int), test_prob)
        threshold_rows.append({"threshold": threshold, "precision_churn": m["precision_churn"], "recall_churn": m["recall_churn"], "f1_churn": m["f1_churn"], "predicted_at_risk": int((test_prob >= threshold).sum())})
    pd.DataFrame(threshold_rows).to_csv(OUT / "threshold_sensitivity.csv", index=False)
    effects = pd.DataFrame({"encoded_feature": train_encoded.columns, "standardized_log_odds_coefficient": weights})
    effects["odds_ratio_per_train_sd"] = np.exp(np.clip(effects["standardized_log_odds_coefficient"], -20, 20))
    effects.reindex(effects["standardized_log_odds_coefficient"].abs().sort_values(ascending=False).index).to_csv(OUT / "model_coefficients.csv", index=False)

    report = {
        "project": "E-commerce churn risk: current reproducible reconstruction",
        "source_file": source.name, "source_sheet": sheet,
        "records": int(len(df)), "features_used": feature_cols,
        "features_excluded": excluded, "duplicate_customer_ids": int(df.CustomerID.duplicated().sum()),
        "missing_values_by_feature": {k: int(v) for k, v in df[feature_cols].isna().sum().items()},
        "target_positive_rate": float(y.mean()), "split": {"method": "stratified holdout", "test_fraction": TEST_FRACTION, "seed": SEED, "train_n": int(len(train_idx)), "test_n": int(len(test_idx)), "train_churn_rate": float(y_train.mean()), "test_churn_rate": float(y_test.mean())},
        "preprocessing": {"numeric_missing": "median fitted on training split", "categorical_missing": "mode fitted on training split", "categorical_encoding": "one-hot; unseen test categories map to all-zero columns", "scaling": "mean/std fitted on training split"},
        "model": {"name": "L2-regularized logistic regression", "optimizer": "full-batch gradient descent", "steps": steps, "learning_rate": learning_rate, "l2": l2, "decision_threshold": 0.5},
        "metrics": {"majority_baseline": metrics(y_test, baseline_pred, baseline_prob), "logistic_regression": metrics(y_test, test_pred, test_prob)},
        "limitations": ["Single stratified holdout; no repeated cross-validation or threshold tuning.", "Results describe this dataset and split only; they do not establish business impact.", "Feature coefficients are associations in this fitted model, not causal effects."]
    }
    (OUT / "evaluation.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report["metrics"], indent=2))
    print(f"Wrote outputs to {OUT}")

if __name__ == "__main__":
    main()

