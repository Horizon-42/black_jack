import random
from collections import defaultdict
from tqdm import tqdm
from enum import Enum

from deck import NormalDeck

from env import *
import numpy as np
from random import choice
from itertools import product

from episodes_generator import EpisodesGenerator
from init_strategy import generate_basic_strategy
from test import test
from learning_utils import add_double_in

# -----------------------------
# Monte Carlo, e-greedy, with Double
# -----------------------------


def mc_control(env: BlackjackEnv, num_episodes=200000, epsilon=0.01, init_policy: dict = {}):
    Q: dict[BaseState, dict[Action, float]] = defaultdict(
        lambda: defaultdict(float))
    returns_sum: dict[BaseState, dict[Action, float]] = defaultdict(
        lambda: defaultdict(float))
    returns_count: dict[BaseState, dict[Action, int]
                        ] = defaultdict(lambda: defaultdict(float))
    policy: dict[BaseState, Action] = init_policy

    episodes_generator = EpisodesGenerator(epsilon)

    epslon_decayed = 1
    decay_scale = 0.9999

    def gpi_func(state: BaseState, possible_actions: list[Action]):
        if epslon_decayed > epsilon:
            print(f"Epsilon decayed:{epslon_decayed}")
        if state not in policy or np.random.rand() < epslon_decayed:
            return choice(possible_actions)
        else:
            return policy[state]
        # equal to the formula given by the book

    avg_rewards = 0
    win_rate = 0
    sub_episodes_count = 0
    for i in tqdm(range(num_episodes)):
        epslon_decayed = max(epsilon, epslon_decayed*decay_scale**i)
        sub_episodes, rewards, _ = episodes_generator.generate_episodes_with_func(
            env, gpi_func)

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

                    policy[state] = max(
                        get_possible_actions(state), key=lambda a: Q[state][a])

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

    soft_actions = [Action.Stand, Action.Hit]
    start_state_actions.extend(
        [(state, action) for state, action in product(soft_start_cards, soft_actions)])
    # add double if allowed
    start_state_actions.extend(
        [(cards, Action.Double)
         for cards in soft_start_cards if can_double(cards[:-1])]
    )


    # have pair
    player_pair_cards = range(1, 11) # 10 all seen as one card
    split_cards = [(player_pair_card, player_pair_card, delar_card)
                    for player_pair_card, delar_card in product(player_pair_cards, delear_up_cards)]
    logging.debug(f"Split start cards:{split_cards}")
    
    split_actions = [Action.Stand, Action.Hit]
    # split_actions.append(Action.Split)

    start_state_actions.extend(
        [(state, action) for state, action in product(split_cards, split_actions)])
    start_state_actions.extend(
        [(cards, Action.Double)
         for cards in split_cards if can_double(cards[:-1])]
    )


    # hard totals
    player_first_cards = range(2, 11)
    player_second_cards = range(2, 11)
    hard_cards = [(player_first_card, player_second_card, delar_card) for
                    player_first_card, player_second_card, delar_card in product(
        player_first_cards, player_second_cards, delear_up_cards) if player_first_card !=player_second_card]
    hard_actions = [Action.Stand, Action.Hit]
    start_state_actions.extend(
        [(state, action) for state, action in product(hard_cards, hard_actions)])
    start_state_actions.extend(
        [(cards, Action.Double)
         for cards in hard_cards if can_double(cards[:-1])]
    )

    logging.debug(f"Hard start cards:{hard_cards}")

    return start_state_actions


def mc_exploring_starts(env: BlackjackEnv, num_episodes: int = 200000, init_policy: dict = {}, init_Q: dict = {}):
    
    # gernerating starts
    all_starts = generate_exploring_starts()

    logging.info(f"Traing mc_exploring_starts with {len(all_starts)} starts...")

    Q: dict[BaseState, dict[Action, float]] = defaultdict(
        lambda: defaultdict(float))
    for s in init_Q:
        for a in init_Q[s]:
            Q[s][a] = init_Q[s][a]

    returns_sum: dict[BaseState, dict[Action, float]] = defaultdict(
        lambda: defaultdict(float))
    returns_count: dict[BaseState, dict[Action, int]
                        ] = defaultdict(lambda: defaultdict(float))
    policy: dict[BaseState, Action] = init_policy

    episodes_generator = EpisodesGenerator(0)

    avg_rewards = 0
    win_rate = 0
    sub_episodes_count = 0
    for i in tqdm(range(num_episodes)):
        start = all_starts[i % (len(all_starts)-1)]
        sub_episodes, rewards, _ = episodes_generator.generate_episodes_with_start(
            env, policy, start)

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
                        get_possible_actions(state), key=lambda a: Q[state][a])
                    policy[state] = best_action

    avg_rewards /= sub_episodes_count
    win_rate /= sub_episodes_count
    print(
        f"Finish {sub_episodes_count} sub episodes, avg rwd:{avg_rewards}, win_rate:{win_rate}")
    return policy, Q





if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import os
    import pickle

    pretrained_agent_name = "MCEpsilon_StandHitStand"

    env: BlackjackEnv = BlackjackEnv()

    with open(f"results/{pretrained_agent_name}/policy.pkl", "rb") as f:
        pre_policy = pickle.load(f)
    with open(f"results/{pretrained_agent_name}/Q.pkl", "rb") as f:
        pre_Q = pickle.load(f)

    # basic_policy = generate_basic_strategy()

    policy, Q = mc_control(env, num_episodes=40000000,
                           epsilon=0.05, init_policy=pre_policy)
    # pre_policy = add_double_in(pre_policy)
    # policy, Q = mc_exploring_starts(
    #     env, num_episodes=1000000)

    # policy, Q = mc_epsilon_soft(env, num_episodes=10000000,
    #                             epsilon=0.005, init_policy=pre_policy)

    print("Finish training.")

    test(env, policy, 100000)

    name = "MCEpsilon_StandHitDoubleSplit"
    save_dir = f"results/{name}/"
    os.makedirs(save_dir, exist_ok=True)
    with open(os.path.join(save_dir, "policy.pkl"), "wb") as f:
        pickle.dump(dict(policy), f)
    with open(os.path.join(save_dir, "Q.pkl"), "wb") as f:
        Q = dict(Q)
        for k in Q:
            Q[k] = dict(Q[k])
        pickle.dump(Q, f)
