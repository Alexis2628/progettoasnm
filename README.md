# Progetto ASNM

Questo repository raccoglie alcuni strumenti per l'analisi di reti sociali e di contenuti testuali. Al suo interno sono presenti script dedicati al rilevamento delle comunità, allo studio della polarizzazione e alla propagazione dell'influenza.

## Installazione
1. Assicurarsi di avere Python ≥ 3.11.
2. Installare [uv](https://github.com/astral-sh/uv):
   ```bash
   pip install uv
   ```
3. Dalla cartella radice eseguire:
   ```bash
   uv sync
   ```
   in modo da installare tutte le dipendenze definite nel progetto.

## Struttura del codice
- `Code/data_extraction` contiene gli script per l'estrazione e la preparazione dei dati.
- `Code/notebook/community_detection` implementa diversi algoritmi di community detection.
- `Code/notebook/Analisi della polarizzazione dei contenuti` offre strumenti per analizzare opinioni e temi predominanti.
- `Code/notebook/Studio della propagazione dell'influenza` permette di simulare la diffusione di informazioni nella rete.

## Utilizzo rapido
Ogni cartella principale include un file `main.py` eseguibile dalla riga di comando. Ad esempio, per avviare la community detection:

```bash
python Code/notebook/community_detection/main.py
```

Aggiungendo l'opzione `--help` è possibile visualizzare i parametri disponibili per ciascun script. I risultati vengono salvati nelle rispettive cartelle `output/`.
