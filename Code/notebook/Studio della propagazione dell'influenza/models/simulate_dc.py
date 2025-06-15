import random


def simulate_dc(graph, initial_prob, decay_factor, steps, seed=None, prob_cutoff=1e-4):
    """
    Simula la diffusione deterministica e caotica su un grafo.

    Parametri:
        - graph: Il grafo (networkx.DiGraph o Graph) su cui eseguire la simulazione.
        - initial_prob: Probabilità iniziale di attivazione di un nodo.
        - decay_factor: Fattore di decadimento della probabilità a ogni passo.
        - steps: Numero di iterazioni della simulazione.
        - seed: Nodo iniziale da attivare (opzionale). Se None, viene scelto casualmente.
        - prob_cutoff: Soglia sotto la quale la probabilità è considerata trascurabile.

    Ritorna:
        - Un dizionario contenente l'insieme dei nodi attivati a ogni passo, con lo step come chiave.
    """
    seed = seed if seed is not None else random.choice(list(graph.nodes))
    activated = set(seed)

    prob = initial_prob
    evolution = {}
    evolution[0] = activated.copy()
    for step in range(1, steps + 1):
        if prob < prob_cutoff:
            break

        new_activated = activated.copy()
        for node in graph.nodes:
            if node not in activated:
                for neighbor in graph.neighbors(node):
                    if neighbor in activated and random.random() < prob:
                        new_activated.add(node)
                        break

        activated = new_activated
        evolution[step] = activated.copy()
        prob *= decay_factor

    return evolution
