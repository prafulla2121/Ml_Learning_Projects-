# Amazon Review Intelligence (Production-Style E2E)

This repository implements the prompt in `amazon_review_intelligence_prompt.md` as a practical end-to-end project with a smaller default dataset slice for fast iteration.

Default dataset choice:
- Amazon Reviews 2023 category: `All_Beauty` (about 701k rows, much smaller than Electronics)
- Training sample default: 120k reviews
- ABSA auxiliary dataset: `yqzheng/semeval2014`

## What is implemented

- Data ingestion from Hugging Face datasets
- Raw to processed feature pipeline (text + structured features + targets)
- Classical baseline:
  - TF-IDF + structured features
  - XGBoost classifier (stars 1-5)
  - XGBoost regressor (helpfulness)
- Multi-task transformer training:
  - Shared RoBERTa encoder
  - Three heads:
    - star classification
    - helpfulness regression
    - ABSA token tagging
  - Alternating loaders for Amazon and SemEval ABSA
- Serving:
  - FastAPI `/health` and `/predict`
  - Gradio demo app
- Artifact outputs for downstream deployment

## Quickstart

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

1) Download data

```bash
ari-download --config configs/default.yaml
```

2) Build processed splits

```bash
ari-preprocess --config configs/default.yaml
```

3) Train baseline model

```bash
ari-train-baseline --config configs/default.yaml
```

4) Train multi-task transformer

```bash
ari-train-mtl --config configs/default.yaml
```

5) Run API

```bash
ari-serve --config configs/default.yaml
```

6) Run demo UI

```bash
ari-gradio --config configs/default.yaml
```

## Project layout

```text
configs/
src/amazon_review_intel/
  data/
  features/
  models/
  training/
  evaluation/
  serving/
  ui/
data/
  raw/
  processed/
artifacts/
outputs/
```

## Notes

- The default configuration is tuned for local iteration speed.
- For stronger production quality, raise sample sizes and epochs after smoke testing.
- If GPU is available, `ari-train-mtl` will use it automatically.

