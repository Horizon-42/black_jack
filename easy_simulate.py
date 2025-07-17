import random
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

# -----------------------------
# Blackjack 环境实现
# -----------------------------

def draw_card():
    card = random.randint(1, 13)
    return min(card, 10)  # J, Q, K 视为 10

def draw_hand():
    return [draw_card(), draw_card()]

def usable_ace(hand):
    return 1 in hand and sum(hand) + 10 <= 21

def sum_hand(hand):
    s = sum(hand)
    if usable_ace(hand):
        return s + 10
    return s

def is_bust(hand):
    return sum_hand(hand) > 21

def score(hand):
    return 0 if is_bust(hand) else sum_hand(hand)

def is_natural(hand):
    return sorted(hand) == [1, 10]

class BlackjackEnv:
    def reset(self):
        self.dealer = draw_hand()
        self.player = draw_hand()
        # Auto-hit if player sum < 12 (avoid meaningless choices)
        while sum_hand(self.player) < 12:
            self.player.append(draw_card())
        return self._get_obs()

    def _get_obs(self):
        return (sum_hand(self.player), self.dealer[0], usable_ace(self.player))

    def step(self, action):
        if action:  # Hit
            self.player.append(draw_card())
            if is_bust(self.player):
                return self._get_obs(), -1.0, True, {}
            else:
                return self._get_obs(), 0.0, False, {}
        else:  # Stand
            while sum_hand(self.dealer) < 17:
                self.dealer.append(draw_card())
            return self._get_obs(), cmp(score(self.player), score(self.dealer)), True, {}

def cmp(a, b):
    return float(a > b) - float(a < b)

# -----------------------------
# Monte Carlo 训练
# -----------------------------

def generate_episode(env, policy, epsilon=0.1):
    episode = []
    state = env.reset()
    while True:
        if random.random() < epsilon or state not in policy:
            action = random.choice([0, 1])
        else:
            action = policy[state]
        next_state, reward, done, _ = env.step(action)
        episode.append((state, action, reward))
        if done:
            break
        state = next_state
    return episode

def mc_control(num_episodes=500000):
    Q = defaultdict(lambda: [0.0, 0.0])
    returns_sum = defaultdict(lambda: [0.0, 0.0])
    returns_count = defaultdict(lambda: [0, 0])
    policy = {}

    for i in range(num_episodes):
        episode = generate_episode(env, policy)
        G = 0
        visited = set()
        for t in reversed(range(len(episode))):
            state, action, reward = episode[t]
            G = reward
            if (state, action) not in visited:
                visited.add((state, action))
                returns_sum[state][action] += G
                returns_count[state][action] += 1
                Q[state][action] = returns_sum[state][action] / returns_count[state][action]
                # policy improvement
                policy[state] = 0 if Q[state][0] > Q[state][1] else 1
    return policy, Q

# -----------------------------
# 策略可视化
# -----------------------------

def plot_policy(policy):
    player_sum = np.arange(12, 22)
    dealer_show = np.arange(1, 11)
    usable = np.zeros((10, 10))
    unusable = np.zeros((10, 10))

    for i, ps in enumerate(player_sum):
        for j, ds in enumerate(dealer_show):
            for ua in [True, False]:
                a = policy.get((ps, ds, ua), -1)
                if ua:
                    usable[i, j] = a
                else:
                    unusable[i, j] = a

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.imshow(usable, cmap='cool')
    ax1.set_title('Usable Ace')
    ax1.set_xlabel('Dealer Showing')
    ax1.set_ylabel('Player Sum')
    ax1.set_xticks(np.arange(10))
    ax1.set_yticks(np.arange(10))
    ax1.set_xticklabels(dealer_show)
    ax1.set_yticklabels(player_sum)

    ax2.imshow(unusable, cmap='cool')
    ax2.set_title('No Usable Ace')
    ax2.set_xlabel('Dealer Showing')
    ax2.set_ylabel('Player Sum')
    ax2.set_xticks(np.arange(10))
    ax2.set_yticks(np.arange(10))
    ax2.set_xticklabels(dealer_show)
    ax2.set_yticklabels(player_sum)

    plt.tight_layout()
    plt.show()

# -----------------------------
# 执行训练与可视化
# -----------------------------

if __name__ == "__main__":
    env = BlackjackEnv()
    policy, Q = mc_control(num_episodes=500000)
    plot_policy(policy)
