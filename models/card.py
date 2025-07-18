from enum import Enum
from random import choice


class Suit(Enum):
    Spades = "♠"
    Hearts = "♥"
    Diamonds = "♦"
    Clubs = "♣"

class Rank(Enum):
    TWO = '2'
    THREE = '3'
    FOUR = '4'
    FIVE = '5'
    SIX = '6'
    SEVEN = '7'
    EIGHT = '8'
    NINE = '9'
    TEN = '10'
    JACK = 'J'
    QUEEN = 'Q'
    KING = 'K'
    ACE = 'A'
    


class Card(object):
    suit = None
    rank = None
    point = None

    def __init__(self, suit:Suit, rank:Rank):
        self.suit: Suit = suit
        self.rank: Rank = rank
        self.point: int = Card.get_point(rank)
    
    @staticmethod
    def get_point(rank: Rank) -> int:
        if rank == Rank.ACE:
            return 11
        elif rank in [Rank.JACK, Rank.QUEEN, Rank.KING]:
            return 10
        else:
            return int(rank.value)

    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.rank == other.rank

    def __hash__(self):
        return hash((self.suit, self.rank))

    def __str__(self):
        return f"{self.suit.value}{self.rank.value}"


def get_random_card():
    return Card(choice([suit for suit in Suit]), choice([rank for rank in Rank]))



if __name__ == "__main__":
    for rank in Rank:
        print(rank.value)

    # card = Card()
    # print(card)