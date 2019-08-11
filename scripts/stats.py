import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.cm as cm
import numpy as np
import mc
import better_graph
import copy


def get_absorbing_map(node_map, target_conf):
    length = len(node_map)
    winning_nodes = []
    nmap = copy.deepcopy(node_map)
    for key in node_map:
        if node_map[key].attack_blocks > target_conf:
            nmap[key].right = node_map[key].id
            nmap[key].left = node_map[key].id
            winning_nodes.append(copy.deepcopy(node_map[key]))
        elif node_map[key].honest_blocks == target_conf:
            if length not in node_map:
                nmap[length] = mc.Node(
                    len(node_map),
                    node_map[key].alpha,
                    node_map[key].beta,
                    None)
                nmap[length].set_prob(0.0)
                nmap[length].set_children(
                    length,
                    length)
            nmap[key].right = length

    return nmap, winning_nodes


def run():
    alpha = 0.3
    beta = 0.5
    # target confirmations
    for k in range(2, 8):
        node_map, winning_nodes = get_absorbing_map(mc.build_rect_graph(alpha, beta, k), k)
        for i in node_map:
            print(node_map[i])
        matrix = mc.markov_chain_gen(node_map)
        final = mc.start(matrix, k, alpha, beta)
        win_prob = 0.0
        print(final)
        for inx, elt in enumerate(winning_nodes):

            win_prob += final[0, elt.id]
        print(win_prob)


def run_split():
    alpha = 0.3
    beta = 0.5
    # target confirmations
    for k in range(2, 7):
        node_map = better_graph.split_graph(alpha, beta, k)
        matrix = better_graph.markov_chain_gen(node_map)
        mc.start(matrix, k, alpha, beta, title="split")


if __name__ == '__main__':
    run_split()
