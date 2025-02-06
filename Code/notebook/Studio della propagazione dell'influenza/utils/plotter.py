import matplotlib.pyplot as plt
import os
import logging

class Plotter:

    def plot_model_results(self, model_results,output_dir, save = True):
        output_dir = os.path.join(output_dir, "figure")
        os.makedirs(output_dir, exist_ok=True)
        for model_name, result in model_results.items():
            logging.info(f"Salvataggio figura : {model_name}")
            steps = list(result.keys())
            active_counts = []
            for step in steps:
                if isinstance(result[step], tuple):
                    _, I, _ = result[step]
                    active_counts.append(len(I))
                else:
                    active_counts.append(len(result[step]))
            # active_counts = [len(result[step]) for step in steps]
            plt.figure()
            plt.plot(steps, active_counts, marker="o", label=model_name)
            plt.title(f"{model_name} - Nodi attivi per step")
            plt.xlabel("Step")
            plt.ylabel("Numero di nodi attivi")
            plt.grid(True)
            plt.legend()
            if save:
                plt.savefig(os.path.join(output_dir, f"{model_name}_plot.png"))
                plt.close()
            else:
                plt.show()

    def plot_all_results(self, all_results, seed_lengths, output_dir,use_centrality_labels=False, save = True):
        output_dir = os.path.join(output_dir, "figure")
        os.makedirs(output_dir, exist_ok=True)
        for seed_length, model_results in all_results.items():
            for model_name in next(iter(all_results.values())).keys():
                plt.figure(figsize=(10, 6))
                for seed_length in seed_lengths:
                    result = all_results[seed_length][model_name]
                    steps = list(result.keys())
                    active_counts = []

                    for step in steps:
                        if isinstance(result[step], tuple):
                            _, I, _ = result[step]
                            active_counts.append(len(I))
                        else:
                            active_counts.append(len(result[step]))

                    # Cambia l'etichetta in base al flag
                    label = f"Centrality: {seed_length}" if use_centrality_labels else f"Seed Length: {seed_length}"
                    plt.plot(steps, active_counts, marker="o", label=label)

                plt.title(f"{model_name} - Nodi attivi per step")
                plt.xlabel("Step")
                plt.ylabel("Numero di nodi attivi")
                plt.grid(True)
                plt.legend()
                if save:
                    plt.savefig(os.path.join(output_dir, f"{model_name}_comparative_plot.png"))
                    plt.close()
                else:
                    plt.show()

    def plot_all_optimizer(self, all_results, output_dir,save = True):
        # Risultato finale
        output_dir = os.path.join(output_dir, "figure")
        os.makedirs(output_dir, exist_ok=True)
        for modello, metodi in all_results.items():
            plt.figure(figsize=(10, 6))
            for model_name, result in metodi.items():
                steps = list(result.keys())
                active_counts = []
                for step in steps:
                    if isinstance(result[step], tuple):
                        _, I, _ = result[step]
                        active_counts.append(len(I))
                    else:
                        active_counts.append(len(result[step]))
                plt.plot(steps, active_counts, marker="o", label=model_name)
            plt.title(f"{modello} - Nodi attivi per step")
            plt.xlabel("Step")
            plt.ylabel("Numero di nodi attivi")
            plt.grid(True)
            plt.legend()
            if save:
                plt.savefig(os.path.join(output_dir, f"{modello}_comparative_plot.png"))
                plt.close()
            else:
                plt.show()