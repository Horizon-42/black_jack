from card import Card, Suit, Rank
import numpy as np

class Deck(object):
    cards:list[Card]

    def __init__(self):
        self.cards = [Card(suit, rank) for suit in Suit for rank in Rank]

    def shuffle():
        pass

    def burn_out():
        pass

    def __str__(self):
        res = ""
        for card in self.cards:
            res+=card.__str__()
            res+='\n'
        return res

if __name__ == "__main__":
    deck = Deck()
    print(deck)