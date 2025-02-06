from models.independent_cascade_model import independent_cascade_model

def celf_plus(graph, k, p=0.1):
    """Algoritmo CELF++ (miglioramento di CELF)"""
    current_seeds = set()  # Semi correnti
    influence_cache = {}   # Cache per memorizzare l'influenza dei nodi

    for _ in range(k):
        best_node = None
        best_influence = 0
        
        for node in graph.nodes():
            if node not in current_seeds:
                # Se l'influenza del nodo non è nella cache, calcolala
                if node not in influence_cache:
                    result = independent_cascade_model(graph, current_seeds | {node}, p)
                    influence_cache[node] = len(
                        result[list(result.keys())[-1]]
                    )
                
                # Ottieni l'influenza del nodo
                influence = influence_cache[node]
                
                # Aggiorna il miglior nodo se l'influenza è maggiore
                if influence > best_influence:
                    best_influence = influence
                    best_node = node
        
        # Aggiungi il nodo con la maggiore influenza ai semi correnti
        current_seeds.add(best_node)
    
    return current_seeds
