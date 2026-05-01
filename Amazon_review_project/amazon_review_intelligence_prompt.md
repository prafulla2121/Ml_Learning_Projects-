# Amazon Review Intelligence System
### End-to-End Project Prompt — ML + NLP Portfolio Project

> **Stack:** Python · PyTorch · HuggingFace Transformers · RoBERTa · XGBoost · SHAP · LibMTL · FastAPI · MLflow · Gradio  
> **Dataset:** Amazon Customer Reviews (McAuley Lab) — **instantly downloadable, zero signup**  
> **Duration:** ~8–9 weeks phased build  
> **Download right now:** `pip install datasets` then `load_dataset("McAuley-Lab/Amazon-Reviews-2023")`

---

## Project Overview

Build a production-grade review intelligence system that ingests raw Amazon customer review text combined with structured product metadata (price, category, rating, verified purchase flag) and performs **three simultaneous tasks** from a single shared encoder:

1. **Sentiment Polarity + Intensity Classification** — 5-class (1–5 star) ordinal classification  
2. **Aspect-Based Sentiment Analysis (ABSA)** — extract product aspects (battery, screen, delivery) and their sentiment (pos/neg/neutral) per aspect  
3. **Helpfulness Score Regression** — predict how many users will find the review helpful

Every architectural decision must be justifiable. You must be able to explain why this algorithm over alternatives, what the tradeoff is, and where it breaks.

---

## Why This Dataset Is Perfect

| Property | Detail |
|---|---|
| **Instant access** | One line of Python — no forms, no email, no waiting |
| **Structured + unstructured** | Review text (NLP) + rating, price, category, verified_purchase (classical ML) |
| **Real class imbalance** | 5-star reviews dominate (~60%) — forces you to handle imbalance properly |
| **Multiple tasks** | Stars → classification, helpfulness → regression, aspects → NER/span extraction |
| **Scale** | 571M reviews across 33 categories — you pick a subset (Electronics = ~20M, manageable) |
| **Well studied** | Papers exist to compare against — justification for your design choices |

---

## Dataset Download — Do This Right Now

```bash
# Install HuggingFace datasets
pip install datasets

# Option A: Load a single category (recommended — start with Electronics)
from datasets import load_dataset

ds = load_dataset(
    "McAuley-Lab/Amazon-Reviews-2023",
    "raw_review_Electronics",   # or: All_Beauty, Books, Sports_and_Outdoors
    trust_remote_code=True,
    split="full"
)
df = ds.to_pandas()
df.to_parquet("data/raw/electronics_reviews.parquet")
print(df.columns.tolist())
# ['rating', 'title', 'text', 'asin', 'parent_asin', 'user_id',
#  'timestamp', 'helpful_vote', 'verified_purchase']
```

```bash
# Option B: Also grab product metadata (structured features)
meta = load_dataset(
    "McAuley-Lab/Amazon-Reviews-2023",
    "raw_meta_Electronics",
    trust_remote_code=True,
    split="full"
)
meta_df = meta.to_pandas()
meta_df.to_parquet("data/raw/electronics_meta.parquet")
# columns: ['main_category', 'title', 'average_rating', 'rating_number',
#           'features', 'description', 'price', 'store', 'categories', 'details']
```

```bash
# For ABSA labels: use SemEval 2014 Task 4 — Laptop & Restaurant reviews
# Instantly downloadable from HuggingFace
absa = load_dataset("yqzheng/semeval2014", trust_remote_code=True)
# Contains: sentence, aspect_terms, polarities — pre-labeled for ABSA
```

> **Electronics category is recommended.** It has rich vocabulary, clear aspect terms (battery life, display, performance, build quality, price), meaningful helpfulness votes, and is the category used in most Amazon NLP papers — giving you benchmarks to compare against.

---

## Environment Setup

```bash
# Create environment
conda create -n amazon_nlp python=3.10 -y
conda activate amazon_nlp

# Core ML + NLP
pip install torch torchvision transformers datasets accelerate
pip install scikit-learn xgboost shap imbalanced-learn lightgbm
pip install pandas numpy matplotlib seaborn

# ABSA specific
pip install spacy && python -m spacy download en_core_web_lg

# Evaluation
pip install netcal seqeval absa-utils

# Multi-task + serving
pip install LibMTL fastapi uvicorn gradio onnx onnxruntime mlflow

# Start MLflow
mlflow server --host 127.0.0.1 --port 5000
```

```bash
# Project structure
mkdir -p amazon_nlp/{data/{raw,processed,absa},notebooks,
  src/{preprocessing,models,evaluation,serving},experiments,outputs}
```

---

## Papers to Read Before Writing Any Code

