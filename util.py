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
        broadcast_time,
        time_from_last,
        is_valid,
        identifier
    ):
        super(Block, self).__init__()
        self.hash = block_hash
        self.height = height
        self.parent = parent
        self.broadcast_time = broadcast_time
        self.time_from_last = time_from_last
        self.is_valid = is_valid
        self.identifier = identifier

    def add_delay(self, delay):
        return Block(
            self.hash,
            self.height,
            self.parent,
            self.broadcast_time + delay,
            self.time_from_last,
            self.is_valid,
            self.identifier,
        )

    def __str__(self):
        return format('Hash: {}, Height: {}, Brdcast Time: {}, Time from last: {}, Identifier: {}'
            .format(self.hash,
                    self.height,
                    self.broadcast_time,
                    self.time_from_last,
                    self.identifier))
