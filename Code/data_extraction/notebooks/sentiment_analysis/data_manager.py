import os
import logging
from typing import Optional, Set

import pandas as pd

logger = logging.getLogger(__name__)

class DataManager:
    """
    Classe per gestire il caricamento dei CSV di input/output, il filtraggio dei post già
    processati e il salvataggio dei risultati. Ora supporta un output_dir diverso da input.
    """

    def __init__(self, input_path: str, output_dir: Optional[str] = None, suffix: str = "_sentiment_analysis"):
        """
        Parametri:
            input_path (str): percorso al file CSV di input.
            output_dir (str o None): cartella in cui salvare il file di output. 
                                     Se None, salva nella stessa cartella di input.
            suffix (str): suffisso da aggiungere al nome base per il file di output (default "_sentiment_analysis").
        """
        logger.info(f"Inizializzazione DataManager con input_path: '{input_path}', output_dir: '{output_dir}', suffisso: '{suffix}'")
        self.input_path = input_path

        # Estrai nome base del file (senza path e senza estensione)
        base_filename = os.path.splitext(os.path.basename(input_path))[0]
        output_filename = f"{base_filename}{suffix}.csv"

        # Se è stata fornita una cartella di output, assicurati che esista o la crei
        if output_dir:
            if not os.path.isdir(output_dir):
                try:
                    os.makedirs(output_dir, exist_ok=True)
                    logger.info(f"Cartella di output '{output_dir}' creata (o già esistente).")
                except Exception as e:
                    logger.error(f"Impossibile creare la cartella di output '{output_dir}': {e}")
                    raise
            # Costruisci il percorso completo in output_dir
            self.output_path = os.path.join(output_dir, output_filename)
        else:
            # Comportamento originale: stesso percorso di input, stesse cartelle
            base, _ = os.path.splitext(input_path)
            self.output_path = f"{base}{suffix}.csv"

        logger.debug(f"Percorso di output calcolato: '{self.output_path}'")

        self.df_input: Optional[pd.DataFrame] = None    # DataFrame con tutti i dati di input
        self.df_output: Optional[pd.DataFrame] = None   # DataFrame con i dati già processati (se esiste)
        self.df_new: Optional[pd.DataFrame] = None      # DataFrame con i soli post nuovi da processare

    def load_input(self) -> bool:
        """
        Carica il file CSV di input in self.df_input. 
        Ritorna True se l'operazione ha avuto successo, False altrimenti.
        """
        logger.info(f"Caricamento file di input: '{self.input_path}'")
        try:
            self.df_input = pd.read_csv(
                self.input_path,
                dtype={'id': object, 'post_pk': object}
            )
            logger.info(f"File di input caricato correttamente ({len(self.df_input)} righe).")
            return True
        except Exception as e:
            logger.error(f"Errore nel caricamento del file di input '{self.input_path}': {e}")
            self.df_input = None
            return False

    def load_existing_output(self) -> None:
        """
        Se il file di output già esiste, lo carica in self.df_output.
        Altrimenti lascia self.df_output = None.
        """
        logger.info(f"Verifica esistenza file di output: '{self.output_path}'")
        if os.path.isfile(self.output_path):
            logger.info(f"Il file di output esiste. Tentativo di caricamento: '{self.output_path}'")
            try:
                self.df_output = pd.read_csv(
                    self.output_path,
                    dtype={'id': object, 'post_pk': object}
                )
                logger.info(f"File di output caricato correttamente ({len(self.df_output)} righe).")
            except Exception as e:
                logger.error(f"Errore nel caricamento del file di output '{self.output_path}': {e}")
                self.df_output = None
        else:
            logger.info("Nessun file di output esistente trovato.")
            self.df_output = None

    def filter_new_posts(self) -> None:
        """
        Filtra i post nuovi (non ancora processati) mettendoli in self.df_new.
        Se non esiste file di output, tutti i post di input sono nuovi.
        """
        if self.df_input is None:
            logger.error("filter_new_posts chiamato prima di load_input. df_input è None.")
            raise RuntimeError("Prima di filtrare devi aver caricato df_input.")

        if self.df_output is None:
            # Tutti i post di input sono nuovi
            self.df_new = self.df_input.copy()
            logger.info(f"Tutti i {len(self.df_new)} post di input saranno processati (nessun file di output precedente).")
        else:
            processed_pks: Set = set(self.df_output['post_pk'].astype(str).tolist())
            total_input = len(self.df_input)
            logger.info(f"File di output precedente contiene {len(processed_pks)} post_pk già processati.")
            mask_new = ~self.df_input['post_pk'].astype(str).isin(processed_pks)
            self.df_new = self.df_input[mask_new].copy()
            new_count = len(self.df_new)
            logger.info(f"Su {total_input} post totali, {new_count} risultati nuovi da processare.")

    def save_combined(self, df_combined: pd.DataFrame) -> None:
        """
        Salva il DataFrame df_combined (concatenazione di output esistente + nuovi) nel file di output.
        """
        logger.info(f"Salvataggio DataFrame combinato su '{self.output_path}' ({len(df_combined)} righe).")
        try:
            df_combined.to_csv(self.output_path, index=False)
            logger.info("Salvataggio completato con successo.")
        except Exception as e:
            logger.error(f"Errore nel salvataggio del file di output '{self.output_path}': {e}")

    def get_output_columns(self) -> list:
        """
        Ritorna la lista di colonne presenti in un eventuale df_output. 
        Se non esiste output, ritorna una lista vuota.
        """
        if self.df_output is not None:
            cols = list(self.df_output.columns)
            logger.debug(f"Colonne trovate in df_output: {cols}")
            return cols
        logger.debug("Nessun df_output esistente: restituisco lista vuota di colonne.")
        return []
