from textblob import TextBlob
from transformers import pipeline
import torch
import logging

class SentimentAnalyzer:
    def __init__(self, method="textblob"):
        self.method = method
        if self.method == "huggingface":
            self.device = 0 if torch.cuda.is_available() else -1
            self.pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english", device=self.device)

    def analyze(self, user_opinions):
        logging.info(f"Analisi del sentiment utilizzando il metodo {self.method}.")
        if self.method == "textblob":
            return {user_id: TextBlob(text).sentiment.polarity for user_id, text in user_opinions.items()}
        elif self.method == "huggingface":
            return self._analyze_huggingface(user_opinions)

    def _analyze_huggingface(self, user_opinions):
        results = {}
        for user_id, text in user_opinions.items():
            result = self.pipeline(text[:512])[0]
            results[user_id] = result['label']
        return results

    def extract_sentiments_from_graph(self,graph_builder):
        logging.info("Estrazione dei dati di sentiment aggregati per utente.")
        df_data = graph_builder.data
        def compute_sentiment(scores, labels):
            sentiments = []
            for score, label in zip(scores, labels):
                if label == "POSITIVE":
                    sentiments.append(score)
                elif label == "NEGATIVE":
                    sentiments.append(1 - score)
                else:
                    sentiments.append(0.5)
            return sum(sentiments) / len(sentiments) if sentiments else 0.5
        
        sentiment_scores = df_data.groupby("thread_user_pk").apply(
            lambda x: compute_sentiment(x["sentiment_score"], x["sentiment_label"])
        ).to_dict()
        
        logging.info("Estrazione dei dati di sentiment completata.")
        return sentiment_scores
