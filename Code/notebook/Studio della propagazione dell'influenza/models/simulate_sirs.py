# """
# Modello SIRS (Susceptible-Infected-Recovered-Susceptible)
# Teoria: Il modello SIRS è una variante del modello SIR che considera che la guarigione non conferisce un'immunità permanente. Gli individui che si sono ripresi dalla malattia possono tornare suscettibili dopo un certo periodo.
# Dinamiche:
# •	Gli individui Recuperati (R) tornano a essere Suscettibili (S) con una probabilità λ\lambda, rappresentando il decadimento dell'immunità.
# Equazioni:
# •	Le dinamiche del modello SIRS sono rappresentate da: dSdt=−β⋅S⋅I+λ⋅R\frac{dS}{dt} = -\beta \cdot S \cdot I + \lambda \cdot R dIdt=β⋅S⋅I−γ⋅I\frac{dI}{dt} = \beta \cdot S \cdot I - \gamma \cdot I dRdt=γ⋅I−λ⋅R\frac{dR}{dt} = \gamma \cdot I - \lambda \cdot R
# Applicazioni:
# •	Malattie con immunità temporanea: Ad esempio, infezioni dove una persona può tornare suscettibile dopo un po' di tempo (come alcune malattie stagionali).
# Implementazione: Nel codice, il nodo infetto può diventare recuperato, e dopo un po', può tornare suscettibile, creando una dinamica ciclica.
# """

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
        R = {node for node, state in states.items() if state == "R"}
        
        dynamics[step]= (S, I, R)

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
            elif states[node] == "I":
                # Transizione I -> R
                if random.random() < gamma:
                    new_states[node] = "R"
            elif states[node] == "R":
                # Transizione R -> S
                if random.random() < lambda_:
                    new_states[node] = "S"
        
        states = new_states

    return dynamics

