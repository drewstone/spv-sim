from enum import Enum


class BlockType(Enum):
    InvalidBlock = 0
    EmptyBlock = 1
    FullBlock = 2
    HeaderOnly = 3


class Block(object):
    """docstring for Block"""
    def __init__(
        self,
        block_hash,
        height,
        parent,
        time,
        is_valid,
        identifier
    ):
        super(Block, self).__init__()
        self.hash = block_hash
        self.height = height
        self.parent = parent
        self.time = time
        self.is_valid = is_valid
        self.identifier = identifier

    def add_delay(self, delay):
        return Block(
            self.hash,
            self.height,
            self.parent,
            self.time + delay,
            self.time_from_last,
            self.is_valid,
            self.identifier,
        )

    def __str__(self):
        return format('Hash: {}, Height: {}, Brdcast Time: {}, Time from last: {}, Identifier: {}'
            .format(self.hash,
                    self.height,
                    self.time,
                    self.time_from_last,
                    self.identifier))


def print_blocks(_id, blocks):
    print(list(map(lambda b: "{} | {}, delivery_time {}"
        .format(_id, b.identifier, b.time), blocks)))


def print_stats_for_round_sim(simulator):
    stats = {}
    attack_blocks = []
    temp_block = simulator.spv.chain_tip
    while temp_block.height > 0:
        if temp_block.identifier in stats:
            stats[temp_block.identifier] += 1
        else:
            stats[temp_block.identifier] = 1

        if not temp_block.is_valid:
            attack_blocks.append(temp_block)

        temp_block = temp_block.parent

    honest_blocks = []
    if len(attack_blocks) > 0:
        temp = simulator.honest.chain_tip
        for _ in range(len(attack_blocks)):
            honest_blocks.append(temp)
            temp = temp.parent

    temp_stats = dict(stats)
    for key in temp_stats:
        stats["{}-frac".format(key)] = (temp_stats[key] * 1.0
            / simulator.num_rounds)

    if simulator.attack:
        print(simulator.attack.unvalidated_spends)

    print(stats)
