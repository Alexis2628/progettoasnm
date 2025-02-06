def simpath(graph, k, p=0.1, path_limit=3):
    """Algoritmo SIMPATH basato sui percorsi influenti"""

    def compute_path_influence(node, path_limit):
        visited = set()
        stack = [(node, 0)]
        influence = 0

        while stack:
            current_node, depth = stack.pop()
            if depth > path_limit or current_node in visited:
                continue
            visited.add(current_node)
            influence += 1
            for neighbor in graph.neighbors(current_node):
                stack.append((neighbor, depth + 1))
        return influence

    seed_set = set()
    for _ in range(k):
        best_node = max(
            graph.nodes(), key=lambda n: compute_path_influence(n, path_limit)
        )
        seed_set.add(best_node)
        graph.remove_node(best_node)
    return seed_set
