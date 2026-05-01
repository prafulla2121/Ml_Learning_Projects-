from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier, XGBRegressor

from amazon_review_intel.features.engineering import STRUCTURED_FEATURES


@dataclass
class BaselineArtifacts:
    vectorizer: TfidfVectorizer
    scaler: StandardScaler
    clf: XGBClassifier
    reg: XGBRegressor


def build_feature_matrix(
    df: pd.DataFrame,
    vectorizer: TfidfVectorizer | None = None,
    scaler: StandardScaler | None = None,
    fit: bool = False,
):
    texts = df["full_text"].fillna("").tolist()
    struct = df[STRUCTURED_FEATURES].fillna(0.0).astype(float).values

    if vectorizer is None:
        raise ValueError("Vectorizer must be provided.")
    if scaler is None:
        raise ValueError("Scaler must be provided.")

    if fit:
        x_text = vectorizer.fit_transform(texts)
        x_struct = scaler.fit_transform(struct)
    else:
        x_text = vectorizer.transform(texts)
        x_struct = scaler.transform(struct)

    x = hstack([x_text, csr_matrix(x_struct)], format="csr")
    return x


def make_vectorizer(config: dict) -> TfidfVectorizer:
    return TfidfVectorizer(
        max_features=int(config["tfidf_max_features"]),
        ngram_range=(int(config["tfidf_ngram_min"]), int(config["tfidf_ngram_max"])),
        min_df=5,
        sublinear_tf=True,
        strip_accents="unicode",
    )


def make_classifier(cfg: dict) -> XGBClassifier:
    return XGBClassifier(
        objective="multi:softmax",
        num_class=5,
        n_estimators=int(cfg["n_estimators"]),
        learning_rate=float(cfg["learning_rate"]),
        max_depth=int(cfg["max_depth"]),
        subsample=float(cfg["subsample"]),
        colsample_bytree=float(cfg["colsample_bytree"]),
        reg_lambda=float(cfg["reg_lambda"]),
        tree_method="hist",
        eval_metric="mlogloss",
        n_jobs=-1,
    )


def make_regressor(cfg: dict) -> XGBRegressor:
    return XGBRegressor(
        objective="reg:squarederror",
        n_estimators=int(cfg["n_estimators"]),
        learning_rate=float(cfg["learning_rate"]),
        max_depth=int(cfg["max_depth"]),
        subsample=float(cfg["subsample"]),
        colsample_bytree=float(cfg["colsample_bytree"]),
        reg_lambda=float(cfg["reg_lambda"]),
        tree_method="hist",
        eval_metric="rmse",
        n_jobs=-1,
    )


def inverse_freq_weights(stars: np.ndarray) -> np.ndarray:
    values, counts = np.unique(stars, return_counts=True)
    n = float(len(stars))
    k = float(len(values))
    balanced = {int(v): n / (k * float(c)) for v, c in zip(values, counts)}
    return np.array([balanced[int(v)] for v in stars], dtype=float)
