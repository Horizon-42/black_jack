from .card import Card, Suit, Rank
from .hand import PlayerHand
from .deck import Deck


class Player(object):
    def __init__(self, id: int, bank_money: int):
        self.__id = id
        self.__bank = bank_money

        self.__hand = None
        self.__splited_hands = []
        self.__all_hands = []

        self.__insuranced = 0
        self.__main_bet = 0

    @property
    def id(self):
        return self.__id

    @property
    def points(self):
        if self.__hand is None:
            return 0
        return self.__hand.points

    def init_hand(self, cards: list[Card], bet_money: int):
        if len(cards) != 2:
            raise ValueError("Wrong initial cards for player")
        self.__main_bet = bet_money
        self.__hand = PlayerHand(cards, bet_money)

    def get_bank_amount(self):
        return self.__bank

    def get_insurance_amount(self):
        return self.__insuranced

    def __move_to_nex_hand(self):
        try:
            self.__hand = self.__splited_hands.pop(-1)
        except IndexError:
            self.__hand = None

    def stand(self):
        self.__all_hands.append(self.__hand)
        self.__move_to_nex_hand()

    def hit(self, card: Card):
        self.__hand.add_card(card)

    def double(self, card: Card):
        self.__hand.add_bet(self.__hand.bet)
        self.__hand.add_card(card)
        self.__hand.mark_as_doubled()

    def split(self):
        if not self.__hand.has_pair():
            raise ValueError("Could not split!!!")
        if self.__bank < self.__hand.bet:
            raise ValueError("Don't have enough chips!!!")

        self.__splited_hands.append(self.__hand.split())
        self.__bank -= self.__hand.bet

    def insurance(self):
        insuranced = self.__hand.bet//2
        if self.__bank < insuranced:
            raise ValueError("Don't have enough chips!!!")
        self.__insuranced = insuranced
        self.__bank -= insuranced

    def is_all_done(self):
        return not self.__all_hands and self.__hand is None

    def is_blackjack(self):
        return self.__hand.is_blackjack()

    def is_bust(self):
        return self.__hand.is_bust()

    def get_insurance_rate(self):
        return self.__insuranced/self.__main_bet

    def pay_out(self, reward: float):
        money = self.__main_bet * reward
        self.__bank += money

    def reset(self):
        self.__hand = None
        self.__splited_hands = []
        self.__all_hands = []
        self.__insuranced = 0
        self.__main_bet = 0

    def __str__(self):
        return f"Player {self.__id}, has {self.__bank} chips lefted,\n play hand {self.__hand},\n main bet {self.__hand.bet}, {self.__insuranced} insurance"
