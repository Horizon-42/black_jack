from env import BlackjackEnv, BaseState, Action, get_possible_actions
from collections import defaultdict
import random
import numpy as np
from test import Metric, compute_episodes_metrics, test, draw_metrics
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

    measure_segment = 100
    # divide episodes to measure_segment length unit, to estimate training performance
    evaluation_times = num_episodes//measure_segment
    metrics:list[Metric] = [None]*evaluation_times
    for i in tqdm(range(evaluation_times)):
        # could learn online, but use episodes generator, to deal with split more easy
        # generating use epsilon greedy
        episodes, rewards, bet_units = generate_episodes(env, policy, epsilon, measure_segment)
        # print(episodes)
        # print(rewards)
        metrics[i] = compute_episodes_metrics(episodes,rewards,bet_units)
        metrics[i].compute_average()

        for episode, ep_return in zip(episodes, rewards):
            if not episode:
                assert(ep_return == 1.5 or ep_return == 0)
                # meet black jack
                continue 
            for t in range(len(episode)-1):
                St, At = episode[t]
                # Rt = ep_return # use episode return as R
                Rt = 0
                S_next, _ = episode[t+1]
                best_next_action = max(
                            get_possible_actions(S_next), key=lambda a: Q[S_next][a])
                # gamma is 1, no discount
                Q[St][At] += alpha*(Rt + Q[S_next][best_next_action] - Q[St][At])
                # update policy
                policy[St] = max(Q[St], key=lambda a: Q[St][a])
            # update the last non-terminal state
            S_last, A_last = episode[-1]
            R_last = ep_return
            # q vaule of terminal is 0
            Q[S_last][A_last] += alpha*(R_last -Q[S_last][A_last])
            policy[S_last] =  max(Q[S_last], key=lambda a: Q[S_last][a])
    
    # compute policy from Q
    # for S in Q:
    #     policy[S] = max(Q[S], key=lambda a: Q[S][a])

    return policy, Q, metrics

def double_q_learning(env:BlackjackEnv, num_episodes:int=200000, alpha:float=0.5, epsilon:float=0.01,init_policy: dict = {}):
    # random init
    Q1: dict[BaseState, dict[Action, float]] = defaultdict(
        lambda: defaultdict(lambda: 0.0))
    Q2: dict[BaseState, dict[Action, float]] = defaultdict(
        lambda: defaultdict(lambda: 0.0))
    
    policy: dict[BaseState, Action] = init_policy

    episodes_generator = EpisodesGenerator(epsilon)

    for i in tqdm(range(num_episodes)):
        # could learn online, but use episodes generator, to deal with split more easy
        # generating use epsilon greedy
        episodes, rewards, _ = episodes_generator.generate_episodes(env, policy)

        for episode, ep_return in zip(episodes, rewards):
            if not episode:
                assert(ep_return == 1.5 or ep_return == 0)
                # meet black jack
                continue 
            for t in range(len(episode)-1):
                St, At = episode[t]
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
                policy[St] = max(get_possible_actions(St), key=lambda a: Q1[St][a]+Q2[St][a])
            # update the last non-terminal state
            S_last, A_last = episode[-1]
            R_last = ep_return
            # q vaule of terminal is 0
            if np.random.rand()<0.5:
                Q1[S_last][A_last] += alpha*(R_last + 0 - Q1[S_last][A_last])
            else:
                Q2[S_last][A_last] += alpha*(R_last + 0 - Q2[S_last][A_last])
            # update policy
            policy[S_last] = max(get_possible_actions(S_last), key=lambda a: Q1[S_last][a]+Q2[S_last][a])
    return policy, Q1, None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import os
    import pickle

    name = "DoubleQLearningWithBasic"

    env: BlackjackEnv = BlackjackEnv()


    basic_policy = generate_basic_strategy()

    policy, Q, _ = double_q_learning(env, num_episodes=1000000, alpha=0.1, epsilon=0.001, init_policy=basic_policy)

    logging.info(f"Finsh {name} traing.")

    # draw_metrics(metrics)

    test(env, policy, 100000)


    save_dir = f"results/agent_{name}/"
    os.makedirs(save_dir, exist_ok=True)
    with open(os.path.join(save_dir, "policy.pkl"), "wb") as f:
        pickle.dump(dict(policy), f)
    with open(os.path.join(save_dir, "Q.pkl"), "wb") as f:
        Q = dict(Q)
        for k in Q:
            Q[k] = dict(Q[k])
        pickle.dump(Q, f)