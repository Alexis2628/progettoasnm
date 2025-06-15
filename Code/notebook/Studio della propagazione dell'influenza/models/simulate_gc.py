import random


def simulate_gc(graph, prob, steps, seed=None, edge_probabilities=None):
    """
    Simula la diffusione con il General Cascade Model su un grafo.

    Parametri:
        - graph: Il grafo (networkx.DiGraph o Graph) su cui eseguire la simulazione.
        - prob: Probabilità uniforme di attivazione di un vicino (usata se edge_probabilities è None).
        - steps: Numero di iterazioni della simulazione.
        - seed: Nodo iniziale da attivare (opzionale). Se None, viene scelto casualmente.
        - edge_probabilities: Dizionario {(u, v): p_uv} con probabilità specifiche per arco (opzionale).

    Ritorna:
        - Una lista contenente l'insieme dei nodi attivati a ogni passo.
    """

    seed = seed if seed is not None else random.choice(list(graph.nodes))
    activated = set(seed)

    evolution = {}

    evolution[0] = activated.copy()
    for step in range(1, steps + 1):
        new_activated = activated.copy()
        for node in graph.nodes:
            if node not in activated:
                for neighbor in graph.neighbors(node):
                    if neighbor in activated:

                        activation_prob = (
                            edge_probabilities.get((neighbor, node), prob)
                            if edge_probabilities
                            else prob
                        )
                        if random.random() < activation_prob:
                            new_activated.add(node)
                            break
        if new_activated == activated:
            break
        activated = new_activated
        evolution[step] = activated.copy()

    return evolution
