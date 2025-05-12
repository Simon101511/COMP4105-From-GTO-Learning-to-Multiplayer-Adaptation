import numpy as np
import torch
# 在 rl_env.py 的顶部添加
from shared_data import ShortDeckSimulator

class RLShortDeckEnv:
    def __init__(self, agent, opponent, max_rounds=1000):
        from cfr_gto_agent import CFRGTOAgent  # 避免循环导入问题
        from opponent_passive import Bot  # 可换成任意你现有的对手
        from shared_data import ShortDeckSimulator  # 你自己定义或包装的对局模拟器

        self.agent = agent
        self.opponent = opponent
        self.simulator = ShortDeckSimulator()
        self.simulator.set_players(agent, opponent)
        self.max_rounds = max_rounds
        self.round = 0
        self.done = False

    def get_state_tensor(self):
        state = self.simulator._get_state()
        round_state = state.get("round_state", {})
        seats = round_state.get("seats", [])
        community = round_state.get("community_card", [])
        player1 = next((p for p in seats if p.get("name") == "Player1"), {})
        opponent = next((p for p in seats if p.get("name") != "Player1"), {})

        community_count = len(community)
        is_flop = int(community_count >= 3)
        is_turn = int(community_count >= 4)
        is_river = int(community_count == 5)

        chip_diff = (player1.get("stack", 0) - opponent.get("stack", 0)) / 1000.0

        histories = round_state.get("action_histories", {})
        all_actions = sum(len(v) for v in histories.values())
        p1_actions = sum(
            sum(1 for act in v if act.get("player_name") == "Player1")
            for v in histories.values()
        )
        opp_actions = all_actions - p1_actions

        is_dealer = int(round_state.get("dealer_btn") == 0)
        pot = round_state.get("pot", {}).get("main", 0) / 1000.0

        return [
            player1.get("stack", 0),  # 1: player_stack
            player1.get("bet", 0),  # 2: player_bet
            opponent.get("stack", 0),  # 3: opp_stack
            opponent.get("bet", 0),  # 4: opp_bet
            round_state.get("pot", {}).get("main", 0),  # 5: pot_size
            is_flop,  # 6
            is_turn,  # 7
            is_river,  # 8
            0.0,  # 9: hand_strength placeholder
            0.0,  # 10: hand_rank placeholder
            len(seats),  # 11: num_players
            sum(1 for p in seats if p.get("state") == "participating"),  # 12: num_active
            0.0  # 13: last_action placeholder
        ]

    def reset(self):
        self.simulator = ShortDeckSimulator()  # 重建模拟器
        self.simulator.set_players(self.agent, self.opponent)
        state = self.simulator.get_state_tensor()
        return state

    def step(self, action):
        reward, done = self.simulator.play_step(action)
        self.round += 1
        self.done = done or self.round >= self.max_rounds
        obs = self._get_obs()
        return obs, reward, self.done, {}

    def _get_obs(self):
        # 示例状态：玩家堆叠、对手堆叠、社区牌、手牌等（自己定）
        state = self.simulator.get_state_tensor()
        return torch.tensor(state, dtype=torch.float32)

    def get_valid_actions(self):
        return self.simulator.get_legal_actions()

from pypokerengine.players import BasePokerPlayer

class DQNPlayerWrapper(BasePokerPlayer):
    def __init__(self, dqn_agent):
        self.agent = dqn_agent
        self.name = None  # 会在注册时赋值

    def set_uuid(self, uuid):
        self.uuid = uuid

    def declare_action(self, valid_actions, hole_card, round_state):
        seats = round_state["seats"]
        # 找出自己的 player 实例（根据 uuid 匹配）
        player = next((p for p in seats if p["uuid"] == self.uuid), None)
        if player is None:
            raise ValueError(f"Cannot find player with uuid: {self.uuid}")

        others = [p for p in seats if p["uuid"] != self.uuid]
        opponent = others[0] if others else {"stack": 0, "bet": 0}

        community = round_state.get("community_card", [])
        is_flop = int(len(community) >= 3)
        is_turn = int(len(community) >= 4)
        is_river = int(len(community) == 5)

        pot = round_state.get("pot", {})
        main_pot = pot["main"] if isinstance(pot, dict) and "main" in pot else 0

        state_vector = [
            float(player.get("stack", 0)),
            float(player.get("bet", 0)),
            float(opponent.get("stack", 0)),
            float(opponent.get("bet", 0)),
            float(main_pot.get("main", 0)),  # 如果你不确定是否 float
            float(is_flop),
            float(is_turn),
            float(is_river),
            0.0,  # hand_strength
            0.0,  # hand_rank
            float(len(seats)),
            float(sum(1 for p in seats if p.get("state") == "participating")),
            0.0  # last_action
        ]

        state_tensor = torch.tensor(state_vector, dtype=torch.float32).unsqueeze(0)
        with torch.no_grad():
            q_values = self.agent.policy_net(state_tensor).squeeze().numpy()

        action_index = np.argmax(q_values)
        legal_actions = [act["action"] for act in valid_actions]
        selected_action = legal_actions[action_index % len(legal_actions)]
        action_info = next(a for a in valid_actions if a["action"] == selected_action)
        return selected_action, action_info["amount"]


    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, new_action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

