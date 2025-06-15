import re
import logging
import string

import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from config.settings import SUPPORTED_LANGUAGES


nltk.download("stopwords")
nltk.download("punkt")


class TextPreprocessor:
    """
    Classe per il preprocessing dei testi: normalizzazione, rimozione di URL, email, punteggiatura,
    stopword e tokenizzazione.
    """

    _URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
    _EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
    _WHITESPACE_PATTERN = re.compile(r"[\r\n\t]+")

    def __init__(self):
        """Inizializza lo stopword set e i pattern di pulizia."""

        self.stop_words = set()
        for lang in SUPPORTED_LANGUAGES:
            try:
                self.stop_words.update(stopwords.words(lang))
            except OSError:
                logging.warning(
                    f"Stopwords per la lingua '{lang}' non trovate in NLTK."
                )

        punct_to_remove = string.punctuation.replace("#", "").replace("@", "")
        self._punct_translator = str.maketrans({p: " " for p in punct_to_remove})

    def preprocess_text(self, text: str) -> str:
        """
        Esegue i seguenti passaggi:
        1. Lowercase
        2. Rimozione di whitespace multipli (\n, \r, \t)
        3. Sostituzione di trattini e underscore con spazio
        4. Rimozione di email e URL
        5. Rimozione della punteggiatura (tranne
        6. Tokenizzazione
        7. Filtraggio stopword, token vuoti e token non alfabetici
        8. Ricostruzione della stringa pulita
        """
        if not isinstance(text, str):
            return ""

        text = text.lower()

        text = self._WHITESPACE_PATTERN.sub(" ", text)

        text = text.replace("-", " ").replace("_", " ")

        text = self._EMAIL_PATTERN.sub(" ", text)
        text = self._URL_PATTERN.sub(" ", text)

        text = text.translate(self._punct_translator)

        tokens = word_tokenize(text, language="english")

        clean_tokens = []
        for token in tokens:

            if token in self.stop_words:
                continue
            if not token.isalpha():
                continue
            if len(token) < 2:
                continue
            clean_tokens.append(token)

        return " ".join(clean_tokens)

    def extract_user_opinions(self, graph_builder) -> dict:
        """
        Raggruppa i testi (dopo preprocessing) per 'thread_user_pk' e li unisce in un'unica stringa per utente.
        Restituisce un dizionario {thread_user_pk: opinione_preprocessata}.
        """
        logging.info("Estrazione delle opinioni degli utenti in corso...")
        df_data = graph_builder.data

        def merge_and_clean(texts):
            """Unisce i testi preprocessandoli."""
            cleaned = []
            for text in texts.astype(str):
                if pd.isna(text) or text.strip().lower() == "nan":
                    continue
                processed = self.preprocess_text(text)
                if processed:
                    cleaned.append(processed)
            return "\n\n".join(cleaned)

        user_opinions = (
            df_data.groupby("thread_user_pk")["caption_text_translated"]
            .apply(merge_and_clean)
            .to_dict()
        )

        logging.info("Estrazione delle opinioni degli utenti completata.")
        return user_opinions
