import logging
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from Code.notebook.graph.GraphConstructor import GraphConstructor
from preprocessing.text_preprocessor import TextPreprocessor
from models.clustering import Clustering
from visualization.cluster_visualizer import ClusterVisualizer
from models.sentiment_analysis import SentimentAnalyzer
from visualization.sentiment_visualizer import SentimentVisualizer
from visualization.wordcloud_visualizer import WordCloudVisualizer
from visualization.lda_visualizer import LDAViz
from models.topic_modeling import TopicModeling


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


def main():
    logging.info("Inizio del processo principale.")
    output_dir = r"Code//notebook//Analisi della polarizzazione dei contenuti//output"
    # Costruzione del grafo
    graph_builder = GraphConstructor(followers_path="dataset/dataset_cleaned.json")
    graph_builder.build_graph()
    graph = graph_builder.graph

    # Estrazione e pre-elaborazione dei testi
    preprocessor = TextPreprocessor()
    user_opinions = preprocessor.extract_user_opinions(graph)

    # Estrazione dei sentiment dal grafo
    sentiment_scores = SentimentAnalyzer().extract_sentiments_from_graph(graph)

    # Clustering
    clustering = Clustering()
    cluster_labels = clustering.cluster(user_opinions, method="dbscan")

    # Visualizzazione dei cluster
    cluster_visualizer = ClusterVisualizer(output_dir=output_dir)
    cluster_visualizer.visualize(user_opinions, cluster_labels)

    # Visualizzazione del sentiment
    sentiment_visualizer = SentimentVisualizer(output_dir=output_dir)

    # Visualizza la distribuzione del sentiment
    sentiment_visualizer.visualize_sentiment_distribution(
        sentiment_scores, cluster_labels
    )

    # Visualizza la mappa di calore sentiment vs temi
    sentiment_visualizer.visualize_sentiment_vs_themes_heatmap(
        sentiment_scores, user_opinions, cluster_labels
    )

    # Identificazione e visualizzazione temi polarizzanti

    # UnGram
    polarizing_words = clustering.identify_polarizing_themes(
        user_opinions, cluster_labels
    )
    wordcloud_visualizer = WordCloudVisualizer()
    wordcloud_visualizer.visualize(polarizing_words, output_dir, "Un")

    # BiGram
    polarizing_words = clustering.identify_polarizing_themes_bigram(
        user_opinions, cluster_labels
    )
    wordcloud_visualizer.visualize(polarizing_words, output_dir, "Bi")

    # Topic Modeling

    topic_modeling = TopicModeling()
    lda_model, dictionary, corpus = topic_modeling.perform_topic_modeling(
        user_opinions, len(set(cluster_labels.values()))
    )

    # Visualizzazione dei temi
    lda_visualizer = LDAViz()
    lda_visualizer.visualize(lda_model, corpus, dictionary, output_dir=output_dir)

    logging.info("Processo principale completato.")


if __name__ == "__main__":
    main()
