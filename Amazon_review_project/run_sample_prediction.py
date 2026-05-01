import sys
from pathlib import Path

sys.path.insert(0, "src")

import joblib
import pandas as pd
from amazon_review_intel.features.engineering import build_structured_features, clean_text
from amazon_review_intel.models.baseline import build_feature_matrix

base = Path("artifacts/baseline")
vectorizer = joblib.load(base / "tfidf_vectorizer.joblib")
scaler = joblib.load(base / "structured_scaler.joblib")
clf = joblib.load(base / "star_classifier.joblib")
reg = joblib.load(base / "helpfulness_regressor.joblib")

review_title = "Great headphones but battery is weak"
review_text = (
    "The sound quality is amazing and bass is full, but the battery only lasts 4 hours "
    "and charging takes too long."
)
price = 129.99
verified = True

df = pd.DataFrame(
    [
        {
            "title": review_title,
            "text": review_text,
            "full_text": clean_text(review_title + " " + review_text),
            "price": price,
            "verified_purchase": verified,
            "main_category": "All_Beauty",
            "average_rating": 4.0,
            "rating_number": 100,
            "rating": 4,
        }
    ]
)

df = build_structured_features(df)
cols = [
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
for col in cols:
    if col not in df.columns:
        df[col] = 0.0

x = build_feature_matrix(df, vectorizer=vectorizer, scaler=scaler, fit=False)
pred_star = int(clf.predict(x)[0]) + 1
confidence = float(clf.predict_proba(x)[0].max()) if hasattr(clf, "predict_proba") else 0.5
helpfulness = float(reg.predict(x)[0])

print("predicted_stars", pred_star)
print("confidence", confidence)
print("helpfulness_score", helpfulness)
