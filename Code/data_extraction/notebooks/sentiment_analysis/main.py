import os
import sys
import argparse
import logging
import math
from typing import List, Optional

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
import pandas as pd

from Code.data_extraction.notebooks.sentiment_analysis.data_manager import DataManager
from Code.data_extraction.notebooks.sentiment_analysis.preprocessor import Preprocessor
from Code.data_extraction.notebooks.sentiment_analysis.analyzers import VaderSentimentAnalyzer, TransformerSentimentAnalyzer
from Code.data_extraction.notebooks.sentiment_analysis.summarizer import Summarizer

# Configurazione base di logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def main(input_files: List[str], output_dir: Optional[str] = None):
    """
    Per ciascun file CSV di input:
      1) Inizializza DataManager con input_path.
      2) Carica input e output (se esiste).
      3) Filtra i post nuovi.
      4) Suddivide i nuovi post in blocchi di 1000 righe.
      5) Per ogni blocco:
         a) Pre-elabora i testi
         b) Esegue l'analisi del sentiment (VADER + Transformer)
         c) Aggiunge le colonne di sentiment
         d) Scrive (o appende) il blocco di 1000 righe sul CSV di output
         e) Aggiorna in memoria df_output concatenando il blocco
      6) Al termine di tutti i blocchi, stampa un riepilogo.
    """
    # Inizializza gli analizzatori di sentiment
    logger.info("Inizializzazione degli analizzatori di sentiment...")
    vader_analyzer = VaderSentimentAnalyzer()
    transformer_analyzer = TransformerSentimentAnalyzer()
    logger.info("Analizzatori di sentiment pronti.")

    for input_path in input_files:
        file_label = os.path.basename(input_path)
        logger.info(f"--- Elaborazione file: {file_label} ---")

        # 1) Inizializza DataManager
        dm = DataManager(input_path, output_dir=output_dir)
        logger.info(f"Creata istanza DataManager per '{file_label}', output previsto: '{os.path.basename(dm.output_path)}'")

        # 2) Carica eventuale output esistente
        dm.load_existing_output()

        # Carica file di input
        if not dm.load_input():
            logger.error(f"Caricamento del file di input '{file_label}' fallito. Passo al prossimo.")
            continue

        # 3) Filtra i post nuovi
        logger.info(f"Filtraggio dei post nuovi rispetto a quelli già processati (se presenti) per '{file_label}'...")
        dm.filter_new_posts()

        # Se non ci sono post nuovi, stampo riepilogo rapido e vado avanti
        if dm.df_new is None or dm.df_new.empty:
            if dm.df_output is not None:
                logger.info(f"Nessun nuovo post da processare in '{file_label}'. Stampo riepilogo basato su output esistente.")
                Summarizer.print_summary(dm.df_new, dm.df_output, file_label)
            else:
                logger.info(f"[{file_label}] Nessun dato da processare e nessun output precedente.")
            continue

        # Impostiamo variabili per il salvataggio a blocchi
        total_new = len(dm.df_new)
        blocco_size = 1000
        num_blocchi = math.ceil(total_new / blocco_size)
        logger.info(f"Totale nuovi post da processare: {total_new} → {num_blocchi} blocchi da {blocco_size} righe (ultimo blocco potrebbe essere più piccolo).")

        # Se esiste già un output precedente, partiremo appending; altrimenti il primo blocco scriverà con header.
        output_exists = os.path.isfile(dm.output_path)

        # Se esiste output, carichiamolo in df_output_in_memory per aggiornare la lista dei processati
        if dm.df_output is not None:
            df_output_in_memory = dm.df_output.copy()
        else:
            df_output_in_memory = pd.DataFrame()  # vuoto, verrà popolato dai blocchi

        # 4) Loop sui blocchi di 1000 righe di df_new
        for i in range(num_blocchi):
            start_idx = i * blocco_size
            end_idx = min(start_idx + blocco_size, total_new)
            blocco_df = dm.df_new.iloc[start_idx:end_idx].copy()
            blocco_label = f"blocco {i+1}/{num_blocchi} (righe {start_idx+1}-{end_idx})"
            logger.info(f"Elaborazione {blocco_label} di '{file_label}'...")

            # 4.a) Pre-elaborazione testi
            blocco_df['text_clean'] = blocco_df['caption_text_translated'].apply(Preprocessor.preprocess_text)

            # 4.b) Analisi del sentiment
            texts = blocco_df['text_clean'].tolist()

            logger.info(f"[{blocco_label}] Avvio VADER per {len(texts)} testi...")
            vader_results = vader_analyzer.analyze(texts)
            logger.info(f"[{blocco_label}] VADER completato.")

            logger.info(f"[{blocco_label}] Avvio Transformer per {len(texts)} testi...")
            transformer_results = transformer_analyzer.analyze(texts)
            logger.info(f"[{blocco_label}] Transformer completato.")

            # 4.c) Aggiunta colonne di sentiment
            blocco_df['vader_compound'] = [t[0] for t in vader_results]
            blocco_df['vader_label'] = [t[1] for t in vader_results]
            blocco_df['transformer_label'] = [t[0] for t in transformer_results]
            blocco_df['transformer_score'] = [t[1] for t in transformer_results]

            # 4.d) Scrittura/appending su file di output
            # Se l'output non esisteva (primo blocco) → scrivi con header; altrimenti append senza header.
            if i == 0 and not output_exists:
                # Primo blocco e file di output ancora inesistente: scrive con header
                logger.info(f"[{blocco_label}] Scrivo file di output (nuovo) con header: '{dm.output_path}'")
                blocco_df.to_csv(dm.output_path, index=False, mode='w', header=True)
                output_exists = True
            else:
                # Blocchi successivi o file di output già esistente: append senza header
                logger.info(f"[{blocco_label}] Aggiungo (append) su '{dm.output_path}' senza header.")
                blocco_df.to_csv(dm.output_path, index=False, mode='a', header=False)

            # 4.e) Aggiorna df_output_in_memory concatenando il blocco
            if df_output_in_memory.empty:
                df_output_in_memory = blocco_df.copy()
            else:
                # In questo modo, df_output_in_memory mantiene tutti i processati fino ad ora
                df_output_in_memory = pd.concat([df_output_in_memory, blocco_df], ignore_index=True)

            logger.info(f"[{blocco_label}] Salvato su disco. Totale processati in memoria: {len(df_output_in_memory)}")

        # 5) Al termine di tutti i blocchi, stampo riepilogo
        logger.info(f"Tutti i blocchi elaborati per '{file_label}'. Stampo riepilogo finale.")
        Summarizer.print_summary(dm.df_new, df_output_in_memory, file_label)

        logger.info(f"--- Fine elaborazione file: {file_label} ---\n")

    logger.info("Elaborazione completata per tutti i file.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script per analisi del sentiment su post social media in file CSV."
    )
    parser.add_argument(
        "--input_files",
        nargs="+",
        required=False,
        help="Percorsi dei file CSV di input (almeno uno, separati da spazio).",
        default=[
            r"Code\data_extraction\data\interim\post_data\total_post1.csv",
            r"Code\data_extraction\data\interim\post_data\total_post2.csv",
            r"Code\data_extraction\data\interim\post_data\total_post3.csv"
        ]
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        required=False,
        default=None,
        help="Cartella in cui salvare i file di output. Se non specificata, salva nella stessa cartella di input."
    )
    args = parser.parse_args()

    # Controllo che tutti i file di input esistano
    missing = [f for f in args.input_files if not os.path.isfile(f)]
    if missing:
        logger.error(f"I seguenti file di input non esistono: {missing}")
        sys.exit(1)

    main(args.input_files, args.output_dir)
