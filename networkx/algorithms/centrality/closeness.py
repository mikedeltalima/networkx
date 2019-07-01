#    Copyright (C) 2004-2019 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#
# Authors:  Aric Hagberg <aric.hagberg@gmail.com>
#           Pieter Swart <swart@lanl.gov>
#           Sasha Gutfraind <ag362@cornell.edu>
#           Dan Schult <dschult@colgate.edu>
#           Michael Lauria <michael.david.lauria@gmail.com>
"""
Closeness centrality measures.
"""
import functools
import networkx as nx
from networkx.exception import NetworkXError
from networkx.utils.decorators import not_implemented_for

__all__ = ['closeness_centrality', 'incremental_closeness_centrality']


def closeness_centrality(G, u=None, distance=None, wf_improved=True):
    r"""Compute closeness centrality for nodes.

    Closeness centrality [1]_ of a node `u` is the reciprocal of the
    average shortest path distance to `u` over all `n-1` reachable nodes.

    .. math::

        C(u) = \frac{n - 1}{\sum_{v=1}^{n-1} d(v, u)},

    where `d(v, u)` is the shortest-path distance between `v` and `u`,
    and `n` is the number of nodes that can reach `u`. Notice that the
    closeness distance function computes the incoming distance to `u`
    for directed graphs. To use outward distance, act on `G.reverse()`.

    Notice that higher values of closeness indicate higher centrality.

    Wasserman and Faust propose an improved formula for graphs with
    more than one connected component. The result is "a ratio of the
    fraction of actors in the group who are reachable, to the average
    distance" from the reachable actors [2]_. You might think this
    scale factor is inverted but it is not. As is, nodes from small
    components receive a smaller closeness value. Letting `N` denote
    the number of nodes in the graph,

    .. math::

        C_{WF}(u) = \frac{n-1}{N-1} \frac{n - 1}{\sum_{v=1}^{n-1} d(v, u)},

    Parameters
    ----------
    G : graph
      A NetworkX graph

    u : node, optional
      Return only the value for node u

    distance : edge attribute key, optional (default=None)
      Use the specified edge attribute as the edge distance in shortest
      path calculations

    wf_improved : bool, optional (default=True)
      If True, scale by the fraction of nodes reachable. This gives the
      Wasserman and Faust improved formula. For single component graphs
      it is the same as the original formula.

    Returns
    -------
    nodes : dictionary
      Dictionary of nodes with closeness centrality as the value.

    See Also
    --------
    betweenness_centrality, load_centrality, eigenvector_centrality,
    degree_centrality

    Notes
    -----
    The closeness centrality is normalized to `(n-1)/(|G|-1)` where
    `n` is the number of nodes in the connected part of graph
    containing the node.  If the graph is not completely connected,
    this algorithm computes the closeness centrality for each
    connected part separately scaled by that parts size.

    If the 'distance' keyword is set to an edge attribute key then the
    shortest-path length will be computed using Dijkstra's algorithm with
    that edge attribute as the edge weight.

    In NetworkX 2.2 and earlier a bug caused Dijkstra's algorithm to use the
    outward distance rather than the inward distance. If you use a 'distance'
    keyword and a DiGraph, your results will change between v2.2 and v2.3.

    References
    ----------
    .. [1] Linton C. Freeman: Centrality in networks: I.
       Conceptual clarification. Social Networks 1:215-239, 1979.
       http://leonidzhukov.ru/hse/2013/socialnetworks/papers/freeman79-centrality.pdf
    .. [2] pg. 201 of Wasserman, S. and Faust, K.,
       Social Network Analysis: Methods and Applications, 1994,
       Cambridge University Press.
    """
    if G.is_directed():
        G = G.reverse()  # create a reversed graph view

    if distance is not None:
        # use Dijkstra's algorithm with specified attribute as edge weight
        path_length = functools.partial(
            nx.single_source_dijkstra_path_length, weight=distance)
    else:
        path_length = nx.single_source_shortest_path_length

    if u is None:
        nodes = G.nodes
    else:
        nodes = [u]
    closeness_centrality = {}
    for n in nodes:
        sp = dict(path_length(G, n))
        totsp = sum(sp.values())
        if totsp > 0.0 and len(G) > 1:
            closeness_centrality[n] = (len(sp) - 1.0) / totsp
            # normalize to number of nodes-1 in connected part
            if wf_improved:
                s = (len(sp) - 1.0) / (len(G) - 1)
                closeness_centrality[n] *= s
        else:
            closeness_centrality[n] = 0.0
    if u is not None:
        return closeness_centrality[u]
    else:
        return closeness_centrality


