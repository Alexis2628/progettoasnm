# """
# Simulazione con Diffusione Deterministica e Caotica)
# Teoria: Il modello Deterministic and Chaotic Diffusion (DC) unisce aspetti della diffusione deterministica e caotica, dove la diffusione segue leggi deterministiche in alcuni periodi, ma può diventare caotica in altre fasi. La transizione tra questi due stati dipende da vari fattori esterni e dalle interazioni tra i nodi.
# 1.	Determinismo: La diffusione segue regole precise basate sulla rete e le caratteristiche dei nodi.
# 2.	Caos: In altri momenti, la diffusione diventa imprevedibile e sensibile alle condizioni iniziali, producendo risultati caotici.
# Dinamica:
# •	In una fase, la diffusione può seguire un modello di cascata o soglia deterministico, ma successivamente può entrare in una fase caotica, dove l'attivazione di un nodo dipende in modo non lineare da vari fattori.
# Applicazioni:
# •	Comportamenti complessi: Quando il comportamento di una popolazione o sistema sociale diventa imprevedibile a causa di influenze non lineari.
# •	Sistema economici: Mercati o sistemi economici che alternano fasi stabili e caotiche.
# Implementazione: Nel codice, simulate_dc modella la transizione tra una diffusione deterministica (basata su probabilità e soglie) e una caotica (dove le dinamiche diventano imprevedibili).
# """


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
    evolution = {}  # Traccia l'evoluzione dell'attivazione
    evolution[0] = activated.copy()
    for step in range(1,steps+1):
        if prob < prob_cutoff:  # Interrompi se la probabilità è troppo bassa
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
        prob *= decay_factor  # Decay della probabilità

    return evolution
