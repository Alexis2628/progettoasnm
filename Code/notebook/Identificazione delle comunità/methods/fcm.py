import numpy as np
import networkx as nx
import skfuzzy as fuzz


def fcm_clustering(
    graph: nx.Graph,
    c: int = 3,
    m: float = 2.0,
    error: float = 0.005,
    maxiter: int = 1000,
) -> dict:
    """
    Cluster a grafo usando Fuzzy C-Means su vettori di adiacenza.

    Parameters
    ----------
    graph : networkx.Graph
    c : int
        Numero di cluster.
    m : float
        Fuzziness exponent.
    error : float
    maxiter : int

    Returns
    -------
    labels : dict
        Mappa nodo->cluster (int).
    """
    X = nx.to_numpy_array(graph).T
    cntr, u, _, _, _, _, _ = fuzz.cluster.cmeans(X, c, m, error=error, maxiter=maxiter)
    labels = np.argmax(u, axis=0)
    nodes = list(graph.nodes())
    return dict(zip(nodes, labels))
