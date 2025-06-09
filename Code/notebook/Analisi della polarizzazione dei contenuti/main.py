import logging
import sys
import os
import argparse
from ast import literal_eval

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


def parse_args():
    parser = argparse.ArgumentParser(
        description="Analisi della polarizzazione dei contenuti (configurabile via CLI)."
    )

    # Output directory
    parser.add_argument(
        "--output-dir",
        type=str,
        default=r"Code/notebook/Analisi della polarizzazione dei contenuti/output",
        help="Cartella in cui salvare tutti i risultati."
    )

    # Scelta tra TF-IDF o Embeddings
    tfidf_group = parser.add_mutually_exclusive_group()
    tfidf_group.add_argument(
        "--use-tfidf",
        dest="use_tfidf",
        action="store_true",
        help="Usa ClusteringTFIDF (default)."
    )
    tfidf_group.add_argument(
        "--no-tfidf",
        dest="use_tfidf",
        action="store_false",
        help="Usa ClusteringEmbeddings."
    )
    parser.set_defaults(use_tfidf=True)

    # Parametri per ClusteringTFIDF
    parser.add_argument(
        "--max-features",
        type=int,
        default=5000,
        help="Numero massimo di feature per il vettorizzatore TF-IDF."
    )
    parser.add_argument(
        "--ngram-range",
        type=str,
        default="(1,2)",
        help="Range di n-grammi per TF-IDF, specificato come tuple, es. \"(1,2)\"."
    )
    parser.add_argument(
        "--stop-words",
        type=str,
        default="english",
        help="Lingua per stop_words del TF-IDF (es. 'english') o None."
    )
    parser.add_argument(
        "--min-df",
        type=float,
        default=0.01,
        help="min_df per il vettorizzatore TF-IDF."
    )
    parser.add_argument(
        "--max-df",
        type=float,
        default=0.8,
        help="max_df per il vettorizzatore TF-IDF."
    )
    parser.add_argument(
        "--lsa-components",
        type=int,
        default=200,
        help="Numero di componenti LSA se use_lsa=True."
    )
    parser.add_argument(
        "--use-lsa",
        action="store_true",
        help="Se specificato, abilitare LSA nel pipeline TF-IDF."
    )

    # Parametri per ClusteringEmbeddings
    parser.add_argument(
        "--embedding-model",
        type=str,
        default="all-MiniLM-L6-v2",
        help="Nome del modello SBERT da usare (solo per ClusteringEmbeddings)."
    )
    parser.add_argument(
        "--use-umap",
        action="store_true",
        help="Se specificato, ridurre dimensionalità con UMAP (solo per ClusteringEmbeddings)."
    )
    parser.add_argument(
        "--umap-components",
        type=int,
        default=50,
        help="Numero di componenti UMAP (solo per ClusteringEmbeddings)."
    )

    # Parametri comuni di clustering
    parser.add_argument(
        "--method",
        type=str,
        default="hdbscan",
        choices=["hdbscan", "kmeans"],
        help="Metodo di clustering da usare (HDBSCAN o KMeans)."
    )
    parser.add_argument(
        "--n-clusters",
        type=int,
        default=10,
        help="Numero di cluster target (usato da HDBSCAN come suggerimento o da KMeans)."
    )
    parser.add_argument(
        "--hdbscan-min-cluster-size",
        type=int,
        default=10,
        help="Minimo numero di elementi in un cluster, se si usa HDBSCAN."
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="Random seed da passare ai metodi di clustering."
    )

    # Identificazione temi polarizzanti (solo TF-IDF)
    parser.add_argument(
        "--top-n",
        type=int,
        default=15,
        help="Numero di parole chiave per tema polarizzante da estrarre (TF-IDF)."
    )
    parser.add_argument(
        "--polar-ngram-range-unigrams",
        type=str,
        default="(1,1)",
        help="ngram_range per unigrams polarizzanti, es. \"(1,1)\"."
    )
    parser.add_argument(
        "--polar-ngram-range-bigrams",
        type=str,
        default="(2,2)",
        help="ngram_range per bigrams polarizzanti, es. \"(2,2)\"."
    )
    parser.add_argument(
        "--polar-min-df",
        type=int,
        default=2,
        help="min_df per estrarre temi polarizzanti (TF-IDF)."
    )
    parser.add_argument(
        "--polar-max-df",
        type=float,
        default=0.7,
        help="max_df per estrarre temi polarizzanti (TF-IDF)."
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # Configurazione del logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    logging.info("Inizio del processo principale.")

    # Preparo la cartella di output
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    logging.info(f"Output directory: {output_dir}")

    # Costruzione del grafo
    graph_builder = GraphConstructor()
    graph_builder.build_graph()

    # Preprocessing e estrazione delle opinioni
    preprocessor = TextPreprocessor()
    user_opinions = preprocessor.extract_user_opinions(graph_builder)

    # Estrazione dei sentiment
    sentiment_scores = SentimentAnalyzer().extract_sentiments_from_graph(graph_builder)

    # Parametri combinati da argparse
    ngram_range = literal_eval(args.ngram_range)
    polar_unigram_range = literal_eval(args.polar_ngram_range_unigrams)
    polar_bigram_range = literal_eval(args.polar_ngram_range_bigrams)
    stop_words = args.stop_words if args.stop_words.lower() != "none" else None

    # Clustering
    if args.use_tfidf:
        logging.info("Utilizzo ClusteringTFIDF (TF-IDF + LSA + HDBSCAN).")

        clustering = ClusteringTFIDF(
            max_features=args.max_features,
            ngram_range=ngram_range,
            stop_words=stop_words,
            min_df=args.min_df,
            max_df=args.max_df,
            use_lsa=args.use_lsa,
            lsa_components=args.lsa_components,
            cluster_file='cluster_labels_tfidf.pkl',
            vectorizer_file= 'tfidf_vectorizer.pkl',
            output_dir=output_dir
        )
        cluster_labels = clustering.cluster(
            user_opinions=user_opinions,
            method=args.method,
            n_clusters=args.n_clusters,
            spherical=False,
            hdbscan_min_cluster_size=args.hdbscan_min_cluster_size,
            random_state=args.random_state
        )
    else:
        logging.info("Utilizzo ClusteringEmbeddings (SBERT + UMAP + Clustering).")

        clustering = ClusteringEmbeddings(
            model_name=args.embedding_model,
            use_umap=args.use_umap,
            umap_components=args.umap_components,
            embedding_file='sentence_embeddings.pkl',
            cluster_file='cluster_labels_emb.pkl',
            output_dir=output_dir
        )
        cluster_labels = clustering.cluster(
            user_opinions=user_opinions,
            method=args.method,
            n_clusters=args.n_clusters,
            random_state=args.random_state
        )

    num_cluster_detected = len(set(cluster_labels.values()))
    logging.info(f"Cluster ottenuti: {num_cluster_detected} distinti (incluso -1 per rumore, se presente).")

    # Visualizzazione dei cluster
    cluster_visualizer = ClusterVisualizer(output_dir=output_dir)
    cluster_visualizer.visualize(user_opinions, cluster_labels)

    # Visualizzazione dei sentiment per cluster
    sentiment_visualizer = SentimentVisualizer(output_dir=output_dir)
    sentiment_visualizer.visualize_sentiment_distribution(
        sentiment_scores, cluster_labels
    )
    sentiment_visualizer.visualize_sentiment_vs_themes_heatmap(
        sentiment_scores, user_opinions, cluster_labels
    )

    # Identificazione dei temi polarizzanti (solo per TF-IDF)
    if args.use_tfidf:
        logging.info("Identificazione dei temi polarizzanti (unigrams).")
        polarizing_dict = clustering.identify_polarizing_themes(
            user_opinions, cluster_labels,
            top_n=args.top_n,
            ngram_range=polar_unigram_range,
            min_df=args.polar_min_df,
            max_df=args.polar_max_df
        )
        logging.info("Identificazione dei temi polarizzanti (bigrams).")
        polarizing_bigrams_dict = clustering.identify_polarizing_themes(
            user_opinions, cluster_labels,
            top_n=args.top_n,
            ngram_range=polar_bigram_range,
            min_df=args.polar_min_df,
            max_df=args.polar_max_df
        )
    else:
        logging.info("Identificazione dei temi polarizzanti (Embeddings).")
        polarizing_dict = clustering.identify_polarizing_themes(
            user_opinions, cluster_labels,
            top_n=args.top_n
        )
        polarizing_bigrams_dict = polarizing_dict

    # Funzione di utilità per appiattire le liste di keyword
    def _flatten_keywords(polar_dict):
        all_kw = set()
        for kw_list in polar_dict.values():
            all_kw.update(kw_list)
        return list(all_kw)

    flat_unigrams = _flatten_keywords(polarizing_dict)
    flat_bigrams = _flatten_keywords(polarizing_bigrams_dict)

    # WordCloud dei temi polarizzanti
    wordcloud_visualizer = WordCloudVisualizer()
    prefix = "TFIDF" if args.use_tfidf else "EMB"
    wordcloud_visualizer.visualize(
        flat_unigrams,
        output_dir=output_dir,
        prefix=f"{prefix}_Un"
    )
    wordcloud_visualizer.visualize(
        flat_bigrams,
        output_dir=output_dir,
        prefix=f"{prefix}_Bi"
    )

    # Topic modeling con LDA: uso il numero di cluster (escludendo -1 per rumore)
    num_clusters_effective = len({label for label in cluster_labels.values() if label != -1})
    topic_modeling = TopicModeling()
    lda_model, dictionary, corpus = topic_modeling.perform_topic_modeling(
        user_opinions,
        n_topics=num_clusters_effective
    )

    # Visualizzazione LDA
    lda_visualizer = LDAViz()
    lda_visualizer.visualize(lda_model, corpus, dictionary, output_dir=output_dir)

    logging.info("Processo principale completato.")


if __name__ == "__main__":
    main()
