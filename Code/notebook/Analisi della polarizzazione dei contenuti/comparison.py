# -*- coding: utf-8 -*-
"""Utility per confrontare diverse run di analisi della polarizzazione.

Per ciascuna cartella di output vengono calcolate varie metriche di coesione
geometrica, coerenza tematica e polarizzazione emotiva.
"""
from __future__ import annotations

import os
import sys
import pickle
from typing import Dict, List

import numpy as np
import pandas as pd
from gensim.corpora import Dictionary
from gensim.models import CoherenceModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score,
)
from scipy.spatial.distance import jensenshannon

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from models.sentiment_analysis import SentimentAnalyzer
from Code.notebook.graph.GraphConstructor import GraphConstructor


class RunComparator:
    """Confronta più run salvate in cartelle differenti."""

    def __init__(self, runs: Dict[str, str], out_dir: str) -> None:
        self.runs = runs
        self.out_dir = out_dir
        os.makedirs(self.out_dir, exist_ok=True)

        gc = GraphConstructor()
        gc.build_graph()
        df = gc.data
        self.user_opinions = (
            df.groupby("thread_user_pk")["text_clean"]
            .apply(lambda s: "\n\n".join(s.dropna().astype(str)))
            .to_dict()
        )
        self.sentiments = SentimentAnalyzer().extract_sentiments_from_graph(gc)
        self.users = list(self.user_opinions.keys())

    def _load_features(self, run_path: str) -> np.ndarray:
        """Recupera la matrice di feature dalla cartella della run."""
        emb_file = os.path.join(run_path, "sentence_embeddings.pkl")
        if os.path.exists(emb_file):
            with open(emb_file, "rb") as f:
                emb = pickle.load(f)
            return emb

        vect_file = os.path.join(run_path, "tfidf_vectorizer.pkl")
        with open(vect_file, "rb") as f:
            vect: TfidfVectorizer = pickle.load(f)
        X = vect.transform(list(self.user_opinions.values()))

        lsa_file = os.path.join(run_path, "lsa_model.pkl")
        if os.path.exists(lsa_file):
            with open(lsa_file, "rb") as f:
                svd = pickle.load(f)
            X = svd.transform(X)
        return X.toarray() if hasattr(X, "toarray") else X

    def _get_labels(self, run_path: str) -> List[int]:
        for name in ("cluster_labels_tfidf.pkl", "cluster_labels_emb.pkl"):
            path = os.path.join(run_path, name)
            if os.path.exists(path):
                with open(path, "rb") as f:
                    labels_dict = pickle.load(f)
                return [labels_dict[u] for u in self.users]
        raise FileNotFoundError("File label non trovato in " + run_path)

    def _topic_coherence(self, texts: List[str], labels: List[int]) -> float:
        docs = [t.split() for t in texts]
        dictionary = Dictionary(docs)
        topics = []
        for c in sorted(set(labels)):
            if c == -1:
                continue
            idx = [i for i, l in enumerate(labels) if l == c]
            if not idx:
                continue
            subset = [docs[i] for i in idx]
            freq = Dictionary(subset)
            bow = [freq.doc2bow(d) for d in subset]
            tfidf = TfidfVectorizer(stop_words="english")
            X = tfidf.fit_transform([" ".join(d) for d in subset])
            mean = np.asarray(X.mean(axis=0)).ravel()
            top = np.argsort(-mean)[:10]
            topic = [tfidf.get_feature_names_out()[t] for t in top]
            topics.append(topic)
        if not topics:
            return float("nan")
        cm = CoherenceModel(topics=topics, texts=docs, dictionary=dictionary, coherence="c_v")
        return float(cm.get_coherence())

    def _sentiment_metrics(self, labels: List[int]) -> (float, float):
        scores = np.array([self.sentiments[u]["average_score"] for u in self.users])
        overall_mean = scores.mean()
        ss_total = np.sum((scores - overall_mean) ** 2)
        ss_between = 0.0
        for c in set(labels):
            idx = [i for i, l in enumerate(labels) if l == c]
            if not idx:
                continue
            mean_c = scores[idx].mean()
            ss_between += len(idx) * (mean_c - overall_mean) ** 2
        eta2 = ss_between / ss_total if ss_total > 0 else float("nan")
        # Jensen–Shannon tra i due cluster maggiori
        clusters = [(c, labels.count(c)) for c in set(labels) if c != -1]
        clusters.sort(key=lambda x: x[1], reverse=True)
        if len(clusters) >= 2:
            c1, c2 = clusters[0][0], clusters[1][0]
            s1 = scores[[i for i, l in enumerate(labels) if l == c1]]
            s2 = scores[[i for i, l in enumerate(labels) if l == c2]]
            bins = np.linspace(scores.min(), scores.max(), 20)
            p, _ = np.histogram(s1, bins=bins, density=True)
            q, _ = np.histogram(s2, bins=bins, density=True)
            p += 1e-12
            q += 1e-12
            p /= p.sum()
            q /= q.sum()
            js = jensenshannon(p, q, base=2.0) ** 2
        else:
            js = float("nan")
        return eta2, js

    def compute_metrics(self) -> pd.DataFrame:
        records = []
        texts = list(self.user_opinions.values())
        for name, path in self.runs.items():
            labels = self._get_labels(path)
            features = self._load_features(path)
            if len(set(labels)) < 2:
                sil = db = ch = float("nan")
            else:
                sil = silhouette_score(features, labels)
                db = davies_bouldin_score(features, labels)
                ch = calinski_harabasz_score(features, labels)
            cv = self._topic_coherence(texts, labels)
            eta2, js = self._sentiment_metrics(labels)
            records.append({
                "run": name,
                "silhouette": sil,
                "davies_bouldin": db,
                "calinski_harabasz": ch,
                "coherence_cv": cv,
                "eta_squared": eta2,
                "js_divergence": js,
            })
        df = pd.DataFrame(records)
        df.to_csv(os.path.join(self.out_dir, "comparison_metrics.csv"), index=False)
        return df


def main():
    runs = {
        "run1": os.path.join(os.path.dirname(__file__), "output", "1"),
        "run2": os.path.join(os.path.dirname(__file__), "output", "2"),
        "run3": os.path.join(os.path.dirname(__file__), "output", "3"),
        "run4": os.path.join(os.path.dirname(__file__), "output", "4"),
        "run5": os.path.join(os.path.dirname(__file__), "output", "5"),
    }
    comparator = RunComparator(runs, os.path.join(os.path.dirname(__file__), "output"))
    df = comparator.compute_metrics()
    print(df)


if __name__ == "__main__":
    main()
