# """
# Dinamicità amico-nemico con soglia lineare)
# Teoria: Nel modello Friend-Foe Dynamic Linear Threshold, la rete viene suddivisa in due categorie principali: amici e nemici. Ogni nodo ha una soglia e viene influenzato dai suoi vicini, che possono essere amici (che rinforzano il comportamento) o nemici (che contrastano l'influenza).
# 1.	Amici: I vicini amici aumentano la probabilità che un nodo si attivi o adotti un comportamento.
# 2.	Nemici: I vicini nemici riducono la probabilità di attivazione.
# Dinamica: Ogni nodo ha una soglia e viene influenzato in modo diverso da amici e nemici. Un nodo si attiva solo se l'influenza netta (amici - nemici) supera una soglia prestabilita.
# Equazione:
# •	La somma delle influenze dei vicini amichevoli e nemici deve superare la soglia per l'attivazione: ∑j∈amiciwij−∑k∈nemiciwik>θi\sum_{j \in \text{amici}} w_{ij} - \sum_{k \in \text{nemici}} w_{ik} > \theta_i
# Applicazioni:
# •	Dinamiche sociali: Influenze positive (amici) e negative (nemici) che determinano se un comportamento o una tendenza si diffonde.
# •	Politiche: Come le opinioni politiche o ideologiche si diffondono tra alleati e oppositori.
# Implementazione: La funzione friend_foe_dynamic_linear_threshold implementa una rete di influenze in cui gli amici rinforzano l'influenza e i nemici la indeboliscono, determinando l'attivazione in base alla soglia lineare.
# """

import random

def friend_foe_dynamic_linear_threshold(graph, seed_nodes, trust_function):
    """
    Esegue il modello Friend-Foe Dynamic Linear Threshold per una rete.
    :param graph: Grafo con nodi e archi.
    :param seed_nodes: Nodi iniziali (seminal nodes) da cui parte la diffusione.
    :param trust_function: Funzione che calcola la fiducia tra due nodi.
    :return: Dizionario con i nodi attivati a ogni passo temporale.
    """
    activated = set(seed_nodes)  # I nodi iniziali che sono attivi.
    propagation_steps = {0: set(seed_nodes)}  # Per salvare i nodi attivati in ogni passo
    step = 0

    while True:
        new_activations = set()
        
        # Per ogni nodo non ancora attivo
        for node in graph.nodes():
            if node not in activated:
                # Somma delle influenze positive (amici) e negative (nemici)
                positive_influence = 0
                negative_influence = 0
                
                # Calcolare l'influenza da parte degli amici e nemici
                for neighbor in graph.neighbors(node):
                    influence = trust_function(neighbor, node)
                    
                    if influence > 0:
                        positive_influence += influence
                    elif influence < 0:
                        negative_influence += -influence  # Negativo per nemici

                # Se l'influenza netta supera la soglia del nodo, attiva il nodo
                if positive_influence - negative_influence >= graph.nodes[node]["threshold"]:
                    new_activations.add(node)

        # Se non ci sono nuove attivazioni, il processo è terminato
        if not new_activations:
            break

        step += 1
        activated.update(new_activations)
        propagation_steps[step] = activated.copy()  # Salva i nuovi attivati

    return propagation_steps
