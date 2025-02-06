def static(graph, k, p=0.1):
    """Algoritmo Static (scelta statica dei nodi basata sulla centralità)"""
    current_seeds = set()
    sorted_nodes = sorted(
        graph.nodes(), key=lambda node: graph.degree(node), reverse=True
    )
    return set(sorted_nodes[:k])
