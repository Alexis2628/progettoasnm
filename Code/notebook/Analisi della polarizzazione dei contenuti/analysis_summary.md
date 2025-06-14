Analisi del Codice in: Code/notebook/Analisi della polarizzazione dei contenuti
Dettagli dall'Analisi del Codice:

Metodologie/Algoritmi Rilevati:
- Costruzione di grafi di follower e calcolo di centralità (degree, closeness, betweenness, pagerank, katz, eigenvector, HITS).
- Preprocessing testuale con rimozione URL/email, tokenizzazione e filtraggio stopword.
- Clustering di testi tramite TF–IDF + LSA + HDBSCAN/KMeans o SBERT + UMAP + clustering.
- Estrazione dei sentiment da modelli precomputati (DistilBERT, VADER, RoBERTa).
- Topic modeling con LDA (Gensim) e visualizzazione con pyLDAvis.

Librerie Python Utilizzate:
- networkx per grafi e centralità.
- nltk per preprocessing.
- scikit-learn (TfidfVectorizer, TruncatedSVD, KMeans, DBSCAN, Agglomerative, Spectral).
- hdbscan per clustering denso.
- sentence-transformers per SBERT; umap-learn per riduzione dimensionale.
- gensim per LDA; matplotlib e seaborn per grafici; wordcloud e pyLDAvis per visualizzazioni.

Concetti/Domini Principali:
- Polarizzazione dei contenuti e opinioni online.
- Analisi del sentiment e clustering tematico.
- Costruzione di grafi sociali e studio dei temi polarizzanti.

Parole chiave di ricerca suggerite per articoli scientifici:
"SBERT embeddings UMAP clustering social media polarization"
"HDBSCAN sentiment analysis political content"
"LDA topic modeling social network polarization"
"networkx centrality analysis online graphs"

Articoli scientifici individuati:
- "Analyzing Social Networks and Topic Clustering in Backpacker Tourism Content Reviews using K-means, Fast HDBScan, and Gaussian Mixture with Communalytic" (DOI: 10.47065/josh.v6i1.5969)
- "An Implementation of the HDBSCAN* Clustering Algorithm" (DOI: 10.3390/app12052405)
