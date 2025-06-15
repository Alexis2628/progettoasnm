import random


def simulate_sirs(graph, beta, gamma, lambda_, steps, initial_infected=None):
    """
    Simula la diffusione dell'infezione utilizzando il modello SIRS (Susceptible-Infected-Recovered-Susceptible).

    Parametri:
        - graph: Il grafo (networkx.Graph o DiGraph) su cui eseguire la simulazione.
        - beta: Probabilità di trasmissione per ogni contatto infetto-suscettibile.
        - gamma: Probabilità di recupero di un nodo infetto a ogni passo.
        - lambda_: Probabilità di ritorno alla suscettibilità di un nodo recuperato.
        - steps: Numero massimo di iterazioni della simulazione.
        - initial_infected: Lista di nodi inizialmente infetti (opzionale). Se None, viene scelto un nodo casualmente.

    Ritorna:
        - Una lista di tuple (S, I, R) dove S, I e R sono i set di nodi suscettibili, infetti e recuperati a ogni passo.
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
            elif states[node] == "I":

                if random.random() < gamma:
                    new_states[node] = "R"
            elif states[node] == "R":

                if random.random() < lambda_:
                    new_states[node] = "S"

        states = new_states

    return dynamics
