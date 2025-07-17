import random
from collections import defaultdict
from utils import plot_policy_sns
from tqdm import tqdm
from enum import Enum

from deck import NormalDeck

from env import *
import numpy as np
from random import choice
from itertools import product

from episodes_generator import EpisodesGenerator


# -----------------------------
# Monte Carlo, e-greedy, with Double
# -----------------------------

def mc_control(env:BlackjackEnv, num_episodes=200000, epsilon=0.01):
    Q: dict[BaseState, dict[Action, float]] = defaultdict(
        lambda: defaultdict(float))
    returns_sum: dict[BaseState, dict[Action, float]] = defaultdict(
        lambda: defaultdict(float))
    returns_count: dict[BaseState, dict[Action, int]
                        ] = defaultdict(lambda: defaultdict(float))
    policy: dict[BaseState, Action] = {}

    episodes_generator = EpisodesGenerator(epsilon)

    avg_rewards = 0
    win_rate = 0
    sub_episodes_count = 0
    for i in tqdm(range(num_episodes)):
        sub_episodes, rewards = episodes_generator.generate_episodes(env, policy)

        avg_rewards += sum(rewards)
        win_rate += sum(1 for r in rewards if r > 0 and r != 1.5)
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

# -----------------------------
# Monte Carlo, e-greedy, with Double
# -----------------------------

def generate_exploring_starts():
    start_state_actions: list[tuple[tuple, Action]] = []

    delear_up_cards: list[int] = range(1,11) # Ace seen as 1  

    # agent cards
    # have useable ace
    player_useble_ace = 1
    # second card can be any rank, maximum sum 21, two aces count as 12
    # didn't count 10 in because directly lead to blackjack
    player_second_cards = range(2, 10)

    soft_start_cards = [(player_useble_ace, player_second_card, delar_card)
                        for player_second_card, delar_card in product(player_second_cards, delear_up_cards)]
    
    logging.debug(f"Soft start cards:{soft_start_cards}")

    soft_actions = [Action.Stand, Action.Hit, Action.Double]
    start_state_actions.extend(
        [(state, action) for state, action in product(soft_start_cards, soft_actions)])

    # have pair
    player_pair_cards = range(1, 11) # 10 all seen as one card
    split_cards = [(player_pair_card, player_pair_card, delar_card)
                    for player_pair_card, delar_card in product(player_pair_cards, delear_up_cards)]
    logging.debug(f"Split start cards:{split_cards}")
    
    split_actions = [Action.Stand, Action.Hit, Action.Double,
                     Action.Split]  # disable split temproraly

    start_state_actions.extend(
        [(state, action) for state, action in product(split_cards, split_actions)])


    # hard totals
    player_first_cards = range(2, 11)
    player_second_cards = range(2, 11)
    hard_cards = [(player_first_card, player_second_card, delar_card) for
                    player_first_card, player_second_card, delar_card in product(
        player_first_cards, player_second_cards, delear_up_cards) if player_first_card !=player_second_card]
    hard_actions = [Action.Stand, Action.Hit, Action.Double]
    start_state_actions.extend(
        [(state, action) for state, action in product(hard_cards, hard_actions)])

    logging.debug(f"Hard start cards:{hard_cards}")

    return start_state_actions

def mc_exploring_starts(env:BlackjackEnv, num_episodes:int = 200000):
    
    # gernerating starts
    all_starts = generate_exploring_starts()

    logging.info(f"Traing mc_exploring_starts with {len(all_starts)} starts...")

    Q: dict[BaseState, dict[Action, float]] = defaultdict(
        lambda: defaultdict(float))
    returns_sum: dict[BaseState, dict[Action, float]] = defaultdict(
        lambda: defaultdict(float))
    returns_count: dict[BaseState, dict[Action, int]
                        ] = defaultdict(lambda: defaultdict(float))
    policy: dict[BaseState, Action] = {}

    episodes_generator = EpisodesGenerator(0)

    avg_rewards = 0
    win_rate = 0
    sub_episodes_count = 0
    for _ in tqdm(range(num_episodes)):
        start = choice(all_starts)
        sub_episodes, rewards = episodes_generator.generate_episodes_with_start(env, policy, start)

        avg_rewards += sum(rewards)
        win_rate += sum(1 for r in rewards if r > 0 and r != 1.5)
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
    black_jack_rate = 0
    draw_rate = 0
    loss_rate = 0

    sub_episodes_count = 0

    episodes_generator = EpisodesGenerator(0)

    for i in tqdm(range(num_episodes)):
        episodes, rewards = episodes_generator.generate_episodes(
            env, policy)  # use optimal policy

        avg_rewards += sum(rewards)
        sub_episodes_count += len(rewards)

        if not episodes[0] and rewards[0] == 1.5:
            black_jack_rate += 1
            continue
        win_rate += sum(1 for r in rewards if r > 0)
        draw_rate += sum(1 for r in rewards if r == 0)
        loss_rate += sum(1 for r in rewards if r < 0)


    avg_rewards /= sub_episodes_count
    win_rate /= sub_episodes_count
    draw_rate /= sub_episodes_count
    loss_rate /= sub_episodes_count
    black_jack_rate /= sub_episodes_count
    print(
        f"Finish {sub_episodes_count} sub episodes, avg rwd:{avg_rewards}, win_rate:{win_rate}")

    logging.info(f"Test finish with avg_rewards: {avg_rewards}, win_rate: {win_rate}, \
                 black_jack_rate:{black_jack_rate}, draw_rate:{draw_rate}, loss_rate:{loss_rate}")
    return avg_rewards, win_rate, black_jack_rate, draw_rate, loss_rate


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import os
    import pickle

    env: BlackjackEnv = BlackjackEnv()
    # policy, Q = mc_control(env, num_episodes=6000000, epsilon=0.001)
    policy, Q = mc_exploring_starts(env, num_episodes=600000)

    print("Finish training.")

    test(env, policy, 100000)

    name = "MCES0"
    save_dir = f"results/agent_{name}/"
    os.makedirs(save_dir, exist_ok=True)
    with open(os.path.join(save_dir, "policy.pkl"), "wb") as f:
        pickle.dump(dict(policy), f)
    with open(os.path.join(save_dir, "Q.pkl"), "wb") as f:
        Q = dict(Q)
        for k in Q:
            Q[k] = dict(Q[k])
        pickle.dump(Q, f)
