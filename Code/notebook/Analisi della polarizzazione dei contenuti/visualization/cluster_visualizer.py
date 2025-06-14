import os
import logging

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer


class ClusterVisualizer:
    def __init__(self, output_dir):
        """Imposta la cartella di output per i grafici."""
        self.output_dir = output_dir

    def visualize(self, user_opinions, cluster_labels):
        """
        Riduce i vettori TF-IDF a 2D tramite TruncatedSVD e disegna uno scatter
        con colorazione in base al cluster di appartenenza.

        - user_opinions: dict {user_id: testo_opinione}
        - cluster_labels: dict {user_id: label_cluster}
        """
        # 1. Assicuriamoci che output_dir esista
        os.makedirs(self.output_dir, exist_ok=True)

        output_path = os.path.join(self.output_dir, "clusters.png")
        if os.path.exists(output_path):
            logging.info("Il file clusters.png esiste già. Salto la visualizzazione.")
            return

        logging.info("Inizio visualizzazione dei cluster.")
        # 2. TF-IDF sui testi
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(user_opinions.values())

        # 3. Riduzione a 2 dimensioni con TruncatedSVD
        svd = TruncatedSVD(n_components=2, random_state=42)
        reduced_data = svd.fit_transform(tfidf_matrix)

        # 4. Prepariamo un DataFrame per Seaborn
        #    Convertiamo i label in stringhe per evitare problemi di tipo
        users = list(user_opinions.keys())
        labels = [str(cluster_labels[u]) for u in users]
        df = pd.DataFrame({
            "x": reduced_data[:, 0],
            "y": reduced_data[:, 1],
            "Cluster": labels
        })

        # 5. Scatter plot con palette adatta ai cluster
        plt.figure(figsize=(10, 8))
        sns.scatterplot(
            data=df,
            x="x",
            y="y",
            hue="Cluster",
            palette="tab20",  # palette con massimo 20 colori; se hai >20 cluster, sfumature verranno riciclate
            legend="full",
            alpha=0.7,
            edgecolor="w",
            linewidth=0.5
        )
        plt.title("Cluster Utenti (2D via TruncatedSVD)")
        plt.xlabel("Componente 1")
        plt.ylabel("Componente 2")
        plt.legend(title="Cluster", bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.tight_layout()

        # 6. Salvo figura
        plt.savefig(output_path, dpi=300)
        plt.close()
        logging.info(f"Visualizzazione dei cluster completata e salvata in {output_path}.")
