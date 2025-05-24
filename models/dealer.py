from .hand import Hand
from .card import Card
from .deck import Deck
from copy import deepcopy

class Dealer(object):
    __hand: Hand = None
    __hiden_card: Card = None


    def init_hand(self, cards: list[Card]):
        self.__hand = Hand(cards)
        self.__hiden_card = self.__hand.cards.pop(0)

    def hits(self, deck: Deck, hit_soft17=False):
        self.__hand.add_card(self.__hiden_card)
        self.__hiden_card = None
        # stand on soft 17
        while True:
            points = self.__hand.points
            if points < 17:
                self.__hand.add_card(deck.deal_card())
            elif points == 17 and self.__hand.is_soft and hit_soft17:
                self.__hand.add_card(deck.deal_card())
            else:
                break

    def is_black_jack(self):
        return self.__hiden_card is None and self.__hand.is_blackjack()


    def reveal_hand(self):
        return self.__hand.points

    def get_face_point(self):
        return self.__hand.cards[0].point

    def is_bust(self):
        return self.__hand.is_bust()

    def is_blackjack(self):
        return self.__hand.is_blackjack()
