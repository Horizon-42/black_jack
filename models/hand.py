from .card import Card, Rank, Suit
import itertools


class Hand(object):
    def __init__(self, cards:list[Card]):
        self.is_soft: bool = False

        if not (1 <= len(cards) <= 2):
            raise ValueError("Wrong cards number!")
        self.cards: list[Card] = cards

    def add_card(self, card:Card):
        self.cards.append(card)

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

    def __potential_evalue(self):
        total = 0
        ace_count = 0
        for card in self.cards:
            if card.rank is not Rank.ACE:
                total += card.point
            else:
                ace_count += 1
        potential_points = [total + i +
                            (ace_count-i)*11 for i in range(ace_count+1)]
        if potential_points[-1] > 21:
            # if all combinations are over 21, return the last one
            return potential_points[-1:]
        potential_points = [point for point in potential_points if point <= 21]
        return potential_points

    @property
    def points(self):
        return self.__evalue()

    @property
    def potiential_points(self):
        return self.__potential_evalue()

    def is_blackjack(self):
        return len(self.cards) == 2 and self.points == 21
    
    def is_bust(self):
        return self.points > 21

    def __str__(self):
        res = ""
        for card in self.cards:
            res += f"{card}, "
        res += f"Points: {self.potiential_points}"
        return res

    def __eq__(self, value):
        return isinstance(value, Hand) and self.potiential_points == value.potiential_points


class PlayerHand(Hand):
    def __init__(self, cards: list[Card], chips_bet_on: int):
        super().__init__(cards)
        if not isinstance(chips_bet_on, int):
            raise ValueError("Bet amount must be an integer!")
        if chips_bet_on < 0:
            raise ValueError("Bet amount must be positive!")
        self.__bet = chips_bet_on
        self.__doubled = False
        self.__is_initial = True

    @property
    def bet(self):
        return self.__bet

    @property
    def is_initial(self):
        return self.__is_initial
    @is_initial.setter
    def is_initial(self, value):
        if not isinstance(value, bool):
            raise ValueError("is_initial must be a boolean!")
        self.__is_initial = value

    @property
    def doubled(self):
        return self.__doubled

    def add_bet(self, bet_amount):
        if not isinstance(bet_amount, int):
            raise ValueError("Bet amount must be an integer!")
        if bet_amount < 0:
            raise ValueError("Bet amount must be positive!")

        # for double or insurance
        self.__bet += bet_amount

    def mark_as_doubled(self):
        self.__doubled = True

    def has_pair(self):
        return len(self.cards) == 2 and self.cards[0].point == self.cards[1].point

    # TODO its better to split as player
    def split(self):
        if not self.has_pair():
            raise ValueError("Have No pair!")
        return PlayerHand([self.cards.pop(1)], self.__bet)


if __name__ == "__main__":
    hand = Hand([Card(Suit.Clubs, Rank.ACE), Card(Suit.Hearts, Rank.FIVE)])
    print(hand)
