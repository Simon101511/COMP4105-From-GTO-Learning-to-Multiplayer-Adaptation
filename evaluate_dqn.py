# evaluate_dqn.py

from dqn_agent import DQNAgent
from rl_env import RLShortDeckEnv
import torch

# 加载已训练模型
state_dim = 13
action_dim = 3
agent = DQNAgent(state_dim, action_dim)
agent.load_model("trained_dqn.pt")

# 包含所有五种风格的对手
opponent_types = ["gto", "random", "passive", "aggressive", "bluff"]
num_games = 1000

for opponent in opponent_types:
    win_count = 0
    env = RLShortDeckEnv(agent=agent, opponent=opponent)

    for _ in range(num_games):
        state = env.reset()
        done = False
        while not done:
            valid_actions = env.get_valid_actions()
            action = agent.select_action(state, valid_actions)
            next_state, reward, done, _ = env.step(action)
            state = next_state
        if reward > 0:
            win_count += 1

    win_rate = win_count / num_games
    print(f"[🎯] DQN Win Rate vs {opponent.upper()}: {win_count} / {num_games} = {win_rate:.2%}")
