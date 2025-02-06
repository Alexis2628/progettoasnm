# """
# Modello di Soglia Lineare (Linear Threshold Model)
# Teoria: Il modello di soglia lineare è un modello di diffusione in cui i nodi di una rete (individui) sono soggetti a un meccanismo di attivazione basato su una soglia di influenza. Ogni nodo ha una soglia probabilistica che rappresenta la quantità minima di influenza che deve ricevere dai suoi vicini per attivarsi. Ogni arco (connessione) tra due nodi ha un peso che rappresenta l'intensità dell'influenza che un nodo esercita sull'altro. Quando la somma delle influenze dai vicini supera la soglia di attivazione di un nodo, esso diventa attivo.
# 1.	Soglia casuale: Ogni nodo ha una soglia generata casualmente (compresa tra 0 e 1).
# 2.	Attivazione: Un nodo diventa attivo se la somma delle influenze (ovvero, il peso degli archi dai vicini attivi) supera la sua soglia.
# 3.	Propagazione: Una volta che un nodo diventa attivo, influenza i suoi vicini, i quali potrebbero a loro volta superare la loro soglia di attivazione.
# Formula: La soglia θi\theta_i per ogni nodo ii è generata casualmente tra 0 e 1. Un nodo ii diventa attivo se:
# ∑j∈N(i)wijxj≥θi\sum_{j \in N(i)} w_{ij} x_j \geq \theta_i
# Dove:
# •	N(i)N(i) è l'insieme dei vicini del nodo ii,
# •	wijw_{ij} è il peso dell'arco che collega il nodo jj con ii,
# •	xjx_j è lo stato del nodo jj (1 se attivo, 0 altrimenti),
# •	θi\theta_i è la soglia di attivazione del nodo ii.
# Applicazioni:
# •	Marketing virale: Diffusione di un prodotto o messaggio attraverso una rete sociale.
# •	Norme sociali: L'adozione di un comportamento da parte di una persona dipende dalle persone intorno a lei che l'hanno già adottato.
# •	Diffusione di idee: Le idee si diffondono in modo simile a una catena, in cui ogni individuo può influenzare quelli che lo circondano.
# Implementazione: Nel codice, l'attivazione di un nodo dipende dall'influenza ricevuta dai suoi vicini. Ogni nodo ha una soglia casuale, e la propagazione continua finché ci sono nodi che possono essere attivati.
# """

import random
def linear_threshold_model(graph, seed_nodes):
    activated = set(seed_nodes)
    newly_activated = set(seed_nodes)
    
    # Assegna l'influenza agli archi
    for node in graph.nodes():
        neighbors = list(graph.successors(node))
        if neighbors:
            weight = 1 / len(neighbors)
            for neighbor in neighbors:
                graph.edges[node, neighbor]["influence"] = weight

    propagation_steps = {0: set(seed_nodes)}  # Salva i risultati per step
    step = 0

    while newly_activated:
        next_activated = set()
        for node in graph.nodes():
            if node not in activated:
                total_influence = sum(
                    graph.edges[neighbor, node]["influence"]
                    for neighbor in graph.predecessors(node)
                    if neighbor in activated
                )
                if total_influence >= graph.nodes[node]["threshold"]:
                    next_activated.add(node)

        newly_activated = next_activated
        step += 1
        activated.update(newly_activated)
        propagation_steps[step] = activated.copy()

    return propagation_steps