import re
import logging
from nltk.corpus import stopwords
from config.settings import SUPPORTED_LANGUAGES
import nltk
import string
import pandas as pd

nltk.download("stopwords")
nltk.download("punkt_tab")


class TextPreprocessor:
    def __init__(self):
        self.stop_words = [
            word for lang in SUPPORTED_LANGUAGES for word in stopwords.words(lang)
        ]

    def preprocess_text(self, text):
        text = text.lower()
        text = re.sub(r"[\r\n\t]", " ", text)
        text = re.sub(r"[-_]", " ", text)
        text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", " ", text)
        text = re.sub(r"https?://\S+|www\.\S+", " ", text)
        text = text.translate(
            str.maketrans("", "", string.punctuation.replace("#", "").replace("@", ""))
        )
        text = " ".join(word for word in text.split() if word not in self.stop_words)
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def extract_user_opinions(self, graph_builder):
        logging.info("Estrazione delle opinioni degli utenti.")
        df_data = graph_builder.data
        user_opinions = df_data.groupby("thread_user_pk")["caption_text_translated"]\
    .apply(lambda texts: " ".join(self.preprocess_text(text) for text in texts.astype(str) if pd.notna(text) and str.strip(text) != "nan"))\
    .to_dict()
        logging.info("Estrazione delle opinioni degli utenti completata.")
        return user_opinions

