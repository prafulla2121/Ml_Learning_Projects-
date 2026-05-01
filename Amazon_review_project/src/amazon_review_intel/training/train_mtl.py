from __future__ import annotations

import argparse
import ast
import itertools
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import f1_score
from torch import nn
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import AutoTokenizer, get_cosine_schedule_with_warmup

from amazon_review_intel.config import ensure_dirs, load_config
from amazon_review_intel.evaluation.metrics import helpfulness_metrics, star_metrics
from amazon_review_intel.logging_utils import get_logger
from amazon_review_intel.models.mtl import ABSA_LABELS, ABSA_LABEL_TO_ID, AmazonMTLModel

LOGGER = get_logger(__name__)


def maybe_log_mlflow(config: dict, params: dict, metrics: dict) -> None:
    if not config["mlflow"]["enabled"]:
        return
    try:
        import mlflow

        mlflow.set_experiment(config["mlflow"]["experiment_name"])
        with mlflow.start_run(run_name="roberta_mtl"):
            mlflow.log_params(params)
            mlflow.log_metrics(metrics)
    except Exception as exc:  # pragma: no cover
        LOGGER.warning("MLflow logging failed: %s", exc)


@dataclass
class TokenizedSample:
    input_ids: torch.Tensor
    attention_mask: torch.Tensor


class AmazonReviewDataset(Dataset):
    def __init__(self, df: pd.DataFrame, tokenizer, max_length: int):
        self.df = df.reset_index(drop=True)
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        row = self.df.iloc[idx]
        enc = self.tokenizer(
            row["full_text"],
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt",
        )
        return {
            "input_ids": enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "star_labels": torch.tensor(int(row["label_stars"]) - 1, dtype=torch.long),
            "help_labels": torch.tensor(float(row["label_helpfulness"]), dtype=torch.float),
        }


def _extract_sentence(row: pd.Series) -> str:
    if "sentence" in row and pd.notna(row["sentence"]):
        return str(row["sentence"])
    if "text" in row and pd.notna(row["text"]):
        return str(row["text"])
    if "input" in row and pd.notna(row["input"]):
        val = row["input"]
        if isinstance(val, list) and val:
            return str(val[0])
        return str(val)
    return ""


def _safe_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = ast.literal_eval(value)
            if isinstance(parsed, list):
                return parsed
        except (SyntaxError, ValueError):
            return []
    return []


def _extract_aspects_and_polarities(row: pd.Series) -> list[tuple[str, str]]:
    if "aspect_terms" in row and "polarities" in row:
        terms = _safe_list(row["aspect_terms"])
        pols = _safe_list(row["polarities"])
        return [(str(t), str(p)) for t, p in zip(terms, pols)]
    if "output" in row:
        out = _safe_list(row["output"])
        pairs: list[tuple[str, str]] = []
        for item in out:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                pairs.append((str(item[0]), str(item[1])))
        return pairs
    return []


def _polarity_to_tags(pol: str) -> tuple[str, str]:
    p = pol.lower()
    if p.startswith("pos"):
        return "B-POS", "I-POS"
    if p.startswith("neg"):
        return "B-NEG", "I-NEG"
    return "B-NEU", "I-NEU"


class ABSADataset(Dataset):
    def __init__(self, df: pd.DataFrame, tokenizer, max_length: int):
        self.df = df.reset_index(drop=True)
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        row = self.df.iloc[idx]
        sentence = _extract_sentence(row)
        pairs = _extract_aspects_and_polarities(row)

        enc = self.tokenizer(
            sentence,
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_offsets_mapping=True,
            return_tensors="pt",
        )
        input_ids = enc["input_ids"].squeeze(0)
        attention_mask = enc["attention_mask"].squeeze(0)
        offsets = enc["offset_mapping"].squeeze(0).tolist()

        labels = np.full((len(offsets),), fill_value=ABSA_LABEL_TO_ID["O"], dtype=np.int64)
        labels[(attention_mask == 0).numpy()] = -100

        lower_sentence = sentence.lower()
        for term, polarity in pairs:
            term_norm = str(term).strip()
            if not term_norm:
                continue
            start_char = lower_sentence.find(term_norm.lower())
            if start_char == -1:
                continue
            end_char = start_char + len(term_norm)
            b_tag, i_tag = _polarity_to_tags(polarity)
            first_token = True
            for i, (s, e) in enumerate(offsets):
                if s == 0 and e == 0:
                    labels[i] = -100
                    continue
                if s >= start_char and e <= end_char:
                    labels[i] = ABSA_LABEL_TO_ID[b_tag if first_token else i_tag]
                    first_token = False

        labels[(attention_mask == 0).numpy()] = -100
        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "absa_labels": torch.tensor(labels, dtype=torch.long),
        }


