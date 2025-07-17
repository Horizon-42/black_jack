import random
from collections import defaultdict
from utils import plot_policy_sns
from tqdm import tqdm
from enum import Enum

from env import *
import numpy as np
from random import choice


# -----------------------------
# Monte Carlo with Split + Double
# -----------------------------


def generate_sub_episodes(env: BlackjackEnv, policy: dict, epsilon: float):
    env.reset()
    sub_episodes = []
    state_action_space: dict[BaseState, list[Action]] = {}

    for i in range(len(env.hands)):
        env.current = i
        hand = env.hands[i]
        finished = env.finished[i]
        episode = []

        if is_blackjack(hand, i):
            sub_episodes.append([])
            continue

        while not finished:
            state = env.get_state()

            possible_actions = env.get_possible_actions()

            if state not in policy or np.random.rand() < epsilon:
                action = choice(possible_actions)
            else:
                action = policy[state]

            if state not in state_action_space:
                state_action_space[state] = possible_actions

            logging.debug(f"running...{state}, {action}")
            episode.append((state, action))
            next_state, _, done, _ = env.step(action)

            finished = env.finished[i]
            hand = env.hands[i]

        sub_episodes.append(episode)

    # 所有手牌打完后，dealer处理，返回每手 reward
    rewards = env.finish()
    # 对split的return进行特殊处理，每个split动作的收益是其之后所有手收益之和
    if (len(rewards) > 1):
        for i in range(len(rewards)-2, -1, -1):
            rewards[i] += rewards[i+1]


    logging.debug(sub_episodes)
    logging.debug(rewards)
    return sub_episodes, rewards, state_action_space


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
        sub_episodes, rewards, _ = generate_sub_episodes(env, policy, epsilon)

        avg_rewards += rewards[0]
        win_rate += rewards[0] > 0
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
        _, rewards, _ = generate_sub_episodes(
            env, policy, 0)  # use optimal policy

        avg_rewards += rewards[0]
        win_rate += rewards[0] > 0
        sub_episodes_count += len(rewards)

    avg_rewards /= sub_episodes_count
    win_rate /= sub_episodes_count
    print(
        f"Finish {sub_episodes_count} sub episodes, avg rwd:{avg_rewards}, win_rate:{win_rate}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import os
    import pickle

    env: BlackjackEnv = BlackjackEnv()
    policy, Q = mc_control(num_episodes=300000, epsilon=0.5)
    print("Finish training.")

    test(env, policy, 100000)

    name = "MCE5"
    save_dir = f"results/agent_{name}/"
    os.makedirs(save_dir, exist_ok=True)
    with open(os.path.join(save_dir, "policy.pkl"), "wb") as f:
        pickle.dump(dict(policy), f)
    with open(os.path.join(save_dir, "Q.pkl"), "wb") as f:
        Q = dict(Q)
        for k in Q:
            Q[k] = dict(Q[k])
        pickle.dump(Q, f)
