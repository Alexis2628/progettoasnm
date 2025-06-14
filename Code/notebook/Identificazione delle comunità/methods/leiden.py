import networkx as nx
import igraph as ig
import leidenalg


def leiden_clustering(graph: nx.Graph, resolution: float = 1.0) -> dict:
    """
    Cluster a graph usando l’algoritmo di Leiden.

    Parameters
    ----------
    graph : networkx.Graph
        Il grafo su cui operare.
    resolution : float, optional
        Parametro di risoluzione del clustering (default=1.0).

    Returns
    -------
    labels : dict
        Mappa nodo->cluster (int).
    """
    ig_graph = ig.Graph.TupleList(
        graph.edges(), directed=False, vertex_name_attr="name"
    )
    partition = leidenalg.find_partition(
        ig_graph,
        leidenalg.RBConfigurationVertexPartition,
        resolution_parameter=resolution,
    )
    membership = partition.membership
    names = ig_graph.vs["name"]
    return {names[i]: membership[i] for i in range(len(names))}
