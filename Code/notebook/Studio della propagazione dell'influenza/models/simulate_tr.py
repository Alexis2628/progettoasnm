# """
# Simulazione con Threshold Reversibile
# Teoria: Nel modello Threshold Reversibile, i nodi hanno una soglia di attivazione che può essere influenzata da dinamiche reversibili. Una volta che un nodo diventa attivo, esso può tornare allo stato non attivo se una condizione reversibile è soddisfatta. Questo è simile a un modello SIS, ma con soglie specifiche per l'attivazione e la disattivazione.
# 1.	Dinamica: Un nodo attivo può diventare di nuovo non attivo se l'influenza ricevuta dai suoi vicini scende al di sotto della sua soglia.
# 2.	Reversibilità: I nodi non sono permanentemente attivi, ma possono passare avanti e indietro tra gli stati.
# Condizione:
# •	Un nodo ii è attivo se la somma dell'influenza dei vicini è maggiore della sua soglia θi\theta_i. Se la somma scende al di sotto di θi\theta_i, il nodo torna non attivo.
# Applicazioni:
# •	Comportamenti dinamici: Situazioni dove le persone o gli oggetti possono entrare e uscire dallo stato attivo, come l'adozione di comportamenti che possono essere abbandonati.
# •	Mercati finanziari: Comportamenti che oscillano tra l'attivo e il non attivo in risposta a cambiamenti nel contesto.
# Implementazione: Nel codice, simulate_tr implementa la dinamica reversibile, permettendo ai nodi di attivarsi o disattivarsi in base alla soglia e all'influenza ricevuta.
# """
import random
def simulate_tr(graph, steps, initial_active = None):
    """
    Simula la diffusione con il modello Threshold Reversibile.

    Parametri:
        - graph: Il grafo (networkx.Graph o DiGraph) su cui eseguire la simulazione.
                 Ogni nodo deve avere una proprietà 'threshold' con la soglia di attivazione/disattivazione.
        - steps: Numero massimo di iterazioni della simulazione.

    Ritorna:
        - Un dizionario {step: num_nodi_attivi} con il numero di nodi attivi a ogni passo temporale.
    """
    # Stato iniziale: tutti i nodi sono inattivi
    states = {node: False for node in graph.nodes}  # False = inattivo, True = attivo
    for node in initial_active:
        states[node] = True
    # Tracciamento della dinamica
    dynamics = {}

    for step in range(0,steps):
        new_states = states.copy()

        for node in graph.nodes:
            # Calcola la somma delle influenze dai vicini attivi
            active_neighbors = sum(1 for neighbor in graph.neighbors(node) if states[neighbor])
            influence = active_neighbors / max(1, len(list(graph.neighbors(node))))  # Usa i vicini
            # influence = active_neighbors / max(1, graph.degree[node])  # Normalizza per il grado


            # Regole di attivazione e disattivazione
            if not states[node] and influence >= graph.nodes[node]["threshold"]:
                new_states[node] = True  # Attivazione
            elif states[node] and influence < graph.nodes[node]["threshold"]:
                new_states[node] = False  # Disattivazione

        states = new_states
        active_nodes = {node for node, active in states.items() if active}
        dynamics[step] = active_nodes.copy() 

        # Interrompe se lo stato si stabilizza
        if step > 0 and dynamics[step] == dynamics[step - 1]:
            break

    return dynamics
