from sklearn.cluster import KMeans, DBSCAN
import numpy as np
from transformers import BertTokenizer, BertModel
import torch
from sklearn.cluster import MiniBatchKMeans, DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import logging
import re
import pickle
import os

class Clustering:
    def __init__(self, max_features=10000, cluster_file='../output/cluster_labels.pkl'):
        """
        Inizializza la classe con:
        - max_features: limite sul numero massimo di feature per TF-IDF.
        - cluster_file: percorso del file dove salvare i cluster.
        """
        self.max_features = max_features
        self.cluster_file = cluster_file

    def cluster(self, user_opinions, method="kmeans", n_clusters=20):
        # Se il file dei cluster esiste, carica i risultati salvati
        if os.path.exists(self.cluster_file):
            logging.info(f"Carico i cluster da {self.cluster_file}")
            with open(self.cluster_file, "rb") as f:
                cluster_labels = pickle.load(f)
            return cluster_labels
        
        logging.info(f"Clustering degli utenti utilizzando il metodo {method}.")
        texts = list(user_opinions.values())
        vectorizer = TfidfVectorizer(max_features=self.max_features)
        embeddings = vectorizer.fit_transform(texts)
        
        if method == "kmeans":
            model = MiniBatchKMeans(n_clusters=n_clusters, random_state=42)
        elif method == "dbscan":
            # Convertiamo in matrice densa e poi in array NumPy per evitare il tipo np.matrix
            embeddings = np.asarray(embeddings.todense())
            model = DBSCAN(metric="cosine")
        else:
            raise ValueError(f"Metodo {method} non supportato.")
        
        labels = model.fit_predict(embeddings)
        cluster_labels = dict(zip(user_opinions.keys(), labels))
        
        # Salva i risultati su file
        with open(self.cluster_file, "wb") as f:
            pickle.dump(cluster_labels, f)
        logging.info("Clustering completato e salvato.")
        return cluster_labels

    def identify_polarizing_themes(self, user_opinions, cluster_labels):
        logging.info("Identificazione dei temi polarizzanti.")
        texts = list(user_opinions.values())
        vectorizer = TfidfVectorizer(ngram_range=(1, 1), max_features=self.max_features)
        embeddings = vectorizer.fit_transform(texts)
        polarizing_words = []
        labels = list(cluster_labels.values())
        for cluster in set(labels):
            cluster_indices = [i for i, label in enumerate(labels) if label == cluster]
            cluster_mean = embeddings[cluster_indices].mean(axis=0).A1
            top_features_indices = np.argsort(-cluster_mean)[:10]
            polarizing_words.extend(
                [vectorizer.get_feature_names_out()[i] for i in top_features_indices]
            )
        logging.info("Identificazione dei temi polarizzanti completata.")
        return polarizing_words

    def identify_polarizing_themes_bigram(self, user_opinions, cluster_labels):
        logging.info("Identificazione dei temi polarizzanti con bigrammi.")
        texts = list(user_opinions.values())
        vectorizer = TfidfVectorizer(ngram_range=(2, 2), max_features=self.max_features)
        embeddings = vectorizer.fit_transform(texts)
        polarizing_words = []
        labels = list(cluster_labels.values())
        for cluster in set(labels):
            cluster_indices = [i for i, label in enumerate(labels) if label == cluster]
            cluster_mean = embeddings[cluster_indices].mean(axis=0).A1
            top_features_indices = np.argsort(-cluster_mean)[:10]
            polarizing_words.extend(
                [vectorizer.get_feature_names_out()[i] for i in top_features_indices]
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
