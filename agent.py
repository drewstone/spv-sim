import numpy as np
import operator
from util import Block, BlockType

MAX_INT = 99999999999999999999999999.999


class Agent(object):
    """docstring for Agent"""
    def __init__(self, block_rate, sig_digits=3):
        super(Agent, self).__init__()
        self.rate = block_rate
        # initialize with genesis block
        self.genesis = Block(0, 0, None, 0.0, 0.0, True, 'genesis')
        self.chain_tip = self.genesis
        self.sig_digits = sig_digits
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
            has_data = True
        elif block_type == BlockType.HeaderOnly:
            has_data = True
        elif block_type == BlockType.FullBlock:
            has_data = True
        else:
            has_data = False

        block_hash = np.random.randint(0, 1e15)
        block_time = round(np.random.exponential(self.rate), self.sig_digits)
        block = Block(
            block_hash,
            self.chain_tip.height + 1,
            self.chain_tip,
            self.chain_tip.broadcast_time + block_time,
            block_time,
            has_data,
            identifier)
        # print(block, has_data)
        # print("Parent: {}".format(block.parent))
        return block

    def mine(self):
        raise NotImplementedError


class HonestAgent(Agent):
    """
    HonestAgent
    """
    def __init__(self, block_rate):
        super().__init__(block_rate)
        # print('honest: {}'.format(block_rate))

    def mine(self):
        block = self.setup_new_block(BlockType.FullBlock, 'honest')
        return block

    def resolve_fork(self, blocks):
        leftover_blocks = blocks
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
            # print("Honest resolve {}".format(list(map(lambda b: (b.broadcast_time, b.time_from_last), max_ht_blocks))))
            # get rest of blocks
            leftover_blocks = list(filter(
                lambda e: not e.height == max_ht_block.height and e.height,
                leftover_blocks)
            )
            # sort max height blocks by time, ascending
            min_time_blocks = sorted(max_ht_blocks, key=lambda e: e.broadcast_time)
            # print("Min time Honest blocks {}".format(list(map(lambda b: (b.broadcast_time, b.time_from_last), min_time_blocks))))
            while len(min_time_blocks) > 0:
                elt = min_time_blocks.pop(0)
                # print(elt)
                temp_fork_blk = elt
                temp_self_blk = self.chain_tip
                while not temp_fork_blk.hash == temp_self_blk.hash:
                    # break on genesis
                    if temp_fork_blk.height == 0 or temp_self_blk == 0:
                        # print(temp_fork_blk)
                        # print(temp_self_blk)
                        break

                    if temp_fork_blk.height > temp_self_blk.height:
                        # print(temp_fork_blk)
                        # print(temp_self_blk)
                        # honest agent rejects invalid forks (without data)
                        if not temp_fork_blk.has_data:
                            break
                        temp_fork_blk = temp_fork_blk.parent
                    elif temp_fork_blk.height < temp_self_blk.height:
                        temp_self_blk = temp_self_blk.parent
                    else:
                        temp_fork_blk = temp_fork_blk.parent
                        temp_self_blk = temp_self_blk.parent

                # grab next element if block is invalid, otherwise add to tip
                if not temp_fork_blk.has_data:
                    continue
                else:
                    self.add_block(elt)
                    break

            # check if tip was set, otherwise repeat with leftovers
            if self.chain_tip.height == max_ht_block.height:
                break
            else:
                continue


class SPVAgent(Agent):
    """
    SPVAgent

    The SPVAgent always choses among the longest
    chains. If there are ties for longest chains,
    the SPVAgent chooses the one it receives the
    earliest.
    """
    def __init__(self, block_rate):
        super().__init__(block_rate)
        # print('spv: {}'.format(block_rate))

    def mine(self):
        block = self.setup_new_block(BlockType.EmptyBlock, 'spv')
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
    def __init__(self, block_rate):
        super().__init__(block_rate)

    def resolve_fork(self, my_block, other_blocks):
        # ensure spv_block is always indexed first
        return

    def mine(self):
        return self.setup_new_block(BlockType.InvalidBlock, 'attack')

    def process_honest_block(self, block):
        # TODO: Add pre-processing?
        # Resolve fork if honest block
        pass
