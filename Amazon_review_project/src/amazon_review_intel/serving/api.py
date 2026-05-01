from __future__ import annotations

import argparse

import uvicorn
from fastapi import FastAPI

from amazon_review_intel.config import load_config
from amazon_review_intel.serving.pipeline import InferencePipeline
from amazon_review_intel.serving.schemas import (
    ReviewBatchRequest,
    ReviewBatchResponse,
    ReviewRequest,
    ReviewResponse,
)

APP = FastAPI(title="Amazon Review Intelligence API", version="1.0.0")
PIPELINE: InferencePipeline | None = None


@APP.on_event("startup")
def _startup() -> None:
    global PIPELINE
    if PIPELINE is None:
        PIPELINE = InferencePipeline()


@APP.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "amazon-review-intelligence"}


@APP.post("/predict", response_model=ReviewResponse)
def predict(payload: ReviewRequest) -> ReviewResponse:
    if PIPELINE is None:
        raise RuntimeError("Pipeline is not initialized.")
    result = PIPELINE.predict(
        review_title=payload.review_title,
        review_text=payload.review_text,
        product_price=payload.product_price,
        verified_purchase=payload.verified_purchase,
    )
    return ReviewResponse(**result)


@APP.post("/predict/batch", response_model=ReviewBatchResponse)
def predict_batch(payload: ReviewBatchRequest) -> ReviewBatchResponse:
    if PIPELINE is None:
        raise RuntimeError("Pipeline is not initialized.")
    records = [
        {
            "review_title": r.review_title,
            "review_text": r.review_text,
            "product_price": r.product_price,
            "verified_purchase": r.verified_purchase,
        }
        for r in payload.reviews
    ]
    results = PIPELINE.predict_batch(records)
    return ReviewBatchResponse(results=[ReviewResponse(**result) for result in results])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run FastAPI server.")
    parser.add_argument("--config", default="configs/default.yaml", help="Path to YAML config.")
    return parser.parse_args()


def run() -> None:
    args = parse_args()
    cfg = load_config(args.config)
    PIPELINE_LOCAL = InferencePipeline(args.config)
    global PIPELINE
    PIPELINE = PIPELINE_LOCAL
    uvicorn.run(
        "amazon_review_intel.serving.api:APP",
        host=cfg["serving"]["host"],
        port=int(cfg["serving"]["port"]),
        reload=False,
    )


if __name__ == "__main__":
    run()

