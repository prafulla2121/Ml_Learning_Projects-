from __future__ import annotations

from pydantic import BaseModel, Field


class ReviewRequest(BaseModel):
    review_title: str = Field(default="")
    review_text: str
    product_price: float | None = None
    verified_purchase: bool = True


class AspectPrediction(BaseModel):
    text: str
    sentiment: str
    start: int
    end: int


class ReviewResponse(BaseModel):
    predicted_stars: int
    star_confidence: float
    helpfulness_score: float
    aspects: list[AspectPrediction]
    explanation: dict
    model_type: str


class ReviewBatchRequest(BaseModel):
    reviews: list[ReviewRequest]


class ReviewBatchResponse(BaseModel):
    results: list[ReviewResponse]

