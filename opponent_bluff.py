import random
from pypokerengine.players import BasePokerPlayer

class Bot(BasePokerPlayer):
    """
    BluffBot：主要策略是诈唬（bluff），无论手牌如何，经常加注。
    - 70% 时候会加注（raise），即使手牌很差
    - 其余时候会随机跟注（call）或弃牌（fold）
    """

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

    def declare_action(self, valid_actions, hole_card, round_state):
        # 70% 诈唬，加注（raise）
        bluff_prob = 0.7

        raise_action = next((a for a in valid_actions if a["action"] == "raise"), None)
        call_action = next((a for a in valid_actions if a["action"] == "call"), None)
        fold_action = next((a for a in valid_actions if a["action"] == "fold"), None)

        if raise_action and random.random() < bluff_prob:
            return "raise", raise_action["amount"]["min"]  # 加注最小金额
        elif call_action:
            return "call", call_action["amount"]  # 跟注
        else:
            return "fold", 0  # 弃牌
