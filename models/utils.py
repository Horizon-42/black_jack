from enum import Enum
from dataclasses import dataclass
from .hand import Hand, PlayerHand

class Action(Enum):
    Stand = 0  # -> done with this hand
    Hit = 1  # -> hit or stand
    Split = 2  # -> hit, stand or possible split again
    Double = 3  # -> done with this hand
    Insurance = 4  # Insurance -> hit or stand

@dataclass(frozen=True)
class BaseState:
    player_sum: int
    dealer_card: int
    usible_ace: bool
    splitable: bool


class ShowState(object):
    def __init__(self, dealer_hand: Hand, player_hand: PlayerHand):
        self.__dealer_hand: Hand = dealer_hand
        self.__player_hand: PlayerHand = player_hand

    def __str__(self):
        res = ""
        res += f"Dealer's hand: {self.__dealer_hand},\n"
        res += f"Player's hand: {self.__player_hand}\n"
        return res

    def get_state(self) -> BaseState:
        player_sum = self.__player_hand.points
        usable_ace = self.__player_hand.is_soft
        splitable = self.__player_hand.has_pair()

        dealer_card = self.__dealer_hand.cards[0].point
        return BaseState(player_sum, dealer_card, usable_ace, splitable)
