import numpy as np
from util import Block, BlockType, print_blocks


MAX_INT = 9999999999999999999999999999999999999999999999999999


class Agent(object):
    """docstring for Agent"""
    def __init__(self, block_rate, block_type, identifier, network):
        super(Agent, self).__init__()
        self.rate = block_rate
        # initialize with genesis block
        self.genesis = Block(0, 0, None, 0.0, 0.0, True, 'genesis')
        self.chain_tip = self.genesis
        self.block_type = block_type
        self.identifier = identifier
        self.time = 0
        self.network = network

    def add_block(self, block):
        """
        Adding a block should ONLY occur after
        all validation of the block or new fork.

        This method assumes that the block has
        passed all validity conditions for the
        respective agent, which should be handled
        in their respective classes
        """
        self.chain_tip = block

    def mine(self):
        if self.block_type == BlockType.EmptyBlock:
            is_valid = True
        elif self.block_type == BlockType.HeaderOnly:
            is_valid = True
        elif self.block_type == BlockType.FullBlock:
            is_valid = True
        else:
            is_valid = False

        block_time = round(np.random.exponential(self.rate), 6)
        block_data = [
            self.chain_tip.parent.hash,
            self.chain_tip.height + 1,
            self.chain_tip.time + block_time,
            self.identifier
        ]

        block_hash = hash(tuple(block_data)) % MAX_INT

        return Block(
            block_hash,
            self.chain_tip.height + 1,
            self.chain_tip,
            self.chain_tip.time + block_time,
            is_valid,
            self.identifier)

    def broadcast_block(self, env, block):
        self.network.broadcast_block(env, block)
