import random


def simulate_sis(graph, beta, gamma, steps, initial_infected=None):
    """
    Simula la diffusione dell'infezione utilizzando il modello SIS (Susceptible-Infected-Susceptible).

    Parametri:
        - graph: Il grafo (networkx.Graph o DiGraph) su cui eseguire la simulazione.
        - beta: Probabilità di trasmissione per ogni contatto infetto-suscettibile.
        - gamma: Probabilità di recupero di un nodo infetto a ogni passo.
        - steps: Numero massimo di iterazioni della simulazione.
        - initial_infected: Lista di nodi inizialmente infetti (opzionale). Se None, viene scelto un nodo casualmente.

    Ritorna:
        - Una lista di tuple (S, I) dove S e I sono i set di nodi suscettibili e infetti a ogni passo.
    """

    states = {node: "S" for node in graph.nodes}

    if initial_infected is None:
        initial_infected = [random.choice(list(graph.nodes))]
    for node in initial_infected:
        states[node] = "I"

    dynamics = {}

    for step in range(0, steps):

        S = {node for node, state in states.items() if state == "S"}
        I = {node for node, state in states.items() if state == "I"}

        dynamics[step] = (S, I, None)

        if not I:
            break

        new_states = states.copy()
        for node in graph.nodes:
            if states[node] == "S":

                for neighbor in graph.neighbors(node):
                    if states[neighbor] == "I" and random.random() < beta:
                        new_states[node] = "I"
                        break
            elif states[node] == "I" and random.random() < gamma:

                new_states[node] = "S"

        states = new_states

    return dynamics
