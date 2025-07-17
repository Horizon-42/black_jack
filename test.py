from train import BlackjackEnv, BaseState,Action, test
import os
import pickle
import logging
import random


import random


class BlackJackDeck:
    def __init__(self):
        self._initialize_deck()

    def _initialize_deck(self):
        """
        初始化牌组，确保前四张牌能组成一个 Blackjack，
        然后将剩余的牌随机洗牌。
        """
        self.deck: list = list(range(1, 11))*4
        random.shuffle(self.deck)

        # burnout
        self.deck.pop(0)

        black_jack_pair = [1, 10]
        random.shuffle(black_jack_pair)

        self.deck.remove(1)
        self.deck.remove(10)

        self.deck.insert(0, black_jack_pair[0])
        self.deck.insert(2, black_jack_pair[1])

    def deal_card(self):
        """
        从牌组顶部发一张牌。
        """
        if len(self.deck) < 20:
            logging.info("Deck is empty, refill cards")
            self._initialize_deck()  # 如果牌发完，重新初始化牌组

        return self.deck.pop(0)  # 从牌组顶部取牌

    def __len__(self):
        """
        返回牌组中剩余牌的数量。
        """
        return len(self.deck)

    def __str__(self):
        """
        返回牌组的字符串表示（主要用于调试）。
        """
        return f"当前牌组 ({len(self.deck)} 张牌): {self.deck[:10]}..."  # 只显示前10张



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    deck = BlackJackDeck()
    env: BlackjackEnv = BlackjackEnv(given_draw_card=deck.deal_card)

    name = "MCE3"
    save_dir = f"results/agent_{name}/"

    with open(f"{save_dir}/policy.pkl", "rb") as f:
        policy = pickle.load(f)
    with open(f"{save_dir}/Q.pkl", "rb") as f:
        Q = pickle.load(f)

    test(env=env, policy=policy, num_episodes=10)
