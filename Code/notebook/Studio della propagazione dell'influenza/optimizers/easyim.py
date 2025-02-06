import random


def easyim(graph, k, p=0.1):
    """EaSyIM: Ottimizzato con Sketching e campioni"""
    sketch = {node: random.uniform(0, 1) for node in graph.nodes()}
    seed_set = set(sorted(sketch, key=sketch.get)[:k])
    return seed_set
