import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities


def modularity_maximization_clustering(graph: nx.Graph) -> dict:
    """
    Esegue il clustering sul grafo utilizzando la massimizzazione della modularità (approccio greedy).

    Parameters
    ----------
    graph : networkx.Graph
        Il grafo su cui eseguire il clustering.

    Returns
    -------
    dict
        Mappa nodo->cluster (int).
    """
    # Trova le comunità massimizzando la modularità
    communities = greedy_modularity_communities(graph)
    # Assegna un'etichetta a ogni nodo
    labels = {}
    for cluster_id, community in enumerate(communities):
        for node in community:
            labels[node] = cluster_id
    return labels
