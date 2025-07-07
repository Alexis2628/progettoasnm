# Analisi della polarizzazione dei contenuti

Questa directory ospita gli script necessari per esaminare opinioni e argomenti espressi dagli utenti. Il file principale è `main.py` e consente di avviare l'intera pipeline:

1. caricamento e pulizia dei testi;
2. rappresentazione mediante TF‑IDF o embedding;
3. raggruppamento degli utenti in cluster;
4. individuazione di temi e sentiment predominanti.

Per eseguire il flusso standard è sufficiente digitare:

```bash
python main.py
```

Tutti i parametri sono configurabili da riga di comando; è possibile ottenere la lista completa tramite `--help`. I risultati e i grafici generati verranno salvati nella cartella `output/`.

### Run Effettuate
```bash
python.exe main.py --output-dir "Code/notebook/Analisi della polarizzazione dei contenuti/output/1"
```
```bash
python.exe main.py --use-tfidf --use-lsa --output-dir "Code/notebook/Analisi della polarizzazione dei contenuti/output/2"
```
```bash
python.exe main.py --use-tfidf --method kmeans --n-clusters 15 --output-dir "Code/notebook/Analisi della polarizzazione dei contenuti/output/3"
```
```bash
python.exe main.py --no-tfidf --output-dir "Code/notebook/Analisi della polarizzazione dei contenuti/output/4"
```
```bash
python.exe main.py --no-tfidf --use-umap --embedding-model all-mpnet-base-v2 --output-dir "Code/notebook/Analisi della polarizzazione dei contenuti/output/5"
```

### Confronto delle run

Per valutare le differenti configurazioni è presente lo script `comparison.py` che calcola
metriche di coesione, separazione e polarizzazione emotiva. Lanciandolo verrà creato il
file `comparison_metrics.csv` nella directory `output/`.

```bash
python comparison.py
```