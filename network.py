import copy


class Network(object):
    """docstring for Network"""
    def __init__(self, simulation, log):
        super(Network, self).__init__()
        self.sim = simulation
        self._log = log

    def add_miner(self, miner, delay):
        self.miners[miner.identifier] = miner
        self.delays[miner.identifier] = delay

    def broadcast_block(self, block):
        for key in self.miners:
            if block.identifier != key:
                self.simulation.send_block(block.identifier, key, block)
