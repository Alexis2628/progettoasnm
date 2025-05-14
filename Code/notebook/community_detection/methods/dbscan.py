import networkx as nx
from sklearn.cluster import DBSCAN


def dbscan_clustering(graph: nx.Graph, eps: float = 0.5, min_samples: int = 5) -> dict:
    """
    Cluster a graph usando DBSCAN su feature di adiacenza.

    Parameters
    ----------
    graph : networkx.Graph
    eps : float, optional
    min_samples : int, optional

    Returns
    -------
    labels : dict
        Mappa nodo->cluster (int, con -1 per rumore).
    """
    # matrice di adiacenza come feature
    X = nx.to_numpy_array(graph)
    db = DBSCAN(eps=eps, min_samples=min_samples)
    y = db.fit_predict(X)
    nodes = list(graph.nodes())
    return dict(zip(nodes, y))
