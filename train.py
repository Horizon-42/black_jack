import random
from collections import defaultdict
from utils import plot_policy_sns
from tqdm import tqdm
from enum import Enum

from env import *



# -----------------------------
# Monte Carlo with Split + Double
# -----------------------------


def generate_sub_episodes(env: BlackjackEnv, policy, epsilon=0.01, learning=True):
    env.reset()
    sub_episodes = []

    for i in range(len(env.hands)):
        env.current = i
        hand = env.hands[i]
        finished = env.finished[i]
        episode = []

        if is_blackjack(hand, i):
            sub_episodes.append([])
            continue

        while not finished:
            state = BaseState(
                sum_hand(hand),
                env.dealer[1],  # deal 第二张牌是明牌
                usable_ace(hand),
                env.can_split(),
                can_double(hand)
            )

            if (learning and random.random() < epsilon) or (state not in policy):
                action = random.choice(env.get_possible_actions())
            else:
                action = policy[state]

            episode.append((state, action))
            next_state, _, done, _ = env.step(action)

            finished = env.finished[i]
            hand = env.hands[i]

        sub_episodes.append(episode)

    # 所有手牌打完后，dealer处理，返回每手 reward
    rewards = env.finish()
    logging.debug(sub_episodes)
    logging.debug(rewards)
    return sub_episodes, rewards


def mc_control(num_episodes=200000, epsilon=0.01):
    Q: dict[BaseState, dict[Action, float]] = defaultdict(
        lambda: defaultdict(float))
    returns_sum: dict[BaseState, dict[Action, float]] = defaultdict(
        lambda: defaultdict(float))
    returns_count: dict[BaseState, dict[Action, int]
                        ] = defaultdict(lambda: defaultdict(float))
    policy: dict[BaseState, Action] = {}

    avg_rewards = 0
    win_rate = 0
    sub_episodes_count = 0
    for i in tqdm(range(num_episodes)):
        sub_episodes, rewards = generate_sub_episodes(env, policy, epsilon)

        avg_rewards += sum(rewards)
        win_rate += sum(1 for r in rewards if r > 0)
        sub_episodes_count += len(rewards)

        for episode, reward in zip(sub_episodes, rewards):
            visited = set()
            for state, action in episode:
                if (state, action) not in visited:
                    visited.add((state, action))
                    returns_sum[state][action] += reward
                    returns_count[state][action] += 1
                    Q[state][action] = returns_sum[state][action] / \
                        returns_count[state][action]
                    best_action = max(
                        Q[state], key=lambda a: Q[state][a])
                    policy[state] = best_action

    avg_rewards /= sub_episodes_count
    win_rate /= sub_episodes_count
    print(
        f"Finish {sub_episodes_count} sub episodes, avg rwd:{avg_rewards}, win_rate:{win_rate}")
    return policy, Q


def test(env: BlackjackEnv, policy: dict, num_episodes=10000):
    avg_rewards = 0
    win_rate = 0
    sub_episodes_count = 0

    for i in range(num_episodes):
        _, rewards = generate_sub_episodes(
            env, policy, learning=False)  # use optimal policy

        avg_rewards += sum(rewards)
        win_rate += sum(1 for r in rewards if r > 0)
        sub_episodes_count += len(rewards)

    avg_rewards /= sub_episodes_count
    win_rate /= sub_episodes_count
    print(
        f"Finish {sub_episodes_count} sub episodes, avg rwd:{avg_rewards}, win_rate:{win_rate}")


if __name__ == "__main__":
    import os
    import pickle

    env: BlackjackEnv = BlackjackEnv()
    policy, Q = mc_control(num_episodes=300000, epsilon=0.3)
    print("Finish training.")

    test(env, policy, 100000)

    name = "MCE3"
    save_dir = f"results/agent_{name}/"
    os.makedirs(save_dir, exist_ok=True)
    with open(os.path.join(save_dir, "policy.pkl"), "wb") as f:
        pickle.dump(dict(policy), f)
    with open(os.path.join(save_dir, "Q.pkl"), "wb") as f:
        Q = dict(Q)
        for k in Q:
            Q[k] = dict(Q[k])
        pickle.dump(Q, f)
