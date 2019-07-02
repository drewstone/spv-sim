from agent import HonestAgent, MaliciousAgent, SPVAgent


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
            # print(list(map(lambda b: (b.time_from_last, b.identifier), blocks)))
            # select new chains for agents based on blocks
            non_malice_decisions = []
            if self.honest:
                self.honest.resolve_fork(blocks)
                non_malice_decisions.append(self.honest.chain_tip)

            if self.spv:
                self.spv.resolve_fork(blocks)
                non_malice_decisions.append(self.spv.chain_tip)

            if self.attack:
                self.attack.resolve_fork(blocks, non_malice_decisions)

        self.print_stats()

    def print_stats(self):
        stats = {}
        attack_blocks = []
        temp_block = self.spv.chain_tip
        while temp_block.height > 0:
            if temp_block.identifier in stats:
                stats[temp_block.identifier] += 1
            else:
                stats[temp_block.identifier] = 1

            if temp_block.identifier == 'attack':
                attack_blocks.append(temp_block)

            temp_block = temp_block.parent

        temp_stats = dict(stats)
        for key in temp_stats:
            stats["{}-frac".format(key)] = (temp_stats[key] * 1.0
                / self.num_rounds)

        print(stats)
        print(list(map(lambda b: b.height, attack_blocks)))
        print(self.attack.unvalidated_spends)

if __name__ == '__main__':
    rate = 60
    honest = 0.70
    attack = 0.20
    spv = 0.10
    num_rounds = 10000
    confirmations = 15
    sim = Simulator(
        honest,
        attack,
        spv,
        rate,
        num_rounds,
        k_conf=confirmations)
    sim.run()
