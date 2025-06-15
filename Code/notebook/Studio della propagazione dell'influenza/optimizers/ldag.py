import random
import networkx as nx


def ldag(graph, k, p=0.1, threshold=0.5):
    """Algoritmo LDAG: Local DAG-based propagation"""

    def build_local_dag(node, threshold):
        """Crea il DAG locale partendo da ``node``.

        Parameters
        ----------
        node : hashable
            Nodo di partenza per l'esplorazione.
        threshold : float
            Probabilità di seguire un arco nella costruzione.

        Returns
        -------
        networkx.DiGraph
            Sottografo orientato che rappresenta la porzione locale esplorata.
        """

        local_dag = nx.DiGraph()
        visited = set([node])
        queue = [node]
        while queue:
            current = queue.pop(0)
            for neighbor in graph.neighbors(current):
                if random.random() < threshold:
                    local_dag.add_edge(current, neighbor)
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
        return local_dag

    seed_set = set()
    for _ in range(k):
        best_node = max(graph.nodes(), key=lambda n: len(build_local_dag(n, threshold)))
        seed_set.add(best_node)
    return seed_set
