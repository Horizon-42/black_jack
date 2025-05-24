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
        if self.__hand is None or self.get_hand_length() == 0:
            raise ValueError("Dealer's hand is not initialized or empty.")
        return self.__hand.cards[0].point

    def get_face_card(self):
        return deepcopy(self.__hand.cards[0]) if self.__hand else None

    def get_hand(self):
        return deepcopy(self.__hand) if self.__hand else None

    def is_bust(self):
        return self.__hand.is_bust()

    def is_blackjack(self):
        return self.__hand.is_blackjack() if self.__hand else False

    def reset(self):
        self.__hand = None
        self.__hiden_card = None

    def get_hiden_card(self):
        return deepcopy(self.__hiden_card) if self.__hiden_card else None

    def get_hand_length(self):
        return len(self.__hand.cards) if self.__hand else 0

    def __str__(self):
        res = "Dealer's hand: "
        if self.__hiden_card is not None:
            res += f"[{self.__hiden_card}, ?], "
        else:
            res += "["
        for card in self.__hand.cards:
            res += f"{card}, "
        res += f"get points: {self.__hand.points}"
        return res
