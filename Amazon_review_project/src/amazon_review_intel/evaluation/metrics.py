from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import accuracy_score, cohen_kappa_score, mean_absolute_error, r2_score


def star_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "qwk": float(cohen_kappa_score(y_true, y_pred, weights="quadratic")),
    }


def helpfulness_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    mae = float(mean_absolute_error(y_true, y_pred))
    mse = float(np.mean((y_true - y_pred) ** 2))
    r2 = float(r2_score(y_true, y_pred))
    return {"mae": mae, "mse": mse, "r2": r2}


def flatten_dict(prefix: str, metrics: dict[str, Any]) -> dict[str, Any]:
    return {f"{prefix}_{k}": v for k, v in metrics.items()}

