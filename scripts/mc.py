import numpy as np


class Node(object):
    def __init__(self, _id, alpha, beta, level):
        super(Node, self).__init__()
        self.id = _id
        self.alpha = alpha
        self.beta = beta
        self.level = level
        self.left = None
        self.right = None
        self.attack_blocks = None
        self.honest_blocks = None

    def set_children(self, left, right):
        self.left = left
        self.right = right

    def set_state(self, attack_blocks, honest_blocks):
        self.attack_blocks = attack_blocks
        self.honest_blocks = honest_blocks

        if attack_blocks >= honest_blocks:
            self.left_prob = 1 - self.beta
            self.right_prob = self.beta
        else:
            self.left_prob = self.alpha
            self.right_prob = 1 - self.alpha

    def __str__(self):
        return "Node [ id: {}, level: {}, left: {}, right: {}, state: ({}, {}) ]".format(
            self.id,
            self.level,
            self.left,
            self.right,
            self.attack_blocks,
            self.honest_blocks)


def create_node_map(alpha, beta, levels):
    node_map = {}
    ctr = 0
    for i in range(levels):
        for j in range(i+1):
            node_map[ctr] = Node(ctr, alpha, beta, i)
            ctr += 1
    return node_map


def build_graph(alpha, beta, target_conf):
    num_nodes = (target_conf * (target_conf + 1)) / 2
    node_map = create_node_map(alpha, beta, target_conf)
    in_queue = {0: True, 1: True, 2: True}
    # setup root node children
    root = node_map[0]
    root.set_children(1, 2)
    root.set_state(0, 0)
    # setup level 1 children state
    node_map[1].set_state(1, 0)
    node_map[2].set_state(0, 1)
    queue = [node_map[1], node_map[2]]
    # start counter at first no root child
    ctr = 3
    last_level = 1
    while len(queue) > 0:
        node = queue.pop(0)
        # if we drop down another level, increment counter again
        if node.level > last_level:
            ctr += 1
            last_level = node.level

        if ctr >= num_nodes:
            return node_map

        print(node.id, ctr, ctr + 1)
        node.set_children(ctr, ctr + 1)
        if ctr not in in_queue:
            queue.append(node_map[ctr])
            node_map[ctr].set_state(node.attack_blocks + 1, node.honest_blocks)
            in_queue[ctr] = True
        if ctr + 1 not in in_queue and ctr + 1 < num_nodes:
            queue.append(node_map[ctr + 1])
            node_map[ctr + 1].set_state(node.attack_blocks, node.honest_blocks + 1)
            in_queue[ctr + 1] = True

        ctr += 1

        if ctr >= num_nodes:
            return node_map


def print_queue(queue):
    for _, elt in enumerate(queue):
        print("In queue: {}".format(elt))

if __name__ == '__main__':
    alpha = 0.3
    beta = 0.5
    # target confirmations
    k = 4
    node_map = build_graph(alpha, beta, k)
    for key in node_map:
        print(node_map[key])
