from models.models import Models
from utils.file_utils import save_results_to_file, convert_sets_in_dict
from utils.plotter import Plotter
import os

def run_models_on_different_seed_lengths(graph_builder,top_influencers,save_to_file,save_fig,steps,seed_lengths, output= "model"):
    graph = graph_builder.graph
    all_results = {}
    output_dir = r"Code\notebook\Studio della propagazione dell'influenza\output/"+output
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
            save_results_to_file(model_results, os.path.join(output_dir+"/save", f"steps_{seed_length}"))
    if save_fig:
        plotter = Plotter()
        plotter.plot_all_results(all_results, seed_lengths,output_dir+"/plot_comparative_seed_length")


def run_models_on_differnt_centralities(centralities, graph_builder, save_to_file, save_fig,seed_length,steps, output= "model"):
    centrality_metrics = ["Degree Centrality", "Closeness Centrality", "Betweenness Centrality",
                          "PageRank", "Katz Centrality","Eigenvector Centrality","HITS Hub Scores","HITS Authority Scores"]
    graph = graph_builder.graph
    seed_nodes_by_centrality = {}
    output_dir = r"Code\notebook\Studio della propagazione dell'influenza\output/"+output
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
            save_results_to_file(model_results, os.path.join(output_dir + "/save", f"{metric}_steps_{seed_length}"))

    if save_fig:
        plotter = Plotter()
        plotter.plot_all_results(all_results_by_centrality, centrality_metrics,output_dir + "/plot_centrality_comparison",use_centrality_labels=True)

def run_models_on_differnt_optimizer(optimization_results, graph_builder, save_fig,steps):
    optmizer_methods = ["Greedy", "CELF", "CELF++","Stop-And-Go", 
                          "Static","SIMPATH","LDAG","IRIE",
                          "PMC","TIM+","EaSyIM","Sketching","Singles"]
    graph = graph_builder.graph
 
    all_res = {}
    output_dir = r"Code\notebook\Studio della propagazione dell'influenza\output/optimizer_output"
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
        plotter.plot_all_optimizer(dizionario_invertito, output_dir + "/plot_optimizer_comparison",save = True)