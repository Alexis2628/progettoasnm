from models.independent_cascade_model import independent_cascade_model


def singles(graph, k, p=0.1):
    """Singles: Valutazione dei singoli nodi per selezionare i k nodi più influenti"""

    influence_cache = {}

    for node in graph.nodes():
        if node not in influence_cache:
            result = independent_cascade_model(graph, {node}, p)
            influence_cache[node] = len(result[list(result.keys())[-1]])

    return set(sorted(influence_cache, key=influence_cache.get, reverse=True)[:k])
