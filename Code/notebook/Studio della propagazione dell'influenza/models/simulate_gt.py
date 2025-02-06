# """
# Simulazione con Threshold - Greater-Than Model)
# Teoria: Il Greater-Than (GT) Model è un tipo di modello di diffusione basato su soglie in cui un nodo diventa attivo o infetto se la somma delle influenze che riceve dai suoi vicini supera una certa soglia predefinita. La "Greater-Than" fa riferimento alla condizione in cui un nodo diventa attivo solo quando l'influenza combinata dei suoi vicini supera un valore specificato.
# 1.	Dinamica: Ogni nodo ha una soglia e una probabilità associata. Se la somma delle probabilità di attivazione dei suoi vicini supera la soglia, il nodo si attiva.
# 2.	Condizione: Un nodo ii diventa attivo se: ∑j∈N(i)pij>θi\sum_{j \in N(i)} p_{ij} > \theta_i Dove pijp_{ij} è la probabilità che il nodo jj attivi il nodo ii, e θi\theta_i è la soglia di attivazione di ii.
# Applicazioni:
# •	Comportamenti collettivi: Come l'adozione di una nuova tecnologia o comportamento.
# •	Infezioni virali: Il contagio si verifica solo quando un nodo supera una certa "soglia" di esposizione.
# Implementazione: Nel codice, la funzione simulate_gt simula la diffusione in una rete, dove ogni nodo ha una soglia e si attiva quando la somma delle probabilità degli archi che lo connettono supera questa soglia.
# """

import random


def simulate_gt(graph, steps, seed=None):
    """
    Simula la diffusione con il modello Greater-Than (GT) su un grafo.

    Parametri:
        - graph: Il grafo (networkx.DiGraph o Graph) su cui eseguire la simulazione.
                 Ogni nodo deve avere una proprietà 'threshold' con la soglia di attivazione.
        - steps: Numero massimo di iterazioni della simulazione.
        - seed: Nodo iniziale da attivare (opzionale). Se None, viene scelto casualmente.

    Ritorna:
        - Un dizionario {step: num_nodi_attivi} con il numero di nodi attivati a ogni passo temporale.
    """
    
    
   
    # Inizializza l'insieme dei nodi attivati
    seed = seed if seed is not None else random.choice(list(graph.nodes))
    activated = set(seed)

    evolution = {}  # Traccia l'evoluzione dell'attivazione
    evolution[0] = activated.copy()
    
    for step in range(1,steps+1):
        new_activated = activated.copy()
        for node in graph.nodes:
            if node not in activated:
                # Calcola la somma pesata delle influenze dei vicini attivi
                influence = sum(
                    1 for neighbor in graph.neighbors(node) if neighbor in activated
                ) / graph.degree[node] if graph.degree[node] > 0 else 0

                # Confronta con la soglia del nodo
                if influence >= graph.nodes[node]["threshold"]:
                    new_activated.add(node)

        # Registra il numero di nodi attivi
        evolution[step] = new_activated.copy()

        # Interrompi se non ci sono nuove attivazioni
        if new_activated == activated:
            break

        activated = new_activated

    return evolution

