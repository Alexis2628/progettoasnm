import networkx as nx
from collections import defaultdict
import pandas as pd


def build_clusters_from_partition(partition):
    """Costruisce un mapping cluster_id -> lista di nodi.

    Parameters
    ----------
    partition : dict
        Dizionario nodo -> id del cluster.

    Returns
    -------
    dict
        Mappatura cluster_id -> lista di nodi.
    """
    clusters = defaultdict(list)
    for node, cid in partition.items():
        clusters[cid].append(node)
    return dict(clusters)


def compute_cluster_connections(G, partition):
    """Trova i cluster collegati da almeno un arco uscente.

    Parameters
    ----------
    G : networkx.Graph
        Grafo su cui lavorare.
    partition : dict
        Mappatura nodo -> cluster_id.

    Returns
    -------
    dict
        Cluster_id -> lista ordinata di cluster adiacenti.
    """
    connections = defaultdict(set)
    for u, v in G.edges():
        cu = partition.get(u)
        cv = partition.get(v)
        if cu is not None and cv is not None and cu != cv:
            connections[cu].add(cv)
            connections[cv].add(cu)
    return {cid: sorted(neigh) for cid, neigh in connections.items()}


def compute_cluster_stats(G, df_data, clusters, top_n=5):
    """Calcola statistiche e top utenti per ciascun cluster.

    Parameters
    ----------
    G : networkx.Graph
        Grafo di riferimento.
    df_data : pandas.DataFrame
        Dati utente da cui estrarre statistiche.
    clusters : dict
        Mappatura cluster_id -> lista di nodi.
    top_n : int, optional
        Numero di utenti top per grado da restituire.

    Returns
    -------
    dict
        cluster_id -> statistiche calcolate.
    """

    df_user = (
        df_data.groupby("thread_user_pk")
        .agg(
            username=pd.NamedAgg("username", "first"),
            post_count=pd.NamedAgg("id", "count"),
            total_likes=pd.NamedAgg("like_count", "sum"),
            avg_likes=pd.NamedAgg("like_count", "mean"),
            total_quotes=pd.NamedAgg("quote_count", "sum"),
            total_reposts=pd.NamedAgg("repost_count", "sum"),
            total_reshares=pd.NamedAgg("reshare_count", "sum"),
            avg_sentiment=pd.NamedAgg("sentiment_score", "mean"),
        )
        .reset_index()
        .set_index("thread_user_pk")
    )

    stats = {}
    for cid, nodes in clusters.items():
        subg = G.subgraph(nodes)
        num_nodes = subg.number_of_nodes()
        num_edges = subg.number_of_edges()
        degs = dict(subg.degree())
        avg_degree = sum(degs.values()) / num_nodes if num_nodes > 0 else 0
        density = nx.density(subg)

        top_nodes = sorted(degs.items(), key=lambda x: x[1], reverse=True)[:top_n]
        top_stats = []
        for node_id, deg in top_nodes:
            user_pk = str(node_id)
            if user_pk in df_user.index:
                row = df_user.loc[user_pk].to_dict()
            else:
                row = {col: None for col in df_user.columns}
            entry = {"user_pk": user_pk, "degree": deg, **row}
            top_stats.append(entry)

        stats[cid] = {
            "num_nodes": num_nodes,
            "num_edges": num_edges,
            "avg_degree": avg_degree,
            "density": density,
            "top_users": top_stats,
        }
    return stats
