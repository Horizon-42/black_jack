import random
import logging


class NormalDeck:
    def __init__(self, deck_num: int = 6):
        self.__deck_num = deck_num
        self._initialize_deck()

    def _initialize_deck(self):
        """
        初始化牌组，确保前四张牌能组成一个 Blackjack，
        然后将剩余的牌随机洗牌。
        """
        card_rank = list(range(1, 14))
        card_rank[10:] = [10]*3  # make J, Q, K ti 10
        self.deck: list = card_rank*4*self.__deck_num  # for 4 suits
        random.shuffle(self.deck)

        # burnout
        self.deck.pop(0)

    def deal_card(self):
        """
        从牌组顶部发一张牌。
        """
        if len(self.deck) == 0:
            logging.debug("Deck is empty, refill cards")
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


class BlackJackDeck(NormalDeck):
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
