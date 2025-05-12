import pandas as pd
import matplotlib.pyplot as plt

# 读取真实数据
df = pd.read_csv("dqn_avg_profit_by_type.csv")

# 检查数据有效性
if df.empty or "opponent_type" not in df.columns or "average_profit" not in df.columns:
    raise ValueError("❌ 数据文件缺失有效列名或为空，请确认 evaluate_multiplayer_dqn.py 是否成功运行")

# 可选：设置固定对手类型顺序（防止顺序乱）
desired_order = ["Aggressive", "Passive", "Random", "Bluff"]
df = df.set_index("opponent_type").reindex(desired_order).dropna().reset_index()

# 绘制柱状图
plt.figure(figsize=(8, 5))
bars = plt.bar(df["opponent_type"], df["average_profit"], color='mediumseagreen')
plt.title("DQN Average Profit vs Opponent Types\n(Multiplayer Mode - Real Data)")
plt.ylabel("Average Profit per Game")
plt.grid(axis="y", linestyle="--", alpha=0.7)

# 添加标签
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, yval + 0.1, f"{yval:.1f}", ha='center', va='bottom')

plt.tight_layout()
plt.savefig("dqn_avg_profit_bar_real.png")
plt.close()

print("✅ 图表已保存为：dqn_avg_profit_bar_real.png")
