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
        violin_plot_path = os.path.join(self.output_dir, "sentiment_violin_plot.png")
        bar_plot_path = os.path.join(self.output_dir, "sentiment_bar_plot.png")

        if os.path.exists(violin_plot_path) and os.path.exists(bar_plot_path):
            logging.info("I grafici di distribuzione del sentiment esistono già. Salto la generazione.")
            return

        logging.info("Visualizzazione della distribuzione del sentiment tra i cluster.")

        # Costruisco il DataFrame
        data = pd.DataFrame(
            {
                "User": list(sentiment_scores.keys()),
                "Sentiment": list(sentiment_scores.values()),
                "Cluster": [cluster_labels[user] for user in sentiment_scores.keys()],
            }
        )

        # 1) Assicurarsi che 'Cluster' sia un tipo stringa/categoria
        #    in modo che Seaborn non tenti di usare .cat.categories su tipi non compatibili.
        data["Cluster"] = data["Cluster"].astype(str)

        # 2) Assicurarsi che 'Sentiment' sia numeric (float)
        data["Sentiment"] = pd.to_numeric(data["Sentiment"], errors="coerce")

        # Eliminare eventuali righe dove 'Sentiment' non è convertibile a float
        data = data.dropna(subset=["Sentiment"])

        # Ora genero i due grafici, se non esistono già
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
        heatmap_path = os.path.join(self.output_dir, "sentiment_themes_heatmap.png")

        if os.path.exists(heatmap_path):
            logging.info(
                "La heatmap sentiment vs temi polarizzanti esiste già. Salto la generazione."
            )
            return

        logging.info("Creazione della heatmap tra sentiment e temi polarizzanti.")

        # (1) Preparo un DataFrame temporaneo per allineare user, sentiment e testo
        df = pd.DataFrame({
            "User": list(user_opinions.keys()),
            "Text": list(user_opinions.values()),
            "Sentiment": [sentiment_scores.get(u, None) for u in user_opinions.keys()],
        })

        # (2) Convertiamo 'Sentiment' in numerico; se non è convertibile, diventa NaN
        df["Sentiment"] = pd.to_numeric(df["Sentiment"], errors="coerce")

        # (3) Scartiamo le righe in cui Sentiment è NaN
        df_valid = df.dropna(subset=["Sentiment"])
        if df_valid.empty:
            logging.warning(
                "Nessun valore di sentiment valido dopo la conversione. "
                "Non posso creare la heatmap."
            )
            return

        # (4) Calcolo TF-IDF solo sui testi corrispondenti a df_valid
        vectorizer = TfidfVectorizer(max_features=1000)
        tfidf_matrix = vectorizer.fit_transform(df_valid["Text"])
        feature_names = vectorizer.get_feature_names_out()

        # (5) Creiamo un array dei sentiment validi
        sentiment_array = df_valid["Sentiment"].to_numpy()

        # (6) Per ogni termine TF-IDF calcoliamo la correlazione con il sentiment_array
        correlations = []
        for i in range(tfidf_matrix.shape[1]):
            term_vector = tfidf_matrix[:, i].toarray().flatten()
            # Se term_vector è costantemente zero, corrcoef ritorna NaN: gestiamolo
            if np.all(term_vector == 0):
                correlations.append(0.0)
            else:
                corr = np.corrcoef(sentiment_array, term_vector)[0, 1]
                # In rari casi corr può essere NaN (ad es. varianza zero); sostituiamo con 0
                correlations.append(0.0 if np.isnan(corr) else corr)

        correlations = np.array(correlations)

        # (7) Selezioniamo i 20 termini con correlazione in valore assoluto più alta
        top_indices = np.argsort(np.abs(correlations))[-20:]
        top_words = [feature_names[i] for i in top_indices]
        top_corrs = correlations[top_indices]

        # (8) Costruiamo il DataFrame per la heatmap
        heatmap_data = pd.DataFrame({
            "Terms": top_words,
            "Correlation": top_corrs
        }).pivot_table(index="Terms", values="Correlation")

        # (9) Disegniamo la heatmap
        plt.figure(figsize=(12, 8))
        sns.heatmap(
            heatmap_data,
            annot=True,
            fmt=".2f",
            cmap="coolwarm",
            cbar=True,
            linewidths=0.5,
            linecolor="lightgray",
        )
        plt.title("Relazione tra Sentiment e Temi Polarizzanti")
        plt.savefig(heatmap_path, bbox_inches="tight")
        plt.close()
        gc.collect()

        logging.info("Heatmap sentiment vs temi polarizzanti creata e salvata.")