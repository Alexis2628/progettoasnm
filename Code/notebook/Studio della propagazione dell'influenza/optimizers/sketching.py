def sketching(graph, k, p=0.1):
    """Sketching: Riduzione e selezione ottimizzata"""
    reduced_nodes = sorted(graph.nodes(), key=lambda n: graph.degree(n), reverse=True)[
        : len(graph.nodes()) // 2
    ]
    subgraph = graph.subgraph(reduced_nodes)
    return set(sorted(subgraph.nodes(), key=subgraph.degree, reverse=True)[:k])
