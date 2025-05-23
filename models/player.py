from .card import Card, Suit, Rank
from .hand import PlayerHand
from .deck import Deck

class Player(object):
    __id: int
    hand: PlayerHand = None
    splited_hands: list[PlayerHand] = []
    __bank: int = 0

    def __init__(self, id: int, bank_money: int):
        self.__id = id
        self.__bank = bank_money

    def init_hand(self, cards: list[Card], bet_money: int):
        if len(cards) != 2:
            raise ValueError("Wrong initial cards for player")
        self.hand = PlayerHand(cards, bet_money)

    def get_bank_amount(self):
        return self.__bank


    # TODO BET

    # TODO ACT ???

    def stand(self, card: Card):
        pass

    def hit(self, card: Card):
        self.hand.add_card(card)

    def double(self, card: Card):
        self.hand.add_bet(self.hand.bet)
        self.hand.add_card(card)
        self.hand.mark_as_doubled()

    def split(self, card: Card):
        if not self.hand.has_pair():
            raise ValueError("Could not split!!!")
        if self.__bank < self.hand.bet:
            raise ValueError("Don't have enough chips!!!")

        self.splited_hands.append(self.hand.split())
        self.__bank -= self.hand.bet
        self.hit(card)

    def insurance(self, card):
        pass

    def __str__(self):
        return f"Player {self.__id}, {self.__bank}chips lefted"
