import networkx as nx
from community import community_louvain


def louvain_clustering(graph: nx.Graph) -> dict:
    """
    Cluster a graph using the Louvain method.

    Parameters
    ----------
    graph : networkx.Graph
        Il grafo su cui eseguire il clustering.

    Returns
    -------
    partition : dict
        Mappa nodo->cluster (int).
    """
    graph_undir = graph.to_undirected()
    # best_partition restituisce un dict {nodo: comunità}
    partition = community_louvain.best_partition(graph_undir)
    return partition
