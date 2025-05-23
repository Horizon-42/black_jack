from player import Player
from card import Card
from hand import Hand
from deck import Deck
from dealer import Dealer
from enum import Enum

def cash_in_chips(player_id: int) -> int:
    # read money from terminal
    try:
        return int(input("How many chips do you want to cash in? "))
    except ValueError:
        return 0


def get_init_bet(player_id: int, max_bet: int):
    bet = 0
    try:
        bet = int("How many chips do you want to bet on this hand?")
    except ValueError:
        pass
    return bet if bet <= max_bet else 0


class Action(Enum):
    Stand = 0  # -> done with this hand
    Hit = 1  # -> hit or stand
    Split = 2  # -> hit, stand or possible split again
    Double = 3  # -> done with this hand
    Insurance = 4  # Insurance -> hit or stand


class State(object):
    def __init__(self):
        self.__deal_point: int
        self.__player_point: int

    def __str__(self):
        return f"Dealer point:{self.__deal_point},\n Player point{self.__player_point}"

class BlackJackGame(object):
    player: Player
    dealer: Dealer
    deck: Deck

    # TODO Rewards

    def __init__(self):
        self.deck = Deck(6)
        self.__init_player()
        self.dealer = Dealer()
        self.__init_hands()

    def __init_player(self):
        bank = cash_in_chips()
        self.player = Player(0, bank)

    def __init_hands(self):
        bet = get_init_bet(self.player.__id, self.player.get_bank_amount())
        cards = [self.deck.deal_card() for _ in range(4)]
        self.player.init_hand([cards[0], cards[2]], bet)
        self.dealer.init_hand([cards[1], cards[3]])

    def _get_state(self) -> State:
        return State(self.player)

    def _get_possible_actions(self):
        pass

    # setp
    def step(self, action: Action):
        pass

    # TODO reset
    def reset(self):
        pass
