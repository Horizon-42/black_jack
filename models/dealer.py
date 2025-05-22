from .hand import Hand
from .card import Card
from .deck import Deck
from copy import deepcopy

class Dealer(object):
    hand:Hand = None
    hiden_card:Card = None

    def __init__(self, intial_cards:list[Card]):
        self.hand = Hand(intial_cards)
        self.hiden_card = self.hand.hide_card()

    def hits(self, deck: Deck):
        self.hand.add_card(self.hiden_card)
        # hit on soft 17

    def reveal_hand(self):
        return self.hand.get_final_points()

    # def get_top_card(self)->Card:
    #     # the first one is hiden
    #     return deepcopy(self.hand.cards[1])