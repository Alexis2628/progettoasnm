import heapq
from models.independent_cascade_model import independent_cascade_model


def celf(graph, k, p=0.1):
    """Algoritmo CELF (Cost-Effective Lazy Greedy)"""
    current_seeds = set()
    influence_cache = {}
    heap = []

    for _ in range(k):
        best_node = None
        best_influence = 0

        for node in graph.nodes():
            if node not in current_seeds:
                if node not in influence_cache:

                    result = independent_cascade_model(graph, current_seeds | {node}, p)
                    influence_cache[node] = len(result[list(result.keys())[-1]])

                influence = influence_cache[node]

                if influence > best_influence:
                    best_influence = influence
                    best_node = node

        current_seeds.add(best_node)

        heapq.heappush(heap, (-best_influence, best_node))

    return current_seeds
