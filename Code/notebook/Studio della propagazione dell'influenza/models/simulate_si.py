import random


def simulate_si(graph, beta, steps, initial_infected=None):
    """
    Simula la diffusione dell'infezione utilizzando il modello SI (Susceptible-Infected).

    Parametri:
        - graph: Il grafo (networkx.DiGraph o Graph) su cui eseguire la simulazione.
        - beta: Probabilità di trasmissione per ogni contatto infetto-suscettibile.
        - steps: Numero massimo di iterazioni della simulazione.
        - initial_infected: Lista di nodi inizialmente infetti (opzionale). Se None, viene scelto un nodo casualmente.

    Ritorna:
        - Una lista contenente i set dei nodi infetti a ogni passo.
    """

    states = {node: "S" for node in graph.nodes}

    if initial_infected is None:
        initial_infected = [random.choice(list(graph.nodes))]
    for node in initial_infected:
        states[node] = "I"

    evolution = {}
    evolution[0] = initial_infected.copy()
    for step in range(1, steps + 1):
        new_states = states.copy()
        new_infected = set()

        for node in graph.nodes:
            if states[node] == "S":

                for neighbor in graph.neighbors(node):
                    if states[neighbor] == "I" and random.random() < beta:
                        new_states[node] = "I"
                        new_infected.add(node)
                        break

        if not new_infected:
            break

        states = new_states
        evolution[step] = {node for node, state in states.items() if state == "I"}

    return evolution
