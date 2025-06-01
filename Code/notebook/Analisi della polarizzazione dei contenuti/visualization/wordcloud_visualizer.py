import logging
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os


class WordCloudVisualizer:
    @staticmethod
    def visualize(polarizing_words, output_dir, num):
        output_path = os.path.join(output_dir, f"polarizing_themes_{num}Gram.png")

        if os.path.exists(output_path):
            logging.info(f"Il file {output_path} esiste già. Salto la generazione della word cloud.")
            return

        logging.info("Creazione della word cloud.")
        word_cloud = WordCloud(
            width=800, height=400, background_color="white"
        ).generate(" ".join(polarizing_words))
        plt.figure(figsize=(10, 6))
        plt.imshow(word_cloud, interpolation="bilinear")
        plt.axis("off")
        plt.savefig(output_path)
        plt.close()
        logging.info("Word cloud creata e salvata.")
