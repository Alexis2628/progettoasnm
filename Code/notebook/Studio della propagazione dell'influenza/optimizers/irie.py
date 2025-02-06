def irie(graph, k, p=0.1):
    """Algoritmo IRIE basato su Random Walk e Linear Influence"""
    influence_scores = {node: 1 for node in graph.nodes()}

    for _ in range(5):
        new_scores = {}
        for node in graph.nodes():
            new_scores[node] = 1 + sum(
                influence_scores[neighbor] * p for neighbor in graph.predecessors(node)
            )
        influence_scores = new_scores

    seed_set = set(sorted(influence_scores, key=influence_scores.get, reverse=True)[:k])
    return seed_set
