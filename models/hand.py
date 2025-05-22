from .card import Card, Rank, Suit
import itertools

class Hand(object):
    cards:list[Card]=[]
    __points_value = 0

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
            if card.rank is Rank.ACE:
                ace_count += 1
            else:
                total += card.point
        
        # count on 11 as more as possible
        for i in range(ace_count):
            ace_total = (ace_count-i)*11 + i
            if ace_total + total <=21:
                return total + ace_total
        # count zero 11
        return total + ace_count

    @property
    def points(self):
        self.__points_value = self.__evalue()
        return self.__points_value
    
    def is_blackjack(self):
        return len(self.cards) == 2 and self.points == 21
    
    def is_bust(self):
        return self.points > 21
    
    # TODO its better to split as player
    def split(self):
        if self.cards[0].rank != self.cards[1].rank:
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
