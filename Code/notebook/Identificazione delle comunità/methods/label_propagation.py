import networkx as nx
from networkx.algorithms.community import label_propagation_communities


def label_propagation_clustering(graph: nx.Graph) -> dict:
    """
    Cluster a graph usando Label Propagation.

    Parameters
    ----------
    graph : networkx.Graph
        Il grafo su cui eseguire il clustering.

    Returns
    -------
    labels : dict
        Mappa nodo->cluster (int).
    """
    graph_undir = graph.to_undirected()
    communities = label_propagation_communities(graph_undir)
    labels = {}
    for i, community in enumerate(communities):
        for node in community:
            labels[node] = i
    return labels
