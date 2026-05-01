from __future__ import annotations

import re

import numpy as np
import pandas as pd

STRUCTURED_FEATURES = [
    "review_length",
    "word_count",
    "exclamation_count",
    "question_count",
    "caps_ratio",
    "avg_word_length",
    "price_log",
    "is_verified",
    "category_enc",
    "rating_gap",
    "rating_number",
]


def clean_text(value: str) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text


def build_targets(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["label_stars"] = out["rating"].astype(int).clip(1, 5)
    out["review_age_days"] = (
        pd.Timestamp.utcnow().tz_localize(None) - pd.to_datetime(out["timestamp"], unit="ms")
    ).dt.days.clip(lower=0)
    out["helpfulness_rate"] = out["helpful_vote"].fillna(0) / (out["review_age_days"] + 1)
    out["label_helpfulness"] = np.log1p(out["helpfulness_rate"])
    return out


def build_structured_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["review_length"] = out["text"].fillna("").str.len()
    out["word_count"] = out["text"].fillna("").str.split().str.len()
    out["exclamation_count"] = out["text"].fillna("").str.count("!")
    out["question_count"] = out["text"].fillna("").str.count(r"\?")
    out["caps_ratio"] = out["text"].fillna("").str.count(r"[A-Z]") / (out["review_length"] + 1)
    out["avg_word_length"] = out["text"].fillna("").apply(
        lambda t: float(np.mean([len(w) for w in t.split()])) if t.split() else 0.0
    )
    out["price_clean"] = pd.to_numeric(
        out.get("price", pd.Series(index=out.index)).astype(str).str.replace(r"[^\d.]", "", regex=True),
        errors="coerce",
    )
    median_price = out["price_clean"].median() if not out["price_clean"].dropna().empty else 0.0
    out["price_log"] = np.log1p(out["price_clean"].fillna(median_price))
    out["is_verified"] = out["verified_purchase"].fillna(False).astype(int)
    out["main_category"] = out["main_category"].fillna("Unknown")
    out["category_enc"] = pd.factorize(out["main_category"])[0]
    if "label_stars" in out.columns:
        stars_ref = out["label_stars"]
    else:
        stars_ref = out["rating"].fillna(4).astype(float)
    out["average_rating"] = out["average_rating"].fillna(stars_ref)
    out["rating_gap"] = stars_ref - out["average_rating"]
    out["rating_number"] = out["rating_number"].fillna(0)
    return out
