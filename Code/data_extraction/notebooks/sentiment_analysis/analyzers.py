import logging
from typing import List, Tuple

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

logger = logging.getLogger(__name__)

# VADER (nemmeno toccato, ma lo includo per contesto)
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    logger.info("Lessico VADER non trovato. Avvio download del lexicon...")
    nltk.download('vader_lexicon')
    logger.info("Download del lessico VADER completato.")

class VaderSentimentAnalyzer:
    def __init__(self):
        logger.info("Inizializzazione di SentimentIntensityAnalyzer (VADER)...")
        self.analyzer = SentimentIntensityAnalyzer()
        logger.info("VADER inizializzato correttamente.")

    def analyze(self, texts: List[str]) -> List[Tuple[float, str]]:
        logger.info(f"Avvio analisi VADER su {len(texts)} testi.")
        results = []
        for idx, txt in enumerate(texts, start=1):
            vs = self.analyzer.polarity_scores(txt)
            compound = vs['compound']
            if compound >= 0.05:
                label = 'positive'
            elif compound <= -0.05:
                label = 'negative'
            else:
                label = 'neutral'
            results.append((compound, label))

            if idx % 100 == 0:
                logger.debug(f"VADER: elaborati {idx}/{len(texts)} testi.")

        logger.info("Analisi VADER completata.")
        return results


class TransformerSentimentAnalyzer:

    def __init__(self, model_name: str = "cardiffnlp/twitter-roberta-base-sentiment"):
        logger.info(f"Inizializzazione del modello Transformer '{model_name}'...")
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
            # Passiamo device e lasciamo che il pipeline gestisca truncation dinamicamente
            self.nlp_pipeline = pipeline(
                "sentiment-analysis",
                model=model,
                tokenizer=tokenizer,
                return_all_scores=False,
                top_k=1,
                device=0  # usa GPU se disponibile, altrimenti -1 per CPU
            )
            logger.info(f"Modello Transformer '{model_name}' caricato correttamente.")
        except Exception as e:
            logger.error(f"Errore nel caricamento del modello Transformer '{model_name}': {e}")
            raise

    def analyze(self, texts: List[str]) -> List[Tuple[str, float]]:
        """
        Parametri:
            texts: lista di stringhe già pre-elaborate.

        Ritorna:
            lista di tuple (label: str, score: float). In caso di eccezione su un testo,
            ritorna ("error", 0.0) per quel singolo elemento.
        Ora gestisce automaticamente il troncamento di testi > 512 token.
        """
        logger.info(f"Avvio analisi Transformer su {len(texts)} testi.")
        results = []
        for idx, txt in enumerate(texts, start=1):
            try:
                # Passiamo truncation=True per troncare automaticamente input più lunghi di 512
                out = self.nlp_pipeline(txt, truncation=True, max_length=512)

                # Gestiamo i tre possibili formati di output [[{…}]] / [{…}] / {…}
                if isinstance(out, list) and len(out) > 0 and isinstance(out[0], list) \
                   and len(out[0]) > 0 and isinstance(out[0][0], dict):
                    label = out[0][0].get('label', 'error')
                    score = out[0][0].get('score', 0.0)
                elif isinstance(out, list) and len(out) > 0 and isinstance(out[0], dict):
                    label = out[0].get('label', 'error')
                    score = out[0].get('score', 0.0)
                elif isinstance(out, dict):
                    label = out.get('label', 'error')
                    score = out.get('score', 0.0)
                else:
                    logger.warning(f"Formato output Transformer inaspettato per index={idx}: {out!r}")
                    label = "error"
                    score = 0.0

                results.append((label, score))

            except Exception as e:
                logger.warning(
                    f"Errore nell'analisi Transformer per testo index={idx}: '{txt[:30]}...' – {e}"
                )
                results.append(("error", 0.0))

            if idx % 100 == 0:
                logger.debug(f"Transformer: elaborati {idx}/{len(texts)} testi.")

        logger.info("Analisi Transformer completata.")
        return results