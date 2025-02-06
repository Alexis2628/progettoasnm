import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from utils.logger import setup_logger
from Code.notebook.graph.GraphConstructor import GraphConstructor
from utils.plotter import Plotter
from utils.file_utils import save_results_to_file, convert_sets_in_dict
import os
from utils.run_models import (
    run_models_on_different_seed_lengths,
    run_models_on_differnt_centralities,
    run_models_on_differnt_optimizer,
)
import random

random.seed(42)
from models.models import Models
from optimizers.optimizer import Optimizer
import logging

setup_logger()
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting the influence propagation analysis script.")

    # Parameters
    run_models = False
    run_optimizers = False
    logger.info_centrality = True
    save_to_file = False
    save_fig = False
    steps = 100
    seed_lengths = [10, 50, 100, 200]  # Various seed_node lengths

    logger.info(
        "Parameters set. Run models: S%s, Run optimizers: %s",
        run_models,
        run_optimizers,
    )

    logger.info("Initializing GraphConstructor")
    gc = GraphConstructor(
        # followers_path="Code/data_extraction/followers_dataset_combined.csv",
        # data_path="Code/data_extraction/data.csv",
        info_filepath="graph_info.json",
        centralities_filepath="centralities_info.json",
    )
    gc.build_graph()
    graph = gc.graph
    gc.log_graph_info()

    # Ottieni e stampa le informazioni complete sul grafo
    all_info = gc.get_all_graph_info()
    print("\nInformazioni complete sul grafo:")
    for key, value in all_info.items():
        print(f"{key}: {value}")

    # Ottieni e stampa le centralità
    centralities = gc.get_centralities_info()
    print("\nCentralità calcolate:")
    for centrality_name, values in centralities.items():
        print(f"\n{centrality_name}:")
        # Visualizza i primi 5 nodi in base al valore della centralità
        sorted_values = sorted(values.items(), key=lambda x: x[1], reverse=True)[:5]
        for node, score in sorted_values:
            print(f"  Nodo {node}: {score:.4f}")

    if run_models:
        logger.info("Running models on different centralities...")
        run_models_on_differnt_centralities(
            centralities, gc, save_to_file, save_fig, 100, steps
        )

        logger.info("Sorting top influencers by Katz Centrality...")
        top_influencers = sorted(
            centralities["Katz Centrality"].items(), key=lambda x: x[1], reverse=True
        )

        logger.info("Running models on different seed lengths...")
        run_models_on_different_seed_lengths(
            gc, top_influencers, save_to_file, save_fig, steps, seed_lengths
        )

    if run_optimizers:
        logger.info("Running optimizers...")
        optimizer = Optimizer(graph)
        optimization_results = optimizer.run_all(
            k=10, p=0.1, path_limit=3, threshold=0.5, rr_sets=100
        )
        logger.info("Optimization completed successfully.")
        run_models_on_differnt_optimizer(optimization_results, gc, save_fig, steps)
        if save_to_file:
            output_dir = r"Code\notebook\Studio della propagazione dell'influenza\output/optimizer_output"
            logger.info("Saving optimization results to directory: %s", output_dir)
            save_results_to_file(optimization_results, os.path.join(output_dir, "save"))
            logger.info("Results saved successfully.")

    logger.info("Script execution completed.")
