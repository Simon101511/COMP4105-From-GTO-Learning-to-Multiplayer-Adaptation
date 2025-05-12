# 🃏 Poker AI: From GTO Learning to Multiplayer Reinforcement Adaptation

This project implements an intelligent poker-playing agent that begins from game-theoretic optimal (GTO) strategies and evolves through deep reinforcement learning to handle both 1v1 and multiplayer short-deck poker scenarios.

> Developed for COMP4105 - Designing Intelligent Agents (Spring 2025)

---

## 📌 Project Highlights

- ✅ **GTO Strategy (CFR)** in Kuhn Poker
- ✅ **DQN Agent** for 1v1 short-deck poker
- ✅ **Multiplayer Extension** with 6–8 random players
- ✅ **Custom Opponent Types**: Passive, Aggressive, Bluff, Random
- ✅ **Evaluation & Visualization**: win rate, profit trend, bar charts
- ✅ **Average ROI in multiplayer**: 102.28%

---

---

## 🧠 Key Techniques

- **CFR / CFR+** for GTO computation in simplified settings
- **DQN (Deep Q-Network)** with epsilon-greedy, target net, replay buffer
- **State representation**: 13-dimensional vector encoding stack, phase, players
- **Logging & charting**: cumulative win rate, average profit per type

---

## 📊 Sample Results

- DQN vs Passive: **65.2% win rate**
- DQN vs GTO: **52.1% win rate**
- Multiplayer ROI: **+102.28 chips per hand**
- Profit chart: `dqn_avg_profit_bar_real.png`

---

## 🛠 Requirements

- Python 3.8+
- `PyTorch`
- `pypokerengine`
- `matplotlib`
- `pandas`, `numpy`

Install dependencies:
```bash
pip install -r requirements.txt


