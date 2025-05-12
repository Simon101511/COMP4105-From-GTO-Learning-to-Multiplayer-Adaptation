import pandas as pd
import matplotlib.pyplot as plt

# 读取 evaluate_multiplayer_dqn.py 生成的胜率追踪文件
df = pd.read_csv("dqn_multiplayer_winrate_trace.csv")

# 画图
plt.figure(figsize=(10, 6))
plt.plot(df["game_index"], df["cumulative_win_rate"], label="DQN Multiplayer Win Rate", color='purple')
plt.title("DQN Win Rate Over 1000 Games (Multiplayer Mode - Real Data)")
plt.xlabel("Game Index")
plt.ylabel("Cumulative Win Rate")
plt.ylim(0.0, 1.0)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("dqn_multiplayer_winrate_curve_real.png")
plt.close()

print("✅ 图表已保存为：dqn_multiplayer_winrate_curve_real.png")
