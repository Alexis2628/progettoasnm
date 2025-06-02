import re
import logging
from typing import Union

logger = logging.getLogger(__name__)

class Preprocessor:
    """
    Classe per la pre-elaborazione minima del testo:
      - trasformazione in minuscolo
      - rimozione di URL e menzioni (@username)
      - mantenimento di emoji e caratteri speciali
    """

    @staticmethod
    def preprocess_text(text: Union[str, None]) -> str:
        """
        Parametri:
            text: stringa originale (o anche None). Se None o non str, ritorna stringa vuota.

        Ritorna:
            stringa pre-elaborata.
        """
        if not isinstance(text, str):
            logger.warning(f"preprocess_text ricevuto input non-stringa: {text!r}. Restituisco stringa vuota.")
            return ""

        logger.debug(f"Pre-elaborazione testo originale: '{text[:30]}...'")

        # 1) minuscolo
        text = text.lower()
        logger.debug(" - Trasformato in minuscolo")

        # 2) rimozione URL (http, https, www)
        text = re.sub(r'http\S+|www\.\S+', '', text)
        logger.debug(" - Rimosse eventuali URL")

        # 3) rimozione menzioni @username
        text = re.sub(r'@\w+', '', text)
        logger.debug(" - Rimosse eventuali menzioni @username")

        # 4) riduce spazi multipli
        text = re.sub(r'\s+', ' ', text).strip()
        logger.debug(" - Ridotti spazi multipli e rimosso leading/trailing spaces")

        logger.debug(f"Testo pre-elaborato: '{text[:30]}...'")
        return text
