from .hand import Hand
from .card import Card
from copy import deepcopy

class Dealer(object):
    hand:Hand = None
    hiden_card:Card = None

    def __init__(self, intial_cards:list[Card]):
        self.hand = Hand(intial_cards)
        self.hiden_card = self.hand.hide_card()
    
    def get_face_point(self):
        return self.hand.get_points()
    
    def get_final_point(self):
        self.hand.cards.append(self.hiden_card)
        return self.hand.get_points()

    # def get_top_card(self)->Card:
    #     # the first one is hiden
    #     return deepcopy(self.hand.cards[1])