import argparse
import logging
import sys
from pathlib import Path
import os
sys.path.insert(0, os.path.abspath("../../../"))
import pandas as pd
from deep_translator import GoogleTranslator


def setup_logging(level: str = "INFO") -> None:
    """
    Configura il logging di base per tutto il modulo.
    """
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def translate_text(text: str, target_lang: str = "en") -> str:
    """
    Traduce il testo passato in target_lang (default 'en').
    Se la traduzione fallisce, restituisce il testo originale.
    """
    try:
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except Exception as e:
        logging.warning(f"[translate_text] Errore durante la traduzione: {e}")
        return text


def process_single_file(
    in_path: Path, out_path: Path, target_lang: str = "en"
) -> None:
    """
    Esegue la pulizia e traduzione di un singolo file CSV.
    - Controlla l'esistenza del file
    - Crea la cartella di destinazione se necessario
    - Verifica la presenza delle colonne attese
    - Converte i tipi, rimuove duplicati, traduce i testi
    - Gestisce eventuali errori senza interrompere l'intero flusso
    """
    logging.info(f"Inizio elaborazione: '{in_path}'")

    if not in_path.exists():
        logging.error(f"File non trovato: {in_path}")
        return

    try:
        df = pd.read_csv(in_path)
    except Exception as e:
        logging.error(f"Impossibile leggere '{in_path}': {e}")
        return

    expected_cols = {
        "id",
        "post_pk",
        "like_count",
        "quote_count",
        "repost_count",
        "reshare_count",
        "taken_at",
        "username",
        "user_pk",
        "caption_text",
        "caption_text_translated",
        "sentiment_score",
        "sentiment_label",
        "thread_user_pk",
    }
    missing = expected_cols - set(df.columns)
    if missing:
        logging.warning(
            f"Il file '{in_path.name}' manca delle colonne: {sorted(missing)}. "
            "Procedo comunque con le colonne disponibili."
        )

    # 1. Conversione tipi di colonna (se esistono)
    try:
        if "id" in df.columns:
            df["id"] = df["id"].astype(str)
        if "post_pk" in df.columns:
            df["post_pk"] = df["post_pk"].astype(str)
        if "like_count" in df.columns:
            df["like_count"] = pd.to_numeric(df["like_count"], errors="coerce", downcast="integer")
        if "quote_count" in df.columns:
            df["quote_count"] = pd.to_numeric(df["quote_count"], errors="coerce", downcast="integer")
        if "repost_count" in df.columns:
            df["repost_count"] = pd.to_numeric(df["repost_count"], errors="coerce", downcast="integer")
        if "reshare_count" in df.columns:
            df["reshare_count"] = pd.to_numeric(df["reshare_count"], errors="coerce", downcast="integer")
        if "taken_at" in df.columns:
            df["taken_at"] = pd.to_datetime(df["taken_at"], errors="coerce")
        if "username" in df.columns:
            df["username"] = df["username"].astype(str)
        if "user_pk" in df.columns:
            df["user_pk"] = pd.to_numeric(df["user_pk"], errors="coerce", downcast="integer")
        if "caption_text" in df.columns:
            df["caption_text"] = df["caption_text"].astype(str)
        if "caption_text_translated" in df.columns:
            df["caption_text_translated"] = df["caption_text_translated"].astype(str)
        if "sentiment_score" in df.columns:
            df["sentiment_score"] = pd.to_numeric(df["sentiment_score"], errors="coerce")
        if "sentiment_label" in df.columns:
            df["sentiment_label"] = df["sentiment_label"].astype("category")
        if "thread_user_pk" in df.columns:
            df["thread_user_pk"] = pd.to_numeric(df["thread_user_pk"], errors="coerce", downcast="integer")
    except Exception as e:
        logging.error(f"Errore nella conversione dei tipi nel file '{in_path.name}': {e}")

    # 2. Sostituzione delle date default "1970-01-01" con NaT (se c'è 'taken_at')
    if "taken_at" in df.columns:
        default_date = pd.Timestamp("1970-01-01 00:00:00")
        df["taken_at"] = df["taken_at"].replace(default_date, pd.NaT)

    # 3. Rimozione duplicati basati su più colonne
    before = df.shape[0]
    df = df.drop_duplicates(subset=["id", "post_pk", "username", "thread_user_pk"])
    after = df.shape[0]
    logging.info(f"Droppati {before - after} duplicati (colonne 'id,post_pk,username,thread_user_pk'). Dimensione attuale: {df.shape}")

    # 4. Traduzione: solo se 'caption_text_translated' è vuoto o uguale all'originale
    if "caption_text" in df.columns and "caption_text_translated" in df.columns:
        total_rows = len(df)
        translated_texts = []
        for idx, row in df.iterrows():
            orig = row["caption_text"]
            translated = row["caption_text_translated"]
            if not isinstance(translated, str) or translated.strip() == "":
                new_text = translate_text(orig, target_lang=target_lang)
            else:
                new_text = translated
            translated_texts.append(new_text)

            # Log ogni 1000 righe
            if (idx + 1) % 1000 == 0:
                logging.info(f"Tradotte {idx + 1} righe su {total_rows}...")

        df["caption_text_translated"] = translated_texts
    else:
        logging.warning(
            f"Non trovo le colonne 'caption_text' e/o 'caption_text_translated' in '{in_path.name}', salto traduzione."
        )

    # 5. Creazione cartella di destinazione (se non esiste)
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logging.error(f"Impossibile creare la directory '{out_path.parent}': {e}")
        return

    # 6. Salvataggio del risultato
    try:
        df.to_csv(out_path, index=False)
        logging.info(f"File pulito e tradotto salvato in: '{out_path}'")
    except Exception as e:
        logging.error(f"Errore nel salvataggio di '{out_path}': {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Pulisce e traduce una serie di file CSV con post, rimuovendo duplicati e gestendo i tipi."
    )
    parser.add_argument(
        "--input-dir",
        "-i",
        type=Path,
        default=Path("Code/data_extraction/data/raw/post_data"),
        help="Directory contenente i file CSV di input (default: %(default)s)",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=Path("Code/data_extraction/data/interim/post_data"),
        help="Directory in cui salvare i CSV processati (default: %(default)s)",
    )
    parser.add_argument(
        "--files",
        "-f",
        nargs="+",
        default=["total_post1.csv", "total_post2.csv", "total_post3.csv"],
        help="Lista di nomi file CSV da elaborare (default: %(default)s)",
    )
    parser.add_argument(
        "--lang",
        "-l",
        type=str,
        default="en",
        help="Lingua target per la traduzione (default: 'en')",
    )
    parser.add_argument(
        "--log-level",
        "-L",
        type=str,
        default="INFO",
        help="Livello di logging (DEBUG, INFO, WARNING, ERROR; default: %(default)s)",
    )

    args = parser.parse_args()

    setup_logging(args.log_level)
    logging.info("Script avviato")
    logging.debug(f"Argomenti ricevuti: {args}")

    for filename in args.files:
        in_path = args.input_dir / filename
        out_path = args.output_dir / filename
        try:
            process_single_file(in_path, out_path, target_lang=args.lang)
        except Exception as e:
            logging.error(f"Errore inatteso durante l'elaborazione di '{filename}': {e}", exc_info=True)

    logging.info("Elaborazione terminata per tutti i file.")


if __name__ == "__main__":
    main()
