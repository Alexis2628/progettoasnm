import random
import networkx as nx


def pmc(graph, k, p=0.1):
    """PMC: Approssimazione usando grafi ridotti"""
    reduced_graph = graph.copy()
    for u, v in graph.edges():
        if random.random() > p:
            reduced_graph.remove_edge(u, v)
    seed_set = set(
        sorted(
            reduced_graph.nodes(), 
            key=lambda node: nx.degree_centrality(reduced_graph)[node], 
            reverse=True
        )[:k]
    )
    return seed_set