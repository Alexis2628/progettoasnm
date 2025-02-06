from sklearn.cluster import KMeans, DBSCAN
import numpy as np
from transformers import BertTokenizer, BertModel
import torch
from sklearn.cluster import KMeans, DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import logging
import re


class Clustering:

    def cluster(self, user_opinions, method="kmeans", n_clusters=20):
        logging.info(f"Clustering degli utenti utilizzando il metodo {method}.")
        vectorizer = TfidfVectorizer()
        texts = list(user_opinions.values())
        embeddings = vectorizer.fit_transform(texts).toarray()
        if method == "kmeans":
            model = KMeans(n_clusters=n_clusters)
        elif method == "dbscan":
            model = DBSCAN(metric="cosine")
        labels = model.fit_predict(embeddings)
        logging.info("Clustering completato.")
        return dict(zip(user_opinions.keys(), labels))

    def identify_polarizing_themes(self, user_opinions, cluster_labels):
        logging.info("Identificazione dei temi polarizzanti.")
        vectorizer = TfidfVectorizer(ngram_range=(1, 1))
        texts = list(user_opinions.values())
        embeddings = vectorizer.fit_transform(texts).toarray()
        polarizing_words = []
        for cluster in set(cluster_labels.values()):
            cluster_indices = [
                i for i, label in enumerate(cluster_labels.values()) if label == cluster
            ]
            cluster_mean = embeddings[cluster_indices].mean(axis=0)
            top_features_indices = np.argsort(-cluster_mean)[:10]
            polarizing_words.extend(
                [vectorizer.get_feature_names_out()[i] for i in top_features_indices]
            )
        logging.info("Identificazione dei temi polarizzanti completata.")
        return polarizing_words

    def identify_polarizing_themes_bigram(self, user_opinions, cluster_labels):
        logging.info("Identificazione dei temi polarizzanti.")
        vectorizer = TfidfVectorizer(ngram_range=(2, 2))
        texts = list(user_opinions.values())
        embeddings = vectorizer.fit_transform(texts).toarray()
        polarizing_words = []
        for cluster in set(cluster_labels.values()):
            cluster_indices = [
                i for i, label in enumerate(cluster_labels.values()) if label == cluster
            ]
            cluster_mean = embeddings[cluster_indices].mean(axis=0)
            top_features_indices = np.argsort(-cluster_mean)[:10]
            polarizing_words.extend(
                vectorizer.get_feature_names_out()[i] for i in top_features_indices
            )

        unique_bigrams = set()
        filtered_polarizing_words = []
        for bigram in polarizing_words:
            words = bigram.split()
            ordered_bigram = tuple(sorted(words))
            if ordered_bigram not in unique_bigrams and len(set(words)) > 1:
                unique_bigrams.add(ordered_bigram)
                filtered_polarizing_words.append(re.sub(" ", "_", bigram))

        logging.info("Identificazione dei temi polarizzanti completata.")
        return filtered_polarizing_words


class ClusteringEmdedding:
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
        self.model = BertModel.from_pretrained("bert-base-uncased")

    def embed_texts(self, texts, batch_size=8):
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i : i + batch_size]
            inputs = self.tokenizer(
                batch_texts, return_tensors="pt", padding=True, truncation=True
            )
            with torch.no_grad():
                outputs = self.model(**inputs)
            batch_embeddings = outputs.last_hidden_state.mean(dim=1)
            embeddings.append(batch_embeddings)
        return torch.cat(embeddings, dim=0)

    def cluster(self, user_opinions, method="kmeans", n_clusters=20):
        logging.info(f"Clustering degli utenti utilizzando il metodo {method}.")
        texts = list(user_opinions.values())
        embeddings = self.embed_texts(texts)
        if method == "kmeans":
            model = KMeans(n_clusters=n_clusters)
        elif method == "dbscan":
            model = DBSCAN(metric="cosine")
        labels = model.fit_predict(embeddings)
        logging.info("Clustering completato.")
        return dict(zip(user_opinions.keys(), labels))

    def identify_polarizing_themes(self, user_opinions, cluster_labels):
        logging.info("Identificazione dei temi polarizzanti.")
        texts = list(user_opinions.values())
        embeddings = self.embed_texts(texts)
        polarizing_words = []
        for cluster in set(cluster_labels.values()):
            cluster_indices = [
                i for i, label in enumerate(cluster_labels.values()) if label == cluster
            ]
            cluster_mean = embeddings[cluster_indices].mean(axis=0)
            polarizing_words.extend(
                [self.tokenizer.decode([i]) for i in torch.argsort(-cluster_mean)[:10]]
            )
        logging.info("Identificazione dei temi polarizzanti completata.")
        return polarizing_words
