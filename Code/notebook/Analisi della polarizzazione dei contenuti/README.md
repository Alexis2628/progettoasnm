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
