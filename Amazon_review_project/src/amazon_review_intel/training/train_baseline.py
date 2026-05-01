from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler

from amazon_review_intel.config import ensure_dirs, load_config
from amazon_review_intel.evaluation.metrics import flatten_dict, helpfulness_metrics, star_metrics
from amazon_review_intel.logging_utils import get_logger
from amazon_review_intel.models.baseline import (
    build_feature_matrix,
    inverse_freq_weights,
    make_classifier,
    make_regressor,
    make_vectorizer,
)

LOGGER = get_logger(__name__)


def maybe_log_mlflow(config: dict, params: dict, metrics: dict) -> None:
    if not config["mlflow"]["enabled"]:
        return
    try:
        import mlflow

        mlflow.set_experiment(config["mlflow"]["experiment_name"])
        with mlflow.start_run(run_name="baseline_xgboost"):
            mlflow.log_params(params)
            mlflow.log_metrics(metrics)
    except Exception as exc:  # pragma: no cover
        LOGGER.warning("MLflow logging failed: %s", exc)


def train_baseline(config: dict) -> None:
    processed_dir = Path(config["data"]["processed_dir"])
    artifact_dir = Path(config["project"]["artifact_dir"]) / "baseline"
    ensure_dirs([artifact_dir])

    train_df = pd.read_parquet(processed_dir / "train.parquet")
    val_df = pd.read_parquet(processed_dir / "val.parquet")
    test_df = pd.read_parquet(processed_dir / "test.parquet")

    vectorizer = make_vectorizer(config["baseline"])
    scaler = StandardScaler()

    x_train = build_feature_matrix(train_df, vectorizer=vectorizer, scaler=scaler, fit=True)
    x_val = build_feature_matrix(val_df, vectorizer=vectorizer, scaler=scaler, fit=False)
    x_test = build_feature_matrix(test_df, vectorizer=vectorizer, scaler=scaler, fit=False)

    y_train_stars = train_df["label_stars"].astype(int).values
    y_val_stars = val_df["label_stars"].astype(int).values
    y_test_stars = test_df["label_stars"].astype(int).values

    y_train_help = train_df["label_helpfulness"].astype(float).values
    y_val_help = val_df["label_helpfulness"].astype(float).values
    y_test_help = test_df["label_helpfulness"].astype(float).values

    clf = make_classifier(config["baseline"]["xgb_classifier"])
    clf.fit(x_train, y_train_stars - 1, sample_weight=inverse_freq_weights(y_train_stars))

    reg = make_regressor(config["baseline"]["xgb_regressor"])
    reg.fit(x_train, y_train_help)

    val_pred_stars = clf.predict(x_val) + 1
    test_pred_stars = clf.predict(x_test) + 1
    val_pred_help = reg.predict(x_val)
    test_pred_help = reg.predict(x_test)

    val_star = star_metrics(y_val_stars, val_pred_stars)
    test_star = star_metrics(y_test_stars, test_pred_stars)
    val_help = helpfulness_metrics(y_val_help, val_pred_help)
    test_help = helpfulness_metrics(y_test_help, test_pred_help)

    metrics = {}
    metrics.update(flatten_dict("val_star", val_star))
    metrics.update(flatten_dict("test_star", test_star))
    metrics.update(flatten_dict("val_help", val_help))
    metrics.update(flatten_dict("test_help", test_help))

    params = {
        "tfidf_max_features": int(config["baseline"]["tfidf_max_features"]),
        "tfidf_ngram_max": int(config["baseline"]["tfidf_ngram_max"]),
        "clf_n_estimators": int(config["baseline"]["xgb_classifier"]["n_estimators"]),
        "reg_n_estimators": int(config["baseline"]["xgb_regressor"]["n_estimators"]),
    }
    maybe_log_mlflow(config, params, metrics)

    joblib.dump(vectorizer, artifact_dir / "tfidf_vectorizer.joblib")
    joblib.dump(scaler, artifact_dir / "structured_scaler.joblib")
    joblib.dump(clf, artifact_dir / "star_classifier.joblib")
    joblib.dump(reg, artifact_dir / "helpfulness_regressor.joblib")
    with (artifact_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    LOGGER.info("Baseline metrics: %s", metrics)
    LOGGER.info("Saved baseline artifacts to %s", artifact_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train TF-IDF + XGBoost baseline models.")
    parser.add_argument("--config", default="configs/default.yaml", help="Path to YAML config.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)
    train_baseline(cfg)


if __name__ == "__main__":
    main()

