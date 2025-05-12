import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np
from collections import deque
from shared_data import ACTION_SPACE


class GTO_DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(GTO_DQN, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, output_dim)
        )

    def forward(self, x):
        return self.model(x)


class DQNAgent:
    def __init__(self, state_dim, action_dim, lr=1e-3, gamma=0.99, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995):
        self.state_dim = state_dim
        self.action_dim = action_dim

        self.policy_net = GTO_DQN(state_dim, action_dim)
        self.target_net = GTO_DQN(state_dim, action_dim)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()

        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=lr)
        self.criterion = nn.MSELoss()

        self.memory = deque(maxlen=5000)
        self.batch_size = 64

        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

    def save_model(self, path):
        torch.save(self.policy_net.state_dict(), path)

    def load_model(self, path):
        self.policy_net.load_state_dict(torch.load(path))
        self.policy_net.eval()

    def select_action(self, state, valid_actions, epsilon=0.1):
        self.policy_net.eval()
        if np.random.rand() < epsilon:
            return random.choice(valid_actions)
        else:
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            with torch.no_grad():
                q_values = self.policy_net(state_tensor).squeeze().numpy()
            action_indices = {a: i for i, a in enumerate(ACTION_SPACE)}
            valid_q_values = {a: q_values[action_indices[a]] for a in valid_actions}
            return max(valid_q_values, key=valid_q_values.get)

    def remember(self, state, action, reward, next_state, done):
        action_indices = {a: i for i, a in enumerate(ACTION_SPACE)}
        self.memory.append((state, action_indices[action], reward, next_state, done))

    def act(self, state):
        if np.random.rand() < self.epsilon:
            return random.randrange(self.action_dim)
        state = torch.FloatTensor(state).unsqueeze(0)
        with torch.no_grad():
            q_values = self.policy_net(state)
        return torch.argmax(q_values).item()

    def replay(self):
        if len(self.memory) < self.batch_size:
            return

        batch = random.sample(self.memory, self.batch_size)
        state, action, reward, next_state, done = zip(*batch)

        state = torch.FloatTensor(state)
        next_state = torch.FloatTensor(next_state)
        action = torch.LongTensor(action)
        reward = torch.FloatTensor(reward)
        done = torch.BoolTensor(done)

        current_q = self.policy_net(state).gather(1, action.unsqueeze(1)).squeeze()
        next_q = self.target_net(next_state).max(1)[0]
        target_q = reward + (1 - done.float()) * self.gamma * next_q

        loss = self.criterion(current_q, target_q.detach())

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def update_target(self):
        self.target_net.load_state_dict(self.policy_net.state_dict())

    def save(self, path="dqn_model.pt"):
        torch.save(self.policy_net.state_dict(), path)

    def load(self, path="dqn_model.pt"):
        self.policy_net.load_state_dict(torch.load(path))
        self.update_target()
