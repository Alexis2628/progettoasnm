from textblob import TextBlob
from transformers import pipeline
import torch
import logging
import pandas as pd

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
        df_data:pd.DataFrame = graph_builder.data
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
        
        sentiment_scores = df_data.groupby("thread_user_pk", group_keys=False).apply(
            lambda x: compute_sentiment(x["sentiment_score"], x["sentiment_label"])
        ).to_dict()
        
        logging.info("Estrazione dei dati di sentiment completata.")
        return sentiment_scores

import logging
import pandas as pd


class SentimentAnalyzer:
    """
    I sentiment sono già presenti in `graph_builder.data`.
    La classe si occupa di leggere e aggregare i valori precomputati.
    models:
    model="distilbert-base-uncased-finetuned-sst-2-english"
    model="cardiffnlp/twitter-roberta-base-sentiment"
    model=VADER
    """

    def __init__(self, method: str = "roberta"):
        valid_methods = ["distilbert", "vader", "roberta"]
        if method not in valid_methods:
            raise ValueError(f"Metodo non valido '{method}'. Scegliere tra {valid_methods}.")
        self.method = method

    def extract_sentiments_from_graph(self, graph_builder) -> dict:
        """
        Raggruppa i valori di sentiment già presenti nel DataFrame per ciascun utente (thread_user_pk),
        calcolando:
          1) Il punteggio medio (average_score)
          2) L’etichetta maggioritaria (major_label)

        Restituisce un dizionario:
            {
              thread_user_pk_1: {"average_score": <float>, "major_label": <str>},
              thread_user_pk_2: {"average_score": <float>, "major_label": <str>},
              ...
            }
        """
        logging.info(f"Estrazione dei sentiment precomputati per utente mediante metodo '{self.method}'.")
        df_data: pd.DataFrame = graph_builder.data

        # Seleziono le colonne giuste in base al metodo scelto
        if self.method == "distilbert":
            score_col = "sentiment_score"
            label_col = "sentiment_label"
        elif self.method == "vader":
            score_col = "vader_compound"
            label_col = "vader_label"
        else:  # "roberta"
            score_col = "transformer_score"
            label_col = "transformer_label"

        # 1) Calcolo del punteggio medio per utente
        avg_scores = df_data.groupby("thread_user_pk")[score_col].mean()

        # 2) Determino l’etichetta più frequente (mode) per utente
        def mode_or_none(series: pd.Series):
            m = series.mode()
            return m.iloc[0] if not m.empty else None

        major_labels = df_data.groupby("thread_user_pk")[label_col].agg(mode_or_none)

        # Costruisco il dizionario di output
        sentiment_by_user = {
            user_id: {
                "average_score": float(avg_scores[user_id]),
                "major_label": major_labels[user_id],
            }
            for user_id in avg_scores.index
        }

        logging.info("Estrazione dei dati di sentiment completata.")
        return sentiment_by_user
