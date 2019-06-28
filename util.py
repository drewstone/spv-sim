from enum import Enum


class BlockType(Enum):
    InvalidBlock = 0
    EmptyBlock = 1
    FullBlock = 2
    HeaderOnly = 3


class Block(object):
    """docstring for Block"""
    def __init__(self, block_hash, height, parent, time, has_data, identifier):
        super(Block, self).__init__()
        self.hash = block_hash
        self.height = height
        self.parent = parent
        self.time = time
        self.has_data = has_data
        self.identifier = identifier

    def __str__(self):
        return format('Hash: {}\nHeight: {}\nTime: {}\nIdentifier: {}\n'
            .format(self.hash,
                    self.height,
                    self.time,
                    self.identifier))
