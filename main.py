from agent import HonestAgent, MaliciousAgent, SPVAgent


class Simulator(object):
    """docstring for Simulator"""
    def __init__(self, honest, attack, spv, rate, num_rounds, gamma=0.0):
        super(Simulator, self).__init__()
        self.honest_rate = honest * rate
        self.attack_rate = attack * rate
        self.spv_rate = spv * rate
        self.num_rounds = num_rounds
        self.gamma = gamma

        self.agents = []
        if self.honest_rate > 0:
            self.agents.append(HonestAgent(self.honest_rate))

        if self.attack_rate > 0:
            self.agents.append(MaliciousAgent(self.attack_rate))

        if self.spv_rate > 0:
            self.agents.append(SPVAgent(self.spv_rate))

    def run(self):
        while True:
            # gets mining events from agents
            blocks = [self.agents[i].mine() for i in range(len(self.agents))]
            sorted_blocks = sorted(blocks, key=lambda b: b.time)
            # select new chains for agents based on blocks
            for inx, a in enumerate(self.agents):
                a.resolve_fork(sorted_blocks)


if __name__ == '__main__':
    rate = 60
    honest = 0.51
    attack = 0.0
    spv = 0.49
    num_rounds = 100
    sim = Simulator(honest, attack, spv, rate, num_rounds)
    sim.run()
    temp_block = sim.honest.chain_tip
    while temp_block is not None:
        print(temp_block)
        temp_block = temp_block.parent
