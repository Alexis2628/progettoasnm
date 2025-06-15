import matplotlib.pyplot as plt
import os
import logging


class Plotter:

    def plot_model_results(self, model_results, output_dir, save=True):
        """Disegna l'evoluzione di un singolo set di risultati.

        Parameters
        ----------
        model_results : dict
            Mappatura step -> nodi attivi o tuple di stati.
        output_dir : str
            Cartella in cui salvare le figure.
        save : bool, optional
            Se ``True`` salva il grafico invece di mostrarlo.
        """
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

    def plot_all_results(
        self,
        all_results,
        seed_lengths,
        output_dir,
        use_centrality_labels=False,
        save=True,
    ):
        """Confronta i risultati per diversi seed length.

        Parameters
        ----------
        all_results : dict
            Dizionario lunghezza_seed -> risultati dei modelli.
        seed_lengths : iterable
            Valori di lunghezza dei seed analizzati.
        output_dir : str
            Cartella in cui salvare le figure.
        use_centrality_labels : bool, optional
            Se ``True`` usa etichette basate sulla centralità.
        save : bool, optional
            Se ``True`` salva le figure invece di mostrarle.
        """
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

                    label = (
                        f"Centrality: {seed_length}"
                        if use_centrality_labels
                        else f"Seed Length: {seed_length}"
                    )
                    plt.plot(steps, active_counts, marker="o", label=label)

                plt.title(f"{model_name} - Nodi attivi per step")
                plt.xlabel("Step")
                plt.ylabel("Numero di nodi attivi")
                plt.grid(True)
                plt.legend()
                if save:
                    plt.savefig(
                        os.path.join(
                            output_dir, f"{str.strip(model_name)}_comparative_plot.png"
                        )
                    )
                    plt.close()
                else:
                    plt.show()

    def plot_all_optimizer(self, all_results, output_dir, save=True):
        """Visualizza i risultati ottenuti con i diversi ottimizzatori.

        Parameters
        ----------
        all_results : dict
            Dizionario modello -> risultati per ottimizzatore.
        output_dir : str
            Cartella in cui salvare i grafici.
        save : bool, optional
            Se ``True`` salva le figure invece di mostrarle.
        """

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
