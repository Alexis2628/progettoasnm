import os
import json
import networkx as nx
import random
import pandas as pd
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed


# Funzioni helper per il calcolo delle centralità
def degree_centrality(graph):
    return nx.degree_centrality(graph)


def closeness_centrality(graph):
    return nx.closeness_centrality(graph)


def betweenness_centrality(graph):
    return nx.betweenness_centrality(graph, normalized=True, weight="weight")


def pagerank(graph):
    return nx.pagerank(graph, alpha=0.85, max_iter=1000, tol=1e-6)


def katz_centrality(graph):
    low_memory = True
    if low_memory:
        eigenvalues = nx.adjacency_spectrum(graph)
        largest_eig = max(abs(ev) for ev in eigenvalues)
        safe_alpha = 0.9 / largest_eig
        logging.info(f"Utilizzo safe_alpha={safe_alpha:.6f} (lambda_max={largest_eig:.6f})")  
        return nx.katz_centrality(
                graph, 
                alpha=safe_alpha, 
                beta=1.0, 
                max_iter=5000, 
                tol=1e-4
        )
    return nx.katz_centrality_numpy(graph, alpha=0.1, beta=1.0)


def eigenvector_centrality(graph):
    return nx.eigenvector_centrality(graph, max_iter=300)


def hits_scores(graph):
    hubs, authorities = nx.hits(graph, max_iter=300, tol=1e-08)
    return hubs, authorities


