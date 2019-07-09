import numpy as np
from util import Block, BlockType, print_blocks


MAX_INT = 99999999999999999999999999.999


class Agent(object):
    """docstring for Agent"""
    def __init__(self, block_rate):
        super(Agent, self).__init__()
        self.rate = block_rate
        # initialize with genesis block
        self.genesis = Block(0, 0, None, 0.0, 0.0, True, 'genesis')
        self.chain_tip = self.genesis
        self.time = 0

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

    def setup_new_block(self, block_type, identifier):
        if block_type == BlockType.EmptyBlock:
            is_valid = True
        elif block_type == BlockType.HeaderOnly:
            is_valid = True
        elif block_type == BlockType.FullBlock:
            is_valid = True
        else:
            is_valid = False

        block_hash = np.random.randint(0, 1e15)
        block_time = round(np.random.exponential(self.rate), 6)
        block = Block(
            block_hash,
            self.chain_tip.height + 1,
            self.chain_tip,
            self.chain_tip.broadcast_time + block_time,
            block_time,
            is_valid,
            identifier)
        return block

    def mine(self):
        raise NotImplementedError


class HonestAgent(Agent):
    """
    HonestAgent
    """
    def __init__(self, block_rate):
        super().__init__(block_rate)
        self.identifier = 'honest'

    def mine(self):
        block = self.setup_new_block(BlockType.FullBlock, self.identifier)
        return block

    def is_valid_chain(self, block):
        temp = block
        while temp.height > 0:
            if temp.is_valid:
                temp = temp.parent
            else:
                return False
        return True

    def resolve_fork(self, blocks):
        leftover_blocks = blocks
        # honest agent processes blocks by max height
        # and min time and discards invalid blocks.
        while len(leftover_blocks) > 0:
            # get max height block
            index, max_ht_block = max(
                enumerate(leftover_blocks),
                key=lambda e: e[1].height)
            if max_ht_block.height < self.chain_tip.height:
                break
            # get all max height blocks
            max_ht_blocks = list(filter(
                lambda e: e.height == max_ht_block.height,
                leftover_blocks)
            )
            # get rest of blocks
            leftover_blocks = list(filter(
                lambda e: not e.height == max_ht_block.height and e.height,
                leftover_blocks)
            )
            # sort max height blocks by time, ascending
            min_time_blocks = sorted(
                max_ht_blocks,
                key=lambda e: e.broadcast_time)

            while len(min_time_blocks) > 0:
                elt = min_time_blocks.pop(0)
                if elt.identifier == 'attack':
                    continue
                elif elt.identifier == 'spv':
                    if self.is_valid_chain(elt):
                        self.add_block(elt)
                        return
                    else:
                        continue
                else:
                    # add honest block
                    self.add_block(elt)
                    return


class SPVAgent(Agent):
    """
    SPVAgent

    The SPVAgent always choses among the longest
    chains. If there are ties for longest chains,
    the SPVAgent chooses the one it receives the
    earliest.
    """
    def __init__(self, block_rate, val_time=0.0):
        super().__init__(block_rate)
        self.identifier = 'spv'
        self.val_time = val_time

    def mine(self):
        if self.chain_tip.is_valid:
            block = self.setup_new_block(
                BlockType.EmptyBlock,
                self.identifier)
        else:
            block = self.setup_new_block(
                BlockType.InvalidBlock,
                self.identifier)
        return block

    def resolve_fork(self, blocks):
        # get max height block
        index, max_ht_block = max(
            enumerate(blocks),
            key=lambda e: e[1].height)

        if max_ht_block.height <= self.chain_tip.height:
            return

        # get all max height blocks
        max_ht_blocks = list(filter(
            lambda e: e.height == max_ht_block.height,
            blocks)
        )
        # sort max height blocks by time, ascending
        min_time_blocks = sorted(max_ht_blocks, key=lambda e: e.broadcast_time)
        self.add_block(min_time_blocks[0])


class MaliciousAgent(Agent):
    """
    MaliciousAgent
    """
    def __init__(self, block_rate, k_conf):
        super().__init__(block_rate)
        self.identifier = 'attack'
        self.k = k_conf
        self.unvalidated_spends = 0

    def resolve_fork(self, blocks, agent_decisions):
        # get max height block
        index, max_ht_block = max(
            enumerate(blocks),
            key=lambda e: e[1].height)

        if max_ht_block.height <= self.chain_tip.height:
            return

        # get all max height blocks
        max_ht_blocks = list(filter(
            lambda e: e.height == max_ht_block.height,
            blocks)
        )
        # sort max height blocks by time, ascending
        min_time_blocks = sorted(max_ht_blocks, key=lambda e: e.broadcast_time)
        # count number of invalid blocks in chain before accepting
        # next valid block (i.e. when SPV miner switches to valid chain)
        if not self.chain_tip.is_valid and min_time_blocks[0].is_valid:
            temp = self.chain_tip
            inx = 0
            while not temp.is_valid:
                temp = temp.parent
                inx += 1

            if inx > self.k:
                self.unvalidated_spends += 1

        self.add_block(min_time_blocks[0])
        return

    def mine(self):
        return self.setup_new_block(BlockType.InvalidBlock, 'attack')

    def process_honest_block(self, block):
        # TODO: Add pre-processing?
        # Resolve fork if honest block
        pass
