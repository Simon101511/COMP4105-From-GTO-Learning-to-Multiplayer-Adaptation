import random
from pypokerengine.players import BasePokerPlayer

class Bot(BasePokerPlayer):

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
        """ 60% 概率加注，否则 Call，尽量不 Fold """
        raise_action = next((a for a in valid_actions if a["action"] == "raise"), None)
        call_action = next((a for a in valid_actions if a["action"] == "call"), None)
        fold_action = next((a for a in valid_actions if a["action"] == "fold"), None)

        if raise_action and random.random() < 0.6:
            return "raise", raise_action["amount"]["min"]
        elif call_action:
            return "call", call_action["amount"]
        else:
            return "fold", 0
