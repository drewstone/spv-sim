import logging
import numpy as np
import copy
import simpy
from agents.honest import HonestAgent
from agents.attack import AttackAgent
from agents.spv import SPVAgent
from util import print_blocks
from network import Network


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
        length=0,
    ):
        super(Simulator, self).__init__()
        self.num_rounds = num_rounds
        self.agents = []
        self.delays = []
        self.agent_probs = []
        self.honest_prob = honest
        self.attack_prob = attack
        self.spv_prob = spv
        self.rate = rate
        self.event_queue = []
        self.env = simpy.Environment()
        self.network = Network(self, self._log)
        self.simulation_length = length

        if honest > 0:
            self.honest = HonestAgent(rate * 1.0 / honest, self.network)
            self.agents.append(self.honest)
            self.agent_probs.append(self.honest_prob)
            self.delays.append(0.0)
        else:
            self.honest = False

        if spv > 0:
            self.spv = SPVAgent(rate * 1.0 / spv, self.network)
            self.agents.append(self.spv)
            self.agent_probs.append(self.spv_prob)
            self.delays.append(0.0)
        else:
            self.spv = False

        if attack > 0:
            self.attack = AttackAgent(rate * 1.0 / attack, k_conf, self.network)
            self.agents.append(self.attack)
            self.agent_probs.append(self.attack_prob)
            self.delays.append(0.0)
        else:
            self.attack = False

    def run_in_rounds(self):
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

    def run(self):
        self.env.process(self._block_generator_process())
        self.env.run(until=self.env.timeout(self.simulation_length))

    def block_generator_process(self):
        while True:
            miner = np.random.choice(self.agents, p=self.agent_probs)
            block = miner.mine()
            yield miner.broadcast_block(self.env, block)

    def send_block(self, sender, receiver, block):
        def send_block_process(self, env):
            receiver.try_add_block(copy.deepcopy(block))
            yield env.timeout(0)

        delay_time = self.network.delays[self.identifier]
        if delay_time <= 0:
            delay_time = 0.0001
        simpy.util.start_delayed(self.env, send_block_process(
            self.env,
            block.add_delay(delay_time)
        ), delay_time)

    def _log(self, text: str):
        """
        Logs the given text with the network_simulation's current timestamp.
        """
        logging.info("Time: " + str(self._env.now) + ", " + text)

if __name__ == '__main__':
    rate = 600
    honest = 0.5
    attack = 0.1
    spv = 0.4
    num_rounds = 10000
    confirmations = 10
    simulation_length = 1000000
    sim = Simulator(
        honest,
        attack,
        spv,
        rate,
        num_rounds,
        k_conf=confirmations,
        length=simulation_length)
    sim.run()
