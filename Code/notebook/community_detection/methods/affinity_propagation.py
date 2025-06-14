import networkx as nx
from sklearn.cluster import AffinityPropagation
import numpy as np


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
    X = nx.to_numpy_array(graph, dtype=np.float32)
    ap = AffinityPropagation(
        damping=damping,
        preference=preference,
        max_iter=200,
        convergence_iter=15,
        verbose=True,
    )
    y = ap.fit_predict(X)
    nodes = list(graph.nodes())
    return dict(zip(nodes, y))
