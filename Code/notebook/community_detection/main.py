import os

os.environ["LOKY_MAX_CPU_COUNT"] = "8"
import sys
import argparse
import json
import logging
import pandas as pd

# community quality metrics
from networkx.algorithms.community.quality import modularity, partition_quality

# Import community detection methods -
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

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from comparison import Comparator
from utils.logger import setup_logger
from Code.notebook.graph.GraphConstructor import GraphConstructor
from Code.notebook.community_detection.utils.cluster_helper import (
    build_clusters_from_partition,
    compute_cluster_connections,
    compute_cluster_stats,
)


def main(force: bool = False):
    # setup logger
    setup_logger()
    logger = logging.getLogger(__name__)

    # 1) Costruisci grafo e df_data
    gc = GraphConstructor()
    gc.build_graph()
    G = gc.graph.to_undirected()
    df_data = (
        pd.DataFrame(gc.data)
        if not isinstance(gc.data, pd.DataFrame)
        else gc.data.copy()
    )

    # Directory di output
    out_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(out_dir, exist_ok=True)

    # Definizione dei metodi
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

    # 2) Esecuzione e salvataggio per ciascun metodo
    for name, func in methods.items():
        out_path = os.path.join(out_dir, f"{name}_cluster_stats.json")

        # Se esiste già ed è senza --force, carico la partition dai 'members' salvati
        if os.path.exists(out_path) and not force:
            logger.info(f"Carico partition esistente per {name} da {out_path}")
            with open(out_path, "r", encoding="utf-8") as f:
                stats = json.load(f)
            # ricostruisco il dict node->cluster_id
            partition = {}
            for cid_str, info in stats.items():
                cid = int(cid_str)
                members = info.get("members", [])
                for node in members:
                    partition[node] = cid
            partitions[name] = partition
            continue

        # Altrimenti eseguo il clustering
        logger.info(f"Eseguo {name}...")
        try:
            partition = func(G)
            partitions[name] = partition
        except Exception as e:
            logger.warning(f"Errore in {name}: {e}")
            continue

        # costruisci strutture base
        clusters = build_clusters_from_partition(partition)
        connections = compute_cluster_connections(G, partition)

        # --- calcolo metriche globali del metodo ---
        comms = list(clusters.values())
        num_comms = len(comms)
        m = modularity(G, comms)
        cov, perf = partition_quality(G, comms)
        # -------------------------------------------

        # statistiche per cluster
        stats = compute_cluster_stats(G, df_data, clusters, top_n=5)

        # integra connessioni, metriche globali e members
        for cid, info in stats.items():
            info["connected_clusters"] = connections.get(cid, [])
            info["num_communities"] = num_comms
            info["modularity"] = m
            info["coverage"] = cov
            info["performance"] = perf
            # aggiungo la lista dei membri per poter ricostruire la partition
            info["members"] = clusters[cid]

        stats = {int(cid): info for cid, info in stats.items()}

        # salva JSON
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(
                stats,
                f,
                indent=2,
                ensure_ascii=False,
                default=lambda x: x.item() if hasattr(x, "item") else x,
            )
        logger.info(f"Salvato: {out_path}")

    # 3) Confronto tra metodi (stats già iniettate, serve solo per plotting/CSV)
    comparator = Comparator(G, partitions, out_dir)
    df_metrics = comparator.compute_metrics()
    comparator.plot_metrics(df_metrics)
    comparator.plot_nmi_heatmap()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Esegue community detection e salva statistiche per cluster."
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Ricalcola anche se i file di output esistono già",
    )
    args = parser.parse_args()
    main(force=args.force)