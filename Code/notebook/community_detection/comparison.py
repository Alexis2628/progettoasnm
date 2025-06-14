import os
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from networkx.algorithms.community.quality import modularity, partition_quality
from sklearn.metrics import normalized_mutual_info_score


class Comparator:
    """
    Classe per confrontare partizioni di community detection su un grafo.

    Attributi
    ---------
    graph : networkx.Graph
        Il grafo su cui confrontare le partizioni.
    partitions : dict
        Dizionario nome_metodo -> dict(nodo->cluster).
    out_dir : str
        Cartella in cui salvare i risultati.
    """

    def __init__(self, graph: nx.Graph, partitions: dict, out_dir: str):
        """Inizializza il comparatore con i dati necessari."""

        self.graph = graph
        self.partitions = partitions
        self.out_dir = out_dir
        os.makedirs(self.out_dir, exist_ok=True)

    def compute_metrics(self) -> pd.DataFrame:
        """Calcola metriche di qualità per ciascuna partizione.

        Returns
        -------
        pandas.DataFrame
            Tabella con colonne ``method``, ``num_communities``, ``modularity``,
            ``coverage`` e ``performance``.
        """
        data = {
            "method": [],
            "num_communities": [],
            "modularity": [],
            "coverage": [],
            "performance": [],
        }
        for name, part in self.partitions.items():
            # costruisci lista di comunità
            comms = [
                [n for n, lbl in part.items() if lbl == c] for c in set(part.values())
            ]

            # modularity
            m = modularity(self.graph, comms)
            # partition_quality restituisce (coverage, performance)
            cov, perf = partition_quality(self.graph, comms)

            data["method"].append(name)
            data["num_communities"].append(len(comms))
            data["modularity"].append(m)
            data["coverage"].append(cov)
            data["performance"].append(perf)

        df = pd.DataFrame(data)
        metrics_csv = os.path.join(self.out_dir, "comparison_metrics.csv")
        df.to_csv(metrics_csv, index=False)
        return df

    def plot_metrics(self, df_metrics: pd.DataFrame):
        """Disegna grafici a barre per ogni metrica.

        Parameters
        ----------
        df_metrics : pandas.DataFrame
            Output di :meth:`compute_metrics`.
        """
        for col in ["num_communities", "modularity", "coverage", "performance"]:
            plt.figure()
            plt.bar(df_metrics["method"], df_metrics[col])
            plt.xlabel("Metodo")
            plt.ylabel(col.replace("_", " ").title())
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            path = os.path.join(self.out_dir, f"{col}.png")
            plt.savefig(path)
            plt.close()

    def plot_nmi_heatmap(self):
        """Visualizza la heatmap delle similarità (NMI) tra le partizioni."""
        names = list(self.partitions.keys())
        n = len(names)
        nmi_mat = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i <= j:
                    pi = self.partitions[names[i]]
                    pj = self.partitions[names[j]]
                    nodes = sorted(self.graph.nodes())
                    vi = [pi[n] for n in nodes]
                    vj = [pj[n] for n in nodes]
                    score = normalized_mutual_info_score(vi, vj)
                    nmi_mat[i][j] = score
                    nmi_mat[j][i] = score

        plt.figure()
        plt.imshow(nmi_mat, interpolation="nearest")
        plt.colorbar()
        plt.xticks(range(n), names, rotation=45, ha="right")
        plt.yticks(range(n), names)
        plt.title("NMI fra metodi")
        plt.tight_layout()
        heatmap_path = os.path.join(self.out_dir, "nmi_heatmap.png")
        plt.savefig(heatmap_path)
        plt.close()
