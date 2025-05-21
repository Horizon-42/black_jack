from .card import Card, Suit, Rank
from .hand import Hand

class Player(object):
    hand:Hand = None

    def __init__(self, initial_cards: list[Card]):
        self.hand = Hand(initial_cards)

    # TODO ACT ???
