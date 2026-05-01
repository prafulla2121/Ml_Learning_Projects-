from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from amazon_review_intel.config import ensure_dirs, load_config
from amazon_review_intel.features.engineering import (
    STRUCTURED_FEATURES,
    build_structured_features,
    build_targets,
    clean_text,
)
from amazon_review_intel.logging_utils import get_logger

LOGGER = get_logger(__name__)


def preprocess(config: dict) -> None:
    data_cfg = config["data"]
    raw_dir = Path(data_cfg["raw_dir"])
    processed_dir = Path(data_cfg["processed_dir"])
    ensure_dirs([processed_dir])

    reviews = pd.read_parquet(raw_dir / "amazon_reviews.parquet")
    meta = pd.read_parquet(raw_dir / "amazon_meta.parquet")

    merge_cols = ["parent_asin", "price", "main_category", "average_rating", "rating_number"]
    merge_cols = [c for c in merge_cols if c in meta.columns]
    df = reviews.merge(meta[merge_cols], on="parent_asin", how="left")
    df["title"] = df["title"].fillna("")
    df["text"] = df["text"].fillna("")
    df["full_text"] = (df["title"] + " " + df["text"]).apply(clean_text)
    df = df[df["full_text"].str.len() >= int(data_cfg["min_text_chars"])].copy()
    df = df[df["rating"].notna()].copy()

    df = build_targets(df)
    df = build_structured_features(df)
    df["split_id"] = range(len(df))

    y = df["label_stars"]
    test_size = float(data_cfg["test_size"])
    val_size = float(data_cfg["val_size"])
    train_df, test_df = train_test_split(
        df, test_size=test_size, random_state=int(config["project"]["seed"]), stratify=y
    )
    relative_val = val_size / (1.0 - test_size)
    train_df, val_df = train_test_split(
        train_df,
        test_size=relative_val,
        random_state=int(config["project"]["seed"]),
        stratify=train_df["label_stars"],
    )

    train_df.to_parquet(processed_dir / "train.parquet", index=False)
    val_df.to_parquet(processed_dir / "val.parquet", index=False)
    test_df.to_parquet(processed_dir / "test.parquet", index=False)

    stats = {
        "train_rows": int(len(train_df)),
        "val_rows": int(len(val_df)),
        "test_rows": int(len(test_df)),
        "star_distribution": train_df["label_stars"].value_counts(normalize=True).sort_index().to_dict(),
        "structured_features": STRUCTURED_FEATURES,
    }
    with (processed_dir / "dataset_stats.json").open("w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    LOGGER.info("Preprocessed rows: %s", len(df))
    LOGGER.info("Split sizes train=%s val=%s test=%s", len(train_df), len(val_df), len(test_df))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preprocess Amazon review data.")
    parser.add_argument("--config", default="configs/default.yaml", help="Path to YAML config.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)
    preprocess(cfg)


if __name__ == "__main__":
    main()

