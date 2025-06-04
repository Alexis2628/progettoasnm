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

        Se il metodo è "roberta", converte LABEL_0/1/2 in NEGATIVE/NEUTRAL/POSITIVE.

        Restituisce un dizionario:
            {
              thread_user_pk_1: {"average_score": <float>, "major_label": <str>},
              thread_user_pk_2: {"average_score": <float>, "major_label": <str>},
              ...
            }
        """
        logging.info(f"Estrazione dei sentiment precomputati per utente mediante metodo '{self.method}'.")
        df_data: pd.DataFrame = graph_builder.data.copy()

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

            # Mappatura da LABEL_n a stringhe testuali
            mapping_roberta = {
                "LABEL_0": "NEGATIVE",
                "LABEL_1": "NEUTRAL",
                "LABEL_2": "POSITIVE"
            }
            # Se la colonna è ad esempio di tipo object/stringa, facciamo la conversione
            df_data[label_col] = df_data[label_col].map(mapping_roberta).fillna(df_data[label_col])

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
