import heapq
from models.independent_cascade_model import independent_cascade_model

def celf(graph, k, p=0.1):
    """Algoritmo CELF (Cost-Effective Lazy Greedy)"""
    current_seeds = set()
    influence_cache = {}  # Memorizza l'influenza dei nodi
    heap = []  # Coda di priorità per selezionare i nodi migliori

    for _ in range(k):
        best_node = None
        best_influence = 0
        
        for node in graph.nodes():
            if node not in current_seeds:
                if node not in influence_cache:
                    # Calcola l'influenza solo se non è già presente nella cache
                    result = independent_cascade_model(graph, current_seeds | {node}, p)
                    influence_cache[node] = len(
                        result[list(result.keys())[-1]]
                    )
                
                # Ottieni l'influenza del nodo
                influence = influence_cache[node]
                
                # Se il nodo ha una migliore influenza, aggiorna il miglior nodo
                if influence > best_influence:
                    best_influence = influence
                    best_node = node
        
        # Aggiungi il nodo migliore trovato come seed
        current_seeds.add(best_node)
        
        # Aggiorna la coda di priorità (heap) con il miglior nodo
        heapq.heappush(heap, (-best_influence, best_node))
        
    return current_seeds
