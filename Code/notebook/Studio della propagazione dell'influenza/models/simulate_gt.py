import random


def simulate_gt(graph, steps, seed=None):
    """
    Simula la diffusione con il modello Greater-Than (GT) su un grafo.

    Parametri:
        - graph: Il grafo (networkx.DiGraph o Graph) su cui eseguire la simulazione.
                 Ogni nodo deve avere una proprietà 'threshold' con la soglia di attivazione.
        - steps: Numero massimo di iterazioni della simulazione.
        - seed: Nodo iniziale da attivare (opzionale). Se None, viene scelto casualmente.

    Ritorna:
        - Un dizionario {step: num_nodi_attivi} con il numero di nodi attivati a ogni passo temporale.
    """

    seed = seed if seed is not None else random.choice(list(graph.nodes))
    activated = set(seed)

    evolution = {}
    evolution[0] = activated.copy()

    for step in range(1, steps + 1):
        new_activated = activated.copy()
        for node in graph.nodes:
            if node not in activated:

                influence = (
                    sum(
                        1 for neighbor in graph.neighbors(node) if neighbor in activated
                    )
                    / graph.degree[node]
                    if graph.degree[node] > 0
                    else 0
                )

                if influence >= graph.nodes[node]["threshold"]:
                    new_activated.add(node)

        evolution[step] = new_activated.copy()

        if new_activated == activated:
            break

        activated = new_activated

    return evolution
