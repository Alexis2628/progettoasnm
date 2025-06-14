import networkx as nx


def girvan_newman_clustering(graph: nx.Graph) -> dict:
    """
    Rileva le comunità in un grafo utilizzando l'algoritmo Girvan-Newman.

    Args:
        graph (networkx.Graph): Il grafo su cui eseguire il clustering.

    Returns:
        list: Una lista di comunità, ciascuna rappresentata da un insieme di nodi.
    """
    # Copia il grafo per non modificare il grafo originale
    graph_copy = graph.copy().to_undirected()
    communities = []

    # Continua a dividere finché non ci sono più di un componente connesso
    while len(list(nx.connected_components(graph_copy))) == 1:
        # Calcola la betweenness centrality per ogni arco
        edge_betweenness = nx.edge_betweenness_centrality(graph_copy)

        # Trova l'arco con la massima betweenness
        edge_to_remove = max(edge_betweenness, key=edge_betweenness.get)

        # Rimuove l'arco con la massima betweenness
        graph_copy.remove_edge(*edge_to_remove)

    # Ottieni i componenti connessi (comunità) nel grafo dopo aver rimosso gli archi
    for component in nx.connected_components(graph_copy):
        communities.append(component)

    labels = {}
    for idx, community in enumerate(communities):
        for node in community:
            labels[node] = idx
    return labels
