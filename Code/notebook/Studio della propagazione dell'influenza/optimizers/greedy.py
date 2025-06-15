from models.independent_cascade_model import independent_cascade_model


def greedy(graph, k, p=0.1):
    """Algoritmo Greedy per la massimizzazione dell'influenza nel modello di cascata indipendente"""
    current_seeds = set()
    for _ in range(k):
        best_node = None
        best_influence = 0
        for node in graph.nodes():
            if node not in current_seeds:

                temp_seeds = current_seeds | {node}

                result = independent_cascade_model(graph, temp_seeds, p)
                influence = len(result[list(result.keys())[-1]])

                if influence > best_influence:
                    best_influence = influence
                    best_node = node

        current_seeds.add(best_node)
    return current_seeds
