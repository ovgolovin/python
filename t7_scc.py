# -*- coding: utf-8 -*-

"""
This module contains algorithm to find strongly connected components in the graph.
See Stanford algorithm class with Tim Roughgarden Part I.
"""

from collections import defaultdict

file_name = 'scc_test2.txt'


def _DFS_loop(nodes, edges, t_n=None):
    """
    Nodes have to be sorted in reverse order
    t_n - {node: time}
    """

    if t_n is not None:
        n_t = dict((b,a) for a,b in t_n.items()) # {time: node}
    get_node_by_time = lambda time: time if t_n is None else n_t[time]
    get_time_by_node = lambda node: node if t_n is None else t_n[node]
    gen_edges = lambda node: map(get_time_by_node,edges[get_node_by_time(node)])

    explored = set()
    leader = dict()
    _DFS_loop.t = 0 # finishing time
    times = dict() # {time: node}

    def DFS(i):
        explored.add(i)
        leader[i] = s
        for j in gen_edges(i):
            if j not in explored:
                DFS(j)
        _DFS_loop.t += 1
        times[i] = _DFS_loop.t

    for i in nodes:
        if i not in explored:
            s = i # leader node
            DFS(i)

    leaders = defaultdict(list)
    for n,l in leader.items():
        leaders[get_node_by_time(l)].append(get_node_by_time(n))

    return times, leaders


def _get_data_from_edges_iterator(edges_iterator):
    nodes = set()
    edges = defaultdict(list)
    edges_rev = defaultdict(list)
    for a, b in edges_iterator:
        nodes.update((a, b))
        edges[a].append(b)
        edges_rev[b].append(a)
    return nodes, edges, edges_rev


def _get_leaders(edges, edges_rev, nodes):
    times, _ = _DFS_loop(sorted(nodes, reverse=True), edges_rev)
    _, leaders = _DFS_loop(sorted(list(times.values()), reverse=True), edges, t_n=times)
    return leaders.values()


def get_leaders_from_edges(edges):
    nodes, edges, edges_rev = _get_data_from_edges_iterator(edges)
    leaders = _get_leaders(edges, edges_rev, nodes)
    return leaders


def _get_leaders_from_file(file_name):
    with open(file_name) as f:
        edges_iterator = (map(int, line.strip().split()) for line in f)
        leaders = get_leaders_from_edges(edges_iterator)
    return leaders


def main():
    leaders = _get_leaders_from_file(file_name)
            
    for leader in leaders:
        print(leader)

if __name__ == '__main__':
    main()

