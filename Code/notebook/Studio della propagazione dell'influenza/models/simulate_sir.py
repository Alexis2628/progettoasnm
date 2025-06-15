import random


def simulate_sir(graph, beta, gamma, steps, initial_infected=None):
    """
    Simula la diffusione dell'infezione utilizzando il modello SIR (Susceptible-Infected-Recovered).

    Parametri:
        - graph: Il grafo (networkx.Graph o DiGraph) su cui eseguire la simulazione.
        - beta: Probabilità di trasmissione per ogni contatto infetto-suscettibile.
        - gamma: Probabilità di recupero di un nodo infetto a ogni passo.
        - steps: Numero massimo di iterazioni della simulazione.
        - initial_infected: Lista di nodi inizialmente infetti (opzionale). Se None, viene scelto un nodo casualmente.

    Ritorna:
        - Un dizionario con chiavi rappresentanti gli step e valori tuple (S, I, R) dove S, I e R sono i set di nodi suscettibili, infetti e recuperati a ogni passo.
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
        R = {node for node, state in states.items() if state == "R"}

        dynamics[step] = (S, I, R)

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
                new_states[node] = "R"

        states = new_states

    return dynamics
