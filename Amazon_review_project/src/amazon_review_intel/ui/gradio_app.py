from __future__ import annotations

import argparse
import pandas as pd

import gradio as gr

from amazon_review_intel.serving.pipeline import InferencePipeline


def build_demo(pipeline: InferencePipeline) -> gr.Blocks:
    def predict_ui(title: str, review: str, price: float, verified: bool):
        result = pipeline.predict(
            review_title=title,
            review_text=review,
            product_price=price,
            verified_purchase=verified,
        )
        aspects = [(a["text"], a["sentiment"]) for a in result["aspects"]]
        summary = f"{result['predicted_stars']} stars ({result['star_confidence']:.1%} confidence)"
        explanation = result["explanation"]
        explanation_text = ", ".join([f"{k}: {v}" for k, v in explanation.items()])
        model_type = result.get("model_type", "unknown")
        return summary, aspects, result["helpfulness_score"], explanation_text, model_type

    def batch_predict(uploaded_file):
        if uploaded_file is None:
            return "Upload a CSV file with columns review_text and optionally review_title, product_price, verified_purchase.", []
        try:
            df = pd.read_csv(uploaded_file.name)
        except Exception as exc:
            return f"Failed to read CSV: {exc}", []

        if "review_text" not in df.columns:
            return "CSV must contain a review_text column.", []

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

        out = pipeline.predict_batch(records)
        table = pd.DataFrame(out)
        return f"Predicted {len(table)} rows.", table

    def history_records():
        history = pipeline.get_history(20)
        records = []
        for entry in history:
            req = entry["request"]
            res = entry["result"]
            records.append(
                {
                    "timestamp": entry["timestamp"],
                    "review_title": req.get("review_title", "")[:80],
                    "review_text": str(req.get("review_text", ""))[:100],
                    "predicted_stars": res.get("predicted_stars"),
                    "confidence": res.get("star_confidence"),
                    "helpfulness": res.get("helpfulness_score"),
                    "model_type": res.get("model_type", "unknown"),
                }
            )
        return records

    def metrics_summary():
        metrics = pipeline.get_evaluation_metrics()
        return metrics

    with gr.Blocks(title="Amazon Review Intelligence") as demo:
        gr.Markdown("# Amazon Review Intelligence")
        gr.Markdown("Multi-task review analysis: stars, helpfulness, ABSA aspects, batch upload, history, and metrics.")

        with gr.Tabs():
            with gr.TabItem("Single Prediction"):
                title = gr.Textbox(label="Review Title", placeholder="Great product but...")
                review = gr.Textbox(label="Review Text", lines=6)
                price = gr.Number(label="Price", value=29.99)
                verified = gr.Checkbox(label="Verified Purchase", value=True)
                predict_button = gr.Button("Analyze")
                rating = gr.Textbox(label="Predicted Rating")
                aspects = gr.HighlightedText(label="Aspect Sentiments")
                helpfulness = gr.Number(label="Predicted Helpfulness")
                explanation = gr.Textbox(label="Explanation")
                model_type = gr.Textbox(label="Model Type")
                predict_button.click(
                    predict_ui,
                    inputs=[title, review, price, verified],
                    outputs=[rating, aspects, helpfulness, explanation, model_type],
                )

            with gr.TabItem("Batch CSV Upload"):
                csv_file = gr.File(label="Upload CSV", file_types=["csv"])
                batch_status = gr.Textbox(label="Batch status")
                batch_table = gr.Dataframe(headers="auto")
                csv_file.change(batch_predict, inputs=[csv_file], outputs=[batch_status, batch_table])

            with gr.TabItem("History"):
                history_button = gr.Button("Load prediction history")
                history_table = gr.Dataframe(headers="auto")
                history_button.click(history_records, inputs=None, outputs=[history_table])

            with gr.TabItem("Metrics"):
                metrics_output = gr.JSON(label="Evaluation Metrics")
                metrics_button = gr.Button("Load metrics")
                metrics_button.click(metrics_summary, inputs=None, outputs=[metrics_output])

        gr.Markdown("---")
        gr.Markdown("**Tip:** You can also call the backend API at `/predict` or view FastAPI docs at `/docs` when the backend is running.")

    return demo


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Gradio app.")
    parser.add_argument("--config", default="configs/default.yaml", help="Path to YAML config.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=7860, type=int)
    return parser.parse_args()


def run() -> None:
    args = parse_args()
    pipeline = InferencePipeline(args.config)
    demo = build_demo(pipeline)
    demo.launch(server_name=args.host, server_port=args.port)


if __name__ == "__main__":
    run()

