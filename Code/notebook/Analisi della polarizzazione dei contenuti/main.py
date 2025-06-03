import logging
import sys
import os

# Configurazione del path per importare i moduli
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from Code.notebook.graph.GraphConstructor import GraphConstructor
from preprocessing.text_preprocessor import TextPreprocessor
from visualization.cluster_visualizer import ClusterVisualizer
from models.sentiment_analysis import SentimentAnalyzer
from visualization.sentiment_visualizer import SentimentVisualizer
from visualization.wordcloud_visualizer import WordCloudVisualizer
from visualization.lda_visualizer import LDAViz
from models.clustering import ClusteringTFIDF, ClusteringEmbeddings
from models.topic_modeling import TopicModeling

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

def main():
    logging.info("Inizio del processo principale.")
    output_dir = r"Code/notebook/Analisi della polarizzazione dei contenuti/output"
    os.makedirs(output_dir, exist_ok=True)
    graph_builder = GraphConstructor()
    graph_builder.build_graph()

    preprocessor = TextPreprocessor()
    user_opinions = preprocessor.extract_user_opinions(graph_builder)

    sentiment_scores = SentimentAnalyzer().extract_sentiments_from_graph(graph_builder)

    use_tfidf = True
    if use_tfidf:
        logging.info("Utilizzo ClusteringTFIDF (TF-IDF + LSA + HDBSCAN).")
        clustering = ClusteringTFIDF(
            max_features=5000,
            ngram_range=(1,2),
            stop_words='english',
            min_df=0.01,
            max_df=0.8,
            use_lsa=True,
            lsa_components=200,
            cluster_file='cluster_labels_tfidf.pkl',
            vectorizer_file='tfidf_vectorizer.pkl',
            output_dir=output_dir
        )
        cluster_labels = clustering.cluster(
            user_opinions=user_opinions,
            method="hdbscan",
            n_clusters=10,                # solo per metodi che lo richiedono (qui ignora)
            spherical=False,               # abilita “spherical HDBSCAN”
            hdbscan_min_cluster_size=10,
            random_state=42
        )

    else:
        logging.info("Utilizzo ClusteringEmbeddings (SBERT + UMAP + K-Means).")
        clustering = ClusteringEmbeddings(
            model_name="all-MiniLM-L6-v2",
            use_umap=True,
            umap_components=50,
            embedding_file='sentence_embeddings.pkl',
            cluster_file='cluster_labels_emb.pkl',
            output_dir=output_dir
        )
        cluster_labels = clustering.cluster(
            user_opinions=user_opinions,
            method="kmeans",
            n_clusters=15,
            random_state=42
        )

    logging.info(f"Cluster ottenuti: {len(set(cluster_labels.values()))} distinti (incluso -1 per rumore, se presente).")

    cluster_visualizer = ClusterVisualizer(output_dir=output_dir)
    cluster_visualizer.visualize(user_opinions, cluster_labels)

    sentiment_visualizer = SentimentVisualizer(output_dir=output_dir)
    sentiment_visualizer.visualize_sentiment_distribution(
        sentiment_scores, cluster_labels
    )
    sentiment_visualizer.visualize_sentiment_vs_themes_heatmap(
        sentiment_scores, user_opinions, cluster_labels
    )

    if use_tfidf:
        # TF-IDF → unigrams
        polarizing_dict = clustering.identify_polarizing_themes(
            user_opinions, cluster_labels,
            top_n=15,
            ngram_range=(1,1),
            min_df=2,
            max_df=0.7
        )
        # TF-IDF → bigrams
        polarizing_bigrams_dict = clustering.identify_polarizing_themes(
            user_opinions, cluster_labels,
            top_n=15,
            ngram_range=(2,2),
            min_df=2,
            max_df=0.7
        )
    else:
        polarizing_dict = clustering.identify_polarizing_themes(
            user_opinions, cluster_labels,
            top_n=10
        )
        polarizing_bigrams_dict = polarizing_dict
    def _flatten_keywords(polar_dict):
        all_kw = set()
        for kw_list in polar_dict.values():
            all_kw.update(kw_list)
        return list(all_kw)

    flat_unigrams = _flatten_keywords(polarizing_dict)
    flat_bigrams = _flatten_keywords(polarizing_bigrams_dict)

    wordcloud_visualizer = WordCloudVisualizer()

    # Generiamo wordcloud dei temi unigrama
    wordcloud_visualizer.visualize(
        flat_unigrams,
        output_dir=output_dir,
        prefix="TFIDF_Un" if use_tfidf else "EMB_Un"
    )
    # Generiamo wordcloud dei temi bigrama
    wordcloud_visualizer.visualize(
        flat_bigrams,
        output_dir=output_dir,
        prefix="TFIDF_Bi" if use_tfidf else "EMB_Bi"
    )

    num_clusters = len({label for label in cluster_labels.values() if label != -1})
    topic_modeling = TopicModeling()
    lda_model, dictionary, corpus = topic_modeling.perform_topic_modeling(
        user_opinions,
        n_topics=num_clusters
    )

    lda_visualizer = LDAViz()
    lda_visualizer.visualize(lda_model, corpus, dictionary, output_dir=output_dir)

    logging.info("Processo principale completato.")

if __name__ == "__main__":
    main()
