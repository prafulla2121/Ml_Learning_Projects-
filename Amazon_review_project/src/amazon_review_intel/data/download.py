from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from datasets import load_dataset
from huggingface_hub import hf_hub_download

from amazon_review_intel.config import ensure_dirs, load_config
from amazon_review_intel.logging_utils import get_logger

LOGGER = get_logger(__name__)


def _sample_dataset(ds, size: int | None, seed: int):
    if size is None:
        return ds
    if size >= len(ds):
        return ds
    return ds.shuffle(seed=seed).select(range(size))


def _category_from_config_name(value: str) -> str:
    if value.startswith("raw_review_"):
        return value.replace("raw_review_", "", 1)
    if value.startswith("raw_meta_"):
        return value.replace("raw_meta_", "", 1)
    return value


def _load_amazon_jsonl(repo_id: str, path_in_repo: str) -> pd.DataFrame:
    local_path = hf_hub_download(repo_id=repo_id, filename=path_in_repo, repo_type="dataset")
    return pd.read_json(local_path, lines=True)


def download_amazon(config: dict) -> None:
    seed = int(config["project"]["seed"])
    data_cfg = config["data"]
    raw_dir = Path(data_cfg["raw_dir"])
    ensure_dirs([raw_dir])

    category = _category_from_config_name(data_cfg["review_config"])
    review_file = f"raw/review_categories/{category}.jsonl"
    meta_file = f"raw/meta_categories/meta_{category}.jsonl"

    LOGGER.info("Downloading Amazon reviews from %s", review_file)
    reviews = _load_amazon_jsonl(data_cfg["amazon_dataset"], review_file)
    if data_cfg.get("sample_size_reviews") and len(reviews) > int(data_cfg["sample_size_reviews"]):
        reviews = reviews.sample(n=int(data_cfg["sample_size_reviews"]), random_state=seed)
    reviews = reviews.reset_index(drop=True)
    reviews_path = raw_dir / "amazon_reviews.parquet"
    reviews.to_parquet(reviews_path, index=False)
    LOGGER.info("Saved %s rows to %s", len(reviews), reviews_path)

    LOGGER.info("Downloading Amazon metadata from %s", meta_file)
    meta = _load_amazon_jsonl(data_cfg["amazon_dataset"], meta_file)
    if data_cfg.get("sample_size_meta") and len(meta) > int(data_cfg["sample_size_meta"]):
        meta = meta.sample(n=int(data_cfg["sample_size_meta"]), random_state=seed)

    parent_asins = set(reviews["parent_asin"].dropna().unique().tolist())
    if parent_asins:
        meta = meta[meta["parent_asin"].isin(parent_asins)]
    meta_path = raw_dir / "amazon_meta.parquet"
    meta.to_parquet(meta_path, index=False)
    LOGGER.info("Saved %s rows to %s", len(meta), meta_path)


def download_absa(config: dict) -> None:
    data_cfg = config["data"]
    raw_dir = Path(data_cfg["raw_dir"])
    LOGGER.info("Loading ABSA dataset: %s", data_cfg["absa_dataset"])
    try:
        absa_ds = load_dataset(data_cfg["absa_dataset"])
    except Exception:
        LOGGER.warning("Primary ABSA dataset unavailable. Falling back to NEUDM/semeval-2014.")
        absa_ds = load_dataset("NEUDM/semeval-2014")
    for split_name, split_ds in absa_ds.items():
        df = split_ds.to_pandas()
        out_path = raw_dir / f"absa_{split_name}.parquet"
        df.to_parquet(out_path, index=False)
        LOGGER.info("Saved ABSA split %s (%s rows) to %s", split_name, len(df), out_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download Amazon + ABSA datasets.")
    parser.add_argument("--config", default="configs/default.yaml", help="Path to YAML config.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)
    download_amazon(cfg)
    download_absa(cfg)
    LOGGER.info("Download complete.")


if __name__ == "__main__":
    main()
