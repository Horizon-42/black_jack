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

    def init_hand(self, cards: list[Card], bet_money: int):
        if len(cards) != 2:
            raise ValueError("Wrong initial cards for player")
        if bet_money > self.__bank:
            raise ValueError("Don't have enough chips to bet!!!")
        self.__main_bet = bet_money
        self.__hand = PlayerHand(cards, bet_money)

    def get_bank_amount(self):
        return self.__bank

    def get_insurance_amount(self):
        return self.__insuranced

    def has_pair(self):
        if self.__hand is None:
            return False
        return self.__hand.has_pair()

    def __move_to_nex_hand(self):
        try:
            self.__hand = self.__splited_hands.pop(-1)
        except IndexError:
            self.__hand = None

    # action methods
    def stand(self):
        if self.__hand is None:
            raise ValueError("Player's hand is not initialized!")
        self.__hand.is_initial = False
        self.done_with_hand()

    def hit(self, card: Card):
        if self.__hand is None:
            raise ValueError("Player's hand is not initialized!")
        self.__hand.add_card(card)
        self.__hand.is_initial = False

    def double(self, card: Card):
        if self.__bank < 2*self.__hand.bet:
            raise ValueError("Don't have enough chips to double!!!")
        self.__hand.add_bet(self.__hand.bet)
        self.__hand.add_card(card)
        self.__hand.mark_as_doubled()
        self.done_with_hand()

    def can_double(self):
        if self.__hand is None:
            raise ValueError("Player's hand is not initialized!")
        return self.__hand.is_initial and self.__bank >= 2 * self.__hand.bet

    def split(self):
        if not self.__hand.has_pair():
            raise ValueError("Could not split!!!")
        if self.__bank < self.__hand.bet:
            raise ValueError("Don't have enough chips!!!")

        self.__splited_hands.append(self.__hand.split())


    def insurance(self):
        insuranced = self.__hand.bet//2
        if self.__bank < insuranced:
            raise ValueError("Don't have enough chips!!!")
        self.__insuranced = insuranced

    def done_with_hand(self):
        if self.__hand is None:
            raise ValueError("Player's hand is not initialized!")
        self.__all_hands.append(self.__hand)
        self.__move_to_nex_hand()

    def is_all_done(self):
        return self.__all_hands and self.__hand is None

    def get_hand(self):
        if self.__hand is None and not self.__all_hands:
            raise ValueError("Player's hand is not initialized!")
        return self.__hand if self.__hand else self.__all_hands[0]

    def get_bet(self):
        if self.__hand is None:
            return 0
        return self.__hand.bet

    def get_all_hands(self):
        if not self.is_all_done():
            raise ValueError("Player is not done with all hands yet!")
        return self.__all_hands

    def get_insurance_rate(self):
        return self.__insuranced/self.__main_bet if self.__main_bet > 0 else 0

    def pay_out(self, rewards: list[float]):
        money = 0
        for reward in rewards:
            money += self.__main_bet * reward
        self.__bank += money
        return money

    def reset(self):
        self.__hand = None
        self.__splited_hands = []
        self.__all_hands = []
        self.__insuranced = 0
        self.__main_bet = 0

    def __str__(self):
        return f"Player {self.__id}, has {self.__bank} chips lefted,\n play hand {self.__hand},\n main bet {self.get_bet()}, {self.__insuranced} insurance"
