import networkx as nx


def girvan_newman_clustering(graph: nx.Graph) -> dict:
    """
    Rileva le comunità in un grafo utilizzando l'algoritmo Girvan-Newman.

    Args:
        graph (networkx.Graph): Il grafo su cui eseguire il clustering.

    Returns:
        list: Una lista di comunità, ciascuna rappresentata da un insieme di nodi.
    """

    graph_copy = graph.copy().to_undirected()
    communities = []

    while len(list(nx.connected_components(graph_copy))) == 1:

        edge_betweenness = nx.edge_betweenness_centrality(graph_copy)

        edge_to_remove = max(edge_betweenness, key=edge_betweenness.get)

        graph_copy.remove_edge(*edge_to_remove)

    for component in nx.connected_components(graph_copy):
        communities.append(component)

    labels = {}
    for idx, community in enumerate(communities):
        for node in community:
            labels[node] = idx
    return labels
