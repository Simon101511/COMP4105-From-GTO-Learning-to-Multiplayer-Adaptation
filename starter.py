import os
import csv
import importlib
import json
from pypokerengine.api.game import setup_config, start_poker
from cfr_gto_agent import CFRGTOAgent
from shared_data import global_action_log
from shared_data import global_action_log

# 确保结构健全
if "data" not in global_action_log:
    global_action_log["data"] = []
if "rounds" not in global_action_log:
    global_action_log["rounds"] = {}

# 创建保存目录
os.makedirs("logs", exist_ok=True)
os.makedirs("training", exist_ok=True)


# 模拟一场游戏，返回 game_log
def simulate_game(opponent_type, rounds=1000):
    import importlib
    from pypokerengine.api.game import setup_config, start_poker
    from shared_data import global_action_log
    import csv
    import os

    print(f"\n▶ Simulating GTO vs {opponent_type.upper()} ({rounds} rounds)...")

    # 清空日志
    global_action_log.clear()
    global_action_log["rounds"] = {}

    global_action_log["data"] = []
    global_action_log["rounds"] = {}

    # 导入对手类
    opponent_module = importlib.import_module(f"opponent_{opponent_type.lower()}")
    Opponent = getattr(opponent_module, "Bot")

    # 导入我们的GTO智能体
    from cfr_gto_agent import CFRGTOAgent
    p1, p2 = CFRGTOAgent(), Opponent()

    config = setup_config(max_round=rounds, initial_stack=1000, small_blind_amount=10, ante=0)
    config.register_player(name="Player1", algorithm=p1)
    config.register_player(name="Opponent", algorithm=p2)

    game_result = start_poker(config, verbose=0)

    # ========== 记录胜率 ==========
    rounds_log = global_action_log.get("rounds", {})
    win_count = 0
    total = 0

    for round_num, round_info in rounds_log.items():
        winner = round_info.get("winner")
        if winner == "Player1":
            win_count += 1
        total += 1

    win_rate = win_count / total if total > 0 else 0
    print(f"\n============================================================")
    print(f"RESULT → GTO vs {opponent_type.upper()}: {win_count}/{total} wins ({win_rate * 100:.2f}%)")
    print(f"============================================================")

    # ========== 保存 CSV ==========
    os.makedirs("logs", exist_ok=True)
    csv_filename = f"logs/log_gto_vs_{opponent_type.lower()}.csv"
    with open(csv_filename, "w", newline="") as csvfile:
        fieldnames = ["round", "player1_stack", "opponent_stack", "winner", "actions"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for round_num, info in rounds_log.items():
            writer.writerow({
                "round": round_num,
                "player1_stack": info.get("player1_stack", ""),
                "opponent_stack": info.get("opponent_stack", ""),
                "winner": info.get("winner", ""),
                "actions": " | ".join(info.get("actions", [])) if info.get("actions") else "no_actions"
            })
    print(f"[✔] Saved detailed game log to: {csv_filename}")

    return win_rate


# 保存游戏日志到 CSV
def save_game_log(name):
    csv_filename = f"logs/log_gto_vs_{name.lower()}.csv"
    with open(csv_filename, "w", newline="") as csvfile:
        fieldnames = ["round", "player1_stack", "opponent_stack", "winner", "actions"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for round_num, round_info in global_action_log.get(name, {}).items():
            writer.writerow({
                "round": round_num,
                "player1_stack": round_info.get("player1_stack", 0),
                "opponent_stack": round_info.get("opponent_stack", 0),
                "winner": round_info.get("winner", ""),
                "actions": round_info.get("actions", "no_actions")
            })

    print(f"[✔] Saved detailed game log to: {csv_filename}")

# 提取训练数据
def extract_training_data():
    print("[🧠] Extracting training data from global_action_log...")

    rounds = global_action_log.get("rounds", {})
    if not rounds:
        print("[!] No rounds found in global_action_log.")
        return

    # 强制转换 round_count 为 int 确保能匹配
    rounds = {int(k): v for k, v in rounds.items()}

    valid_pairs = 0
    for round_num, round_info in rounds.items():
        winner_name = round_info["winner"]

        matched = False
        for entry in reversed(global_action_log["data"]):
            if entry.get("round_count") == round_num and entry["reward"] is None:
                reward = 1 if entry["player_name"] == winner_name else -1
                entry["reward"] = reward
                matched = True
                valid_pairs += 1
                break

        if not matched:
            print(f"[!] No reward matched for round {round_num} | expected winner: {winner_name}")

    if valid_pairs == 0:
        print("[!] No valid state-action pairs found. DQN training skipped.")
        return

    # 保存 JSON 训练数据
    os.makedirs("training", exist_ok=True)
    with open("training/training_data.json", "w") as f:
        json.dump(global_action_log["data"], f, indent=2)

    print(f"[✔] Saved training data to: training/training_data.json")



# ==========================================
# 主程序
if __name__ == "__main__":
    opponent_types = ["PASSIVE", "AGGRESSIVE", "BLUFF", "RANDOM"]

    for opp_type in opponent_types:
        print(f"\n▶ Simulating GTO vs {opp_type} (1000 rounds)...")

        win_rate = simulate_game(opp_type, rounds=1000)

        print("=" * 60)
        print(f"RESULT → GTO vs {opp_type}: {win_rate * 100:.2f}% wins")
        print("=" * 60)

        # 保存对战日志
        save_game_log(opp_type)

    # 提取总的训练数据
    extract_training_data()
