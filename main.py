import numpy as np
from agent import HonestAgent, MaliciousAgent, SPVAgent
from util import print_blocks


class Simulator(object):
    """docstring for Simulator"""
    def __init__(
        self,
        honest,
        attack,
        spv,
        rate,
        num_rounds,
        k_conf=6,
    ):
        super(Simulator, self).__init__()
        self.num_rounds = num_rounds
        self.agents = []
        self.honest_prob = honest
        self.attack_prob = attack
        self.spv_prob = spv
        self.rate = rate

        if honest > 0:
            self.honest = HonestAgent(rate * 1.0 / honest)
            self.agents.append(self.honest)
        else:
            self.honest = False

        if spv > 0:
            self.spv = SPVAgent(rate * 1.0 / spv)
            self.agents.append(self.spv)
        else:
            self.spv = False

        if attack > 0:
            self.attack = MaliciousAgent(rate * 1.0 / attack, k_conf)
            self.agents.append(self.attack)
        else:
            self.attack = False

    def run(self):
        for _ in range(self.num_rounds):
            # gets mining events from agents
            blocks = [self.agents[i].mine() for i in range(len(self.agents))]
            tips = [self.agents[i].chain_tip for i in range(len(self.agents))]
            ### print_blocks('tips', tips)
            # get exponential delays for agents
            # delays = [np.random.exponential(self.rate) for _ in range(len(self.agents))]
            delays = [0.0 for _ in range(len(self.agents))]
            # select new chains for agents based on blocks and delays
            non_malice_decisions = []
            if self.honest:
                blks = [
                    b.add_delay(delays[inx])
                    if b.identifier != 'honest' else b
                    for inx, b in enumerate(blocks)
                ]

                self.honest.resolve_fork(blks)
                non_malice_decisions.append(self.honest.chain_tip)

            if self.spv:
                blks = [
                    b.add_delay(delays[inx])
                    if b.identifier != 'spv' else b
                    for inx, b in enumerate(blocks)
                ]
                self.spv.resolve_fork(blks)
                non_malice_decisions.append(self.spv.chain_tip)

            if self.attack:
                blks = [
                    b.add_delay(delays[inx])
                    if b.identifier != 'attack' else b
                    for inx, b in enumerate(blocks)
                ]
                self.attack.resolve_fork(blks, non_malice_decisions)

        self.print_stats()

    def run_priority_queue(self):
        agents = [self.honest, self.attack, self.spv]
        while True:
            winner = np.random.choice(agents, p=[
                self.honest_prob,
                self.attack_prob,
                self.spv_prob])
            print(winner)

    def print_stats(self):
        stats = {}
        attack_blocks = []
        temp_block = self.spv.chain_tip
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
            temp = self.honest.chain_tip
            for _ in range(len(attack_blocks)):
                honest_blocks.append(temp)
                temp = temp.parent

        temp_stats = dict(stats)
        for key in temp_stats:
            stats["{}-frac".format(key)] = (temp_stats[key] * 1.0
                / self.num_rounds)

        if self.attack:
            print(self.attack.unvalidated_spends)

        print(stats)


if __name__ == '__main__':
    rate = 600
    honest = 0.6
    attack = 0.0
    spv = 0.4
    num_rounds = 10000
    confirmations = 10
    sim = Simulator(
        honest,
        attack,
        spv,
        rate,
        num_rounds,
        k_conf=confirmations)
    sim.run()
