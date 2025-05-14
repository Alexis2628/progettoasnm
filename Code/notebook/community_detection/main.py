import os
import argparse
import json

from methods.louvain import louvain_clustering
from methods.label_propagation import label_propagation_clustering
from methods.girvan_newman import girvan_newman_clustering
from methods.walktrap import walktrap_clustering
from methods.leiden import leiden_clustering
from methods.dbscan import dbscan_clustering
from methods.kmeans import kmeans_clustering
from methods.fcm import fcm_clustering
from methods.gaussian_mixture import gaussian_mixture_clustering
from methods.affinity_propagation import affinity_propagation_clustering
from methods.modularity_maximization import modularity_maximization_clustering
from comparison import Comparator

import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from utils.logger import setup_logger
from Code.notebook.graph.GraphConstructor import GraphConstructor
import logging

setup_logger()
logger = logging.getLogger(__name__)


def main(force: bool = False):
    gc = GraphConstructor()
    gc.build_graph()
    G = gc.graph

    out_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(out_dir, exist_ok=True)

    methods = {
        "louvain": louvain_clustering,
        "label_propagation": label_propagation_clustering,
        "girvan_newman": girvan_newman_clustering,
        "walktrap": walktrap_clustering,
        "leiden": leiden_clustering,
        "dbscan": dbscan_clustering,
        "kmeans": kmeans_clustering,
        "fcm": fcm_clustering,
        "gaussian_mixture": gaussian_mixture_clustering,
        "affinity_propagation": affinity_propagation_clustering,
        "modularity_maximization": modularity_maximization_clustering,
    }

    partitions = {}

    for name, func in methods.items():
        out_path = os.path.join(out_dir, f"{name}_results.json")
        if os.path.exists(out_path) and not force:
            print(f"→ Saltato {name}: già esiste {out_path} (usa --force)")
            continue

        print(f"Eseguo {name}...")
        try:
            result = func(G)  # result: dict nodo -> cluster
        except Exception as e:
            print(f"⚠️ Errore in {name}: {e}")
            continue

        # costruisci la lista dei nodi
        nodes = []
        for n in G.nodes():
            nodes.append(
                {
                    "id": str(n),
                    "cluster": str(result.get(n, "")),
                    "name": G.nodes[n].get("name", ""),
                    "description": G.nodes[n].get("description", ""),
                }
            )

        # costruisci la lista degli archi
        edges = []
        for u, v in G.edges():
            edges.append({"source": str(u), "target": str(v)})

        # unisci in un unico dict
        data = {"nodes": nodes, "edges": edges}

        # salva in JSON
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"→ Salvato: {out_path}")

    # Confronto tra metodi
    comparator = Comparator(G, partitions, out_dir)
    df_metrics = comparator.compute_metrics()
    comparator.plot_metrics(df_metrics)
    comparator.plot_nmi_heatmap()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Esegue tutti i metodi di community detection."
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Forza il ricalcolo anche se il file di output esiste già",
    )
    args = parser.parse_args()
    main(force=args.force)
