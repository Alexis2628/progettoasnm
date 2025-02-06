# """
# Modello SIS (Susceptible-Infected-Susceptible)
# Teoria: Il modello SIS è una variazione del modello SIR, ma non esiste uno stato recuperato permanente. Gli individui che si guariscono tornano suscettibili e possono essere nuovamente infettati. Questo modello è adatto per malattie che non conferiscono immunità permanente.
# Dinamiche:
# •	Gli individui Suscettibili (S) possono diventare Infetti (I) se vengono esposti a un vicino infetto.
# •	Gli individui Infetti (I) possono tornare Suscettibili (S) dopo essersi "recuperati" (senza immunità permanente).
# Equazioni:
# •	Le dinamiche del modello SIS sono descritte dalle seguenti equazioni differenziali: dSdt=−β⋅S⋅I+γ⋅I\frac{dS}{dt} = -\beta \cdot S \cdot I + \gamma \cdot I dIdt=β⋅S⋅I−γ⋅I\frac{dI}{dt} = \beta \cdot S \cdot I - \gamma \cdot I
# Applicazioni:
# •	Malattie infettive senza immunità: Infezioni come l'influenza, dove l'immunità dura solo per un periodo limitato.
# •	Comportamenti ad alta diffusione: Comportamenti sociali che tornano frequentemente a diffondersi in una rete, come tendenze di moda.
# Implementazione: Nel codice, i nodi passano dallo stato infetto a suscettibile e viceversa, creando una dinamica continua di attivazione e guarigione.
# """

import random

def simulate_sis(graph, beta, gamma, steps, initial_infected=None):
    """
    Simula la diffusione dell'infezione utilizzando il modello SIS (Susceptible-Infected-Susceptible).

    Parametri:
        - graph: Il grafo (networkx.Graph o DiGraph) su cui eseguire la simulazione.
        - beta: Probabilità di trasmissione per ogni contatto infetto-suscettibile.
        - gamma: Probabilità di recupero di un nodo infetto a ogni passo.
        - steps: Numero massimo di iterazioni della simulazione.
        - initial_infected: Lista di nodi inizialmente infetti (opzionale). Se None, viene scelto un nodo casualmente.

    Ritorna:
        - Una lista di tuple (S, I) dove S e I sono i set di nodi suscettibili e infetti a ogni passo.
    """
    # Inizializzazione degli stati dei nodi
    states = {node: "S" for node in graph.nodes}
    
    # Configurazione dei nodi inizialmente infetti
    if initial_infected is None:
        initial_infected = [random.choice(list(graph.nodes))]
    for node in initial_infected:
        states[node] = "I"

    # Tracciamento della dinamica
    dynamics = {}

    for step in range(0,steps):
        # Conta i nodi in ciascun stato
        S = {node for node, state in states.items() if state == "S"}
        I = {node for node, state in states.items() if state == "I"}
        
        dynamics[step] = (S, I, None)

        # Se non ci sono più infetti, termina la simulazione
        if not I:
            break

        # Aggiorna gli stati dei nodi
        new_states = states.copy()
        for node in graph.nodes:
            if states[node] == "S":
                # Transizione S -> I
                for neighbor in graph.neighbors(node):
                    if states[neighbor] == "I" and random.random() < beta:
                        new_states[node] = "I"
                        break
            elif states[node] == "I" and random.random() < gamma:
                # Transizione I -> S
                new_states[node] = "S"
        
        states = new_states

    return dynamics
