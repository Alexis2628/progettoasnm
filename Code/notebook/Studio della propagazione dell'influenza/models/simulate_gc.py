# """
# Simulazione con Cascata Stocastica - General Cascade Model)
# Teoria: Il modello General Cascade è un'estensione dei modelli di cascata, come il modello di soglia o il modello a cascata indipendente. In questo caso, l'attivazione di un nodo dipende da una probabilità di attivazione stocastica, che può essere influenzata da diversi fattori.
# 1.	Cascata: I nodi si attivano in base a probabilità calcolate stocasticamente, che sono influenzate sia dalle caratteristiche del nodo stesso che dai suoi vicini.
# 2.	Cascata Multipla: A differenza di un modello di cascata semplice, in un modello generale, più di un nodo può attivare un altro nodo simultaneamente.
# Dinamica:
# •	Ogni nodo ii ha una probabilità di attivarsi basata sull'influenza ricevuta dai suoi vicini, ma l'attivazione di ii è stocastica.
# •	A ogni passo, ogni nodo ha una probabilità di attivare i suoi vicini, creando una cascata di attivazioni.
# Applicazioni:
# •	Diffusione di innovazioni: L'adozione di nuovi prodotti o comportamenti che avviene in modo stocastico.
# •	Epidemie: La diffusione di malattie che può variare in base a variabili ambientali o comportamentali.
# Implementazione: Nel codice, la funzione simulate_gc tiene conto delle probabilità stocastiche, permettendo a un nodo di attivare i suoi vicini con probabilità variabili, innescando una cascata.
# """

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

    evolution = {}  # Traccia l'evoluzione dell'attivazione

    evolution[0] = activated.copy()
    for step in range(1,steps+1):
        new_activated = activated.copy()
        for node in graph.nodes:
            if node not in activated:
                for neighbor in graph.neighbors(node):
                    if neighbor in activated:
                        # Calcola la probabilità di attivazione
                        activation_prob = edge_probabilities.get((neighbor, node), prob) if edge_probabilities else prob
                        if random.random() < activation_prob:
                            new_activated.add(node)
                            break  # Passa al prossimo nodo
        if new_activated == activated:
            break  # Nessuna nuova attivazione, termina la simulazione
        activated = new_activated
        evolution[step] = activated.copy()

    return evolution

