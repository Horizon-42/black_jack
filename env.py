import logging
from dataclasses import dataclass
import logging

from deck import NormalDeck
from enum import Enum
import random

@dataclass(frozen=True)
class BaseState:
    player_sum: int
    dealer_card: int
    usible_ace: bool
    splitable: bool
    can_double: bool


class Action(Enum):
    Stand = 0  # -> done with this hand
    Hit = 1  # -> hit or stand
    Double = 2  # -> done with this hand
    Split = 3  # -> hit, stand or possible split agai
    Insurance = 4  # Insurance -> hit or stand


def draw_card():
    card = random.randint(1, 13)
    return min(card, 10)


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


def is_pair(hand):
    return len(hand) == 2 and hand[0] == hand[1]


def can_double(hand):
    """
    判断手牌是否可以 Double（加倍）。

    规则常见约定：
    - 初始两张牌才能 Double
    - 有些赌场允许任意两张牌加倍，有些仅限特定点数范围（如 9, 10, 11）

    参数:
        hand: list[int]，玩家当前的手牌点数，如 [8, 3] 表示初始牌

    返回:
        bool: 是否可以加倍
    """
    if len(hand) != 2:
        return False

    total = sum(hand)
    # 如果有A算作11再判断
    if 1 in hand and total + 10 <= 21:
        total += 10

    # 允许加倍的总点数范围，可以根据规则定制
    return total in range(2, 21)


def is_blackjack(hand, hand_idx: int):
    return hand_idx == 0 and 1 in hand and 10 in hand


class BlackjackEnv:

    def __init__(self, given_draw_card=NormalDeck().deal_card, max_split_num: int = 1):
        self.draw_card = given_draw_card if given_draw_card else draw_card

        self.__max_hands_num: int = max_split_num + 1

    def reset(self, cards: list[int] = None):
        if not cards:
            cards = [self.draw_card() for _ in range(4)]
        self.hands = [[cards[0], cards[2]]]
        self.dealer = [cards[1], cards[3]]

        self.finished = [False]
        self.doubled = [False]
        self.current = 0
        return self.get_state()

    def get_state(self):
        hand = self.hands[self.current]
        return BaseState(
            sum_hand(hand),
            sum_hand([self.dealer[1]]),
            usable_ace(hand),
            self.can_split(),
            can_double(hand)
        )

    def step(self, action):
        """
        执行玩家对当前手牌的一个动作，并推进游戏状态。

        参数：
            action (int): 玩家动作，0=Stand, 1=Hit, 2=Double, 3=Split
        """
        hand = self.hands[self.current]

        # -----------------------------
        # 动作执行
        # -----------------------------

        if action == Action.Stand:  # Stand（停牌）
            self.finished[self.current] = True

        elif action == Action.Hit:  # Hit（要牌）
            hand.append(draw_card())
            if is_bust(hand):
                self.finished[self.current] = True  # 若爆牌，结束当前手

        elif action == Action.Double:  # Double（双倍下注后只摸一张牌）
            if len(hand) == 2:
                hand.append(draw_card())
                self.finished[self.current] = True  # 不论爆不爆牌都结束
                self.doubled[self.current] = True

        elif action == Action.Split:  # Split（拆牌）
            if is_pair(hand) and len(self.hands) < 4:
                new_hand1 = [hand[0], draw_card()]
                new_hand2 = [hand[1], draw_card()]
                self.hands[self.current] = new_hand1
                self.hands.insert(self.current + 1, new_hand2)
                self.finished.insert(self.current + 1, False)
                self.doubled.insert(self.current + 1, False)
                # 拆牌后不推进 current，仍然继续操作新生成的第一手
                return

        if self.finished[self.current]:
            self.current += 1

    def finish(self):
        """
        执行庄家流程，结算所有手牌的最终 reward。
        仅在所有手牌都完成后调用。
        """

        while sum_hand(self.dealer) < 17:
            self.dealer.append(draw_card())
        dealer_score = score(self.dealer)

        hand_results = []
        for idx, hand in enumerate(self.hands):
            player_score = score(hand)

            if is_blackjack(hand, idx):
                if not is_blackjack(self.dealer, 0):
                    result = 1.5
                else:
                    result = 0

            if is_bust(hand):
                result = -1.0
            else:
                result = float(player_score > dealer_score) - \
                    float(player_score < dealer_score)

            final_reward = 2 * result if self.doubled[idx] else result
            hand_results.append(final_reward)

        logging.debug(f"Dealer's hand: {self.dealer}")
        for i, hand in enumerate(self.hands):
            logging.debug(f"Player's hand {i}, {hand}")
        logging.debug(f"Final rewards:{hand_results}")

        return hand_results

    # ====================== Utilty Functions =====================================
    def is_split_enable(self):
        return self.__max_hands_num > 1

    def can_split(self):
        return is_pair(self.hands[self.current]) and len(self.hands) < self.__max_hands_num

    def get_possible_actions(self):
        res = [Action.Stand, Action.Hit]
        player_hand = self.hands[self.current]
        if can_double(player_hand):
            res.append(Action.Double)
        if self.can_split():
            res.append(Action.Split)
        return res