def cycle_or_none(loader):
    if loader is None:
        return None
    while True:
        for batch in loader:
            yield batch


def _to_device(batch: dict[str, torch.Tensor], device: torch.device) -> dict[str, torch.Tensor]:
    return {k: v.to(device) for k, v in batch.items()}


def evaluate_amazon(model, loader, device: torch.device) -> tuple[dict, dict]:
    model.eval()
    star_true, star_pred = [], []
    help_true, help_pred = [], []
    with torch.no_grad():
        for batch in loader:
            batch = _to_device(batch, device)
            out = model(batch["input_ids"], batch["attention_mask"])
            stars = torch.argmax(out["star_logits"], dim=1).detach().cpu().numpy() + 1
            star_pred.extend(stars.tolist())
            star_true.extend((batch["star_labels"].detach().cpu().numpy() + 1).tolist())
            help_pred.extend(out["help_pred"].detach().cpu().numpy().tolist())
            help_true.extend(batch["help_labels"].detach().cpu().numpy().tolist())
    return star_metrics(np.array(star_true), np.array(star_pred)), helpfulness_metrics(
        np.array(help_true), np.array(help_pred)
    )


def evaluate_absa(model, loader, device: torch.device) -> float:
    if loader is None:
        return 0.0
    model.eval()
    y_true, y_pred = [], []
    with torch.no_grad():
        for batch in loader:
            batch = _to_device(batch, device)
            out = model(batch["input_ids"], batch["attention_mask"])
            pred = torch.argmax(out["absa_logits"], dim=-1).detach().cpu().numpy()
            truth = batch["absa_labels"].detach().cpu().numpy()
            mask = truth != -100
            y_true.extend(truth[mask].tolist())
            y_pred.extend(pred[mask].tolist())
    if not y_true:
        return 0.0
    return float(f1_score(y_true, y_pred, average="macro"))


