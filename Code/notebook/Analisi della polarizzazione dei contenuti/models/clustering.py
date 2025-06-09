import os
import pickle
import logging
from typing import Dict, List, Any, Optional
import numpy as np
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering, SpectralClustering,MiniBatchKMeans
from sklearn.preprocessing import normalize
from sentence_transformers import SentenceTransformer
import hdbscan
import umap
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

class ClusteringTFIDF:
    """
    Classe per effettuare clustering su testi utilizzando TF-IDF, con varie opzioni configurabili:
    - Supporto a riduzione di dimensionalità (LSA)
    - Algoritmi di clustering: k-means, spherical k-means, DBSCAN, HDBSCAN, Spectral, Agglomerative
    - Parametri di TfidfVectorizer personalizzabili
    - Estrazione di parole chiave polarizzanti
    """

    def __init__(
        self,
        max_features: int = 10000,
        ngram_range: tuple = (1, 1),
        stop_words: Optional[str] = 'english',
        min_df: float = 0.0,
        max_df: float = 1.0,
        use_lsa: bool = False,
        lsa_components: int = 100,
        cluster_file: str = 'cluster_labels_tfidf.pkl',
        vectorizer_file: str = 'tfidf_vectorizer.pkl',
        lsa_file: str = 'lsa_model.pkl',
        output_dir: str = ""
    ):
        """
        Parametri:
        - max_features: numero massimo di feature per TF-IDF
        - ngram_range: range degli n-grammi (min_n, max_n)
        - stop_words: stop words ('english', lista personalizzata o None)
        - min_df, max_df: soglie per TF-IDF (valori assoluti o frazioni)
        - use_lsa: se True, applica LSA prima del clustering
        - lsa_components: numero di componenti per la decomposizione SVD
        - cluster_file: percorso per salvare/ripristinare i label dei cluster
        - vectorizer_file: percorso per salvare/ripristinare il vettorizzatore TF-IDF
        - lsa_file: percorso per salvare/ripristinare il modello SVD (solo se use_lsa=True)
        - output_dir: directory di output in cui salvare i file
        """
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.stop_words = stop_words
        self.min_df = min_df
        self.max_df = max_df
        self.use_lsa = use_lsa
        self.lsa_components = lsa_components

        # Percorsi completi per i file di pickle
        self.cluster_file = os.path.join(output_dir, cluster_file)
        self.vectorizer_file = os.path.join(output_dir, vectorizer_file)
        self.lsa_file = os.path.join(output_dir, lsa_file)

        # Variabili interne
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.svd_model: Optional[TruncatedSVD] = None

    def _fit_vectorizer(self, texts: List[str]) -> np.ndarray:
        """
        Inizializza e adatta il TfidfVectorizer sui testi.
        Se use_lsa=True, salva anche il modello SVD per riduzione.
        """
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=self.ngram_range,
            stop_words=self.stop_words,
            min_df=self.min_df,
            max_df=self.max_df
        )
        X = self.vectorizer.fit_transform(texts)
        # Salvo il vettorizzatore per usi futuri
        with open(self.vectorizer_file, 'wb') as f_vec:
            pickle.dump(self.vectorizer, f_vec)
        logging.info(f"TF-IDF Vectorizer salvato in {self.vectorizer_file}")

        if self.use_lsa:
            # Applico LSA (TruncatedSVD) per riduzione di dimensionalità
            self.svd_model = TruncatedSVD(n_components=self.lsa_components, random_state=42)
            X_reduced = self.svd_model.fit_transform(X)
            # Salvo il modello SVD su file
            with open(self.lsa_file, 'wb') as f_svd:
                pickle.dump(self.svd_model, f_svd)
            logging.info(f"Modello LSA salvato in {self.lsa_file} con {self.lsa_components} componenti")
            return X_reduced

        return X

    def _load_vectorizer_if_exists(self) -> Optional[np.ndarray]:
        """
        Se il file del vettorizzatore esiste, lo carica.  
        Se use_lsa=True ed esiste anche il file LSA, carica anche quello.

        Ritorna True se va tutto bene (vettorizzatore caricato), False altrimenti.
        """
        if not os.path.exists(self.vectorizer_file):
            return False

        # Carico TF-IDF
        with open(self.vectorizer_file, 'rb') as f_vec:
            self.vectorizer = pickle.load(f_vec)
        logging.info(f"Vectorizer TF-IDF caricato da {self.vectorizer_file}")

        # Se sto usando LSA, provo a caricare il modello SVD
        if self.use_lsa:
            if os.path.exists(self.lsa_file):
                with open(self.lsa_file, 'rb') as f_svd:
                    self.svd_model = pickle.load(f_svd)
                logging.info(f"Modello LSA caricato da {self.lsa_file}")
            else:
                # LSA non ancora calcolato, devo ricomporlo da zero
                logging.warning(
                    f"use_lsa=True ma {self.lsa_file} non esiste. "
                    "Ricalcolerò SVD da zero pigliando i dati grezzi."
                )
                return False

        return True

    def _transform_texts(self, texts: List[str]) -> np.ndarray:
        """
        Applica il vettorizzatore caricato sui testi e, se richiesto, LSA.
        """
        X = self.vectorizer.transform(texts)
        if self.use_lsa:
            # A questo punto, self.svd_model NON può più essere None perché _load_vectorizer_if_exists
            # lo avrebbe caricato. Se fosse None, significa che dobbiamo ricrearlo ex novo.
            X = self.svd_model.transform(X)
        return X

    def cluster(
        self,
        user_opinions: Dict[Any, str],
        method: str = "kmeans",
        n_clusters: int = 20,
        spherical: bool = False,
        dbscan_eps: float = 0.5,
        dbscan_min_samples: int = 5,
        hdbscan_min_cluster_size: int = 5,
        spectral_affinity: str = 'nearest_neighbors',
        agglo_linkage: str = 'ward',
        random_state: int = 42
    ) -> Dict[Any, int]:
        """
        Esegue il clustering sugli argomenti dati.

        Argomenti:
        - user_opinions: dizionario {id_utente: testo_opinione}
        - method: "kmeans", "dbscan", "hdbscan", "spectral", "agglomerative"
        - n_clusters: numero di cluster (per metodi che lo richiedono)
        - spherical: se True, normalizza i vettori L2 (utile per k-means su cosine)
        - dbscan_eps, dbscan_min_samples: parametri per DBSCAN
        - hdbscan_min_cluster_size: parametro per HDBSCAN
        - spectral_affinity: tipo di matrice di affinità per SpectralClustering
        - agglo_linkage: criterio di linkage per AgglomerativeClustering
        - random_state: seme per riproducibilità
        """
        # Se esistono già i cluster salvati, li carico
        if os.path.exists(self.cluster_file):
            logging.info(f"Carico i cluster esistenti da {self.cluster_file}")
            with open(self.cluster_file, 'rb') as f_cl:
                return pickle.load(f_cl)

        logging.info(f"Avvio clustering con metodo: {method}")
        keys = list(user_opinions.keys())
        texts = list(user_opinions.values())

        # (1) Vettorizzazione / eventuale LSA
        # Se both vectorizer e (se use_lsa=True) SVD esistono, li carico; altrimenti li ricreo
        if not self._load_vectorizer_if_exists():
            X = self._fit_vectorizer(texts)
        else:
            X = self._transform_texts(texts)

        # (2) Normalizzazione L2 se spherical=True (corrisponde a “spherical K-Means”, Dhillon & Modha, 2001)
        if spherical:
            from sklearn.preprocessing import normalize
            X = normalize(X, norm='l2')
            logging.info("Dati normalizzati L2 per spherical k-means (Dhillon & Modha, 2001)")

        # (3) Scelta e addestramento del modello di clustering
        if method == "kmeans":
            model = MiniBatchKMeans(n_clusters=n_clusters, random_state=random_state)
        elif method == "dbscan":
            model = DBSCAN(eps=dbscan_eps, min_samples=dbscan_min_samples, metric='cosine' if spherical else 'euclidean')
        elif method == "hdbscan":
            # Se stiamo usando spherical=True, i vettori sono già normalizzati, 
            # quindi possiamo continuare a usare 'euclidean' senza perdita di coseno-proporzionalità.
            metric_hdb = 'euclidean'
            model = hdbscan.HDBSCAN(min_cluster_size=hdbscan_min_cluster_size, metric=metric_hdb)
        elif method == "spectral":
            model = SpectralClustering(
                n_clusters=n_clusters,
                affinity=spectral_affinity,
                assign_labels='kmeans',
                random_state=random_state
            )
        elif method == "agglomerative":
            model = AgglomerativeClustering(
                n_clusters=n_clusters,
                affinity='cosine' if spherical else 'euclidean',
                linkage=agglo_linkage
            )
        else:
            raise ValueError(f"Metodo {method} non riconosciuto. Scegli tra kmeans, dbscan, hdbscan, spectral, agglomerative.")

        # (4) Fit e predizione delle etichette
        labels = model.fit_predict(X)
        cluster_labels = dict(zip(keys, labels))

        # (5) Salvo risultati su file
        with open(self.cluster_file, 'wb') as f_cl:
            pickle.dump(cluster_labels, f_cl)
        logging.info(f"Cluster salvati in {self.cluster_file}")

        return cluster_labels

    def identify_polarizing_themes(
        self,
        user_opinions: Dict[Any, str],
        cluster_labels: Dict[Any, int],
        top_n: int = 10,
        ngram_range: tuple = (1, 1),
        min_df: float = 0.0,
        max_df: float = 1.0
    ) -> Dict[int, List[str]]:
        """
        Estrae parole chiave (uni- o bi-grammi) maggiormente rappresentative di ciascun cluster,
        basandosi su TF-IDF calcolato SOLO sui testi di ogni cluster.

        Parametri:
        - user_opinions:     dict[id_utente] = "testo"
        - cluster_labels:    dict[id_utente] = cluster_id
        - top_n:             numero di parole chiave per cluster
        - ngram_range:       (min_n, max_n) per TF-IDF
        - min_df, max_df:    parametri per TfidfVectorizer
        """
        logging.info("Identificazione dei temi polarizzanti per cluster.")

        # Ricompongo i testi di ciascun cluster
        clusters: Dict[int, List[str]] = {}
        for uid, label in cluster_labels.items():
            clusters.setdefault(label, []).append(user_opinions[uid])

        polarizing: Dict[int, List[str]] = {}

        for cluster_id, texts in clusters.items():
            # Se è cluster di rumore (-1), skip
            if cluster_id == -1:
                continue

            # Se il cluster ha meno documenti di min_df (ad es. 1 documento e min_df=2),
            # non è possibile calcolare TF-IDF: skip
            if len(texts) < (min_df if isinstance(min_df, int) else 1):
                logging.warning(
                    f"[Cluster {cluster_id}] Dimensione del cluster ({len(texts)}) "
                    f"< min_df ({min_df}). Skipping."
                )
                continue

            # Configuro il vettorizzatore per questo cluster
            vect = TfidfVectorizer(
                max_features=self.max_features,
                ngram_range=ngram_range,
                stop_words=self.stop_words,
                min_df=min_df,
                max_df=max_df
            )
            try:
                Xc = vect.fit_transform(texts)
            except ValueError as e:
                # Questo errore capita quando, dopo aver applicato min_df/max_df,
                # non resta alcuna feature: skip pure questo cluster.
                logging.warning(
                    f"[Cluster {cluster_id}] Errore TfidfVectorizer: {e}. "
                    "Skippo questo cluster."
                )
                continue

            # Calcolo la media TF-IDF per ogni termine all’interno del cluster
            mean_tfidf = np.asarray(Xc.mean(axis=0)).ravel()
            top_indices = np.argsort(-mean_tfidf)[:top_n]
            keywords = [vect.get_feature_names_out()[i] for i in top_indices]

            polarizing[cluster_id] = keywords
            logging.debug(f"Cluster {cluster_id}: {keywords}")

        logging.info("Temi polarizzanti estratti.")
        return polarizing

