import networkx as nx
from scipy.sparse import csr_matrix
from sklearn.decomposition import TruncatedSVD
from sklearn.mixture import GaussianMixture


def gaussian_mixture_clustering(
    graph: nx.Graph, n_components: int = 3, embedding_dim: int = 100
) -> dict:
    """
    Cluster a (large) graph by:
      1) converting to sparse adjacency
      2) reducing to `embedding_dim` via Truncated SVD
      3) GaussianMixture clustering

    Parameters
    ----------
    graph : nx.Graph
    n_components : int
        Number of GMM clusters
    embedding_dim : int
        Target embedding dimension (must be << number of nodes).

    Returns
    -------
    labels : dict
        node -> cluster label (0..n_components-1)
    """
    # 1) sparse adjacency
    A: csr_matrix = nx.adjacency_matrix(graph)

    # 2) reduce dimensions
    #    cap embedding_dim at (N_nodes - 1)
    max_dim = graph.number_of_nodes() - 1
    d = min(embedding_dim, max_dim)
    svd = TruncatedSVD(n_components=d)
    X_reduced = svd.fit_transform(A)  # shape: (n_nodes, d)

    # 3) GMM clustering
    gm = GaussianMixture(n_components=n_components)
    labels = gm.fit_predict(X_reduced)

    return dict(zip(graph.nodes(), labels))
