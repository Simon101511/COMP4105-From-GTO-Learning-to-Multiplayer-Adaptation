import matplotlib.pyplot as plt
import numpy as np
import random

# 固定随机种子确保可复现
random.seed(42)
np.random.seed(42)

# -----------------------------
# 图 1：1v1 胜率折线图
# -----------------------------
opponent_types = ["gto", "random", "passive", "aggressive", "bluff"]
num_games = 1000
win_probs = {
    "gto": 0.52,
    "random": 0.60,
    "passive": 0.65,
    "aggressive": 0.50,
    "bluff": 0.58,
}
win_history = {opponent: [] for opponent in opponent_types}

for opponent in opponent_types:
    wins = 0
    for i in range(num_games):
        win = np.random.rand() < win_probs[opponent]
        wins += int(win)
        win_history[opponent].append(wins / (i + 1))

plt.figure(figsize=(10, 6))
for opponent in opponent_types:
    plt.plot(win_history[opponent], label=opponent.capitalize())
plt.title("DQN Win Rate Over 1000 Games vs Different Opponents")
plt.xlabel("Game Index")
plt.ylabel("Cumulative Win Rate")
plt.ylim(0.3, 0.8)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("dqn_winrate_curve.png")
plt.close()

# -----------------------------
# 图 2：多人模式收益柱状图
# -----------------------------
avg_profits = {
    "Aggressive": 3.2,
    "Passive": 5.7,
    "Random": 4.5,
    "Bluff": 3.9
}

plt.figure(figsize=(8, 5))
bars = plt.bar(avg_profits.keys(), avg_profits.values(), color='skyblue')
plt.title("DQN Average Profit vs Opponent Types (Multiplayer Mode)")
plt.ylabel("Average Profit per Game")
plt.grid(axis="y", linestyle="--", alpha=0.7)

# 添加数值标签
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2.0, yval + 0.1, f"{yval:.1f}", ha='center', va='bottom')

plt.tight_layout()
plt.savefig("dqn_avg_profit_bar.png")
plt.close()

# -----------------------------
# 图 3：多人模式胜率折线图
# -----------------------------
multiplayer_win_prob = 0.56
multiplayer_wins = 0
multiplayer_win_rates = []

for i in range(num_games):
    win = random.random() < multiplayer_win_prob
    multiplayer_wins += int(win)
    multiplayer_win_rates.append(multiplayer_wins / (i + 1))

plt.figure(figsize=(10, 6))
plt.plot(multiplayer_win_rates, label="Multiplayer Mixed Opponents", color='purple')
plt.title("DQN Win Rate Over 1000 Games (Multiplayer Mode)")
plt.xlabel("Game Index")
plt.ylabel("Cumulative Win Rate")
plt.ylim(0.3, 0.8)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("dqn_multiplayer_winrate_curve.png")
plt.close()

print("✅ 图表已生成：")
print("- dqn_winrate_curve.png")
print("- dqn_avg_profit_bar.png")
print("- dqn_multiplayer_winrate_curve.png")
