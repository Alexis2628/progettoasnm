import os
import numpy as np
import pandas as pd
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix
import gc


class SentimentVisualizer:
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def visualize_sentiment_distribution(self, sentiment_scores, cluster_labels):
        violin_plot_path = f"{self.output_dir}/sentiment_violin_plot.png"
        bar_plot_path = f"{self.output_dir}/sentiment_bar_plot.png"

        if os.path.exists(violin_plot_path) and os.path.exists(bar_plot_path):
            logging.info("I grafici di distribuzione del sentiment esistono già. Salto la generazione.")
            return

        logging.info("Visualizzazione della distribuzione del sentiment tra i cluster.")
        data = pd.DataFrame(
            {
                "User": list(sentiment_scores.keys()),
                "Sentiment": list(sentiment_scores.values()),
                "Cluster": [cluster_labels[user] for user in sentiment_scores.keys()],
            }
        )

        if not os.path.exists(violin_plot_path):
            plt.figure(figsize=(12, 6))
            sns.violinplot(
                x="Cluster",
                y="Sentiment",
                data=data,
                hue="Cluster",
                palette="coolwarm",
                legend=False,
            )
            plt.title("Distribuzione del sentiment nei cluster (Violino)")
            plt.xlabel("Cluster")
            plt.ylabel("Sentiment")
            plt.savefig(violin_plot_path)
            plt.close()
            gc.collect()

        if not os.path.exists(bar_plot_path):
            plt.figure(figsize=(12, 6))
            sns.barplot(
                x="Cluster",
                y="Sentiment",
                data=data,
                estimator=np.mean,
                errorbar=None,
                palette="viridis",
                hue="Cluster",
                legend=False,
            )
            plt.title("Sentiment medio per cluster (Barre)")
            plt.xlabel("Cluster")
            plt.ylabel("Sentiment medio")
            plt.savefig(bar_plot_path)
            plt.close()
            gc.collect()

        logging.info("Visualizzazione della distribuzione del sentiment completata.")

    def visualize_sentiment_vs_themes_heatmap(
        self, sentiment_scores, user_opinions, cluster_labels
    ):
        heatmap_path = f"{self.output_dir}/sentiment_themes_heatmap.png"

        if os.path.exists(heatmap_path):
            logging.info("La heatmap sentiment vs temi polarizzanti esiste già. Salto la generazione.")
            return

        logging.info("Creazione della heatmap tra sentiment e temi polarizzanti.")
        vectorizer = TfidfVectorizer(max_features=1000)
        tfidf_matrix = vectorizer.fit_transform(user_opinions.values())
        feature_names = vectorizer.get_feature_names_out()

        sentiment_array = np.array(
            [sentiment_scores[user] for user in user_opinions.keys()]
        )

        sentiment_to_terms_corr = np.array(
            [
                np.corrcoef(sentiment_array, tfidf_matrix[:, i].toarray().flatten())[0, 1]
                for i in range(tfidf_matrix.shape[1])
            ]
        )

        top_indices = np.argsort(np.abs(sentiment_to_terms_corr))[-20:]
        top_words = [feature_names[i] for i in top_indices]
        correlations = sentiment_to_terms_corr[top_indices]

        heatmap_data = pd.DataFrame(
            {"Terms": top_words, "Correlation": correlations}
        ).pivot_table(index="Terms", values="Correlation")

        plt.figure(figsize=(12, 8))
        sns.heatmap(heatmap_data, annot=True, fmt=".2f", cmap="coolwarm", cbar=True)
        plt.title("Relazione tra Sentiment e Temi Polarizzanti")
        plt.savefig(heatmap_path)
        plt.close()
        gc.collect()
        logging.info("Heatmap sentiment vs temi polarizzanti creata e salvata.")
