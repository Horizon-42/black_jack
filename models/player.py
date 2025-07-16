from .card import Card, Suit, Rank
from .hand import PlayerHand
from .deck import Deck


class Player(object):
    def __init__(self, id: int, bank_money: int):
        if not isinstance(bank_money, int) or bank_money <= 0:
            raise ValueError("Bank money must be a positive integer!")
        self.__id = id
        self.__bank = bank_money

        self.__hand = None
        self.__all_hands = []

        # split related
        self.__split_num = 4  # max split hands
        self.__splited_hands = []


        self.__insuranced = 0
        self.__main_bet = 0

    @property
    def id(self):
        return self.__id

    def init_hand(self, cards: list[Card], bet_money: int):
        if not isinstance(cards, list) or not all(isinstance(card, Card) for card in cards):
            raise TypeError("Cards must be a list of two Card instances!")
        if bet_money <= 0 or not isinstance(bet_money, int):
            raise ValueError("Bet money must be a positive integer!")
        if bet_money > self.__bank:
            raise ValueError("Don't have enough chips to bet!!!")
        self.__main_bet = bet_money
        self.__hand = PlayerHand(cards, bet_money)
        self.__bank -= bet_money

    def get_bank_amount(self):
        return self.__bank

    def set_bank_amount(self, amount: int):
        self.__bank = amount

    def get_insurance_amount(self):
        return self.__insuranced

    def has_pair(self):
        if self.__hand is None:
            return False
        return self.__hand.has_pair()

    # action methods ===============================================
    def stand(self):
        if self.__hand is None:
            raise ValueError("Player's hand is not initialized!")
        self.__hand.is_initial = False
        self.done_with_hand()

    def hit(self, card: Card):
        if not isinstance(card, Card):
            raise TypeError("Card must be an instance of Card class!")
        if self.__hand is None:
            raise ValueError("Player's hand is not initialized!")
        self.__hand.add_card(card)
        self.__hand.is_initial = False

    def double(self, card: Card):
        if not isinstance(card, Card):
            raise TypeError("Card must be an instance of Card class!")
        if self.__hand is None:
            raise ValueError("Player's hand is not initialized!")
        if self.__bank < self.__hand.bet:
            raise ValueError("Don't have enough chips to double!!!")
        self.__bank -= self.__hand.bet
        self.__hand.add_bet(self.__hand.bet)
        self.__hand.add_card(card)
        self.__hand.mark_as_doubled()
        self.done_with_hand()

    def can_double(self):
        if self.__hand is None:
            raise ValueError("Player's hand is not initialized!")
        return self.__hand.is_initial and self.__bank >= self.__hand.bet

    def can_split(self):
        if self.__hand is None:
            raise ValueError("Player's hand is not initialized!")
        return self.__hand.has_pair() and self.__bank >= self.__hand.bet and self.__split_num > 0

    def split(self, card1: Card, card2: Card):
        if self.__hand is None:
            raise ValueError("Player's hand is not initialized!")
        if not self.__hand.has_pair():
            raise ValueError("Could not split!!!")
        if self.__bank < self.__hand.bet:
            raise ValueError("Don't have enough chips!!!")

        # Add card to 2
        splited_hand = self.__hand.split()
        splited_hand.add_card(card1)
        self.__hand.add_card(card2)

        self.__splited_hands.append(splited_hand)
        self.__bank -= self.__hand.bet
        self.__split_num -= 1


    def insurance(self):
        if self.__main_bet <= 0 or self.__hand is None:
            raise ValueError(
                "Player's hand is not initialized or main bet is zero!")
        if self.__insuranced > 0:
            raise ValueError("Insurance already taken!")
        insuranced = self.__main_bet//2
        if self.__bank < insuranced:
            raise ValueError("Don't have enough chips!!!")
        self.__insuranced = insuranced
        self.__bank -= insuranced

    def __move_to_nex_hand(self):
        try:
            self.__hand = self.__splited_hands.pop(-1)
        except IndexError:
            self.__hand = None

    def done_with_hand(self):
        if self.__hand is None:
            raise ValueError("Player's hand is not initialized!")
        self.__all_hands.append(self.__hand)
        self.__move_to_nex_hand()

    def is_all_done(self):
        return len(self.__all_hands) > 0 and self.__hand is None

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

    def get_all_bets(self):
        if not self.is_all_done():
            raise ValueError("Player is not done with all hands yet!")
        return sum(hand.bet for hand in self.__all_hands)

    def get_bank_and_bets(self):
        if not self.is_all_done():
            raise ValueError("Player is not done with all hands yet!")
        return self.__bank + self.get_all_bets()

    def pay_out(self, rewards: list[float]):
        if not isinstance(rewards, list) or not all(isinstance(reward, (int, float)) for reward in rewards):
            raise TypeError("Rewards must be a list of numbers!")
        if len(rewards) != len(self.__all_hands) + 1:
            raise ValueError(
                "Rewards list length must match the number of hands!")
        if not self.is_all_done():
            raise ValueError("Player is not done with all hands yet!")
        if not rewards:
            raise ValueError("Rewards list cannot be empty!")
        self.__bank += self.get_all_bets()
        self.__bank += self.__insuranced

        money = 0
        for reward in rewards:
            money += self.__main_bet * reward
        self.__bank += money
        self.__reset()
        return money

    def __reset(self):
        self.__hand = None
        self.__splited_hands = []
        self.__all_hands = []
        self.__insuranced = 0
        self.__main_bet = 0
        self.__split_num = 4

    def __str__(self):
        return f"Player {self.__id}, has {self.__bank} chips left,\n play hand {self.__hand},\n main bet: {self.get_bet()}, insurance: {self.__insuranced}"
