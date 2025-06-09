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

    def visualize_sentiment_distribution(self,sentiment_by_user, cluster_labels):
        """
        sentiment_by_user: dict[user_id] = {"average_score": <float>, "major_label": <str>}
        cluster_labels:      dict[user_id] = <cluster_int>
        """

        # 1) Assicurati che la cartella di output esista
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

        violin_plot_path = os.path.join(self.output_dir, "sentiment_violin_plot.png")
        bar_plot_path = os.path.join(self.output_dir, "sentiment_bar_plot.png")

        logging.info("Visualizzazione della distribuzione del sentiment tra i cluster.")

        # 2) Costruisci il DataFrame estraendo solo 'average_score' come valore numerico
        #    e associandolo al cluster corrispondente.
        data = pd.DataFrame({
            "User": list(sentiment_by_user.keys()),
            "Sentiment": [sentiment_by_user[user]["average_score"] for user in sentiment_by_user.keys()],
            "Cluster": [cluster_labels.get(user, None) for user in sentiment_by_user.keys()],
        })

        # 3) Trasforma 'Cluster' in stringa (utile per Seaborn)
        data["Cluster"] = data["Cluster"].astype(str)

        # 4) 'Sentiment' è già float, quindi non serve to_numeric. Verifica comunque che non ci siano NaN
        data = data.dropna(subset=["Sentiment"])

        if data.empty:
            logging.warning("Il DataFrame risultante è vuoto. Nessun grafico verrà generato.")
            return

        # 5) Grafico a violino
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
            plt.tight_layout()
            plt.savefig(violin_plot_path)
            plt.close()
            gc.collect()
            print(f"Violin plot salvato in: {violin_plot_path} (dimensione: {os.path.getsize(violin_plot_path)} bytes)")

        # 6) Grafico a barre (media per cluster)
        if not os.path.exists(bar_plot_path):
            plt.figure(figsize=(12, 6))
            sns.barplot(
                x="Cluster",
                y="Sentiment",
                data=data,
                estimator=np.mean,
                errorbar=None,
                hue="Cluster",
                palette="viridis",
                legend=False,
            )
            plt.title("Sentiment medio per cluster (Barre)")
            plt.xlabel("Cluster")
            plt.ylabel("Sentiment medio")
            plt.tight_layout()
            plt.savefig(bar_plot_path)
            plt.close()
            gc.collect()
            print(f"Bar plot salvato in: {bar_plot_path} (dimensione: {os.path.getsize(bar_plot_path)} bytes)")

        logging.info("Visualizzazione della distribuzione del sentiment completata.")
    def visualize_sentiment_vs_themes_heatmap(
        self,sentiment_scores, user_opinions, cluster_labels
    ):
        """
        Crea una heatmap che mostra la correlazione tra il sentiment medio di ciascun utente
        e i termini più rilevanti (tf-idf) nei suoi testi.

        Parametri:
        - sentiment_scores:  dict[user_id] = {"average_score": <float>, "major_label": <str>}
        - user_opinions:     dict[user_id] = "<testo dell'opinione>"
        - cluster_labels:    dict[user_id] = <int>  (non usato attivamente in questa funzione,
                            ma lasciato come parametro per eventuali future estensioni)
        - output_dir:        path della cartella in cui salvare "sentiment_themes_heatmap.png"

        Se il file esiste già, non ricrea la heatmap.
        """

        heatmap_path = os.path.join(self.output_dir, "sentiment_themes_heatmap.png")

        if os.path.exists(heatmap_path):
            logging.info(
                "La heatmap sentiment vs temi polarizzanti esiste già. Salto la generazione."
            )
            return

        logging.info("Creazione della heatmap tra sentiment e temi polarizzanti.")

        # Assicuro che output_dir esista
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

        # (1) Costruisco il DataFrame estraendo solo 'average_score' dai dict in sentiment_scores
        df = pd.DataFrame({
            "User": list(user_opinions.keys()),
            "Text": list(user_opinions.values()),
            "Sentiment": [
                # Se l'utente è presente in sentiment_scores e c'è 'average_score', lo prendo; altrimenti None
                sentiment_scores[u]["average_score"]
                if (u in sentiment_scores and 
                    isinstance(sentiment_scores[u], dict) and 
                    "average_score" in sentiment_scores[u])
                else None
                for u in user_opinions.keys()
            ],
            "Cluster": [
                # Anche se non lo usiamo direttamente per la heatmap, lo includo per eventuali debug
                cluster_labels.get(u, None)
                for u in user_opinions.keys()
            ]
        })

        # (2) Elimino eventuali righe con Sentiment = NaN
        df_valid = df.dropna(subset=["Sentiment"])
        if df_valid.empty:
            logging.warning(
                "Nessun valore di sentiment valido dopo l'estrazione di 'average_score'. "
                "Non posso creare la heatmap."
            )
            return

        # (3) Calcolo la matrice TF-IDF sui testi rimasti
        vectorizer = TfidfVectorizer(max_features=1000)
        tfidf_matrix = vectorizer.fit_transform(df_valid["Text"])
        feature_names = vectorizer.get_feature_names_out()

        # (4) Estraggo l'array dei valori di sentiment
        sentiment_array = df_valid["Sentiment"].to_numpy()

        # (5) Calcolo la correlazione tra ciascun termine tf-idf e i sentiment
        correlations = []
        for i in range(tfidf_matrix.shape[1]):
            term_vector = tfidf_matrix[:, i].toarray().flatten()
            # Se il termine non compare in nessun documento, fissiamo a 0
            if np.all(term_vector == 0):
                correlations.append(0.0)
            else:
                corr = np.corrcoef(sentiment_array, term_vector)[0, 1]
                correlations.append(0.0 if np.isnan(corr) else corr)

        correlations = np.array(correlations)

        # (6) Trovo i 20 termini con correlazione più alta in valore assoluto
        top_indices = np.argsort(np.abs(correlations))[-20:]
        top_words = [feature_names[i] for i in top_indices]
        top_corrs = correlations[top_indices]

        # Ordino i termini dal più negativo al più positivo per una heatmap leggibile
        order = np.argsort(top_corrs)
        heatmap_words = [top_words[i] for i in order]
        heatmap_corrs = top_corrs[order]

        # (7) Preparo il DataFrame per la heatmap
        heatmap_data = pd.DataFrame({
            "Terms": heatmap_words,
            "Correlation": heatmap_corrs
        }).set_index("Terms")

        # (8) Disegno e salvo la heatmap
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
        plt.xlabel("Correlazione")
        plt.ylabel("Termini")
        plt.tight_layout()
        plt.savefig(heatmap_path, bbox_inches="tight")
        plt.close()
        gc.collect()

        logging.info("Heatmap sentiment vs temi polarizzanti creata e salvata.")