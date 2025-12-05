# src/cpu_emotion_model.py
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np

class CPUEmotionModel:
    def __init__(self):
        self.device = "cpu"
        self.model_name = "j-hartmann/emotion-english-distilroberta-base"

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, use_fast=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            device_map=None,
            low_cpu_mem_usage=False
        ).to(self.device)

        self.model.eval()
        self.labels = self.model.config.id2label

    def predict(self, text_list, batch_size=16):
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
                emo = {self.labels[j]: float(p[j]) for j in range(len(p))}
                results.append(emo)

        return results
