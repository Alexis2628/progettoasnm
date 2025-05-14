import networkx as nx
from sklearn.cluster import KMeans


def kmeans_clustering(graph: nx.Graph, n_clusters: int = 3) -> dict:
    """
    Cluster a grafo usando K-Means su vettori di adiacenza.

    Parameters
    ----------
    graph : networkx.Graph
    n_clusters : int, optional

    Returns
    -------
    labels : dict
        Mappa nodo->cluster (int).
    """
    X = nx.to_numpy_array(graph)
    km = KMeans(n_clusters=n_clusters)
    y = km.fit_predict(X)
    nodes = list(graph.nodes())
    return dict(zip(nodes, y))