class GraphConstructor:
    def __init__(
        self,
        followers_paths=[
            "Code/data_extraction/followers.csv",
        ],
        data_paths=[
            "Code/data_extraction/total_post1.csv",
            "Code/data_extraction/total_post2.csv",
            "Code/data_extraction/total_post3.csv",
        ],
        info_filepath="graph_info.json",
        centralities_filepath="centralities_info.json",
    ):

        self.df = pd.concat(
            [
                pd.read_csv(
                    followers_paths[0],
                    dtype={
                        "thread_user_pk": str,
                        "thread_follower_pk": str,
                    },
                ),
            ]
        )

        self.data = pd.concat(
            [
                pd.read_csv(
                    data_paths[0],
                    dtype={
                        "id": str,"post_pk": str,"caption_text": str,"like_count": int,"taken_at": str,
                        "username": str,"user_pk": str,"quote_count": int,"repost_count": int,"reshare_count": int,
                        "thread_user_pk": str,"caption_text_translated": str,"sentiment_score": float,"sentiment_label": str,
                    },
                ),
                pd.read_csv(
                    data_paths[1],
                    dtype={
                        "id": str,"post_pk": str,"caption_text": str,"like_count": int,"taken_at": str,
                        "username": str,"user_pk": str,"quote_count": int,"repost_count": int,"reshare_count": int,
                        "thread_user_pk": str,"caption_text_translated": str,"sentiment_score": float,"sentiment_label": str,
                    },
                ),
                pd.read_csv(
                    data_paths[2],
                    dtype={
                        "id": str,"post_pk": str,"caption_text": str,"like_count": int,"taken_at": str,
                        "username": str,"user_pk": str,"quote_count": int,"repost_count": int,"reshare_count": int,
                        "thread_user_pk": str,"caption_text_translated": str,"sentiment_score": float,"sentiment_label": str,
                    },
                ),
            ]
        )

        self.graph = nx.DiGraph()
        self.info_filepath = info_filepath
        self.centralities_filepath = centralities_filepath

    def build_graph(self):
        followers_per_user = (
            self.df.groupby("thread_user_pk")["thread_follower_pk"]
            .apply(list)
            .reset_index()
        )
        for _, (user_pk, listf) in followers_per_user.iterrows():

            for follower_pk in listf:
                self.graph.add_edge(follower_pk, user_pk)
        for node in self.graph.nodes():
            self.graph.nodes[node]["threshold"] = random.uniform(0, 1)

        return self.graph

    def log_graph_info(self):
        logging.info(f"Numero di nodi del grafo: {self.graph.number_of_nodes()}")
        logging.info(f"Numero di archi del grafo: {self.graph.number_of_edges()}")

    def trust_function(self, neighbor, node):
        """
        Funzione di fiducia che determina il livello di fiducia tra un nodo e il suo vicino.
        :param neighbor: Il vicino del nodo corrente.
        :param node: Il nodo corrente.
        :return: Valore di fiducia tra 0 e 1.
        """
        weight = self.graph[node][neighbor].get("weight", 1)
        neighbor_threshold = self.graph.nodes[neighbor].get("threshold", 0.5)
        trust = weight * (1 - neighbor_threshold)
        return max(0, min(trust, 1))

    def calculate_centralities(self):
        centrality_functions = {
            "Degree Centrality": degree_centrality,
            "Closeness Centrality": closeness_centrality,
            "Betweenness Centrality": betweenness_centrality,
            "PageRank": pagerank,
            "Katz Centrality": katz_centrality,
            "Eigenvector Centrality": eigenvector_centrality,
            "HITS": hits_scores,
        }
        centralities = {}
        with ProcessPoolExecutor() as executor:
            future_to_key = {
                executor.submit(func, self.graph): key
                for key, func in centrality_functions.items()
            }
            for future in as_completed(future_to_key):
                key = future_to_key[future]
                try:
                    result = future.result()
                except Exception as exc:
                    logging.error(f"Errore nel calcolo di {key}: {exc}")
                else:
                    if key == "HITS":
                        hubs, authorities = result
                        centralities["HITS Hub Scores"] = hubs
                        centralities["HITS Authority Scores"] = authorities
                    else:
                        centralities[key] = result
        return centralities

    def print_top_centralities(self, centralities=None, top_k=5):
        if not centralities:
            centralities = self.get_centralities_info()
        for centrality_name, values in centralities.items():
            print(f"\n{centrality_name} (Top {top_k}):")
            print("-" * (len(centrality_name) + 10))
            # Ordina i nodi per valore decrescente e seleziona i primi `top_k`
            sorted_values = sorted(values.items(), key=lambda x: x[1], reverse=True)[
                :top_k
            ]
            for node, value in sorted_values:
                print(f"Node {node}: {value:.4f}")

    def get_basic_graph_info(self):
        """
        Restituisce informazioni di base sul grafo.
        """
        num_nodes = self.graph.number_of_nodes()
        num_edges = self.graph.number_of_edges()
        density = nx.density(self.graph)
        avg_degree = float(num_edges) / num_nodes if num_nodes > 0 else 0

        info = {
            "Numero di nodi": num_nodes,
            "Numero di archi": num_edges,
            "Densità": density,
            "Grado medio": avg_degree,
        }
        return info

    def get_connectivity_info(self):
        """
        Estrae informazioni sulla connettività del grafo.
        """
        info = {}
        # Componenti fortemente connesse (per grafi diretti)
        scc = list(nx.strongly_connected_components(self.graph))
        info["Numero di componenti fortemente connesse"] = len(scc)
        largest_scc = max(scc, key=len) if scc else set()
        info["Dimensione della più grande componente fortemente connessa"] = len(
            largest_scc
        )

        # Componenti debolmente connesse
        wcc = list(nx.weakly_connected_components(self.graph))
        info["Numero di componenti debolmente connesse"] = len(wcc)
        largest_wcc = max(wcc, key=len) if wcc else set()
        info["Dimensione della più grande componente debolmente connessa"] = len(
            largest_wcc
        )

        # Calcolo del diametro e della lunghezza media dei cammini sulla componente debolmente connessa più grande
        if largest_wcc:
            subgraph = self.graph.subgraph(largest_wcc).to_undirected()
            try:
                diameter = nx.diameter(subgraph)
                avg_shortest_path = nx.average_shortest_path_length(subgraph)
            except Exception as e:
                diameter = None
                avg_shortest_path = None
                logging.warning(
                    f"Impossibile calcolare il diametro o la lunghezza media dei cammini: {e}"
                )
            info["Diametro (componente connessa più grande)"] = diameter
            info["Lunghezza media dei cammini (componente connessa più grande)"] = (
                avg_shortest_path
            )
        else:
            info["Diametro (componente connessa più grande)"] = None
            info["Lunghezza media dei cammini (componente connessa più grande)"] = None

        return info

    def get_clustering_info(self):
        """
        Calcola il coefficiente di clustering medio e per nodo (su grafo non orientato).
        """
        undirected_graph = self.graph.to_undirected()
        clustering_per_node = nx.clustering(undirected_graph)
        avg_clustering = (
            sum(clustering_per_node.values()) / len(clustering_per_node)
            if clustering_per_node
            else 0
        )

        info = {
            "Coefficiente di clustering medio": avg_clustering,
            "Clustering per nodo": clustering_per_node,
        }
        return info

    def get_assortativity_info(self):
        """
        Calcola il coefficiente di assortatività del grafo basato sul grado.
        """
        try:
            assortativity = nx.degree_assortativity_coefficient(self.graph)
        except Exception as e:
            logging.warning(f"Errore nel calcolo dell'assortatività: {e}")
            assortativity = None
        return {"Assortatività di grado": assortativity}

    def get_degree_distribution(self):
        """
        Restituisce la distribuzione del grado dei nodi.
        """
        degree_sequence = [d for n, d in self.graph.degree()]
        distribution = {}
        for degree in degree_sequence:
            distribution[degree] = distribution.get(degree, 0) + 1
        sorted_distribution = dict(sorted(distribution.items()))
        return sorted_distribution

    def get_all_graph_info(self, force_recalculate=False):
        """
        Raccoglie e restituisce tutte le informazioni estratte dal grafo.
        Se il file esiste e force_recalculate è False, carica i dati salvati.
        Altrimenti, ricalcola e salva le informazioni.
        """
        if not force_recalculate and os.path.exists(self.info_filepath):
            try:
                with open(self.info_filepath, "r", encoding="utf-8") as f:
                    info = json.load(f)
                logging.info(f"Informazioni caricate dal file {self.info_filepath}.")
                return info
            except Exception as e:
                logging.warning(
                    f"Errore nel caricamento del file: {e}. Verrà ricalcolato il tutto."
                )

        info = {}
        logging.info("Calculating basic info")
        info.update(self.get_basic_graph_info())
        logging.info("Calculating connectivity info")
        info.update(self.get_connectivity_info())
        logging.info("Calculating clustering info")
        info.update(self.get_clustering_info())
        logging.info("Calculating assortativity info")
        info.update(self.get_assortativity_info())
        logging.info("Calculating degree distribution info")
        info["Distribuzione del grado"] = self.get_degree_distribution()

        # Salva le informazioni su file in formato JSON
        try:
            with open(self.info_filepath, "w", encoding="utf-8") as f:
                json.dump(info, f, indent=4)
            logging.info(f"Informazioni salvate nel file {self.info_filepath}.")
        except Exception as e:
            logging.error(f"Errore nel salvataggio delle informazioni: {e}")

        return info

    def get_centralities_info(self, force_recalculate=False):
        """
        Calcola e restituisce le centralità del grafo.
        Se il file esiste e force_recalculate è False, carica i dati salvati.
        Altrimenti, ricalcola e salva le centralità.
        """
        if not force_recalculate and os.path.exists(self.centralities_filepath):
            try:
                with open(self.centralities_filepath, "r", encoding="utf-8") as f:
                    centralities = json.load(f)
                logging.info(
                    f"Centralità caricate dal file {self.centralities_filepath}."
                )
                return centralities
            except Exception as e:
                logging.warning(
                    f"Errore nel caricamento del file delle centralità: {e}. Verrà ricalcolato il tutto."
                )

        centralities = self.calculate_centralities()

        # Salva le centralità su file in formato JSON
        try:
            with open(self.centralities_filepath, "w", encoding="utf-8") as f:
                json.dump(centralities, f, indent=4)
            logging.info(f"Centralità salvate nel file {self.centralities_filepath}.")
        except Exception as e:
            logging.error(f"Errore nel salvataggio delle centralità: {e}")

        return centralities
