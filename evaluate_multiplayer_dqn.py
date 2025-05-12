import random
import pandas as pd
import numpy as np
from collections import defaultdict
from pypokerengine.api.game import setup_config, start_poker
from dqn_agent import DQNAgent, ACTION_SPACE
from rl_env import RLShortDeckEnv, DQNPlayerWrapper
from opponent_aggressive import Bot as AggressivePlayer
from opponent_passive import Bot as PassivePlayer
from opponent_random import Bot as RandomPlayer
from opponent_bluff import Bot as BluffPlayer

# 所有可能的对手类型
opponent_classes = [AggressivePlayer, PassivePlayer, RandomPlayer, BluffPlayer]

# 初始化共享环境（用于DQN状态编码）
shared_env = RLShortDeckEnv(agent=None, opponent=None)

# 初始化 DQN 智能体
agent = DQNAgent(state_dim=13, action_dim=len(ACTION_SPACE))
agent.env = shared_env
agent.load_model("trained_dqn.pt")

# 多场对局参数
num_games = 1000
total_profit = 0
wins = 0
win_rate_trace = []

# ✅ 新增：每类对手的盈利记录
profit_by_type = defaultdict(list)

for game_idx in range(num_games):
    num_players = random.randint(6, 8)
    dqn_pos = random.randint(0, num_players - 1)

    seats = []
    current_opponents = []

    for i in range(num_players):
        if i == dqn_pos:
            seats.append(("dqn", DQNPlayerWrapper(agent)))
        else:
            opponent_class = random.choice(opponent_classes)
            opponent_instance = opponent_class()
            seats.append((f"bot_{i}_{game_idx}", opponent_instance))
            # ✅ 记录每类对手类型（只按类名统计）
            opponent_name = opponent_class.__name__.replace("Bot", "").replace("Player", "")
            current_opponents.append(opponent_name)

    config = setup_config(max_round=1, initial_stack=100, small_blind_amount=5)
    for player_name, player_instance in seats:
        config.register_player(name=player_name, algorithm=player_instance)

    try:
        result = start_poker(config, verbose=0)
        dqn_stack = result["players"][dqn_pos]["stack"]
        profit = dqn_stack - 100
        total_profit += profit
        if profit > 0:
            wins += 1
        win_rate_trace.append(wins / (game_idx + 1))
        for opp_type in current_opponents:
            profit_by_type[opp_type].append(profit)
    except Exception as e:
        print(f"[❌] Error in game {game_idx}: {e}")
        win_rate_trace.append(wins / (game_idx + 1))

# 评估结果打印
avg_profit = total_profit / num_games
win_rate = wins / num_games

print(f"\n[📊] Multiplayer Evaluation ({num_games} Games)")
print(f"[🎯] Average Profit: {avg_profit:.2f}")
print(f"[🏆] Win Rate: {win_rate:.2%}")

# ✅ 保存胜率趋势为 CSV
df = pd.DataFrame({
    "game_index": list(range(1, num_games + 1)),
    "cumulative_win_rate": win_rate_trace
})
df.to_csv("dqn_multiplayer_winrate_trace.csv", index=False)
print("[📁] Saved win rate trend to dqn_multiplayer_winrate_trace.csv")

# ✅ 保存每类对手收益为 CSV
profit_summary = {
    "opponent_type": [],
    "average_profit": []
}
for opp_type, profits in profit_by_type.items():
    profit_summary["opponent_type"].append(opp_type)
    profit_summary["average_profit"].append(np.mean(profits))

df_profit = pd.DataFrame(profit_summary)
df_profit.to_csv("dqn_avg_profit_by_type.csv", index=False)
print("[📁] Saved per-opponent profit to dqn_avg_profit_by_type.csv")
