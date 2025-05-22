from .card import Card, Suit, Rank
from .hand import Hand

class Player(object):
    hand:Hand = None
    splited_hands: list[Hand]

    def __init__(self, initial_cards: list[Card]):
        self.hand = Hand(initial_cards)

    # TODO ACT ???
