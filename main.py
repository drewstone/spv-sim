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
        if honest > 0:
            self.agents.append(HonestAgent(rate / honest))

        if attack > 0:
            self.agents.append(MaliciousAgent(rate / attack))

        if spv > 0:
            self.agents.append(SPVAgent(rate / spv))

    def run(self):
        for _ in range(self.num_rounds):
            # gets mining events from agents
            blocks = [self.agents[i].mine() for i in range(len(self.agents))]
            # print("{}: {}, {}: {}".format(
            #     blocks[0].identifier, blocks[0].broadcast_time,
            #     blocks[1].identifier, blocks[1].broadcast_time))

            # print("Sim run: {}\n".format(
            #     list(map(lambda b: (b.broadcast_time, b.time_from_last), blocks))))
            # select new chains for agents based on blocks
            for inx, a in enumerate(self.agents):
                a.resolve_fork(blocks)

        self.print_stats()

    def print_stats(self):
        stats = {}
        temp_block = self.agents[0].chain_tip
        while temp_block.height > 0:
            if temp_block.identifier in stats:
                stats[temp_block.identifier] += 1
            else:
                stats[temp_block.identifier] = 1

            temp_block = temp_block.parent

        print(stats)

if __name__ == '__main__':
    rate = 60
    honest = 0.90
    attack = 0.0
    spv = 0.10
    num_rounds = 1000
    sim = Simulator(honest, attack, spv, rate, num_rounds)
    sim.run()
