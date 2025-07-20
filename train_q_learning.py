from env import BlackjackEnv, BaseState, Action, get_possible_actions
from collections import defaultdict
import random
import numpy as np
from metrics import Metric, compute_episodes_metrics, test, draw_metrics
import logging
from init_strategy import generate_basic_strategy
from tqdm import tqdm

from episodes_generator import EpisodesGenerator

def generate_episodes(env:BlackjackEnv, policy:dict, epsilon:float, num_episodes:int):
    episodes_generator = EpisodesGenerator(epsilon)
    # for convinent, still use episode generator
    episodes : list = []
    rewards :list = []
    bet_units:list = []
    for _ in range(1000):
        # subepisodes due to split
        sub_episodes, sub_rewards, sub_bet_units = episodes_generator.generate_episodes(env, policy)
        episodes.extend(sub_episodes)
        rewards.extend(sub_rewards)
        bet_units.extend(sub_bet_units)
    return episodes, rewards, bet_units

def q_learning(env:BlackjackEnv, num_episodes:int=200000, alpha:float=0.5, epsilon:float=0.01,init_policy: dict = {}):
    # random init
    Q: dict[BaseState, dict[Action, float]] = defaultdict(
        lambda: defaultdict(lambda: 0.0))
    policy: dict[BaseState, Action] = init_policy

    episodes_generator = EpisodesGenerator(epsilon)

    def policy_func(state: BaseState, possible_actions: list[Action]):
        if np.random.rand() < epsilon:
            return random.choice(possible_actions)
        else:
            return max(get_possible_actions(state),
                       key=lambda a: Q[state][a])

    for i in tqdm(range(num_episodes)):
        # could learn online, but use episodes generator, to deal with split more easy
        # generating use epsilon greedy
        episodes, rewards, bet_units = episodes_generator.generate_episodes_with_func(
            env, policy_func)

        for episode, ep_return in zip(episodes, rewards):
            if not episode:
                assert(ep_return == 1.5 or ep_return == 0)
                # meet black jack
                continue 
            for t in range(len(episode)-1):
                St, At = episode[t]
                # Rt for middle state is 0
                Rt = 0
                S_next, _ = episode[t+1]
                best_next_action = max(
                            get_possible_actions(S_next), key=lambda a: Q[S_next][a])
                # gamma is 1, no discount
                Q[St][At] += alpha*(Rt + Q[S_next][best_next_action] - Q[St][At])
                # update policy
            # update the last non-terminal state
            S_last, A_last = episode[-1]
            R_last = ep_return
            # q vaule of terminal is 0
            Q[S_last][A_last] += alpha*(R_last - Q[S_last][A_last])
    
    # compute policy from Q
    for S in Q:
        policy[S] = max(Q[S], key=lambda a: Q[S][a])

    return policy, Q, None


def double_q_learning(env: BlackjackEnv, num_episodes: int = 200000, alpha: float = 0.5, epsilon_min: float = 0.01, init_policy: dict = {}):
    # random init
    Q1: dict[BaseState, dict[Action, float]] = defaultdict(
        lambda: defaultdict(lambda: 0.0))
    Q2: dict[BaseState, dict[Action, float]] = defaultdict(
        lambda: defaultdict(lambda: 0.0))
    
    visit_count: dict[BaseState, dict[Action, int]] = defaultdict(
        lambda: defaultdict(int))

    policy: dict[BaseState, Action] = init_policy

    episodes_generator = EpisodesGenerator(epsilon_min)

    epsilon = 1
    def policy_func(state: BaseState, possible_actions: list[Action]):
        if np.random.rand() < epsilon:
            return random.choice(possible_actions)
        else:
            return max(get_possible_actions(state),
                       key=lambda a: Q1[state][a]+Q2[state][a])
    epsilon_decay = 0.9999
    for i in tqdm(range(num_episodes)):
        # could learn online, but use episodes generator, to deal with split more easy
        # generating use epsilon greedy
        epsilon = max(epsilon_min, epsilon_decay**i)
        episodes, rewards, _ = episodes_generator.generate_episodes_with_func(
            env, policy_func)

        for episode, ep_return in zip(episodes, rewards):
            if not episode:
                assert(ep_return == 1.5 or ep_return == 0)
                # meet black jack
                continue 
            for t in range(len(episode)-1):
                St, At = episode[t]
                visit_count[St][At] += 1
                alpha = 1/visit_count[St][At]
                # Rt = ep_return # use episode return as R
                Rt = 0
                S_next, _ = episode[t+1]
                # gamma is 1, no discount
                if np.random.rand()<0.5:
                    best_next_action = max(
                            get_possible_actions(S_next), key=lambda a: Q1[S_next][a])
                    Q1[St][At] += alpha*(Rt + Q2[S_next][best_next_action] - Q1[St][At])
                else:
                    best_next_action = max(
                            get_possible_actions(S_next), key=lambda a: Q2[S_next][a])
                    Q2[St][At] += alpha*(Rt + Q1[S_next][best_next_action] - Q2[St][At])
                # update policy
            # update the last non-terminal state
            S_last, A_last = episode[-1]
            visit_count[S_last][A_last] += 1
            alpha = 1/visit_count[S_last][A_last]
            R_last = ep_return
            # q vaule of terminal is 0
            if np.random.rand()<0.5:
                Q1[S_last][A_last] += alpha*(R_last + 0 - Q1[S_last][A_last])
            else:
                Q2[S_last][A_last] += alpha*(R_last + 0 - Q2[S_last][A_last])
            # update policy
    states = set(Q1.keys())
    states.update(set(Q2.keys()))
    for S in states:
        policy[S] = max(get_possible_actions(
            S), key=lambda a: Q1[S][a]+Q2[S][a])
    return policy, Q1, None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import os
    import pickle

    name = "DoubleQLearningWithBasicLongRun1"

    env: BlackjackEnv = BlackjackEnv()


    basic_policy = generate_basic_strategy()

    # policy, Q, _ = q_learning(
    #     env, num_episodes=1000000, alpha=0.01, epsilon=0.001)

    policy, Q, _ = double_q_learning(
        env, num_episodes=20000000, alpha=0.01, epsilon_min=0.001)

    logging.info(f"Finsh {name} traing.")

    # draw_metrics(metrics)

    test(env, policy, 100000)

    save_dir = f"results/{name}/"
    os.makedirs(save_dir, exist_ok=True)
    with open(os.path.join(save_dir, "policy.pkl"), "wb") as f:
        pickle.dump(dict(policy), f)
    with open(os.path.join(save_dir, "Q.pkl"), "wb") as f:
        Q = dict(Q)
        for k in Q:
            Q[k] = dict(Q[k])
        pickle.dump(Q, f)