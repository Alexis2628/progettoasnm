import logging
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os


class WordCloudVisualizer:
    @staticmethod
    def visualize(polarizing_words, output_dir, prefix):
        """
        Genera e salva una word cloud partendo da una lista (o dizionario) di parole polarizzanti.

        Args:
            polarizing_words (list[str] | dict[Any, list[str]]):
                - Se è una lista, ogni elemento è una singola parola/termine.
                - Se è un dizionario, viene considerato come {cluster_id: [parola1, parola2, ...]}.
            output_dir (str): cartella di destinazione per salvare il file immagine.
            prefix (str): stringa usata come prefisso per il nome del file (es. "TFIDF_Un" o "EMB_Bi").
        """
        # 1. Creo la cartella di output se non esiste
        os.makedirs(output_dir, exist_ok=True)

        # 2. Appiattisco il dizionario (o copio direttamente la lista)
        if isinstance(polarizing_words, dict):
            flat_list = []
            for cluster_id, kw_list in polarizing_words.items():
                if isinstance(kw_list, (list, tuple, set)):
                    flat_list.extend(kw_list)
                else:
                    logging.warning(
                        f"WordCloudVisualizer: il valore associato al cluster {cluster_id} "
                        f"non è una lista/tuple/set; ignoro {kw_list!r}"
                    )
            polar_list = flat_list
        elif isinstance(polarizing_words, (list, tuple, set)):
            polar_list = list(polarizing_words)
        else:
            logging.error(
                f"WordCloudVisualizer: parametro 'polarizing_words' di tipo non valido ({type(polarizing_words)}). "
                "Deve essere una lista o un dizionario. Esco senza generare la word cloud."
            )
            return

        # 3. Se la lista è vuota, non facciamo nulla
        if not polar_list:
            logging.warning(
                "WordCloudVisualizer: lista di parole polarizzanti vuota. "
                "Niente da visualizzare, salto la generazione della word cloud."
            )
            return

        # 4. Nome completo del file di output
        output_path = os.path.join(output_dir, f"polarizing_themes_{prefix}.png")

        # 5. Se il file esiste già, skippo la creazione
        if os.path.exists(output_path):
            logging.info(f"Il file {output_path} esiste già. Salto la generazione della word cloud.")
            return

        # 6. Creo e salvo la word cloud
        try:
            logging.info("WordCloudVisualizer: inizio creazione della word cloud.")
            text_for_cloud = " ".join(polar_list)

            word_cloud = WordCloud(
                width=800,
                height=400,
                background_color="white"
            ).generate(text_for_cloud)

            plt.figure(figsize=(10, 6))
            plt.imshow(word_cloud, interpolation="bilinear")
            plt.axis("off")
            plt.tight_layout()
            plt.savefig(output_path, bbox_inches="tight")
            plt.close()

            logging.info(f"WordCloudVisualizer: word cloud creata e salvata in {output_path}.")
        except Exception as e:
            logging.error(f"WordCloudVisualizer: errore durante la generazione della word cloud: {e}")
