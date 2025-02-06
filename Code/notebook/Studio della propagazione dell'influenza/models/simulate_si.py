# """
# Simulazione SI - Susceptible-Infected)
# Teoria: Il modello SI (Susceptible-Infected) è una versione semplificata dei modelli epidemiologici, che si concentra solo sulla diffusione di una malattia o comportamento da "suscettibili" a "infetti", senza considerare la fase di recupero. È utile per descrivere situazioni in cui un individuo, una volta infetto, non può mai recuperare o tornare suscettibile (come nel caso di una malattia permanente).
# 1.	Suscettibili (S): Gli individui sono vulnerabili all'infezione e possono diventare infetti.
# 2.	Infetti (I): Gli individui infetti possono trasmettere l'infezione ad altri suscettibili.
# 3.	Dinamica: Gli individui infetti contagiano i suscettibili con una probabilità β\beta.
# La dinamica dell'infezione è modellata con una probabilità β\beta che descrive il rischio che un suscettibile venga infettato da un vicino infetto. Una volta infetti, i nodi non tornano suscettibili, ma continuano a diffondere l'infezione.
# Equazione:
# •	La probabilità di infettare un vicino suscettibile SS da un infetto II è descritta da: dSdt=−β⋅S⋅I\frac{dS}{dt} = -\beta \cdot S \cdot I dIdt=β⋅S⋅I\frac{dI}{dt} = \beta \cdot S \cdot I
# Applicazioni: Questo modello è utilizzato quando non si vuole considerare la fase di recupero, come ad esempio in alcune epidemie acute (es. HIV, dove una volta che una persona è infetta non diventa mai suscettibile).
# Implementazione: Nel codice, la funzione simulate_si modella il flusso da "suscettibile" a "infetto" nei nodi di una rete. I nodi iniziano come suscettibili e diventano infetti quando interagiscono con nodi infetti, con una probabilità β\beta.
# """

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
    # Inizializzazione degli stati dei nodi
    states = {node: "S" for node in graph.nodes}

    # Definizione dei nodi inizialmente infetti
    if initial_infected is None:
        initial_infected = [random.choice(list(graph.nodes))]
    for node in initial_infected:
        states[node] = "I"

    # Tracciamento dell'evoluzione temporale
    evolution = {}
    evolution[0] = initial_infected.copy()
    for step in range(1,steps+1):
        new_states = states.copy()
        new_infected = set()

        for node in graph.nodes:
            if states[node] == "S":
                # Verifica i vicini infetti
                for neighbor in graph.neighbors(node):
                    if states[neighbor] == "I" and random.random() < beta:
                        new_states[node] = "I"
                        new_infected.add(node)
                        break

        if not new_infected:
            break  # Interrompi se non ci sono nuove infezioni

        states = new_states
        evolution[step] = {node for node, state in states.items() if state == "I"}

    return evolution
