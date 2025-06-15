import random


def independent_cascade_model(graph, seed_nodes, p=0.1):
    """
    Implementa il modello a cascata indipendente su un grafo diretto.

    Parametri:
        - graph: Il grafo su cui eseguire la simulazione (directed graph).
        - seed_nodes: Nodi inizialmente attivi.
        - p: Probabilità di attivare un vicino.

    Ritorna:
        - Un dizionario contenente i nodi attivati per ciascun passo temporale.
    """
    activated = set(seed_nodes)
    newly_activated = set(seed_nodes)
    propagation_steps = {0: set(seed_nodes)}
    step = 0

    while newly_activated:
        next_activated = set()
        for node in newly_activated:
            if node in graph:
                neighbors = set(graph.successors(node)) - activated
            else:
                print(f"Node {node} not in graph")
                continue
            for neighbor in neighbors:
                if random.random() < p:
                    next_activated.add(neighbor)
        newly_activated = next_activated
        step += 1
        activated.update(newly_activated)
        propagation_steps[step] = activated.copy()

    return propagation_steps
