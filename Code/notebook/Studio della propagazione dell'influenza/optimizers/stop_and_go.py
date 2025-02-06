from models.independent_cascade_model import independent_cascade_model


def stop_and_go(graph, k, p=0.1):
    """Algoritmo Stop-And-Go ottimizzato"""
    current_seeds = set()
    influence_cache = {}

    while len(current_seeds) < k:
        best_node = None
        best_influence = 0
        for node in graph.nodes():
            if node not in current_seeds:
                if node not in influence_cache:
                    # Calcoliamo l'influenza solo se non è già nella cache
                    result = independent_cascade_model(graph, current_seeds | {node}, p)
                    influence_cache[node] = len(result[list(result.keys())[-1]])
                influence = influence_cache[node]
                
                if influence > best_influence:
                    best_influence = influence
                    best_node = node

        current_seeds.add(best_node)
    return current_seeds
