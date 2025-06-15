import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
sys.setrecursionlimit(10000)
from utils.logger import setup_logger
from Code.notebook.graph.GraphConstructor import GraphConstructor
from utils.file_utils import save_results_to_file
import os
from utils.run_models import (
    run_models_on_different_seed_lengths,
    run_models_on_differnt_centralities,
    run_models_on_differnt_optimizer,
)
import random

random.seed(42)
from optimizers.optimizer import Optimizer
import logging

setup_logger()
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting the influence propagation analysis script.")

    run_models = False
    run_optimizers = False
    force_recalculate = False
    logger.info_centrality = False
    save_to_file = False
    save_fig = False
    steps = 100
    seed_lengths = [10, 50, 100, 200]

    logger.info(
        "Parameters set. Run models: %s, Run optimizers: %s",
        run_models,
        run_optimizers,
    )

    logger.info("Initializing GraphConstructor")
    gc = GraphConstructor()
    gc.build_graph()
    graph = gc.graph
    gc.log_graph_info()

    all_info = gc.get_all_graph_info(force_recalculate=force_recalculate)
    print("\nInformazioni complete sul grafo:")
    for key, value in all_info.items():
        if key == "Clustering per nodo":
            continue
        print(f"{key}: {value}")

    centralities = gc.get_centralities_info(force_recalculate=force_recalculate)
    print("\nCentralità calcolate:")
    for centrality_name, values in centralities.items():
        print(f"\n{centrality_name}:")

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
            output_dir = os.path.join(
                os.path.dirname(__file__), "output", "optimizer_output"
            )
            logger.info("Saving optimization results to directory: %s", output_dir)
            save_results_to_file(optimization_results, os.path.join(output_dir, "save"))
            logger.info("Results saved successfully.")

    logger.info("Script execution completed.")
