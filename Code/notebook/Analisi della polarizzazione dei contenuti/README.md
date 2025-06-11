# Analisi della Polarizzazione dei Contenuti

Questo repository contiene uno script principale (`main.py`) per:

1. Costruire un grafo di opinioni tramite `GraphConstructor`.
2. Estrarre e preprocessare testi (opinioni) tramite `TextPreprocessor`.
3. Calcolare punteggi di sentiment tramite `SentimentAnalyzer`.
4. Applicare tecniche di clustering (TF–IDF + LSA + HDBSCAN oppure SBERT + UMAP + clustering).
5. Generare visualizzazioni:
   - Cluster (`ClusterVisualizer`)
   - Distribuzione dei sentiment (`SentimentVisualizer`)
   - Word cloud dei temi polarizzanti (`WordCloudVisualizer`)
   - Visualizzazione LDA (`LDAViz`)
6. Individuare i temi polarizzanti per ciascun cluster.

Tutti i risultati (modelli, file pickle, grafici) vengono salvati in una cartella di output configurabile da riga di comando.

## Come eseguire `main.py`

`Per lanciare lo script, apri un terminale e posizionati nella cartella `Code/` del tuo progetto.
Dopodiché esegui:

`bash`
python main.py [OPZIONI]

Se non passi alcuna opzione, il comportamento di default è:

- **Pipeline TF–IDF** con LSA abilitato (200 componenti) + HDBSCAN
- Parametri di TF–IDF:
  - `max_features=5000 `  - `ngram_range=(1,2) `  - `stop_words=\"english\" `  - `min_df=0.01 `  - `max_df=0.8 `- Clustering:
  - `method=\"hdbscan\" `  - `n_clusters=10` (come valore guida per HDBSCAN)
  - `hdbscan_min_cluster_size=10 `  - `random_state=42 `- Estrazione temi polarizzanti (TF–IDF):
  - `top_n=15 `  - `polar_ngram_range_unigrams=(1,1) `  - `polar_ngram_range_bigrams=(2,2) `  - `polar_min_df=2 `  - `polar_max_df=0.7 `- `Cartella di output: Code/notebook/Analisi della polarizzazione dei contenuti/output`

`---

## Descrizione delle Opzioni (argomenti)

Di seguito sono elencati tutti gli argomenti configurabili via CLI in `main.py`.
Le tuple _(m,n)_ vanno passate come stringa, ad esempio `\"(1,2)\"`.

### 1. Parametri generali

- `--output-dir <path>`Cartella in cui salvare tutti i risultati (modelli, pickle, grafici).

  - **Default**:
    `Code/notebook/Analisi della polarizzazione dei contenuti/output
- `--random-state` <int>Seed casuale per algoritmi di clustering (HDBSCAN, KMeans). **Default**: `42`

### 2. Scelta tra TF–IDF e Embeddings

- `--use-tfidf`**(Default)** Attiva la pipeline **ClusteringTFIDF**, ovvero:

  1. Vettorizzazione TF–IDF
  2. (Opzionale) LSA
  3. Clustering (HDBSCAN o KMeans)
- `--no-tfidf`Attiva la pipeline **ClusteringEmbeddings**, ossia:

  1. Estrazione embeddings con SBERT
  2. (Opzionale) UMAP
  3. Clustering (HDBSCAN o KMeans)

**Esempi**:

`bash`
`python main.py --use-tfidf`
`python main.py --no-tfidf`

### 3. Parametri per ClusteringTFIDF (validi se `--use-tfidf`)

- `--max-features <int>`Numero massimo di feature da considerare per il vettorizzatore TF–IDF.

  - **Default**: `5000`
- `--ngram-range \"(m,n)\"`Range di n-grammi per la tokenizzazione in TF–IDF.

  - ** Default**: `\"(1,2)\"`
- `--stop-words <string>`  Lingua delle stopwords (es.`\"english\"`) o `None`(stringa`\"None\"`).

  - **Default**: `\"english\"`
- `--min-df <float>`   `min_df`per TF–IDF (esclude termini presenti in meno di`min_df * 100%` dei documenti).

  - **Default**: `0.01`
- `--max-df <float>`   `max_df`per TF–IDF (esclude termini presenti in più di`max_df * 100%` dei documenti).

  - **Default**: `0.8`
- `--use-lsa`Se presente, abilita la riduzione di dimensionalità con **LSA** (SVD) dopo TF–IDF.
- `--lsa-components <int>`Numero di componenti SVD da mantenere se `--use-lsa` è specificato.

  - **Default**: `200`

`**Esempio completo TF–IDF + LSA**:`

`bash python main.py \\ --use-tfidf \\ --max-features 10000 \\ --ngram-range \"(1,1)\" \\ --stop-words None \\ --min-df 0.02 \\ --max-df 0.7 \\ --use-lsa \\ --lsa-components 150`

---

### 4. Parametri per ClusteringEmbeddings (validi se `--no-tfidf`)

- `--embedding-model <string>`Nome del modello SBERT da utilizzare (es. `\"all-MiniLM-L6-v2\"`, `\"all-mpnet-base-v2\"`).
  - **Default**: `\"all-MiniLM-L6-v2\"

`- `--use-umap`Se presente, abilita la riduzione di dimensionalità con **UMAP** sulle embeddings.

- `--umap-components <int>`Numero di dimensioni target del risultato UMAP (se `--use-umap`).
  - **Default**: `50

`**Esempio completo Embeddings + UMAP**:

`bash
python main.py \\
--no-tfidf \\
--embedding-model \"all-mpnet-base-v2\" \\
--use-umap \\
--umap-components 30

`

---

### 5. Parametri di Clustering comuni (sia TF–IDF sia Embeddings)

