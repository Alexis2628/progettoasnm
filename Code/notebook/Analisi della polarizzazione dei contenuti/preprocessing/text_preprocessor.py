import re
import logging
from nltk.corpus import stopwords
from config.settings import SUPPORTED_LANGUAGES
import nltk
import string

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

    def extract_user_opinions(self, graph):
        logging.info("Estrazione delle opinioni degli utenti dal grafo.")
        user_opinions = {}
        for node, data in graph.nodes(data=True):
            threads = data.get("user_data", [])
            if not threads:  # Handle missing threads
                continue
            raw_text = "\n ".join(
                self.preprocess_text(thread.get("Caption Text Translated", ""))
                for thread in threads
                if thread.get("Caption Text Translated")
            )
            if not raw_text.strip():  # Handle empty processed text
                raw_text = ""
            user_opinions[node] = raw_text
        logging.info("Estrazione delle opinioni degli utenti completata.")
        return user_opinions
