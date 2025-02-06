import matplotlib.pyplot as plt
from sklearn.decomposition import TruncatedSVD
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

class ClusterVisualizer:
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def visualize(self, user_opinions, cluster_labels):
        logging.info("Inizio visualizzazione dei cluster.")
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(user_opinions.values())
        svd = TruncatedSVD(n_components=2)
        reduced_data = svd.fit_transform(tfidf_matrix)

        plt.figure(figsize=(10, 8))
        sns.scatterplot(x=reduced_data[:, 0], y=reduced_data[:, 1], hue=list(cluster_labels.values()))
        plt.title("Cluster Utenti")
        plt.savefig(f"{self.output_dir}/clusters.png")
        plt.close()
        logging.info("Visualizzazione dei cluster completata.")
