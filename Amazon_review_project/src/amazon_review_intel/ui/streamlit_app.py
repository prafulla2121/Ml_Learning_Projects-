from __future__ import annotations

import pandas as pd
import streamlit as st

from amazon_review_intel.serving.pipeline import InferencePipeline
from amazon_review_intel.serving.pipeline import NEG_WORDS, POS_WORDS


@st.cache_resource
def load_pipeline(config_path: str) -> InferencePipeline:
    return InferencePipeline(config_path)


def format_explanation(result: dict) -> str:
    top_tokens = result.get("explanation", {}).get("top_tokens", [])
    return ", ".join(f"{token} ({count})" for token, count in top_tokens)


def highlight_text(text: str) -> str:
    tokens = text.split()
    highlighted = []
    for token in tokens:
        clean = token.strip(".,!?;:").lower()
        if clean in POS_WORDS:
            highlighted.append(f"**✅ {token}**")
        elif clean in NEG_WORDS:
            highlighted.append(f"**❌ {token}**")
        else:
            highlighted.append(token)
    return " ".join(highlighted)


def main() -> None:
    st.set_page_config(page_title="Amazon Review Intelligence", layout="wide")
    st.title("Amazon Review Intelligence")
    st.markdown(
        "Analyze Amazon reviews with baseline/MTL inference, batch CSV upload, history, and evaluation metrics."
    )

    pipeline = load_pipeline("configs/default.yaml")

    tabs = st.tabs(["Single prediction", "Batch CSV", "History", "Metrics"])

    with tabs[0]:
        with st.form("review_form"):
            review_title = st.text_input("Review Title", value="Great product but battery life is short")
            review_text = st.text_area(
                "Review Text",
                value=(
                    "The product quality is excellent, but the battery only lasts a few hours "
                    "and the charger feels flimsy."
                ),
                height=160,
            )
            product_price = st.number_input("Price", min_value=0.0, value=79.99, step=0.01)
            verified_purchase = st.checkbox("Verified Purchase", value=True)
            submitted = st.form_submit_button("Analyze Review")

        if submitted:
            try:
                result = pipeline.predict(
                    review_title=review_title,
                    review_text=review_text,
                    product_price=product_price,
                    verified_purchase=verified_purchase,
                )
            except Exception as exc:
                st.error(f"Unable to run inference: {exc}")
            else:
                st.success(f"Predicted rating: {result['predicted_stars']} stars")
                st.write(f"Confidence: {result['star_confidence']:.2%}")
                st.write(f"Helpfulness score: {result['helpfulness_score']:.6f}")
                st.write(f"Model type: {result.get('model_type', 'unknown')}")

                if result.get("aspects"):
                    st.subheader("Detected aspects")
                    for aspect in result["aspects"]:
                        st.write(f"- **{aspect['text']}**: {aspect['sentiment']}")

                st.subheader("Explanation")
                st.write(format_explanation(result))
                st.subheader("Highlighted review text")
                st.markdown(highlight_text(review_text))
        else:
            st.info("Fill in the form and click Analyze Review to see predictions.")

    with tabs[1]:
        st.markdown("### Batch prediction from CSV")
        st.markdown("Upload a CSV file with these columns: `review_text`, optional `review_title`, `product_price`, `verified_purchase`.")
        uploaded_file = st.file_uploader("Upload review CSV", type=["csv"])
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.dataframe(df.head())
                if st.button("Run batch predictions"):
                    records = []
                    for _, row in df.iterrows():
                        records.append(
                            {
                                "review_title": row.get("review_title", "") if not pd.isna(row.get("review_title", "")) else "",
                                "review_text": row.get("review_text", "") if not pd.isna(row.get("review_text", "")) else "",
                                "product_price": float(row.get("product_price", 0.0)) if not pd.isna(row.get("product_price", 0.0)) else None,
                                "verified_purchase": bool(row.get("verified_purchase", True)) if not pd.isna(row.get("verified_purchase", True)) else True,
                            }
                        )
                    if not records:
                        st.error("No valid rows found in the CSV.")
                    else:
                        batch_results = pipeline.predict_batch(records)
                        st.success(f"Predicted {len(batch_results)} rows")
                        st.dataframe(pd.DataFrame(batch_results))
            except Exception as exc:
                st.error(f"Unable to read CSV: {exc}")

    with tabs[2]:
        st.markdown("### Prediction history")
        history = pipeline.get_history(20)
        if history:
            rows = []
            for entry in history:
                rows.append(
                    {
                        "timestamp": entry["timestamp"],
                        "title": entry["request"].get("review_title", "")[:60],
                        "text": str(entry["request"].get("review_text", ""))[:100],
                        "stars": entry["result"].get("predicted_stars"),
                        "confidence": entry["result"].get("star_confidence"),
                        "helpfulness": entry["result"].get("helpfulness_score"),
                        "model_type": entry["result"].get("model_type", "unknown"),
                    }
                )
            st.dataframe(pd.DataFrame(rows))
        else:
            st.info("No prediction history yet.")

    with tabs[3]:
        st.markdown("### Evaluation metrics")
        metrics = pipeline.get_evaluation_metrics()
        if metrics:
            metrics_rows = []
            for model_name, values in metrics.items():
                for metric_name, metric_value in values.items():
                    metrics_rows.append(
                        {
                            "model": model_name,
                            "metric": metric_name,
                            "value": metric_value,
                        }
                    )
            metrics_df = pd.DataFrame(metrics_rows)
            st.dataframe(metrics_df)
            if not metrics_df.empty:
                pivot_df = metrics_df.pivot(index="metric", columns="model", values="value")
                st.line_chart(pivot_df)
        else:
            st.info("No evaluation metrics found in artifacts.")


if __name__ == "__main__":
    main()
