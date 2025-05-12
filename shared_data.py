# shared_data.py

import random
import torch
import numpy as np

ACTION_SPACE = ["fold", "call", "raise"]

# 用于记录所有回合的动作（训练数据）
global_action_log = {
    "rounds": {},
    "data": []  # ✅ 这一行必须保留，避免 KeyError
}

# 强化学习训练数据
training_data = []

# 堆叠信息、公共牌记录（可视化用）
global_stack_info = {}
global_community_cards = {}

# 自定义模拟器
class ShortDeckSimulator:
    def __init__(self):
        self.reset()
        self.round_state = {}

    def set_players(self, agent, opponent):
        self.agent = agent
        self.opponent = opponent

    def reset(self):
        self.player_stack = 1000
        self.opponent_stack = 1000
        self.round = 0
        self.done = False
        self.history = []
        self.round_state = {
            "street": "preflop",
            "seats": [{"stack": self.player_stack}, {"stack": self.opponent_stack}],
            "dealer_pos": 0,
            "pot": {"main": 0}
        }

        # ✅ 初始化 action_history
        self.action_history = {
            "Player1": [],
            "Opponent": []
        }
        return self._get_state()

    def step(self, action):
        self.round += 1
        win = random.random() < 0.51
        reward = 1 if win else -1
        if win:
            self.player_stack += 10
            self.opponent_stack -= 10
        else:
            self.player_stack -= 10
            self.opponent_stack += 10
        self.history.append((self.round, self.player_stack, self.opponent_stack))
        self.done = self.round >= 1000
        self.round_state["seats"] = [{"stack": self.player_stack}, {"stack": self.opponent_stack}]

        return self._get_state(), reward, self.done, {}

    def play_step(self, action):
        # 模拟强化学习的最小接口
        win = random.random() < 0.51
        reward = 1 if win else -1
        if win:
            self.player_stack += 10
            self.opponent_stack -= 10
        else:
            self.player_stack -= 10
            self.opponent_stack += 10
        self.round += 1
        self.done = self.round >= 1000
        return reward, self.done

    def get_state_tensor(self):
        if not self.round_state or "seats" not in self.round_state:
            # 提供默认维度为13的0向量
            return torch.zeros(13)

        seats = self.round_state.get("seats", [])
        player1 = seats[0] if len(seats) > 0 else {}
        opponent = seats[1] if len(seats) > 1 else {}

        player_stack = player1.get("stack", 0)
        player_bet = player1.get("bet", 0)
        opp_stack = opponent.get("stack", 0)
        opp_bet = opponent.get("bet", 0)
        pot_size = self.round_state.get("pot", {}).get("main", 0)

        street = self.round_state.get("street", "")
        is_flop = int(street == "flop")
        is_turn = int(street == "turn")
        is_river = int(street == "river")

        hand_strength = 0.0  # 可以后续补充真实值
        hand_rank = 0.0  # 可以后续补充真实值

        num_players = len(seats)
        num_active = sum(1 for p in seats if p.get("state") == "participating")
        last_action = 0.0  # 可以后续编码

        state = [
            player_stack, player_bet, opp_stack, opp_bet,
            pot_size, is_flop, is_turn, is_river,
            hand_strength, hand_rank
        ]

        # 新增的3项（确保它们在类中存在或能取到）
        num_players = len(self.round_state["seats"])
        num_active = sum(1 for p in self.round_state["seats"] if p["state"] == "participating")
        last_action = self._encode_last_action(self.round_state.get("action_histories", {}))

        # 拼接新状态向量
        state.extend([num_players, num_active, last_action])

        return torch.tensor(state, dtype=torch.float32)

    def _encode_last_action(self, action):
        action_map = {
            "fold": 0,
            "call": 1,
            "raise": 2,
            "allin": 3,
            "check": 4,
            # 如果你有其他动作，也可以继续加
        }
        return action_map.get(action, -1)  # -1 表示未知动作，或者你可以设为 0

    def get_legal_actions(self):
        return ["fold", "call", "raise"]

    def _get_state(self):
        # 提供兼容旧代码的10维状态向量
        return [
            self.player_stack / 1000.0,
            self.opponent_stack / 1000.0,
            (self.player_stack - self.opponent_stack) / 1000.0,
            self.round / 1000.0,
            0.0,  # dummy for community card count
            0.0,  # dummy for dealer position
            0.0,  # pot
            0.0, 0.0, 0.0  # reserved
        ]
