import pandas as pd
import logging

logger = logging.getLogger(__name__)

class Summarizer:
    """
    Classe con metodo statico per stampare un breve riepilogo della distribuzione
    dei sentiment (sia per i post nuovi di questa esecuzione, sia per l'output complessivo).
    """

    @staticmethod
    def print_summary(df_new: pd.DataFrame,
                      df_combined: pd.DataFrame,
                      file_label: str) -> None:
        """
        Parametri:
            df_new (DataFrame): DataFrame dei soli post elaborati in questa esecuzione.
            df_combined (DataFrame): DataFrame complessivo (vecchi + nuovi).
            file_label (str): nome del file di input (per etichettare il riepilogo).
        """
        logger.info(f"Avvio riepilogo per '{file_label}'")

        if df_new is None or df_new.empty:
            logger.info(f"[{file_label}] Nessun nuovo post elaborato in questa esecuzione.")
            print(f"[{file_label}] Nessun nuovo post elaborato in questa esecuzione.\n")
            return

        # Calcolo delle distribuzioni
        logger.debug("Calcolo distribuzione sentiment sui nuovi post...")
        vader_counts = df_new['vader_label'].value_counts().to_dict() if 'vader_label' in df_new else {}
        transformer_counts = df_new['transformer_label'].value_counts().to_dict() if 'transformer_label' in df_new else {}
        logger.debug(f"Distribuzione NUOVI POST - VADER: {vader_counts}")
        logger.debug(f"Distribuzione NUOVI POST - Transformer: {transformer_counts}")

        logger.debug("Calcolo distribuzione sentiment complessiva (vecchi + nuovi)...")
        vader_counts_all = df_combined['vader_label'].value_counts().to_dict() if 'vader_label' in df_combined else {}
        transformer_counts_all = df_combined['transformer_label'].value_counts().to_dict() if 'transformer_label' in df_combined else {}
        logger.debug(f"Distribuzione COMPLESSIVA OUTPUT - VADER: {vader_counts_all}")
        logger.debug(f"Distribuzione COMPLESSIVA OUTPUT - Transformer: {transformer_counts_all}")

        # Stampa a video
        print(f"\n--- Riepilogo per '{file_label}' ---")
        print("1) Distribuzione sentiment NUOVI POST (solo per questa esecuzione):")
        print(f"   - VADER: {vader_counts}")
        print(f"   - Transformer: {transformer_counts}")
        print("2) Distribuzione sentiment COMPLESSIVA OUTPUT:")
        print(f"   - VADER: {vader_counts_all}")
        print(f"   - Transformer: {transformer_counts_all}")
        print(f"--- Fine Riepilogo per '{file_label}' ---\n")

        logger.info(f"Riepilogo per '{file_label}' completato.")
