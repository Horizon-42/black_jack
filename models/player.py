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

    def init_hand(self, cards: list[Card], bet_money: list[int]):
        if len(cards) != 2:
            raise ValueError("Wrong initial cards for player")
        self.hand = PlayerHand(cards)
        self.hand.add_bet(bet_money)

    def get_bank_amount(self):
        return self.__bank


    # TODO BET

    # TODO ACT ???

    def stand(self, card: Deck):
        pass

    def hit(self, deck: Deck):
        self.hand.add_card(deck.deal_card())

    def double(self, deck: Deck):
        # TODO
        pass

    def split(self, deck: Deck):
        if not self.hand.has_pair():
            raise ValueError("Could not split!!!")

        self.splited_hands.append(self.hand.split())
        self.hand.add_card(deck.deal_card())

    def __str__(self):
        return f"Player {self.__id}, {self.__bank}chips lefted"