| Paper | Why It Matters |
|---|---|
| McAuley et al. 2023 — [Amazon Reviews 2023](https://arxiv.org/abs/2403.03952) | The dataset paper — understand collection, biases, review distribution |
| Pontiki et al. 2014 — [SemEval 2014 ABSA](https://aclanthology.org/S14-2004/) | The ABSA task definition — your NER head target |
| Liu et al. 2019 — [Roberta](https://arxiv.org/abs/1907.11692) | Why RoBERTa over BERT — dynamic masking, no NSP, more data |
| Yu et al. 2020 — [Gradient Surgery](https://arxiv.org/abs/2001.06782) | MGDA justification — core of your MTL architecture |
| Ruder 2017 — [MTL Overview](https://arxiv.org/abs/1706.05098) | Hard vs soft sharing, when to use each |
| Lundberg & Lee 2017 — [SHAP](https://arxiv.org/abs/1705.07874) | Explainability foundation |

---

## Phase 1 — Data Exploration & Feature Engineering

### Label Construction

```python
import pandas as pd
import numpy as np

reviews = pd.read_parquet("data/raw/electronics_reviews.parquet")
meta    = pd.read_parquet("data/raw/electronics_meta.parquet")

# Merge reviews with product metadata
df = reviews.merge(meta[["parent_asin","price","main_category",
                           "average_rating","rating_number"]],
                   on="parent_asin", how="left")

# --- Task A: Star rating (already exists as integer 1–5) ---
df["label_stars"] = df["rating"].astype(int)

# --- Task C: Helpfulness regression ---
# Raw helpful_vote is count — normalize by review age to remove time bias
df["review_age_days"] = (pd.Timestamp.now() - pd.to_datetime(df["timestamp"], unit="ms")).dt.days
df["helpfulness_rate"] = df["helpful_vote"] / (df["review_age_days"] + 1)  # +1 avoids div/0
# Log-transform: helpfulness is heavy-tailed (most reviews get 0, few get 1000s)
df["label_helpfulness"] = np.log1p(df["helpfulness_rate"])

# --- Inspect class distribution ---
print(df["label_stars"].value_counts(normalize=True))
# Expected: 5-star ~55-60%, 1-star ~10%, 2-star ~5% (class imbalance is real)
```

> **Key decision — why log-transform helpfulness?**
> Raw helpfulness counts follow a power-law distribution (Zipf-like). MSE on raw counts is dominated by outliers. Log1p compresses the dynamic range, making the regression target more Gaussian-like and improving gradient stability during training.

### Structured Feature Engineering

```python
from sklearn.preprocessing import StandardScaler, LabelEncoder
import re

# Text-derived features (classical)
df["review_length"]    = df["text"].str.len()
df["word_count"]       = df["text"].str.split().str.len()
df["exclamation_count"]= df["text"].str.count("!")
df["question_count"]   = df["text"].str.count(r"\?")
df["caps_ratio"]       = df["text"].str.count(r"[A-Z]") / (df["review_length"] + 1)
df["avg_word_length"]  = df["text"].apply(
    lambda t: np.mean([len(w) for w in str(t).split()]) if str(t).split() else 0
)

# Product features
df["price_clean"] = pd.to_numeric(
    df["price"].str.replace(r"[^\d.]", "", regex=True), errors="coerce"
)
df["price_log"]    = np.log1p(df["price_clean"].fillna(df["price_clean"].median()))
df["is_verified"]  = df["verified_purchase"].astype(int)
df["category_enc"] = LabelEncoder().fit_transform(df["main_category"].fillna("Unknown"))

# Gap between product avg rating and this review — captures reviewer bias
df["rating_gap"] = df["label_stars"] - df["average_rating"].fillna(df["label_stars"])

STRUCTURED_FEATURES = [
    "review_length", "word_count", "exclamation_count", "question_count",
    "caps_ratio", "avg_word_length", "price_log", "is_verified",
    "category_enc", "rating_gap", "rating_number"
]
```

### TF-IDF Baseline Features

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack

# Combine review title + body for richer signal
df["full_text"] = df["title"].fillna("") + " " + df["text"].fillna("")

# TF-IDF: justify ngram_range=(1,3) — bigrams/trigrams capture phrases like
# "battery life", "does not work", "highly recommend"
vect = TfidfVectorizer(
    max_features=100_000,
    ngram_range=(1, 3),
    min_df=10,         # ignore rare terms — reduces noise
    sublinear_tf=True, # log(1+tf) instead of raw tf — compress frequent terms
    strip_accents="unicode",
)
X_text = vect.fit_transform(df["full_text"])

# Combine TF-IDF with structured features
from scipy.sparse import csr_matrix
X_struct = csr_matrix(df[STRUCTURED_FEATURES].fillna(0).values)
X_combined = hstack([X_text, X_struct])
```

---

## Phase 2 — Classical ML Baseline

**Goal:** Strong baseline before any deep learning. Justify every choice. Show that you understand when classical ML competes with transformers.

### Sampling Strategy

```python
# Electronics has ~20M reviews — use a stratified sample for classical ML
# Justify: XGBoost on 500k rows is already powerful; more data doesn't help classical much
# Reserve the full dataset advantage for the transformer (Phase 3)

from sklearn.model_selection import StratifiedShuffleSplit

sss = StratifiedShuffleSplit(n_splits=1, test_size=0.15, random_state=42)
sample_idx = df.sample(n=500_000, stratify=df["label_stars"], random_state=42).index
df_sample = df.loc[sample_idx].reset_index(drop=True)
```

### Ordinal Classification — Why Not Standard Multiclass?

```python
# Stars are ORDINAL: predicting 3 when true is 4 is better than predicting 1.
# Standard softmax treats all misclassifications equally — ignores ordinality.
# Strategy: Ordinal regression via threshold decomposition
# (Frank & Hall 2001) — train K-1 binary classifiers for thresholds >=2, >=3, >=4, >=5

def ordinal_transform(y, num_classes=5):
    """Convert star labels to K-1 binary threshold targets."""
    return np.array([[1 if y_i >= k else 0 for k in range(2, num_classes + 1)]
                     for y_i in y])

# Alternatively: use label encoding + MAE as loss (treats adjacent errors as smaller)
```

### Stratified K-Fold + SMOTE

```python
from sklearn.model_selection import StratifiedKFold
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import xgboost as xgb
import mlflow

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
y   = df_sample["label_stars"].values

for fold, (train_idx, val_idx) in enumerate(skf.split(X_combined, y)):
    X_tr, X_val = X_combined[train_idx], X_combined[val_idx]
    y_tr, y_val = y[train_idx], y[val_idx]

    # SMOTE only inside the training fold — NEVER before the split
    # Justify: applying SMOTE before split leaks synthetic samples into validation,
    # making validation metrics optimistic and unrepresentative of real data
    sm = SMOTE(sampling_strategy="not majority", random_state=42, k_neighbors=5)
    X_tr_res, y_tr_res = sm.fit_resample(X_tr.toarray(), y_tr)

    counts   = np.bincount(y_tr_res - 1)   # class counts (0-indexed)
    weights  = {i+1: 1.0 / c for i, c in enumerate(counts)}  # inverse freq

    model = xgb.XGBClassifier(
        objective="multi:softprob",
        num_class=5,
        n_estimators=500,
        learning_rate=0.05,
        max_depth=7,
        subsample=0.8,
        colsample_bytree=0.8,
        tree_method="hist",   # sparse-aware, fast on high-dim TF-IDF features
        eval_metric="mlogloss",
        early_stopping_rounds=30,
        sample_weight=np.array([weights[y_i] for y_i in y_tr_res]),
    )
    model.fit(X_tr_res, y_tr_res - 1,  # XGBoost expects 0-indexed labels
              eval_set=[(X_val.toarray(), y_val - 1)],
              verbose=False)

    preds = model.predict(X_val.toarray()) + 1
    mae   = np.mean(np.abs(preds - y_val))

    with mlflow.start_run(run_name=f"xgboost_fold{fold}"):
        mlflow.log_params(model.get_params())
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("accuracy", (preds == y_val).mean())
```

> **Key decision — why XGBoost over LightGBM for this task?**  
> Both are excellent. XGBoost's `tree_method="hist"` handles the very high-dimensional sparse TF-IDF matrix efficiently. LightGBM is generally faster but XGBoost is slightly more robust on sparse inputs due to its split-finding being explicitly sparse-aware. Run both and log the result — showing this comparison is better than just picking one.

> **Key decision — why MAE as primary metric, not accuracy?**  
> Accuracy treats "predicted 1, true 5" identically to "predicted 4, true 5". Star ratings are ordinal — adjacent errors are genuinely smaller mistakes. MAE reflects this. For a reviewer of a product, 4 stars vs 5 stars is less wrong than 1 star vs 5 stars.

### SHAP Explainability

```python
import shap

explainer    = shap.TreeExplainer(model)
shap_values  = explainer.shap_values(X_val_sample)

# For multiclass: shap_values is a list of arrays, one per class
# Show SHAP for class "5-star" (most interesting for business)
shap.summary_plot(shap_values[4], X_val_sample,
                  feature_names=vect.get_feature_names_out().tolist() + STRUCTURED_FEATURES,
                  max_display=25)

# Dependence plot: how does review_length affect 5-star probability?
shap.dependence_plot("review_length", shap_values[4], X_val_sample)
```

> **Manual action:** Write 200-word interpretation of your SHAP plots. Which TF-IDF tokens most predict 5-star reviews? Which predict 1-star? How does review length interact with star rating? This prose goes in your README and demonstrates domain understanding — not just code execution.

---

## Phase 3 — RoBERTa Fine-Tuning (Single Task)

**Goal:** Replace TF-IDF with contextual embeddings. Systematically compare against classical baseline.

### Why RoBERTa Over BERT

> BERT uses Next Sentence Prediction (NSP) as a pre-training objective — but NSP adds training overhead and has been shown to be unnecessary (RoBERTa paper, Liu et al. 2019). RoBERTa removes NSP, uses dynamic masking (different mask per epoch rather than static), trains on 10× more data, and uses larger batch sizes. On downstream NLP tasks including sentiment, RoBERTa consistently outperforms BERT by 1–3 points. Demonstrate the OOV rate difference: check how often product-specific terms like "HDMI", "latency", "firmware" are tokenized as whole tokens vs fragmented subwords in BERT vs RoBERTa.

### Tokenization Strategy

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("roberta-base")

def prepare_input(review_text, review_title, max_len=512):
    """
    Combine title + review body.
    Strategy for long reviews (avg ~200 tokens, but tail can be 2000+):
    - Truncate to first 512 tokens (unlike clinical notes, Amazon reviews
      front-load the most important information — first sentences matter most)
    - Justify vs chunking: empirically, Amazon review sentiment is determined
      within first 3-4 sentences. Chunking adds complexity without gain.
    """
    full = f"{review_title} [SEP] {review_text}"
    return tokenizer(
        full,
        max_length=max_len,
        truncation=True,
        padding="max_length",
        return_tensors="pt"
    )
```

### Fine-Tuning for Ordinal Classification

```python
import torch
import torch.nn as nn
from transformers import AutoModel

class RoBERTaSentiment(nn.Module):
    """
    RoBERTa fine-tuned for ordinal star prediction.

    Key design choices:
    1. [CLS] pooling over mean pooling — [CLS] is specifically pre-trained
       as a document-level representation token; mean pooling can dilute
       sentiment signal with boilerplate text ("I bought this on Amazon...")
    2. Ordinal output head: 4 thresholds (>=2, >=3, >=4, >=5) instead of
       5-class softmax — preserves ordering constraint, reduces error on
       adjacent misclassifications
    3. Dropout before classifier — prevents over-reliance on single neurons
    """
    def __init__(self, model_name="roberta-base", dropout=0.1, num_thresholds=4):
        super().__init__()
        self.encoder   = AutoModel.from_pretrained(model_name)
        hidden         = self.encoder.config.hidden_size  # 768
        self.dropout   = nn.Dropout(dropout)
        self.ordinal   = nn.Linear(hidden, num_thresholds)  # 4 binary thresholds

    def forward(self, input_ids, attention_mask):
        out  = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        cls  = out.last_hidden_state[:, 0, :]   # [CLS] representation
        cls  = self.dropout(cls)
        return self.ordinal(cls)                  # logits for 4 thresholds

def ordinal_loss(logits, stars, num_thresholds=4):
    """Binary cross-entropy on K-1 threshold classifiers."""
    targets = torch.zeros(logits.size(0), num_thresholds, device=logits.device)
    for k in range(num_thresholds):
        targets[:, k] = (stars >= k + 2).float()
    return nn.BCEWithLogitsLoss()(logits, targets)

def decode_ordinal(logits):
    """Convert threshold outputs back to star labels 1-5."""
    probs = torch.sigmoid(logits)
    stars = (probs > 0.5).sum(dim=1) + 1   # count thresholds exceeded
    return stars.clamp(1, 5)
```

### Training Loop

```python
from torch.optim import AdamW
from transformers import get_cosine_schedule_with_warmup

model     = RoBERTaSentiment().cuda()
optimizer = AdamW([
    {"params": model.encoder.parameters(), "lr": 2e-5},   # BERT body: low LR
    {"params": model.ordinal.parameters(),  "lr": 1e-4},  # Head: higher LR
], weight_decay=0.01)

# Cosine annealing: learning rate decays smoothly — avoids sharp drops
# that can destabilize fine-tuning late in training
scheduler = get_cosine_schedule_with_warmup(
    optimizer,
    num_warmup_steps=500,    # linear warmup for first 500 steps
    num_training_steps=total_steps
)

# Mixed precision training — 2× faster, half GPU memory
scaler = torch.cuda.amp.GradScaler()

for batch in train_loader:
    with torch.cuda.amp.autocast():
        logits = model(batch["input_ids"].cuda(), batch["attention_mask"].cuda())
        loss   = ordinal_loss(logits, batch["stars"].cuda())

    scaler.scale(loss).backward()
    scaler.unclip_grad_norm_(model.parameters(), max_norm=1.0)  # gradient clipping
    scaler.step(optimizer)
    scaler.update()
    scheduler.step()
    optimizer.zero_grad()
```

> **Key decision — gradient clipping (max_norm=1.0)?**  
> Fine-tuning transformers on domain-specific data can produce large gradient spikes, especially early in training when the head is random but the encoder is pre-trained. Clipping to norm 1.0 stabilizes training without significantly slowing convergence.

---

## Phase 4 — Multi-Task Learning (Core Architecture)

**Goal:** One RoBERTa encoder, three task-specific heads, trained simultaneously with gradient surgery.

### Architecture

```python
from torchcrf import CRF

class AmazonMTLModel(nn.Module):
    """
    Hard parameter sharing across three tasks.

    Why hard sharing here?
    - All three tasks operate on the same review text — the semantic features
      needed for sentiment, aspect extraction, and helpfulness prediction heavily
      overlap. Sharing the encoder is not just a regularization trick; it is
      semantically justified.
    - Dataset is large enough (~500k reviews) that shared representation learning
      doesn't underfit individual tasks — unlike the clinical setting where hard
      sharing is forced by data scarcity.
    """
    def __init__(self, model_name="roberta-base",
                 num_aspect_labels=7,  # B-POS, I-POS, B-NEG, I-NEG, B-NEU, I-NEU, O
                 dropout=0.1):
        super().__init__()
        self.encoder  = AutoModel.from_pretrained(model_name)
        hidden        = self.encoder.config.hidden_size

        # Head A: Ordinal star classification on [CLS]
        self.star_head  = nn.Sequential(nn.Dropout(dropout), nn.Linear(hidden, 4))

        # Head B: Aspect-Based Sentiment NER on token sequence
        # CRF models BIO label transition constraints — prevents invalid sequences
        # like I-POS appearing without B-POS prefix
        self.absa_head  = nn.Linear(hidden, num_aspect_labels)
        self.crf        = CRF(num_aspect_labels, batch_first=True)

        # Head C: Helpfulness regression on [CLS]
        self.help_head  = nn.Sequential(nn.Dropout(dropout), nn.Linear(hidden, 1))

    def forward(self, input_ids, attention_mask, absa_labels=None):
        out    = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        cls    = out.last_hidden_state[:, 0, :]
        seq    = out.last_hidden_state

        star_logits  = self.star_head(cls)
        absa_emit    = self.absa_head(seq)
        help_pred    = self.help_head(cls).squeeze(-1)

        absa_decoded = self.crf.decode(absa_emit, mask=attention_mask.bool())

        return star_logits, absa_emit, absa_decoded, help_pred
```

### Gradient Surgery with LibMTL

```python
# Step 1: Run naive fixed-weight MTL first. Log per-task losses per epoch.
# Show the conflict: as helpfulness regression improves (requires understanding
# review quality/length), star classification may temporarily degrade
# (optimizing for helpfulness drives encoder toward quality signals, not
# sentiment signals). This conflict plot is your killer demo.

# Step 2: Switch to MGDA
from LibMTL.weighting import MGDA

def multi_task_loss(star_logits, absa_emit, help_pred,
                    star_labels, absa_labels, help_labels,
                    attn_mask, crf_module,
                    w_star=1.0, w_absa=1.0, w_help=0.5):
    """
    Weight choices:
    - w_star=1.0: primary task, full weight
    - w_absa=1.0: NER task, equal weight (provides auxiliary signal)
    - w_help=0.5: regression auxiliary — downweighted because scale differs
      from classification losses; prevents regression from dominating
    """
    loss_star = ordinal_loss(star_logits, star_labels)
    loss_absa = -crf_module(absa_emit, absa_labels, mask=attn_mask.bool())  # CRF NLL
    loss_help = nn.MSELoss()(help_pred, help_labels)
    return w_star * loss_star + w_absa * loss_absa + w_help * loss_help
```

> **Key decision — why CRF on the ABSA head?**  
> ABSA uses BIO tagging: B-POS, I-POS, B-NEG, I-NEG, B-NEU, I-NEU, O. A softmax head at each token predicts each label independently — it can produce sequences like `O → I-POS → B-NEG` which are syntactically invalid (I-POS requires a preceding B-POS). CRF adds a learned transition matrix over label pairs, enforcing valid sequences during decoding via the Viterbi algorithm. This is not decorative — it measurably improves entity-level F1 on ABSA.

> **Key decision — why MGDA over fixed loss weights?**  
> The star classification gradient and helpfulness regression gradient can point in opposing directions in shared encoder parameter space. Gradient surgery (MGDA) computes the minimum-norm vector in the convex hull of per-task gradients — guaranteeing no task is actively harmed by another's update. The paper proves convergence to a Pareto-stationary point. Fixed weights have no such guarantee and require expensive hyperparameter tuning.

### Experiment Comparison Table

Fill this during training. This is the centerpiece of your portfolio presentation.

| Config | MAE (stars ↓) | F1 ABSA (↑) | MAE Helpfulness (↓) |
|---|---|---|---|
| XGBoost + TF-IDF | — | — | — |
| RoBERTa single-task (stars only) | — | — | — |
| MTL fixed weights (naive) | — | — | — |
| **MTL + MGDA (final model)** | — | — | — |

---

## Phase 5 — Evaluation & Explainability

### Metrics — Each Justified

```python
import numpy as np
from sklearn.metrics import mean_absolute_error, cohen_kappa_score
from netcal.metrics import ECE
from seqeval.metrics import f1_score as ner_f1_score

# --- Star Rating ---
# MAE: captures ordinal error magnitude (5-star off by 1 is better than off by 4)
mae = mean_absolute_error(y_true, y_pred)

# Quadratic Weighted Kappa (QWK): penalizes larger ordinal disagreements
# THIS is the standard metric for Kaggle Amazon star prediction competitions
# Justify: QWK weights confusion matrix by squared distance — aligns with
# the ordinal nature of star ratings better than F1 or accuracy
qwk = cohen_kappa_score(y_true, y_pred, weights="quadratic")

# Calibration — does P(5-star) = 0.8 mean 80% of such reviews are actually 5-star?
ece = ECE(10).measure(probabilities, y_true_binary)

# --- ABSA NER ---
# Entity-level F1 (seqeval) — not token-level F1
# Token-level inflates because 'O' is majority class (~80% of tokens are O)
entity_f1 = ner_f1_score(true_seqs, pred_seqs)

# --- Helpfulness Regression ---
mse  = mean_squared_error(h_true, h_pred)
r2   = r2_score(h_true, h_pred)  # proportion of variance explained
```

### Explainability — Two Methods, One Comparison

```python
# Method 1: SHAP for XGBoost classical model
import shap
tree_exp   = shap.TreeExplainer(xgb_model)
shap_vals  = tree_exp.shap_values(X_val_sample)
shap.summary_plot(shap_vals[4], X_val_sample, max_display=20)

# Method 2: LIME for RoBERTa
from lime.lime_text import LimeTextExplainer

def predict_proba_wrapper(texts):
    inputs  = tokenizer(texts, truncation=True, padding=True, return_tensors="pt")
    logits  = model(**inputs).star_logits
    probs   = torch.softmax(logits, dim=-1).detach().numpy()
    return probs

lime_exp   = LimeTextExplainer(class_names=["1★","2★","3★","4★","5★"])
explanation = lime_exp.explain_instance(
    sample_review,
    predict_proba_wrapper,
    num_features=20,
    num_samples=1000
)
explanation.show_in_notebook()
```

> **Manual action — write this for your README (this is what interviewers ask):**  
> Compare SHAP vs LIME vs attention weights. SHAP is theoretically grounded (Shapley values from cooperative game theory) but requires a tree model — not directly applicable to transformers. Attention weights in transformers do NOT reliably identify important tokens (Jain & Wallace 2019 showed attention is not explanation). LIME is model-agnostic and local but sensitive to num_samples and perturbation strategy. For production clinical/business decisions, SHAP on a calibrated XGBoost model is more defensible than attention weights on a black-box transformer.

---

## Phase 6 — Serving & MLOps

### ONNX Export

```python
import torch

model.eval()
dummy_ids  = torch.randint(0, 50265, (1, 128))  # RoBERTa vocab size
dummy_mask = torch.ones(1, 128, dtype=torch.long)

torch.onnx.export(
    model,
    (dummy_ids, dummy_mask),
    "outputs/amazon_mtl.onnx",
    input_names=["input_ids", "attention_mask"],
    output_names=["star_logits", "help_pred"],
    dynamic_axes={
        "input_ids":      {0: "batch", 1: "seq_len"},
        "attention_mask": {0: "batch", 1: "seq_len"},
    },
    opset_version=14,
)

# Validate: ONNX must match PyTorch output within 1e-5
import onnxruntime as ort, numpy as np
sess    = ort.InferenceSession("outputs/amazon_mtl.onnx")
ort_out = sess.run(None, {"input_ids": dummy_ids.numpy(),
                           "attention_mask": dummy_mask.numpy()})
pt_out  = model(dummy_ids, dummy_mask)
assert np.allclose(ort_out[0], pt_out[0].detach().numpy(), atol=1e-5), "ONNX mismatch!"
print("ONNX validation passed.")
```

### FastAPI Endpoint

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Amazon Review Intelligence API", version="1.0")

class ReviewRequest(BaseModel):
    review_title: str
    review_text: str
    product_price: float | None = None
    verified_purchase: bool = True

class ReviewResponse(BaseModel):
    predicted_stars: int                  # 1–5
    star_confidence: float                # max class probability
    helpfulness_score: float              # predicted helpfulness
    aspects: list[dict]                   # [{text, sentiment, start, end}]
    explanation: dict                     # SHAP top-5 features

@app.post("/predict", response_model=ReviewResponse)
def predict(req: ReviewRequest):
    # 1. Tokenize + run transformer MTL model
    # 2. Decode ordinal output → star label
    # 3. Decode CRF → aspect entities
    # 4. Return structured response
    ...

@app.get("/health")
def health():
    return {"status": "ok", "model": "amazon-mtl-roberta-mgda"}
```

```bash
# Start API
uvicorn src.serving.api:app --host 0.0.0.0 --port 8000 --reload

# Test
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "review_title": "Great laptop but battery disappoints",
    "review_text": "The display is stunning and performance is excellent. However battery life is terrible, barely 4 hours. Build quality feels premium. Would not recommend for travel.",
    "product_price": 1299.99,
    "verified_purchase": true
  }'
```

### Gradio Demo

```python
import gradio as gr

def predict_ui(title, review, price, verified):
    result = run_pipeline(title, review, float(price), bool(verified))
    highlighted = [(t, s) for t, s in result["aspects"]]
    return (
        f"{result['stars']} ★ ({result['confidence']:.0%} confidence)",
        highlighted,
        round(result["helpfulness"], 3),
    )

demo = gr.Interface(
    fn=predict_ui,
    inputs=[
        gr.Textbox(label="Review Title", placeholder="Great laptop but..."),
        gr.Textbox(label="Review Text", lines=5,
                   placeholder="The display is excellent..."),
        gr.Number(label="Product Price ($)", value=99.99),
        gr.Checkbox(label="Verified Purchase", value=True),
    ],
    outputs=[
        gr.Textbox(label="Predicted Star Rating"),
        gr.HighlightedText(label="Aspect Sentiments",
                           color_map={"POS": "green", "NEG": "red", "NEU": "gray"}),
        gr.Number(label="Predicted Helpfulness Score"),
    ],
    title="Amazon Review Intelligence",
    description="Multi-task NLP: star prediction + aspect sentiment + helpfulness scoring",
    examples=[
        ["Excellent noise cancelling headphones",
         "Sound quality is incredible. Battery lasts 30 hours. Only downside is the price is steep but worth every penny.",
         299.99, True],
        ["Broken on arrival",
         "Product stopped working after 2 days. Packaging was damaged. Customer service was unresponsive. Total waste of money.",
         49.99, True],
    ]
)

demo.launch()
```

**Manual actions for deployment:**
- [ ] Deploy Gradio demo to HuggingFace Spaces (free, `gradio deploy`) — this is your shareable portfolio URL
- [ ] Push model weights to HuggingFace Hub under your username
- [ ] Register best model in MLflow Model Registry with tags: architecture, QWK, dataset, version
- [ ] Write a model card: intended use, training data, known failure modes, out-of-scope uses
- [ ] Push code to GitHub with full README: architecture diagram, results table, dataset description, reproduction steps
- [ ] Record a 3-minute screen demo — walk through a real review prediction, explain each architectural decision as you demo

---

## MLflow Tracking Conventions

```python
import mlflow

mlflow.set_experiment("amazon_review_mtl")

with mlflow.start_run(run_name="roberta_mtl_mgda_fold1"):
    mlflow.log_params({
        "model":          "roberta-base",
        "weighting":      "MGDA",
        "encoder_lr":     2e-5,
        "head_lr":        1e-4,
        "dropout":        0.1,
        "max_len":        512,
        "batch_size":     32,
        "w_star":         1.0,
        "w_absa":         1.0,
        "w_help":         0.5,
        "ordinal_thres":  4,
    })
    mlflow.log_metrics({
        "star_mae":       0.42,
        "star_qwk":       0.71,
        "star_ece":       0.038,
        "absa_f1":        0.68,
        "help_mae":       0.31,
        "help_r2":        0.44,
    })
    mlflow.pytorch.log_model(model, "model")
```

---

## Key Decision Summary — Interview Cheat Sheet

| Question | Your Answer |
|---|---|
| Why RoBERTa over BERT? | RoBERTa removes NSP (shown unnecessary), uses dynamic masking, trained on 10× more data — consistently outperforms BERT on sentiment tasks by 1–3 points |
| Why multi-task learning? | Star classification, ABSA, and helpfulness share semantic representations — aspect mentions co-occur with sentiment signals, helping all tasks |
| Why MGDA over fixed loss weights? | Fixed weights allow task gradients to conflict — one task's improvement actively hurts another. MGDA projects to Pareto-stationary point, guaranteed not to harm any task |
| Why CRF on the ABSA head? | CRF enforces valid BIO transitions via Viterbi — softmax independently predicts each token and produces illegal sequences (I-POS without B-POS) |
| Why ordinal classification over softmax multiclass? | Stars have order: predicting 3 when true is 4 is better than predicting 1. Standard softmax treats all errors equally — ordinal thresholds penalize larger deviations |
| Why MAE + QWK, not accuracy? | Accuracy ignores ordinality — a model predicting all 5-stars scores 55% accuracy without understanding anything. MAE captures error magnitude, QWK penalizes bigger ordinal gaps |
| Why SMOTE inside folds only? | SMOTE before splitting leaks synthetic samples into validation — inflates metrics and gives a false impression of generalization |
| Why log-transform helpfulness? | Raw helpful_vote is heavy-tailed (most reviews: 0, few: 1000+). Log1p compresses dynamic range → more Gaussian target → better MSE gradient behavior |
| Why truncate at 512 vs chunk? | Amazon reviews front-load sentiment information — the first 3-4 sentences determine star rating. Empirically, first 512 tokens capture >95% of the signal. Chunking adds complexity without measurable gain on this domain. |
| Why SHAP over attention for explanation? | Attention weights are not explanations (Jain & Wallace 2019) — attending to a word does not mean it causally drives the prediction. SHAP is game-theoretically grounded and consistent |

---

## Reference Papers

| Paper | ArXiv / Link |
|---|---|
| Hou et al. 2024 — Amazon Reviews 2023 | https://arxiv.org/abs/2403.03952 |
| Liu et al. 2019 — RoBERTa | https://arxiv.org/abs/1907.11692 |
| Devlin et al. 2019 — BERT | https://arxiv.org/abs/1810.04805 |
| Pontiki et al. 2014 — SemEval 2014 ABSA | https://aclanthology.org/S14-2004/ |
| Yu et al. 2020 — Gradient Surgery (MGDA) | https://arxiv.org/abs/2001.06782 |
| Ruder 2017 — MTL in Deep NLP | https://arxiv.org/abs/1706.05098 |
| Lundberg & Lee 2017 — SHAP | https://arxiv.org/abs/1705.07874 |
| Jain & Wallace 2019 — Attention is Not Explanation | https://arxiv.org/abs/1902.10186 |
| Frank & Hall 2001 — Ordinal Classification | https://dl.acm.org/doi/10.5555/645530.655815 |
| Lafferty et al. 2001 — CRF | https://dl.acm.org/doi/10.5555/645530.655813 |

## Key Resource Links

| Resource | Link |
|---|---|
| Dataset (HuggingFace) | `McAuley-Lab/Amazon-Reviews-2023` |
| ABSA Dataset | `yqzheng/semeval2014` on HuggingFace |
| RoBERTa weights | `roberta-base` on HuggingFace |
| HuggingFace fine-tuning course | https://huggingface.co/learn/nlp-course/chapter3/1 |
| LibMTL (gradient surgery) | https://github.com/median-research-group/LibMTL |
| torchcrf (CRF layer) | https://pytorch-crf.readthedocs.io |
| SHAP docs | https://shap.readthedocs.io |
| MLflow quickstart | https://mlflow.org/docs/latest/getting-started/intro-quickstart/ |
| HuggingFace Spaces (free deploy) | https://huggingface.co/spaces |

---

## Phased Build Plan

| Phase | Duration | Deliverable |
|---|---|---|
| **Phase 0** | Day 1 | Environment + data downloaded (one line of Python) |
| **Phase 1** | Week 1 | EDA, feature engineering, label construction, class distribution analysis |
| **Phase 2** | Week 2–3 | XGBoost + TF-IDF baseline with SHAP plots; MLflow logged |
| **Phase 3** | Week 3–4 | RoBERTa fine-tuned single-task; BERT vs XGBoost comparison table |
| **Phase 4** | Week 5–7 | Multi-task model with CRF ABSA head + MGDA; gradient conflict demo |
| **Phase 5** | Week 7–8 | Full evaluation suite; LIME vs SHAP comparison write-up |
| **Phase 6** | Week 8–9 | FastAPI + ONNX + Gradio demo on HuggingFace Spaces |
