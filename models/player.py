from .card import Card, Suit, Rank
from .hand import Hand
from .deck import Deck

class Player(object):
    hand:Hand = None
    splited_hands: list[Hand] = []
    bank: int = 0
    bet: int = 0

    def __init__(self, bank_money: int):
        self.bank = bank_money

    def init_hand(self, cards: list[Card]):
        if len(cards) != 2:
            raise ValueError("Wrong initial cards for player")
        self.hand = Hand(cards)

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
