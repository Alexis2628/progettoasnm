import random


def linear_threshold_model(graph, seed_nodes):
    """Esegue il modello Linear Threshold su ``graph``.

    Parameters
    ----------
    graph : networkx.DiGraph
        Grafo su cui simulare la diffusione.
    seed_nodes : iterable
        Nodi inizialmente attivi.

    Returns
    -------
    dict
        Dizionario step -> insieme di nodi attivi.
    """

    activated = set(seed_nodes)
    newly_activated = set(seed_nodes)

    for node in graph.nodes():
        neighbors = list(graph.successors(node))
        if neighbors:
            weight = 1 / len(neighbors)
            for neighbor in neighbors:
                graph.edges[node, neighbor]["influence"] = weight

    propagation_steps = {0: set(seed_nodes)}
    step = 0

    while newly_activated:
        next_activated = set()
        for node in graph.nodes():
            if node not in activated:
                total_influence = sum(
                    graph.edges[neighbor, node]["influence"]
                    for neighbor in graph.predecessors(node)
                    if neighbor in activated
                )
                if total_influence >= graph.nodes[node]["threshold"]:
                    next_activated.add(node)

        newly_activated = next_activated
        step += 1
        activated.update(newly_activated)
        propagation_steps[step] = activated.copy()

    return propagation_steps
