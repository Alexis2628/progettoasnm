import re
import logging
import string

import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from config.settings import SUPPORTED_LANGUAGES

# Assicurati di aver scaricato almeno questi due pacchetti NLTK:
nltk.download("stopwords")
nltk.download("punkt")


class TextPreprocessor:
    """
    Classe per il preprocessing dei testi: normalizzazione, rimozione di URL, email, punteggiatura,
    stopword e tokenizzazione.
    """

    # Pattern precalcolati per velocizzare le sostituzioni
    _URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
    _EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
    _WHITESPACE_PATTERN = re.compile(r"[\r\n\t]+")

    def __init__(self):
        """Inizializza lo stopword set e i pattern di pulizia."""
        # Carico tutte le stopword supportate da SUPPORTED_LANGUAGES
        self.stop_words = set()
        for lang in SUPPORTED_LANGUAGES:
            try:
                self.stop_words.update(stopwords.words(lang))
            except OSError:
                logging.warning(f"Stopwords per la lingua '{lang}' non trovate in NLTK.")
        # Creo un dizionario per tradurre la punteggiatura in spazio, ma mantengo # e @
        punct_to_remove = string.punctuation.replace("#", "").replace("@", "")
        self._punct_translator = str.maketrans({p: " " for p in punct_to_remove})

    def preprocess_text(self, text: str) -> str:
        """
        Esegue i seguenti passaggi:
        1. Lowercase
        2. Rimozione di whitespace multipli (\n, \r, \t)
        3. Sostituzione di trattini e underscore con spazio
        4. Rimozione di email e URL
        5. Rimozione della punteggiatura (tranne # e @)
        6. Tokenizzazione
        7. Filtraggio stopword, token vuoti e token non alfabetici
        8. Ricostruzione della stringa pulita
        """
        if not isinstance(text, str):
            return ""

        # 1) Lowercase
        text = text.lower()

        # 2) Rimuovo righe vuote, tabulazioni e ritorni a capo
        text = self._WHITESPACE_PATTERN.sub(" ", text)

        # 3) Sostituisco trattini e underscore con spazio
        text = text.replace("-", " ").replace("_", " ")

        # 4) Rimuovo email e URL
        text = self._EMAIL_PATTERN.sub(" ", text)
        text = self._URL_PATTERN.sub(" ", text)

        # 5) Rimuovo la punteggiatura eccetto # e @
        text = text.translate(self._punct_translator)

        # 6) Tokenizzo
        tokens = word_tokenize(text, language="english")  # NLTK non ha parametri diversi per alcune lingue; va bene usare 'english' come default

        # 7) Filtraggio
        clean_tokens = []
        for token in tokens:
            # scarto se è stopword o non è alfabetico o ha lunghezza < 2
            if token in self.stop_words:
                continue
            if not token.isalpha():
                continue
            if len(token) < 2:
                continue
            clean_tokens.append(token)

        # 8) Ricostruisco la stringa
        return " ".join(clean_tokens)

    def extract_user_opinions(self, graph_builder) -> dict:
        """
        Raggruppa i testi (dopo preprocessing) per 'thread_user_pk' e li unisce in un'unica stringa per utente.
        Restituisce un dizionario {thread_user_pk: opinione_preprocessata}.
        """
        logging.info("Estrazione delle opinioni degli utenti in corso...")
        df_data = graph_builder.data

        # Funzione helper per pulire e concatenare i testi di ogni utente
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
