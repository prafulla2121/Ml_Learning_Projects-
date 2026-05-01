from __future__ import annotations

import torch
from torch import nn
from transformers import AutoModel

ABSA_LABELS = [
    "O",
    "B-POS",
    "I-POS",
    "B-NEG",
    "I-NEG",
    "B-NEU",
    "I-NEU",
]
ABSA_LABEL_TO_ID = {label: i for i, label in enumerate(ABSA_LABELS)}


class AmazonMTLModel(nn.Module):
    def __init__(self, model_name: str, absa_num_labels: int = len(ABSA_LABELS), dropout: float = 0.1):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(model_name)
        hidden = self.encoder.config.hidden_size
        self.dropout = nn.Dropout(dropout)
        self.star_head = nn.Linear(hidden, 5)
        self.help_head = nn.Linear(hidden, 1)
        self.absa_head = nn.Linear(hidden, absa_num_labels)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> dict[str, torch.Tensor]:
        out = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        sequence = out.last_hidden_state
        cls = self.dropout(sequence[:, 0, :])
        star_logits = self.star_head(cls)
        help_pred = self.help_head(cls).squeeze(-1)
        absa_logits = self.absa_head(sequence)
        return {"star_logits": star_logits, "help_pred": help_pred, "absa_logits": absa_logits}

