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

    def hits(self, deck: Deck, hit_soft17=False):
        self.hand.add_card(self.hiden_card)
        # stand on soft 17
        while True:
            points = self.hand.points
            if points < 17:
                self.hand.add_card(deck.deal_card())
            elif points == 17 and self.hand.is_soft and hit_soft17:
                self.hand.add_card(deck.deal_card())
            else:
                break

    def reveal_hand(self):
        return self.hand.points

    # def get_top_card(self)->Card:
    #     # the first one is hiden
    #     return deepcopy(self.hand.cards[1])