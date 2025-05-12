import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 四个 CSV 文件路径
files = {
    'Aggressive': 'log_gto_vs_aggressive.csv',
    'Bluff': 'log_gto_vs_bluff.csv',
    'Passive': 'log_gto_vs_passive.csv',
    'Random': 'log_gto_vs_random.csv'
}

all_data = []

for opponent, file in files.items():
    df = pd.read_csv(file)

    # 添加 round 编号（如果没有）
    df["round"] = df.index + 1

    # 添加是否赢（GTO是Player1）
    df["is_win"] = df["winner"].apply(lambda x: 1 if x == "Player1" else 0)

    # 计算累计胜率
    df["win_rate"] = df["is_win"].expanding().mean()

    # 添加对手类型
    df["opponent_type"] = opponent

    all_data.append(df)

# 合并所有数据
merged_df = pd.concat(all_data)

# 设置绘图风格
sns.set(style="whitegrid")

# 绘图
plt.figure(figsize=(12, 6))
sns.lineplot(data=merged_df, x="round", y="win_rate", hue="opponent_type")

# 标题和标签
plt.title("GTO vs Opponents: Cumulative Win Rate")
plt.xlabel("Round")
plt.ylabel("Win Rate (Player1)")
plt.ylim(0, 1)
plt.legend(title="Opponent Type")
plt.tight_layout()

plt.show()

# 可视化对每个对手的堆叠走势（折线图）
def plot_stack_progression(csv_file, opponent_name, window=20):
    df = pd.read_csv(csv_file)
    df["round"] = df["round"].astype(int)

    # 使用滚动平均（滑动窗口）平滑曲线
    df["player1_avg"] = df["player1_stack"].rolling(window=window).mean()
    df["opponent_avg"] = df["opponent_stack"].rolling(window=window).mean()

    plt.figure(figsize=(14, 5))
    plt.plot(df["round"], df["player1_avg"], label="Player1 Avg Stack", linewidth=2, alpha=0.8)
    plt.plot(df["round"], df["opponent_avg"], label="Opponent Avg Stack", linewidth=2, alpha=0.8)

    plt.title(f"Smoothed Stack Progression vs {opponent_name} Opponent (Window={window})")
    plt.xlabel("Round")
    plt.ylabel("Stack")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# 依次绘图
plot_stack_progression("log_gto_vs_aggressive.csv", "Aggressive")
plot_stack_progression("log_gto_vs_bluff.csv", "Bluff")
plot_stack_progression("log_gto_vs_passive.csv", "Passive")
plot_stack_progression("log_gto_vs_random.csv", "Random")