def train_mtl(config: dict) -> None:
    processed_dir = Path(config["data"]["processed_dir"])
    raw_dir = Path(config["data"]["raw_dir"])
    artifact_dir = Path(config["project"]["artifact_dir"]) / "mtl"
    ensure_dirs([artifact_dir])

    train_df = pd.read_parquet(processed_dir / "train.parquet")
    val_df = pd.read_parquet(processed_dir / "val.parquet")

    absa_train_path = raw_dir / "absa_train.parquet"
    absa_val_path = raw_dir / "absa_validation.parquet"
    if not absa_val_path.exists():
        absa_val_path = raw_dir / "absa_test.parquet"

    absa_train_df = pd.read_parquet(absa_train_path) if absa_train_path.exists() else None
    absa_val_df = pd.read_parquet(absa_val_path) if absa_val_path.exists() else None

    mtl_cfg = config["mtl"]
    tokenizer = AutoTokenizer.from_pretrained(mtl_cfg["model_name"], use_fast=True)
    max_length = int(mtl_cfg["max_length"])

    amazon_train_ds = AmazonReviewDataset(train_df, tokenizer, max_length)
    amazon_val_ds = AmazonReviewDataset(val_df, tokenizer, max_length)
    absa_train_ds = ABSADataset(absa_train_df, tokenizer, max_length) if absa_train_df is not None else None
    absa_val_ds = ABSADataset(absa_val_df, tokenizer, max_length) if absa_val_df is not None else None

    batch_size = int(mtl_cfg["batch_size"])
    amazon_train_loader = DataLoader(amazon_train_ds, batch_size=batch_size, shuffle=True)
    amazon_val_loader = DataLoader(amazon_val_ds, batch_size=batch_size, shuffle=False)
    absa_train_loader = (
        DataLoader(absa_train_ds, batch_size=batch_size, shuffle=True) if absa_train_ds is not None else None
    )
    absa_val_loader = (
        DataLoader(absa_val_ds, batch_size=batch_size, shuffle=False) if absa_val_ds is not None else None
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = AmazonMTLModel(model_name=mtl_cfg["model_name"]).to(device)

    optimizer = AdamW(
        [
            {"params": model.encoder.parameters(), "lr": float(mtl_cfg["learning_rate_encoder"])},
            {
                "params": itertools.chain(
                    model.star_head.parameters(), model.help_head.parameters(), model.absa_head.parameters()
                ),
                "lr": float(mtl_cfg["learning_rate_heads"]),
            },
        ],
        weight_decay=float(mtl_cfg["weight_decay"]),
    )

    max_steps = int(mtl_cfg["max_steps_per_epoch"]) * int(mtl_cfg["epochs"])
    warmup = max(1, int(0.1 * max_steps))
    scheduler = get_cosine_schedule_with_warmup(optimizer, num_warmup_steps=warmup, num_training_steps=max_steps)

    ce_star = nn.CrossEntropyLoss()
    mse_help = nn.MSELoss()
    ce_absa = nn.CrossEntropyLoss(ignore_index=-100)

    absa_iter = cycle_or_none(absa_train_loader)
    model.train()
    step = 0
    for epoch in range(int(mtl_cfg["epochs"])):
        for amazon_batch in amazon_train_loader:
            if step >= int(mtl_cfg["max_steps_per_epoch"]) * (epoch + 1):
                break
            optimizer.zero_grad(set_to_none=True)

            amazon_batch = _to_device(amazon_batch, device)
            out = model(amazon_batch["input_ids"], amazon_batch["attention_mask"])
            loss_star = ce_star(out["star_logits"], amazon_batch["star_labels"])
            loss_help = mse_help(out["help_pred"], amazon_batch["help_labels"])
            total_loss = (
                float(mtl_cfg["star_weight"]) * loss_star
                + float(mtl_cfg["helpfulness_weight"]) * loss_help
            )

            if absa_iter is not None:
                absa_batch = next(absa_iter)
                absa_batch = _to_device(absa_batch, device)
                out_absa = model(absa_batch["input_ids"], absa_batch["attention_mask"])
                absa_logits = out_absa["absa_logits"].view(-1, len(ABSA_LABELS))
                absa_targets = absa_batch["absa_labels"].view(-1)
                loss_absa = ce_absa(absa_logits, absa_targets)
                total_loss = total_loss + float(mtl_cfg["absa_weight"]) * loss_absa

            total_loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            scheduler.step()
            step += 1

    val_star, val_help = evaluate_amazon(model, amazon_val_loader, device)
    val_absa_f1 = evaluate_absa(model, absa_val_loader, device)

    metrics = {
        "val_star_accuracy": val_star["accuracy"],
        "val_star_mae": val_star["mae"],
        "val_star_qwk": val_star["qwk"],
        "val_help_mae": val_help["mae"],
        "val_help_mse": val_help["mse"],
        "val_help_r2": val_help["r2"],
        "val_absa_macro_f1": val_absa_f1,
    }

    params = {
        "model_name": mtl_cfg["model_name"],
        "max_length": max_length,
        "batch_size": batch_size,
        "epochs": int(mtl_cfg["epochs"]),
        "lr_encoder": float(mtl_cfg["learning_rate_encoder"]),
        "lr_heads": float(mtl_cfg["learning_rate_heads"]),
    }
    maybe_log_mlflow(config, params, metrics)

    torch.save(model.state_dict(), artifact_dir / "model.pt")
    tokenizer.save_pretrained(artifact_dir / "tokenizer")
    with (artifact_dir / "absa_labels.json").open("w", encoding="utf-8") as f:
        json.dump({"labels": ABSA_LABELS}, f, indent=2)
    with (artifact_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    LOGGER.info("MTL metrics: %s", metrics)
    LOGGER.info("Saved MTL artifacts to %s", artifact_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train multi-task RoBERTa model.")
    parser.add_argument("--config", default="configs/default.yaml", help="Path to YAML config.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)
    train_mtl(cfg)


if __name__ == "__main__":
    main()

