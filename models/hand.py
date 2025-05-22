from .card import Card, Rank, Suit
import itertools

class Hand(object):
    cards:list[Card]=[]
    points_value = 0

    def __init__(self, cards:list[Card]):
        if len(cards)!=2:
            raise ValueError("Too many cards!")
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
    
    def __potential_evalue(self):
        total = 0
        ace_count = 0
        # consider multi ace scenario
        for card in self.cards:
            if card.rank is Rank.ACE:
                ace_count += 1
            else:
                total += card.point
        if ace_count == 0:
            return [total]

        ace_values = [sum(p)
                      for p in itertools.product([11, 1], repeat=ace_count)]
        res = [total+ace for ace in ace_values if total + ace <= 21]
        return res

    def get_points(self) -> list[int]:
        return self.__potential_evalue()

    def get_final_points(self):
        self.points_value = self.__evalue()
        return self.points_value
    
    def is_blackjack(self):
        return self.points_value == 21
    
    def is_bust(self):
        return self.points_value > 21
    
    # TODO its better to split as player
    def split(self, cards: list[Card]):
        if self.cards[0].rank != self.cards[1].rank:
            raise ValueError("Have No pair!")
        return Hand(self.cards[0], cards[0]), Hand(self.cards[1], cards[1])

    def __str__(self):
        res = "With "
        for card in self.cards:
            res += f"{card}, "
        res += f"get points: {self.get_final_points()}"
        return res


if __name__ == "__main__":
    hand = Hand([Card(Suit.Clubs, Rank.ACE), Card(Suit.Hearts, Rank.FIVE)])
    print(hand)