@not_implemented_for('directed')
def incremental_closeness_centrality(G,
                                     edge,
                                     prev_cc=None,
                                     insertion=True,
                                     normalized=True):
    r"""Incremental closeness centrality for nodes.

    Compute closeness centrality for nodes using level-based work filtering
    as described in Incremental Algorithms for Closeness Centrality by Sariyuce,
    A.E. ; Kaya, K. ; Saule, E. ; Catalyiirek, U.V.

    Closeness centrality [1]_ of a node `u` is the reciprocal of the
    sum of the shortest path distances from `u` to all `n-1` other nodes.
    Since the sum of distances depends on the number of nodes in the
    graph, closeness is normalized by the sum of minimum possible
    distances `n-1`.

    .. math::

        C(u) = \frac{n - 1}{\sum_{v=1}^{n-1} d(v, u)},

    where `d(v, u)` is the shortest-path distance between `v` and `u`,
    and `n` is the number of nodes in the graph.

    Notice that higher values of closeness indicate higher centrality.

    Parameters
    ----------
    G : graph
      A NetworkX graph
    edge: tuple
      The modified edge (u, v) in the graph.
    prev_cc: list
      The previous closeness centrality for all nodes in the graph.
    insertion: bool, optional
      If True (default) the edge was inserted, otherwise it was deleted from the graph.
    normalized : bool, optional
      If True (default) normalize by the number of nodes in the connected
      part of the graph.

    Returns
    -------
    nodes : dictionary
      Dictionary of nodes with closeness centrality as the value.

    See Also
    --------
    betweenness_centrality, load_centrality, eigenvector_centrality,
    degree_centrality

    Notes
    -----
    The closeness centrality is normalized to `(n-1)/(|G|-1)` where
    `n` is the number of nodes in the connected part of graph
    containing the node.  If the graph is not completely connected,
    this algorithm computes the closeness centrality for each
    connected part separately.

    This algorithm is applicable to undirected graphs without edge weights.

    References
    ----------
    .. [1] Freeman, L.C., 1979. Centrality in networks: I.
       Conceptual clarification.  Social Networks 1, 215--239.
       http://www.soc.ucsb.edu/faculty/friedkin/Syllabi/Soc146/Freeman78.PDF
       [2]Sariyuce, A.E. ; Kaya, K. ; Saule, E. ; Catalyiirek, U.V. Incremental
       Algorithms for Closeness Centrality
       http://sariyuce.com/papers/bigdata13.pdf
    """

    if prev_cc is not None:
        shared_items = set(prev_cc.keys()) & set(G.nodes())
        count_shared = len(shared_items)
        if len(prev_cc) != count_shared or len(G.nodes()) != count_shared:
            raise NetworkXError(
                "Previous closeness centrality list does not correspond to given\
        graph.")

    # Just aliases G
    G_prime = G

    # Unpack edge
    (u, v) = edge
    path_length = nx.single_source_shortest_path_length

    if insertion:
        # Do this first because G and G_prime refer to the same thing
        du = path_length(G, u)
        dv = path_length(G, v)

        G_prime.add_edge(u, v)
    else:
        G_prime.remove_edge(u, v)

        # For edge removal, we want to know about distances after the edge is gone
        du = path_length(G_prime, u)
        dv = path_length(G_prime, v)

    if prev_cc is None:
        return nx.closeness_centrality(G_prime)

    nodes = G_prime.nodes()
    closeness_centrality = {}
    for n in nodes:
        n_from_u = du.get(n)
        n_from_v = dv.get(n)
        if (n_from_u is not None and n_from_v is not None
                and abs(n_from_u - n_from_v) <= 1):
            closeness_centrality[n] = prev_cc[n]
        else:
            sp = path_length(G_prime, n)
            totsp = sum(sp.values())
            if totsp > 0.0 and len(G_prime) > 1:
                closeness_centrality[n] = (len(sp) - 1.0) / totsp
                # normalize to number of nodes-1 in connected part
                if normalized:
                    s = (len(sp) - 1.0) / (len(G_prime) - 1)
                    closeness_centrality[n] *= s
            else:
                closeness_centrality[n] = 0.0

    # Leave the graph as we found it
    if insertion:
        G_prime.remove_edge(u, v)
    else:
        G_prime.add_edge(u, v)

    return closeness_centrality