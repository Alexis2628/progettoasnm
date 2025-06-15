import random


def simulate_tr(graph, steps, initial_active=None):
    """
    Simula la diffusione con il modello Threshold Reversibile.

    Parametri:
        - graph: Il grafo (networkx.Graph o DiGraph) su cui eseguire la simulazione.
                 Ogni nodo deve avere una proprietà 'threshold' con la soglia di attivazione/disattivazione.
        - steps: Numero massimo di iterazioni della simulazione.

    Ritorna:
        - Un dizionario {step: num_nodi_attivi} con il numero di nodi attivi a ogni passo temporale.
    """

    states = {node: False for node in graph.nodes}
    for node in initial_active:
        states[node] = True

    dynamics = {}

    for step in range(0, steps):
        new_states = states.copy()

        for node in graph.nodes:

            active_neighbors = sum(
                1 for neighbor in graph.neighbors(node) if states[neighbor]
            )
            influence = active_neighbors / max(1, len(list(graph.neighbors(node))))

            if not states[node] and influence >= graph.nodes[node]["threshold"]:
                new_states[node] = True
            elif states[node] and influence < graph.nodes[node]["threshold"]:
                new_states[node] = False

        states = new_states
        active_nodes = {node for node, active in states.items() if active}
        dynamics[step] = active_nodes.copy()

        if step > 0 and dynamics[step] == dynamics[step - 1]:
            break

    return dynamics
