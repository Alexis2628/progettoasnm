import logging
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import re


class WordCloudVisualizer:
    @staticmethod
    def visualize(polarizing_words, output_dir, prefix, font_path=None):
        """Crea e salva una word cloud delle parole polarizzanti."""
        os.makedirs(output_dir, exist_ok=True)

        if isinstance(polarizing_words, dict):
            flat_list = []
            for cluster_id, kw_list in polarizing_words.items():
                if isinstance(kw_list, (list, tuple, set)):
                    flat_list.extend(kw_list)
                else:
                    logging.warning(
                        f"Cluster {cluster_id} non è una lista; ignoro {kw_list!r}"
                    )
            polar_list = flat_list
        elif isinstance(polarizing_words, (list, tuple, set)):
            polar_list = list(polarizing_words)
        else:
            logging.error(
                f"'polarizing_words' di tipo non valido ({type(polarizing_words)})."
            )
            return

        if not polar_list:
            logging.warning("Lista di parole vuota. Skip generation.")
            return

        ascii_pattern = re.compile(r"^[\x00-\x7F]+$")
        filtered = [w for w in polar_list if ascii_pattern.match(w)]
        if len(filtered) < len(polar_list):
            logging.info(f"Filtrate {len(polar_list)-len(filtered)} parole non-ASCII.")
        polar_list = filtered

        if not polar_list:
            logging.warning("Dopo il filtro ASCII la lista è vuota. Skip generation.")
            return

        output_path = os.path.join(output_dir, f"polarizing_themes_{prefix}.png")
        if os.path.exists(output_path):
            logging.info(f"{output_path} già esistente. Skip.")
            return

        try:
            logging.info("Inizio creazione della word cloud.")
            tokens = [kw.replace(" ", "_") if " " in kw else kw for kw in polar_list]
            text_for_cloud = " ".join(tokens)
            word_cloud = WordCloud(
                font_path=font_path if font_path else None,
                background_color="white",
                colormap="viridis",
                collocations=False,
                width=800,
                height=400,
            ).generate(text_for_cloud)

            plt.figure(figsize=(10, 6))
            plt.imshow(word_cloud, interpolation="bilinear")
            plt.axis("off")
            plt.tight_layout()
            plt.savefig(output_path, bbox_inches="tight")
            plt.close()
            logging.info(f"Word cloud salvata in {output_path}.")
        except Exception as e:
            logging.error(f"Errore generazione word cloud: {e}")
