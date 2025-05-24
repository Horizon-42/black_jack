from card import Card, Suit, Rank
import numpy as np

class Deck(object):
    cards:list[Card]

    def __init__(self, deck_num=6):
        self.cards = [Card(suit, rank)
                      for suit in Suit for rank in Rank]*deck_num
        self.shuffle()
        self.burn_out()

    def shuffle(self):
        np.random.shuffle(self.cards)

    def burn_out(self):
        # delete the top card
        del self.cards[0]

    def deal_card(self):
        return self.cards.pop(0)

    def __str__(self):
        res = ""
        for card in self.cards:
            res+=card.__str__()
            res+='\n'
        return res

    def __len__(self):
        return len(self.cards)

if __name__ == "__main__":
    deck = Deck()
    print(deck)
    deck.shuffle()
    print(deck)
    deck.burn_out()
    print(deck)
    print(deck.deal_card())
    print(deck.deal_card())
