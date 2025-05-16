# How to Use

```
pip install uv
```

```
uv sync
```

## Notebook Usage

La cartella `Code/notebook` contiene tre sezioni principali:

- **Community Detection:**
  In questa sezione vengono applicati diversi algoritmi di rilevamento delle comunità (come Louvain, Label Propagation, Girvan-Newman, Walktrap, Leiden, DBSCAN, KMeans, FCM, Gaussian Mixture, Affinity Propagation, Modularity Maximization) su un grafo di utenti.
  Per ogni metodo vengono calcolate e salvate statistiche sui cluster, tra cui modularità, coverage, performance e connessioni tra comunità.
  È inoltre possibile confrontare i risultati dei diversi algoritmi tramite metriche aggregate e visualizzazioni (grafici e heatmap).
  **Per eseguire:**

  ```
  python Code/notebook/community_detection/main.py
  ```
- **Analisi della Polarizzazione dei Contenuti:**
  Questa parte si occupa di analizzare i contenuti testuali prodotti dagli utenti, con particolare attenzione alla polarizzazione.
  Vengono estratte le opinioni degli utenti, calcolati i punteggi di sentiment, e applicati algoritmi di clustering (KMeans, DBSCAN) per raggruppare gli utenti in base alle opinioni espresse.
  Sono disponibili visualizzazioni della distribuzione del sentiment nei cluster, heatmap tra sentiment e temi polarizzanti, wordcloud dei temi più discussi (unigrammi e bigrammi) e analisi dei topic tramite LDA.
  **Per eseguire:**

  ```
  python Code/notebook/Analisi\ della\ polarizzazione\ dei\ contenuti/main.py
  ```
- **Studio della Propagazione dell'Influenza:**
  Questa sezione si focalizza sull'analisi della propagazione dell'influenza nella rete sociale.
  Vengono simulati o analizzati processi di diffusione (ad esempio, modelli di contagio o di influenza), valutando come le informazioni o le opinioni si diffondono tra gli utenti e tra le comunità individuate.
  Sono disponibili strumenti per visualizzare la propagazione e per misurare l'impatto di utenti o gruppi chiave.
  **Per eseguire:**

  ```
  python Code/notebook/propagazione_influenza/main.py
  ```
