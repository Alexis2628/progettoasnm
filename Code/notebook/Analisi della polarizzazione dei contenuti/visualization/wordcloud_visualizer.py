import logging
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os


class WordCloudVisualizer:
    @staticmethod
    def visualize(polarizing_words, output_dir, num):
        """
        Genera e salva una word cloud partendo da una lista (o dizionario) di parole polarizzanti.

        Args:
            polarizing_words (list[str] | dict[Any, list[str]]):
                - Se è una lista, ogni elemento è una singola parola/termine.
                - Se è un dizionario, viene considerato come {cluster_id: [parola1, parola2, ...]}.
            output_dir (str): cartella di destinazione per salvare il file immagine.
            num (str): prefisso per il nome del file (es. "Un", "Bi" o "TFIDF_Un", ...).
        """
        # 1. Assicuriamoci che output_dir esista
        os.makedirs(output_dir, exist_ok=True)

        # 2. Se polarizing_words è un dict, lo appiattiamo in una lista unica
        if isinstance(polarizing_words, dict):
            flat_list = []
            for kw_list in polarizing_words.values():
                if isinstance(kw_list, (list, tuple, set)):
                    flat_list.extend(kw_list)
                else:
                    logging.warning(
                        "WordCloudVisualizer: valore non iterabile rilevato in polarizing_words dict; "
                        f"ignoro il contenuto di cluster {kw_list}"
                    )
            polar_list = flat_list
        elif isinstance(polarizing_words, (list, tuple, set)):
            polar_list = list(polarizing_words)
        else:
            logging.error(
                "WordCloudVisualizer: polarizing_words deve essere una lista o un dizionario, "
                f"ma ho ricevuto {type(polarizing_words)}. Esco senza generare la word cloud."
            )
            return

        # 3. Se la lista risultante è vuota, avvertiamo e usciamo
        if not polar_list:
            logging.warning(
                "WordCloudVisualizer: lista di parole polarizzanti vuota. "
                "Niente da visualizzare, salto la generazione della word cloud."
            )
            return

        # 4. Percorso completo del file di output
        output_path = os.path.join(output_dir, f"polarizing_themes_{num}Gram.png")

        # 5. Se il file esiste già, non rigeneriamo
        if os.path.exists(output_path):
            logging.info(
                f"Il file {output_path} esiste già. Salto la generazione della word cloud."
            )
            return

        # 6. Generazione e salvataggio della word cloud
        try:
            logging.info("Creazione della word cloud.")
            # Join delle parole in un’unica stringa separata da spazi
            text_for_cloud = " ".join(polar_list)

            word_cloud = WordCloud(
                width=800,
                height=400,
                background_color="white"
            ).generate(text_for_cloud)

            plt.figure(figsize=(10, 6))
            plt.imshow(word_cloud, interpolation="bilinear")
            plt.axis("off")
            plt.savefig(output_path, bbox_inches="tight")
            plt.close()
            logging.info(f"Word cloud creata e salvata in {output_path}.")
        except Exception as e:
            logging.error(f"Errore durante la generazione della word cloud: {e}")
