from models.independent_cascade_model import independent_cascade_model

def greedy(graph, k, p=0.1):
    """Algoritmo Greedy per la massimizzazione dell'influenza nel modello di cascata indipendente"""
    current_seeds = set()  # Inizializza il set di nodi seed
    for _ in range(k):
        best_node = None
        best_influence = 0
        for node in graph.nodes():
            if node not in current_seeds:
                # Aggiungi temporaneamente il nodo al set dei seed
                temp_seeds = current_seeds | {node}
                # Calcola l'influenza ottenuta con il nuovo seed
                result = independent_cascade_model(graph, temp_seeds, p)
                influence = len(result[list(result.keys())[-1]])
                # Se l'influenza è maggiore di quella precedentemente registrata, aggiorna
                if influence > best_influence:
                    best_influence = influence
                    best_node = node
        # Aggiungi il miglior nodo al set dei seed
        current_seeds.add(best_node)
    return current_seeds
