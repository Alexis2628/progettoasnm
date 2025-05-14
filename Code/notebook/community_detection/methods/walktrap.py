import networkx as nx
import igraph as ig


def walktrap_clustering(graph: nx.Graph, steps: int = 4) -> dict:
    """
    Cluster a graph usando Walktrap (random walks).

    Parameters
    ----------
    graph : networkx.Graph
        Il grafo da clusterizzare.
    steps : int, optional
        Numero di passi random (default=4).

    Returns
    -------
    labels : dict
        Mappa nodo->cluster (int).
    """
    # converte da networkx a igraph
    ig_graph = ig.Graph.TupleList(
        graph.edges(), directed=False, vertex_name_attr="name"
    )
    dendro = ig_graph.community_walktrap(steps=steps)
    clustering = dendro.as_clustering()
    membership = clustering.membership
    names = ig_graph.vs["name"]
    return {names[i]: membership[i] for i in range(len(names))}
