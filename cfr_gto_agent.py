import random
import json
from pypokerengine.players import BasePokerPlayer
from shared_data import global_action_log, training_data

class CFRGTOAgent(BasePokerPlayer):
    def __init__(self, strategy_file="kuhn_gto_strategy.json"):
        with open(strategy_file, "r") as f:
            self.strategy_map = json.load(f)
        self.uuid = None
        self.name = "GTO"

    def receive_game_start_message(self, game_info):
        for player in game_info["seats"]:
            if player["name"] == self.name:
                self.uuid = player["uuid"]
                break

    def receive_round_start_message(self, round_count, hole_card, seats):
        # 可选：你可以记录 hole_card 或 round_count 做更详细的分析
        pass

    def receive_street_start_message(self, street, round_state):
        # 可选：记录当前街道开始的信息，比如街道名称、公共牌等
        pass

    def receive_game_update_message(self, new_action, round_state):
        # 可用于记录对手动作
        pass

    def declare_action(self, valid_actions, hole_card, round_state):
        card = hole_card[0][0]
        history = self.get_action_history(round_state)
        info_set = card + history

        strategy = self.strategy_map.get(info_set, {"call": 1.0})
        actions = list(strategy.keys())
        probs = list(strategy.values())
        action = random.choices(actions, weights=probs)[0]
        amount = self.get_action_amount(valid_actions, action)

        # ✅ 日志记录
        round_count = round_state.get("round_count", -1)
        try:
            stack = next(p["stack"] for p in round_state["seats"] if p["uuid"] == self.uuid)
        except:
            stack = 0
        state_action_pair = {
            "round_count": round_count,
            "player_uuid": self.uuid,
            "player_name": self.name,
            "hole_card": hole_card,
            "community_card": round_state.get("community_card", []),
            "street": round_state.get("street", ""),
            "player_stack": stack,
            "valid_actions": valid_actions,
            "action_taken": action,
            "amount": amount,
            "reward": None
        }
        global_action_log["data"].append(state_action_pair)
        return action, amount

    def get_action_amount(self, valid_actions, action):
        for act in valid_actions:
            if act["action"] == action:
                if action == "raise" and isinstance(act["amount"], dict):
                    return act["amount"].get("min", 0)
                return act["amount"]
        return 0

    def get_action_history(self, round_state):
        try:
            history = ""
            actions = round_state.get("action_histories", {})
            for street in ["preflop", "flop", "turn", "river"]:
                for act in actions.get(street, []):
                    if act["player_uuid"] == self.uuid:
                        history += act["action"][0].lower()
            return history
        except:
            return ""

    def receive_round_result_message(self, winners, hand_info, round_state):
        try:
            for entry in reversed(global_action_log["data"]):
                if entry["player_uuid"] == self.uuid and entry["reward"] is None:
                    reward = 1 if any(w["uuid"] == self.uuid for w in winners) else -1
                    entry["reward"] = reward
                    break
        except Exception as e:
            print(f"[ERROR] reward assignment failed: {e}")

        # ✅ 添加回合级别的日志记录
        round_count = round_state.get("round_count", -1)
        try:
            player_stack = next(p["stack"] for p in round_state["seats"] if p["uuid"] == self.uuid)
            opponent_stack = next(p["stack"] for p in round_state["seats"] if p["uuid"] != self.uuid)
        except:
            player_stack = 0
            opponent_stack = 0
        global_action_log["rounds"][round_count] = {
            "player1_stack": player_stack,
            "opponent_stack": opponent_stack,
            "winner": winners[0]["name"] if winners else "",
            "actions": [f'{a["action"]}:{a.get("amount", 0)}' for a in round_state.get("action_histories", {}).get("preflop", [])]
           + [f'{a["action"]}:{a.get("amount", 0)}' for a in round_state.get("action_histories", {}).get("flop", [])]
           + [f'{a["action"]}:{a.get("amount", 0)}' for a in round_state.get("action_histories", {}).get("turn", [])]
           + [f'{a["action"]}:{a.get("amount", 0)}' for a in round_state.get("action_histories", {}).get("river", [])]

        }
