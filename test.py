from env import BlackjackEnv, compute_episodes_bet_unit
import os
import pickle
import logging
from deck import BlackJackDeck, NormalDeck
from init_strategy import generate_basic_strategy
from episodes_generator import EpisodesGenerator
from tqdm import tqdm

from dataclasses import dataclass


class Metric:

    def __init__(self):
        self.BlackjackRate: float = 0
        self.WinRate: float = 0
        self.DrawRate: float = 0
        self.LossRate: float = 0
        self.DoubleWinRate: float = 0
        self.DoubleLossRate: float = 0
        self.AvgGain: float = 0
        self.EpisodesCount: int = 0

    def compute_average(self):
        if self.WinRate > 1:
            self.BlackjackRate /= self.EpisodesCount
            self.WinRate /= self.EpisodesCount
            self.DrawRate /= self.EpisodesCount
            self.LossRate /= self.EpisodesCount
            self.DoubleWinRate /= self.EpisodesCount
            self.DoubleLossRate /= self.EpisodesCount
            self.AvgGain /= self.EpisodesCount

    def __str__(self):
        return (f"--- Game Metrics ---\n"
                f"Episodes Played: {self.EpisodesCount}\n"
                f"Blackjack Rate: {self.BlackjackRate:.4%}\n"
                f"Win Rate: {self.WinRate:.4%}\n"
                f"Draw Rate: {self.DrawRate:.4%}\n"
                f"Loss Rate: {self.LossRate:.2%}\n"
                f"Double Down Win Rate: {self.DoubleWinRate:.4%}\n"
                f"Double Down Loss Rate: {self.DoubleLossRate:.4%}\n"
                f"Average Gain per Episode: {self.AvgGain:.4f}\n"
                f"--------------------")


def compute_episodes_metrics(episodes: list, rewards: list[float], bet_units: list[float]):
    metric: Metric = Metric()

    for _, reward, beit_unit in zip(episodes, rewards, bet_units):
        metric.EpisodesCount += 1
        metric.WinRate += reward == 1
        metric.BlackjackRate += reward == 1.5
        metric.DrawRate += reward == 0
        metric.LossRate += reward == -1
        metric.DoubleWinRate += reward == 2
        metric.DoubleLossRate += reward == -2
        metric.AvgGain += reward*beit_unit

    metric.compute_average()
    return metric


def test(env: BlackjackEnv, policy: dict, num_episodes=10000):

    episodes_generator = EpisodesGenerator(0)

    total_eposodes = []
    total_rewards = []
    total_beit_units = []
    for i in tqdm(range(num_episodes)):
        episodes, rewards, bet_units = episodes_generator.generate_episodes(
            env, policy)  # use optimal policy

        total_eposodes.extend(episodes)
        total_rewards.extend(rewards)
        total_beit_units.extend(bet_units)

    metric = compute_episodes_metrics(
        total_eposodes, total_rewards, total_beit_units)
    logging.info(f"Test {num_episodes} episodes,\n {metric}")
    return metric


def test_basic_strategy(deck_num: int = 6):
    env: BlackjackEnv = BlackjackEnv(
        given_draw_card=NormalDeck(deck_num).deal_card)

    policy = generate_basic_strategy()

    metirc = test(env=env, policy=policy, num_episodes=1000000)

    logging.info(f"Test Basic Strategy,\n {metirc}")
    print(f"Expetation of basic strategy is {metirc.AvgGain}")




if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO, filename="test.log")
    logging.basicConfig(level=logging.INFO)

    deck_num = 1

    test_basic_strategy()

    env: BlackjackEnv = BlackjackEnv(
        given_draw_card=NormalDeck(deck_num).deal_card)

    name = "MCE_basic_double_all"
    save_dir = f"results/agent_{name}/"

    with open(f"{save_dir}/policy.pkl", "rb") as f:
        policy = pickle.load(f)
    with open(f"{save_dir}/Q.pkl", "rb") as f:
        Q = pickle.load(f)

    metric = test(env=env, policy=policy, num_episodes=1000000)

    print(f"Expetation of this agent {name} is {metric.AvgGain}")