class ClusteringEmbeddings:
    """
    Classe per clustering basato su embedding di frasi (SBERT), con:
    - Scelta di vari modelli (es. 'all-MiniLM-L6-v2', 'paraphrase-MPNet-base-v2', ecc.)
    - Opzione per riduzione di dimensionalità via UMAP (McInnes et al., 2018)
    - Supporto a K-Means, spherical K-Means, DBSCAN, HDBSCAN, Agglomerative, Spectral
    - Estrazione di temi polarizzanti tramite identificazione di parole chiave attorno ai centri di cluster
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        use_umap: bool = False,
        umap_components: int = 50,
        umap_metric: str = 'cosine',
        embedding_file: str = 'sentence_embeddings.pkl',
        cluster_file: str = 'cluster_labels_emb.pkl',
        output_dir: str = ""
    ):
        """
        Parametri:
        - model_name: nome del modello SBERT da Sentence-Transformers (Reimers & Gurevych, 2019)
        - use_umap: se True, riduce dimensionalità degli embedding via UMAP
        - umap_components: numero di dimensioni target per UMAP (McInnes et al., 2018)
        - umap_metric: metrica per UMAP ('cosine', 'euclidean', ecc.)
        - embedding_file: percorso per salvare/ripristinare gli embeddings calcolati
        - cluster_file: percorso per salvare/ripristinare i label dei cluster
        - output_dir: directory di output per i file
        """
        self.model_name = model_name
        self.use_umap = use_umap
        self.umap_components = umap_components
        self.umap_metric = umap_metric

        self.embedding_file = os.path.join(output_dir, embedding_file)
        self.cluster_file = os.path.join(output_dir, cluster_file)

        # Carica il modello SBERT
        logging.info(f"Caricamento modello SBERT: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.umap_model: Optional[umap.UMAP] = None

    def _compute_embeddings(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Calcola o carica da file gli embedding delle frasi tramite SBERT.
        """
        if os.path.exists(self.embedding_file):
            logging.info(f"Carico embeddings da {self.embedding_file}")
            with open(self.embedding_file, 'rb') as f:
                return pickle.load(f)

        logging.info("Calcolo nuovi embeddings SBERT.")
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True  # normalizza L2 per spherical K-Means
        )

        # Salvo embeddings su file
        with open(self.embedding_file, 'wb') as f:
            pickle.dump(embeddings, f)
        logging.info(f"Embeddings salvati in {self.embedding_file}")
        return embeddings

    def _reduce_dimensionality(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Se richiesto, applica UMAP per ridurre dimensionalità.
        """
        if not self.use_umap:
            return embeddings

        if self.umap_model is None:
            logging.info(f"Applico UMAP: dim originali {embeddings.shape[1]}, ridotte a {self.umap_components}")
            self.umap_model = umap.UMAP(
                n_components=self.umap_components,
                metric=self.umap_metric,
                random_state=42
            )
            reduced = self.umap_model.fit_transform(embeddings)
        else:
            reduced = self.umap_model.transform(embeddings)
        return reduced

    def cluster(
        self,
        user_opinions: Dict[Any, str],
        method: str = "kmeans",
        n_clusters: int = 20,
        dbscan_eps: float = 0.5,
        dbscan_min_samples: int = 5,
        hdbscan_min_cluster_size: int = 5,
        spectral_affinity: str = 'nearest_neighbors',
        agglo_linkage: str = 'average',
        random_state: int = 42
    ) -> Dict[Any, int]:
        """
        Esegue il clustering sugli embedding calcolati via SBERT.

        Argomenti:
        - user_opinions: dizionario {id_utente: testo_opinione}
        - method: "kmeans", "dbscan", "hdbscan", "spectral", "agglomerative"
        - n_clusters: numero di cluster (per metodi che lo richiedono)
        - dbscan_eps, dbscan_min_samples: parametri per DBSCAN
        - hdbscan_min_cluster_size: parametro per HDBSCAN
        - spectral_affinity: tipo di matrice di affinità per SpectralClustering
        - agglo_linkage: criterio di linkage per AgglomerativeClustering (Rosenberg & Hirschberg, 2007)
        - random_state: seme per riproducibilità
        """
        # Se cluster già salvati, li carico
        if os.path.exists(self.cluster_file):
            logging.info(f"Carico cluster esistenti da {self.cluster_file}")
            with open(self.cluster_file, 'rb') as f:
                return pickle.load(f)

        logging.info(f"Avvio clustering embedding con metodo: {method}")
        keys = list(user_opinions.keys())
        texts = list(user_opinions.values())

        # (1) Calcolo embedding (o li carico da file)
        embeddings = self._compute_embeddings(texts)

        # (2) Eventuale riduzione di dimensionalità
        X = self._reduce_dimensionality(embeddings)

        # (3) Scelta modello di clustering
        if method == "kmeans":
            model = KMeans(n_clusters=n_clusters, random_state=random_state)
        elif method == "dbscan":
            model = DBSCAN(eps=dbscan_eps, min_samples=dbscan_min_samples, metric='cosine')
        elif method == "hdbscan":
            model = hdbscan.HDBSCAN(min_cluster_size=hdbscan_min_cluster_size, metric='euclidean')
        elif method == "spectral":
            model = SpectralClustering(
                n_clusters=n_clusters,
                affinity=spectral_affinity,
                assign_labels='kmeans',
                random_state=random_state
            )
        elif method == "agglomerative":
            model = AgglomerativeClustering(
                n_clusters=n_clusters,
                affinity='cosine',
                linkage=agglo_linkage
            )
        else:
            raise ValueError(f"Metodo {method} non riconosciuto. Scegli tra kmeans, dbscan, hdbscan, spectral, agglomerative.")

        labels = model.fit_predict(X)
        cluster_labels = dict(zip(keys, labels))

        # (4) Salvo risultati
        with open(self.cluster_file, 'wb') as f:
            pickle.dump(cluster_labels, f)
        logging.info(f"Cluster embeddings salvati in {self.cluster_file}")

        return cluster_labels

    def identify_polarizing_themes(
        self,
        user_opinions: Dict[Any, str],
        cluster_labels: Dict[Any, int],
        top_n: int = 10
    ) -> Dict[int, List[str]]:
        """
        Estrae parole chiave polarizzanti per ciascun cluster basandosi sui testi
        più vicini al centroide (o medoid) del cluster e poi calcolando TF-IDF su quei testi.

        Ritorna un dizionario {cluster_id: [keyword1, keyword2, ...]}.
        """
        logging.info("Identificazione temi polarizzanti da embedding.")

        # (1) Organizzo i testi per cluster
        clusters: Dict[int, List[str]] = {}
        for uid, label in cluster_labels.items():
            clusters.setdefault(label, []).append(user_opinions[uid])

        polarizing: Dict[int, List[str]] = {}
        for cluster_id, texts in clusters.items():
            if cluster_id == -1 or len(texts) < 2:
                continue
            
            texts = [t for t in texts if t.strip()]
            if not texts:
                logging.warning(f"Cluster {cluster_id}: nessun testo valido dopo il filtro, skip.")
                continue
        
            max_feats = None
            if self.use_umap:
                max_feats = self.umap_components or None
            else:
                max_feats = getattr(self.model, 'get_sentence_embedding_dimension', lambda: None)()
                
            from sklearn.feature_extraction.text import TfidfVectorizer
            vect = TfidfVectorizer(
                max_features=max_feats,
                ngram_range=(1, 2),
                stop_words='english',
                min_df=1,
                max_df=0.9
            )
            try:
                Xc = vect.fit_transform(texts)
            except ValueError as ve:
                logging.error(f"Cluster {cluster_id}: impossibile vettorizzare testi: {ve}")
                continue
            mean_tfidf = np.asarray(Xc.mean(axis=0)).ravel()
            top_indices = np.argsort(-mean_tfidf)[:top_n]
            keywords = [vect.get_feature_names_out()[i] for i in top_indices]
            polarizing[cluster_id] = keywords
            logging.debug(f"[Embedding] Cluster {cluster_id}: {keywords}")

        logging.info("Temi polarizzanti (embedding) estratti.")
        return polarizing
