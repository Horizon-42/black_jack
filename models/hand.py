from .card import Card, Rank, Suit
import itertools

class Hand(object):
    cards:list[Card]=[]
    is_soft = False

    def __init__(self, cards:list[Card]):
        if not (1 <= len(cards) <= 2):
            raise ValueError("Wrong cards number!")
        self.cards = cards

    def add_card(self, card:Card):
        self.cards.append(card)

    def hide_card(self):
        # only for dealer
        return self.cards.pop(0)

    def __evalue(self):
        total = 0
        ace_count = 0
        # consider multi ace scenario
        for card in self.cards:
            total += card.point
            ace_count += int(card.rank is Rank.ACE)
        
        # count on 11 as many as possible
        while total > 21 and ace_count > 0:
            total -= 10
            ace_count -= 1
        self.is_soft = ace_count > 0
        return total

    @property
    def points(self):
        return self.__evalue()


    def is_blackjack(self):
        return len(self.cards) == 2 and self.points == 21
    
    def is_bust(self):
        return self.points > 21
    
    def has_pair(self):
        return len(self.cards) == 2 and self.cards[0].point == self.cards[1].point

    # TODO its better to split as player
    def split(self):
        if not self.has_pair():
            raise ValueError("Have No pair!")
        return Hand(self.cards.pop(1))

    def __str__(self):
        res = "With "
        for card in self.cards:
            res += f"{card}, "
        res += f"get points: {self.get_final_points()}"
        return res


if __name__ == "__main__":
    hand = Hand([Card(Suit.Clubs, Rank.ACE), Card(Suit.Hearts, Rank.FIVE)])
    print(hand)
