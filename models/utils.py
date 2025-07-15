from enum import Enum
from dataclasses import dataclass

class Action(Enum):
    Stand = 0  # -> done with this hand
    Hit = 1  # -> hit or stand
    Split = 2  # -> hit, stand or possible split again
    Double = 3  # -> done with this hand
    Insurance = 4  # Insurance -> hit or stand

@dataclass
class State:
    player_sum: int
    dealer_card: int
    usible_ace: bool
    splitable: bool