from .greedy import greedy
from .celf import celf
from .celf_plus import celf_plus
from .stop_and_go import stop_and_go
from .static import static
from .simpath import simpath
from .ldag import ldag
from .irie import irie
from .pmc import pmc
from .tim_plus import tim_plus
from .easyim import easyim
from .sketching import sketching
from .singles import singles
import logging

# Configure root logger (this can be moved to your main entry point)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


class Optimizer:
    def __init__(self, graph):
        """
        Costruttore della classe Optimizer.
        :param graph: Il grafo su cui eseguire gli algoritmi di ottimizzazione.
        """
        self.graph = graph

    def run_greedy(self, k, p=0.1):
        """Esegue l'algoritmo Greedy."""
        return greedy(self.graph, k, p)

    def run_celf(self, k, p=0.1):
        """Esegue l'algoritmo CELF."""
        return celf(self.graph, k, p)

    def run_celf_plus(self, k, p=0.1):
        """Esegue l'algoritmo CELF++."""
        return celf_plus(self.graph, k, p)

    def run_stop_and_go(self, k, p=0.1):
        """Esegue l'algoritmo Stop-And-Go."""
        return stop_and_go(self.graph, k, p)

    def run_static(self, k, p=0.1):
        """Esegue l'algoritmo Static."""
        return static(self.graph, k, p)

    def run_simpath(self, k, p=0.1, path_limit=3):
        """Esegue l'algoritmo SIMPATH."""
        return simpath(self.graph, k, p, path_limit)

    def run_ldag(self, k, p=0.1, threshold=0.5):
        """Esegue l'algoritmo LDAG."""
        return ldag(self.graph, k, p, threshold)

    def run_irie(self, k, p=0.1):
        """Esegue l'algoritmo IRIE."""
        return irie(self.graph, k, p)

    def run_pmc(self, k, p=0.1):
        """Esegue l'algoritmo PMC."""
        return pmc(self.graph, k, p)

    def run_tim_plus(self, k, p=0.1, rr_sets=100):
        """Esegue l'algoritmo TIM+."""
        return tim_plus(self.graph, k, p, rr_sets)

    def run_easyim(self, k, p=0.1):
        """Esegue l'algoritmo EaSyIM."""
        return easyim(self.graph, k, p)

    def run_sketching(self, k, p=0.1):
        """Esegue l'algoritmo Sketching."""
        return sketching(self.graph, k, p)

    def run_singles(self, k, p=0.1):
        """Esegue l'algoritmo Singles."""
        return singles(self.graph, k, p)

    def run_all(self, k, p=0.1, **kwargs):
        """
        Esegue tutti gli algoritmi di ottimizzazione disponibili.
        :param k: Numero di nodi da selezionare.
        :param p: Probabilità utilizzata per i modelli stocastici.
        :param kwargs: Argomenti opzionali specifici per alcuni algoritmi (e.g., path_limit, threshold).
        :return: Dizionario con i risultati di tutti gli algoritmi.
        """
        results = {}
        algos = [
            ("Greedy", self.run_greedy, {}),
            ("CELF", self.run_celf, {}),
            ("CELF++", self.run_celf_plus, {}),
            ("Stop-And-Go", self.run_stop_and_go, {}),
            ("Static", self.run_static, {}),
            ("SIMPATH", self.run_simpath, {"path_limit": kwargs.get("path_limit", 3)}),
            ("LDAG", self.run_ldag, {"threshold": kwargs.get("threshold", 0.5)}),
            ("IRIE", self.run_irie, {}),
            ("PMC", self.run_pmc, {}),
            ("TIM+", self.run_tim_plus, {"rr_sets": kwargs.get("rr_sets", 100)}),
            ("EaSyIM", self.run_easyim, {}),
            ("Sketching", self.run_sketching, {}),
            ("Singles", self.run_singles, {}),
        ]

        for name, func, extra_args in algos:
            try:
                logger.info(f"Starting algorithm: %s", name)
                # Merge common and specific parameters
                params = {"k": k, "p": p}
                params.update(extra_args)
                result = func(**params)
                results[name] = result
                logger.info(f"Completed algorithm: %s | Result: %s", name, result)
            except Exception as e:
                logger.error(
                    f"Algorithm %s failed with error: %s", name, e, exc_info=True
                )
                results[name] = None

        self.print_results(results)
        return results

    def print_results(self, optimization_results):
        # Stampa dei risultati degli algoritmi di ottimizzazione
        print("\nRisultati degli algoritmi di ottimizzazione:")
        for algo_name, result in optimization_results.items():
            print(f"{algo_name}: {result}")
