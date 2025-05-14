import networkx as nx
from sklearn.cluster import AffinityPropagation
from scipy.sparse import csr_matrix


def affinity_propagation_clustering(
    graph: nx.Graph, damping: float = 0.5, preference=None
) -> dict:
    """
    Cluster a grafo usando Affinity Propagation.

    Parameters
    ----------
    graph : networkx.Graph
    damping : float
    preference : float or None

    Returns
    -------
    labels : dict
        Mappa nodo->cluster (int).
    """
    A: csr_matrix = nx.adjacency_matrix(graph)
    ap = AffinityPropagation(
        damping=damping,
        preference=preference,
        max_iter=200,
        convergence_iter=15,
        verbose=True,
    )
    y = ap.fit_predict(A)
    nodes = list(graph.nodes())
    return dict(zip(nodes, y))
