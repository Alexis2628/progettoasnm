import random


def tim_plus(graph, k, p=0.1, rr_sets=100):
    """TIM+: Reverse Reachable Set Sampling"""

    def generate_rr_set():
        node = random.choice(list(graph.nodes()))
        rr_set = set([node])
        queue = [node]
        while queue:
            current = queue.pop(0)
            for neighbor in graph.predecessors(current):
                if neighbor not in rr_set and random.random() < p:
                    rr_set.add(neighbor)
                    queue.append(neighbor)
        return rr_set

    rr_sets_list = [generate_rr_set() for _ in range(rr_sets)]
    seed_set = set()
    for _ in range(k):
        max_node = max(
            graph.nodes(), key=lambda n: sum(1 for rr in rr_sets_list if n in rr)
        )
        seed_set.add(max_node)
        rr_sets_list = [rr for rr in rr_sets_list if max_node not in rr]
    return seed_set
