import random


def friend_foe_dynamic_linear_threshold(graph, seed_nodes, trust_function):
    """
    Esegue il modello Friend-Foe Dynamic Linear Threshold per una rete.
    :param graph: Grafo con nodi e archi.
    :param seed_nodes: Nodi iniziali (seminal nodes) da cui parte la diffusione.
    :param trust_function: Funzione che calcola la fiducia tra due nodi.
    :return: Dizionario con i nodi attivati a ogni passo temporale.
    """
    activated = set(seed_nodes)
    propagation_steps = {0: set(seed_nodes)}
    step = 0

    while True:
        new_activations = set()

        for node in graph.nodes():
            if node not in activated:

                positive_influence = 0
                negative_influence = 0

                for neighbor in graph.neighbors(node):
                    influence = trust_function(neighbor, node)

                    if influence > 0:
                        positive_influence += influence
                    elif influence < 0:
                        negative_influence += -influence

                if (
                    positive_influence - negative_influence
                    >= graph.nodes[node]["threshold"]
                ):
                    new_activations.add(node)

        if not new_activations:
            break

        step += 1
        activated.update(new_activations)
        propagation_steps[step] = activated.copy()

    return propagation_steps
