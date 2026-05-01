from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

try:
    from transformers import AutoTokenizer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    AutoTokenizer = None  # type: ignore[assignment]
    TRANSFORMERS_AVAILABLE = False

try:
    import torch
except ImportError:
    torch = None

from amazon_review_intel.config import load_config
from amazon_review_intel.features.engineering import (
    STRUCTURED_FEATURES,
    build_structured_features,
    clean_text,
)
from amazon_review_intel.models.baseline import build_feature_matrix

ABSA_LABELS: list[str] = []

POS_WORDS = {"great", "excellent", "amazing", "love", "perfect", "fast", "worth"}
NEG_WORDS = {"bad", "terrible", "broken", "poor", "waste", "slow", "awful"}
ASPECT_HINTS = ["battery", "screen", "display", "delivery", "price", "quality", "performance"]


class InferencePipeline:
    def __init__(self, config_path: str = "configs/default.yaml"):
        self.cfg = load_config(config_path)
        self.mtl_dir = Path(self.cfg["project"]["artifact_dir"]) / "mtl"
        self.baseline_dir = Path(self.cfg["project"]["artifact_dir"]) / "baseline"
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.mtl_model = None
        self.mtl_tokenizer = None
        self.vectorizer = None
        self.scaler = None
        self.star_clf = None
        self.help_reg = None
        self._load_models()
        self.history_file = self._get_history_path()

    def _get_history_path(self) -> Path:
        output_dir = Path(self.cfg["project"]["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir / "prediction_history.json"

    def _load_history(self) -> list[dict]:
        if not self.history_file.exists():
            return []
        try:
            with self.history_file.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        except json.JSONDecodeError:
            return []

    def _save_history(self, history: list[dict]) -> None:
        with self.history_file.open("w", encoding="utf-8") as fh:
            json.dump(history, fh, indent=2)

    def _append_history(self, request: dict, result: dict) -> None:
        entry = {
            "timestamp": datetime.now().isoformat(),
            "request": request,
            "result": result,
        }
        history = self._load_history()
        history.insert(0, entry)
        self._save_history(history[:100])

    def get_history(self, limit: int = 20) -> list[dict]:
        return self._load_history()[:limit]

    def get_evaluation_metrics(self) -> dict[str, dict[str, float]]:
        metrics = {}
        baseline_metrics = self.baseline_dir / "metrics.json"
        if baseline_metrics.exists():
            try:
                with baseline_metrics.open("r", encoding="utf-8") as fh:
                    metrics["baseline"] = json.load(fh)
            except json.JSONDecodeError:
                metrics["baseline"] = {}
        mtl_metrics = self.mtl_dir / "metrics.json"
        if mtl_metrics.exists():
            try:
                with mtl_metrics.open("r", encoding="utf-8") as fh:
                    metrics["mtl"] = json.load(fh)
            except json.JSONDecodeError:
                metrics["mtl"] = {}
        return metrics

    def predict_batch(self, records: list[dict]) -> list[dict]:
        results = []
        for record in records:
            result = self.predict(
                review_title=record.get("review_title", ""),
                review_text=record.get("review_text", ""),
                product_price=record.get("product_price"),
                verified_purchase=record.get("verified_purchase", True),
            )
            results.append({**record, **result})
        return results

    def _load_models(self) -> None:
        model_path = self.mtl_dir / "model.pt"
        if torch is not None and TRANSFORMERS_AVAILABLE and model_path.exists():
            from amazon_review_intel.models.mtl import ABSA_LABELS as _ABSA_LABELS, AmazonMTLModel

            global ABSA_LABELS
            ABSA_LABELS = _ABSA_LABELS

            model_name = self.cfg["mtl"]["model_name"]
            self.mtl_model = AmazonMTLModel(model_name=model_name).to(self.device)
            self.mtl_model.load_state_dict(torch.load(model_path, map_location=self.device))
            self.mtl_model.eval()
            tokenizer_path = self.mtl_dir / "tokenizer"
            self.mtl_tokenizer = AutoTokenizer.from_pretrained(
                tokenizer_path if tokenizer_path.exists() else model_name
            )

        if self.baseline_dir.exists():
            vec = self.baseline_dir / "tfidf_vectorizer.joblib"
            sc = self.baseline_dir / "structured_scaler.joblib"
            clf = self.baseline_dir / "star_classifier.joblib"
            reg = self.baseline_dir / "helpfulness_regressor.joblib"
            if vec.exists() and sc.exists() and clf.exists() and reg.exists():
                self.vectorizer = joblib.load(vec)
                self.scaler = joblib.load(sc)
                self.star_clf = joblib.load(clf)
                self.help_reg = joblib.load(reg)

    def _single_row_frame(self, title: str, text: str, price: float | None, verified: bool) -> pd.DataFrame:
        df = pd.DataFrame(
            [
                {
                    "title": title or "",
                    "text": text or "",
                    "full_text": clean_text(f"{title or ''} {text or ''}"),
                    "price": price if price is not None else 0.0,
                    "verified_purchase": bool(verified),
                    "main_category": "All_Beauty",
                    "average_rating": 4.0,
                    "rating_number": 100,
                    "rating": 4,
                }
            ]
        )
        df = build_structured_features(df)
        for col in STRUCTURED_FEATURES:
            if col not in df.columns:
                df[col] = 0.0
        return df

    def _lexicon_aspects(self, text: str) -> list[dict]:
        lowered = text.lower()
        aspects = []
        for key in ASPECT_HINTS:
            idx = lowered.find(key)
            if idx == -1:
                continue
            window = lowered[max(0, idx - 40) : idx + 40]
            sentiment = "NEU"
            if any(w in window for w in POS_WORDS):
                sentiment = "POS"
            elif any(w in window for w in NEG_WORDS):
                sentiment = "NEG"
            aspects.append({"text": key, "sentiment": sentiment, "start": idx, "end": idx + len(key)})
        return aspects

    def _decode_absa_from_logits(self, text: str, input_ids: torch.Tensor, logits: torch.Tensor) -> list[dict]:
        if self.mtl_tokenizer is None:
            return self._lexicon_aspects(text)
        tokens = self.mtl_tokenizer.convert_ids_to_tokens(input_ids.squeeze(0).tolist())
        pred_ids = torch.argmax(logits, dim=-1).squeeze(0).detach().cpu().numpy().tolist()
        aspects = []
        active = None
        for tok, lbl_id in zip(tokens, pred_ids):
            if tok in {"<s>", "</s>", "<pad>"}:
                continue
            label = ABSA_LABELS[int(lbl_id)] if int(lbl_id) < len(ABSA_LABELS) else "O"
            if label.startswith("B-"):
                if active is not None:
                    aspects.append(active)
                active = {"text": tok.replace("Ġ", "").strip(), "sentiment": label.split("-")[1], "start": -1, "end": -1}
            elif label.startswith("I-") and active is not None:
                piece = tok.replace("Ġ", "").strip()
                if piece:
                    active["text"] = f"{active['text']} {piece}".strip()
            else:
                if active is not None:
                    aspects.append(active)
                    active = None
        if active is not None:
            aspects.append(active)
        return aspects if aspects else self._lexicon_aspects(text)

    def _explanation(self, text: str) -> dict:
        words = [w.strip(".,!?;:").lower() for w in text.split()]
        counts = {}
        for w in words:
            if not w:
                continue
            counts[w] = counts.get(w, 0) + 1
        top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
        return {"top_tokens": top}

    def predict(self, review_title: str, review_text: str, product_price: float | None, verified_purchase: bool) -> dict:
        full_text = clean_text(f"{review_title} {review_text}")
        row_df = self._single_row_frame(review_title, review_text, product_price, verified_purchase)

        if self.mtl_model is not None and self.mtl_tokenizer is not None:
            enc = self.mtl_tokenizer(
                full_text,
                truncation=True,
                max_length=int(self.cfg["mtl"]["max_length"]),
                padding="max_length",
                return_tensors="pt",
            )
            enc = {k: v.to(self.device) for k, v in enc.items()}
            with torch.no_grad():
                out = self.mtl_model(enc["input_ids"], enc["attention_mask"])
            probs = torch.softmax(out["star_logits"], dim=-1).detach().cpu().numpy().squeeze(0)
            stars = int(np.argmax(probs) + 1)
            confidence = float(np.max(probs))
            helpfulness = float(out["help_pred"].detach().cpu().numpy().squeeze(0))
            aspects = self._decode_absa_from_logits(
                full_text, enc["input_ids"].detach().cpu(), out["absa_logits"].detach().cpu()
            )
            model_type = "mtl"
        elif self.star_clf is not None and self.help_reg is not None and self.vectorizer is not None and self.scaler is not None:
            x = build_feature_matrix(row_df, vectorizer=self.vectorizer, scaler=self.scaler, fit=False)
            stars = int(self.star_clf.predict(x)[0] + 1)
            if hasattr(self.star_clf, "predict_proba"):
                confidence = float(np.max(self.star_clf.predict_proba(x)[0]))
            else:
                confidence = 0.5
            helpfulness = float(self.help_reg.predict(x)[0])
            aspects = self._lexicon_aspects(full_text)
            model_type = "baseline"
        else:
            stars = 3
            confidence = 0.2
            helpfulness = 0.0
            aspects = self._lexicon_aspects(full_text)
            model_type = "fallback"

        result = {
            "predicted_stars": stars,
            "star_confidence": confidence,
            "helpfulness_score": helpfulness,
            "aspects": aspects,
            "explanation": self._explanation(full_text),
            "model_type": model_type,
        }
        try:
            self._append_history(
                {
                    "review_title": review_title,
                    "review_text": review_text,
                    "product_price": product_price,
                    "verified_purchase": verified_purchase,
                },
                result,
            )
        except Exception:
            pass
        return result

