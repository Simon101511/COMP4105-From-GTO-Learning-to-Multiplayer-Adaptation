import random
from collections import defaultdict
import json

class KuhnTrainer:
    def __init__(self):
        self.node_map = {}

    def train(self, iterations=100000):
        cards = ['J', 'Q', 'K']
        util = 0
        for _ in range(iterations):
            random.shuffle(cards)
            util += self.cfr(cards[:2], "", 1, 1)
        print("Average game value:", util / iterations)
        print("\n--- Strategy Table ---")
        for key in sorted(self.node_map):
            print(self.node_map[key])

    def cfr(self, cards, history, p0, p1):
        plays = len(history)
        player = plays % 2
        opponent = 1 - player

        if self.is_terminal(history):
            return self.payoff(cards, history)

        info_set = cards[player] + history
        node = self.node_map.get(info_set)
        if node is None:
            node = Node(info_set)
            self.node_map[info_set] = node

        strategy = node.get_strategy(p0 if player == 0 else p1)
        util = [0.0 for _ in range(2)]
        node_util = 0

        for a in range(2):  # 0: pass, 1: bet
            next_history = history + ("p" if a == 0 else "b")
            if player == 0:
                util[a] = -self.cfr(cards, next_history, p0 * strategy[a], p1)
            else:
                util[a] = -self.cfr(cards, next_history, p0, p1 * strategy[a])
            node_util += strategy[a] * util[a]

        for a in range(2):
            regret = util[a] - node_util
            node.regret_sum[a] += (p1 if player == 0 else p0) * regret

        return node_util

    def is_terminal(self, history):
        return history in ["pp", "pbp", "bp", "bb", "pbb"]

    def payoff(self, cards, history):
        player_card = cards[0]
        opp_card = cards[1]
        if history == "pp":
            return 1 if player_card > opp_card else -1
        elif history in ["pbp", "bp"]:
            return 1
        elif history in ["pbb", "bb"]:
            return 2 if player_card > opp_card else -2
        return 0


class Node:
    def __init__(self, info_set):
        self.info_set = info_set
        self.regret_sum = [0.0, 0.0]
        self.strategy = [0.0, 0.0]
        self.strategy_sum = [0.0, 0.0]

    def get_strategy(self, realization_weight):
        normalizing_sum = 0
        for a in range(2):
            self.strategy[a] = max(self.regret_sum[a], 0)
            normalizing_sum += self.strategy[a]
        for a in range(2):
            if normalizing_sum > 0:
                self.strategy[a] /= normalizing_sum
            else:
                self.strategy[a] = 0.5
            self.strategy_sum[a] += realization_weight * self.strategy[a]
        return self.strategy

    def get_average_strategy(self):
        avg_strategy = [0.0, 0.0]
        normalizing_sum = sum(self.strategy_sum)
        for a in range(2):
            if normalizing_sum > 0:
                avg_strategy[a] = self.strategy_sum[a] / normalizing_sum
            else:
                avg_strategy[a] = 0.5
        return avg_strategy

    def __str__(self):
        avg_strategy = self.get_average_strategy()
        return f"{self.info_set}: PASS={avg_strategy[0]:.2f}, BET={avg_strategy[1]:.2f}"


if __name__ == "__main__":
    trainer = KuhnTrainer()
    trainer.train(100000)

    # 保存平均策略为 JSON 文件
    strategy_dict = {}
    for info_set, node in trainer.node_map.items():
        strategy = node.get_average_strategy()
        strategy_dict[info_set] = {"PASS": strategy[0], "BET": strategy[1]}

    with open("kuhn_gto_strategy.json", "w") as f:
        json.dump(strategy_dict, f, indent=2)

    print("\n✅ 策略表已保存为 kuhn_gto_strategy.json")
