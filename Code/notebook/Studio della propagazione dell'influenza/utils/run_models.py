from models.models import Models
from utils.file_utils import save_results_to_file, convert_sets_in_dict
from utils.plotter import Plotter
import os

def run_models_on_different_seed_lengths(
    graph_builder,
    top_influencers,
    save_to_file,
    save_fig,
    steps,
    seed_lengths,
    output="model",
):
    """Esegue i modelli variando il numero di seed iniziali.

    Parameters
    ----------
    graph_builder : GraphConstructor
        Oggetto che contiene il grafo.
    top_influencers : list
        Lista ordinata di nodi con maggiore influenza.
    save_to_file : bool
        Se ``True`` salva i risultati su disco.
    save_fig : bool
        Se ``True`` salva i grafici generati.
    steps : int
        Numero di passi di simulazione.
    seed_lengths : iterable
        Diverse quantità di nodi seed da testare.
    output : str, optional
        Sottocartella di output.
    """
    graph = graph_builder.graph
    all_results = {}
    output_dir = os.path.join(
        os.path.dirname(__file__), "..", "output", output
    )
    for seed_length in seed_lengths:
        seed_nodes = [node for node, _ in top_influencers[:seed_length]]
    # Esecuzione dei modelli
        models = Models(graph)
        model_results = models.run_all(
            seed_nodes=seed_nodes,
            p=0.4,
            beta=0.3,
            gamma=0.03,
            lambda_=0.1,
            steps=steps,
            prob=0.4,
            initial_prob=0.1,
            decay_factor=0.95,
            trust_function=graph_builder.trust_function,
        )
        all_results[seed_length] = model_results
        if save_to_file:
            save_results_to_file(
                model_results, os.path.join(output_dir, "save", f"steps_{seed_length}")
            )
    if save_fig:
        plotter = Plotter()
        plotter.plot_all_results(
            all_results,
            seed_lengths,
            os.path.join(output_dir, "plot_comparative_seed_length"),
        )


def run_models_on_differnt_centralities(
    centralities,
    graph_builder,
    save_to_file,
    save_fig,
    seed_length,
    steps,
    output="model",
):
    """Esegue i modelli scegliendo i seed in base alle centralità.

    Parameters
    ----------
    centralities : dict
        Dizionario nome_centralità -> valori per nodo.
    graph_builder : GraphConstructor
        Oggetto contenente il grafo.
    save_to_file : bool
        Se ``True`` salva i risultati su disco.
    save_fig : bool
        Se ``True`` produce i grafici.
    seed_length : int
        Numero di nodi seed per ciascuna centralità.
    steps : int
        Numero di passi di simulazione.
    output : str, optional
        Sottocartella di output.
    """
    centrality_metrics = ["Degree Centrality", "Closeness Centrality", "Betweenness Centrality",
                          "PageRank", "Katz Centrality","Eigenvector Centrality","HITS Hub Scores","HITS Authority Scores"]
    graph = graph_builder.graph
    seed_nodes_by_centrality = {}
    output_dir = os.path.join(
        os.path.dirname(__file__), "..", "output", output
    )
    for metric in centrality_metrics:
        sorted_nodes = sorted(centralities[metric].items(), key=lambda x: x[1], reverse=True)
        seed_nodes_by_centrality[metric] = [node for node, _ in sorted_nodes[:seed_length]]
        all_results_by_centrality = {}
        for metric, seed_nodes in seed_nodes_by_centrality.items():
            # Esecuzione dei modelli
            models = Models(graph)
            model_results = models.run_all(
                seed_nodes=seed_nodes,
                p=0.4,
                beta=0.3,
                gamma=0.03,
                lambda_=0.1,
                steps=steps,
                prob=0.4,
                initial_prob=0.1,
                decay_factor=0.95,
                trust_function=graph_builder.trust_function,
            )
            all_results_by_centrality[metric] = model_results

        if save_to_file:
            save_results_to_file(
                model_results, os.path.join(output_dir, "save", f"{metric}_steps_{seed_length}")
            )

    if save_fig:
        plotter = Plotter()
        plotter.plot_all_results(
            all_results_by_centrality,
            centrality_metrics,
            os.path.join(output_dir, "plot_centrality_comparison"),
            use_centrality_labels=True,
        )

def run_models_on_differnt_optimizer(
    optimization_results,
    graph_builder,
    save_fig,
    steps,
):
    """Esegue i modelli utilizzando i seed ottenuti dagli ottimizzatori.

    Parameters
    ----------
    optimization_results : dict
        Mappatura nome_ottimizzatore -> nodi seed scelti.
    graph_builder : GraphConstructor
        Oggetto contenente il grafo.
    save_fig : bool
        Se ``True`` genera i grafici comparativi.
    steps : int
        Numero di passi di simulazione.
    """
    optmizer_methods = ["Greedy", "CELF", "CELF++","Stop-And-Go", 
                          "Static","SIMPATH","LDAG","IRIE",
                          "PMC","TIM+","EaSyIM","Sketching","Singles"]
    graph = graph_builder.graph
 
    all_res = {}
    output_dir = os.path.join(
        os.path.dirname(__file__), "..", "output", "optimizer_output"
    )
    for method in optmizer_methods:
        seed_nodes = list(optimization_results[method])
        all_results_by_centrality = {}
        print(f"Running model for optimizer {method}")
        models = Models(graph)
        model_results = models.run_all(
                seed_nodes=seed_nodes,
                p=0.4,
                beta=0.3,
                gamma=0.03,
                lambda_=0.1,
                steps=steps,
                prob=0.4,
                initial_prob=0.1,
                decay_factor=0.95,
                trust_function=graph_builder.trust_function,
        )
        all_res[method] = model_results

    dizionario_invertito = {}
    for metodo, modelli in all_res.items():
        for modello, steps in modelli.items():
            if modello not in dizionario_invertito:
                dizionario_invertito[modello] = {}
            dizionario_invertito[modello][metodo] = steps

    if save_fig:
        plotter = Plotter()
        plotter.plot_all_optimizer(
            dizionario_invertito,
            os.path.join(output_dir, "plot_optimizer_comparison"),
            save=True,
        )