- `--method <hdbscan|kmeans>`Algoritmo di clustering da utilizzare:
  - `hdbscan` (predefinito)
  - `kmeans

`- `--n-clusters <int>`Numero di cluster desiderati:

- Per **KMeans**: numero esatto di cluster da formare.
- Per **HDBSCAN**: valore-guida interno (terra di solito come `min_cluster_size` e `cluster_selection_epsilon`), ma non vincolante.
- **Default**: `10

`- `--hdbscan-min-cluster-size <int>`  Parametro`min_cluster_size` di HDBSCAN (numero minimo di elementi per un cluster).

- **Default**: `10

`**Esempi**:

`bash

# HDBSCAN su TF–IDF (default):

python main.py --method hdbscan --n-clusters 10 --hdbscan-min-cluster-size 5

# KMeans su embeddings:

python main.py --no-tfidf --method kmeans --n-clusters 12 --random-state 0

`

---

### 6. Parametri per l’estrazione dei temi polarizzanti (solo TF–IDF)

Se `--use-tfidf` è abilitato, dopo il clustering vengono estratti i termini più polarizzanti per ciascun cluster. Gli argomenti correlati sono:

- `--top-n <int>`Numero di parole chiave da estrarre per ogni cluster (sia per unigrams sia per bigrams).
  - **Default**: `15

`- `--polar-ngram-range-unigrams \"(1,1)\"`Range di n-grammi per estrarre **unigrams polarizzanti**.

- **Default**: `\"(1,1)\"

`- `--polar-ngram-range-bigrams \"(2,2)\"`Range di n-grammi per estrarre **bigrams polarizzanti**.

- **Default**: `\"(2,2)\"

`- `--polar-min-df <int>`   `min_df` per il conteggio dei termini polarizzanti (TF–IDF).

- **Default**: `2

`- `--polar-max-df <float>`   `max_df` per il conteggio dei termini polarizzanti (TF–IDF).

- **Default**: `0.7

`**Esempio (estrazione temi polarizzanti)**:

`bash
python main.py \\
--use-tfidf \\
--top-n 10 \\
--polar-ngram-range-unigrams \"(1,1)\" \\
--polar-ngram-range-bigrams \"(2,2)\" \\
--polar-min-df 3 \\
--polar-max-df 0.5

`

---

## Esempi di Comandi Comuni

1. **Esecuzione base (TF–IDF + LSA + HDBSCAN)**

`bash
python main.py

`  - Tutti i valori di default (TF–IDF, LSA con 200 componenti, HDBSCAN con`min_cluster_size=10`, 10 cluster-guida).

2. **TF–IDF senza LSA (solo vettorizzazione + HDBSCAN)**

`bash
python main.py \\
--use-tfidf \\
--use-lsa False \\
--method hdbscan \\
--hdbscan-min-cluster-size 5 \\
--n-clusters 8

`   - TF–IDF con default, ma LSA disattivato.

- HDBSCAN: cluster minimo 5, suggerito 8 cluster.

3. **Embeddings (SBERT) senza riduzione, clustering KMeans**

`bash
python main.py \\
--no-tfidf \\
--embedding-model \"all-mpnet-base-v2\" \\
--method kmeans \\
--n-clusters 12 \\
--random-state 2025

`   - Estrae embeddings con \"all-mpnet-base-v2\", nessun UMAP.

- KMeans a 12 cluster.

4. **Embeddings + UMAP + HDBSCAN**

`bash
python main.py \\
--no-tfidf \\
--use-umap \\
--umap-components 40 \\
--method hdbscan \\
--hdbscan-min-cluster-size 8 \\
--n-clusters 10

`   - SBERT + UMAP (40 dimensioni) + HDBSCAN (`min_cluster_size=8`, target 10 cluster).

5. **Personalizzazione rapida del numero di feature TF–IDF e stopwords**

`bash
python main.py \\
--max-features 8000 \\
--ngram-range \"(1,1)\" \\
--stop-words None \\
--min-df 0.02 \\
--max-df 0.6

`---

## Output Generati

Alla fine dell’esecuzione, nella directory `--output-dir` troverai:

1. **Modelli e file pickle**

   - `cluster_labels_tfidf.pkl` o `cluster_labels_emb.pkl`
   - `tfidf_vectorizer.pkl` (se usi TF–IDF)
   - `sentence_embeddings.pkl` (se usi embeddings)
   - `lda_model.pkl`, `dictionary.pkl`, `corpus.pkl` (risultati LDA)
2. **Grafici** (PNG/PDF)

   - Visualizzazione dei cluster (2D o 3D, a seconda dell’implementazione di `ClusterVisualizer`)
   - Distribuzione dei sentiment per cluster (istogrammi o boxplot)
   - Heatmap “Sentiment vs Temi”
   - Word cloud dei temi polarizzanti (unigrams e bigrams)
   - Grafico interattivo/HTML o statico di visualizzazione LDA tramite `LDAViz
3. **File di log**

- Vengono stampate informazioni di processo in console (livello INFO).
  - Eventuali errori vengono mostrati in console.

## Run Effettuate

- python.exe main.py --output-dir "Code/notebook/Analisi della polarizzazione dei contenuti/output/1"
- python.exe main.py --use-tfidf --use-lsa --output-dir "Code/notebook/Analisi della polarizzazione dei contenuti/output/2"
- python.exe main.py --use-tfidf --method kmeans --n-clusters 15 --output-dir "Code/notebook/Analisi della polarizzazione dei contenuti/output/3"
- python.exe main.py --no-tfidf --output-dir "Code/notebook/Analisi della polarizzazione dei contenuti/output/4"
- python.exe main.py --no-tfidf --use-umap --embedding-model all-mpnet-base-v2 --output-dir "Code/notebook/Analisi della polarizzazione dei contenuti/output/5"
