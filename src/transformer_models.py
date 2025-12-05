# transformer_models.py
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class TransformerSentimentModel:
    """
    CPU-only RoBERTa 3-class sentiment model
    NEGATIVE / NEUTRAL / POSITIVE
    """

    def __init__(self):
        self.device = "cpu"
        self.model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, use_fast=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            device_map=None,
            low_cpu_mem_usage=False
        ).to(self.device)
        self.model.eval()

        # Index mapping for this model:
        # 0 = NEGATIVE
        # 1 = NEUTRAL
        # 2 = POSITIVE
        self.labels = {0: "negative", 1: "neutral", 2: "positive"}

    def predict(self, text_list, batch_size=32):
        """
        Returns list of:
        {
            "sentiment_label": "...",
            "negative_score": float,
            "neutral_score": float,
            "positive_score": float
        }
        """

        results = []

        for i in range(0, len(text_list), batch_size):
            batch = text_list[i:i+batch_size]

            inputs = self.tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=256,
                return_tensors="pt"
            ).to(self.device)

            with torch.no_grad():
                logits = self.model(**inputs).logits

            probs = torch.softmax(logits, dim=1).cpu().numpy()

            for p in probs:
                neg = float(p[0])
                neu = float(p[1])
                pos = float(p[2])

                label = self.labels[int(np.argmax(p))]

                results.append({
                    "sentiment_label": label,
                    "negative_score": neg,
                    "neutral_score": neu,
                    "positive_score": pos
                })

        return results
