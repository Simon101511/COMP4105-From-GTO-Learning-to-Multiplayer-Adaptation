import torch
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque
from rl_env import RLShortDeckEnv
from dqn_agent import DQNAgent
from shared_data import ACTION_SPACE  # ⬅️ 确保你这里定义了 ['fold', 'call', 'raise']

# 参数
EPISODES = 5000
GAMMA = 0.99
LR = 0.001
BATCH_SIZE = 64
MEMORY_SIZE = 5000
TARGET_UPDATE = 10

# 初始化
state_dim = 13
action_dim = len(ACTION_SPACE)
agent = DQNAgent(state_dim, action_dim)
env = RLShortDeckEnv(agent=agent, opponent=None)
memory = deque(maxlen=MEMORY_SIZE)
optimizer = optim.Adam(agent.policy_net.parameters(), lr=LR)
loss_fn = nn.MSELoss()

def train_step():
    if len(memory) < BATCH_SIZE:
        return
    batch = random.sample(memory, BATCH_SIZE)
    states, actions, rewards, next_states, dones = zip(*batch)

    # 保证每个 state 是 [13] 的 tensor
    states = torch.stack([s if isinstance(s, torch.Tensor) else torch.tensor(s, dtype=torch.float32) for s in states])
    next_states = torch.stack([s if isinstance(s, torch.Tensor) else torch.tensor(s, dtype=torch.float32) for s in next_states])

    action_map = {"fold": 0, "call": 1, "raise": 2}
    actions = torch.tensor([action_map[a] if isinstance(a, str) else a for a in actions], dtype=torch.long)

    rewards = torch.tensor(rewards, dtype=torch.float32)
    dones = torch.tensor(dones, dtype=torch.float32)

    q_values = agent.policy_net(states).gather(1, actions.unsqueeze(1)).squeeze()
    next_q = agent.target_net(next_states).max(1)[0]
    target = rewards + GAMMA * next_q * (1 - dones)

    loss = loss_fn(q_values, target.detach())
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

# 主训练循环
for episode in range(EPISODES):
    state = env.reset()
    total_reward = 0
    done = False

    while not done:
        valid_actions = env.get_valid_actions()
        action = agent.select_action(state, valid_actions)
        next_state, reward, done, _ = env.step(action)

        memory.append((state, action, reward, next_state, done))
        train_step()
        state = next_state
        total_reward += reward

    if episode % TARGET_UPDATE == 0:
        agent.target_net.load_state_dict(agent.policy_net.state_dict())

    print(f"[Episode {episode}] Total reward: {total_reward}")

# 保存模型
agent.save_model("trained_dqn.pt")
