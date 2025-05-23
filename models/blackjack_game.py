from player import Player
from card import Card
from hand import Hand
from deck import Deck
from dealer import Dealer


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

class BlackJackGame(object):
    players: list[Player]
    dealer: Dealer
    deck: Deck

    # TODO Rewards

    def __init__(self, player_num=1):
        self.deck = Deck(6)
        self.__init_players(player_num)
        self.dealer = Dealer()
        self.__init_hands()

    def __init_players(self, player_num: int = 1):
        for i in range(player_num):
            # input from terminal
            bank = cash_in_chips(i)
            if bank > 0:
                self.players.append(Player(i, bank))

    def __init_hands(self):
        players_bet = []
        for i, player in enumerate(self.players):
            bet = get_init_bet(i, player.get_bank_amount())
            if bet > 0:
                players_bet.append(bet)
            else:
                self.players.remove(player)

        n = len(self.players)+1
        if n == 1:
            raise ValueError("No player!")
        cards = [self.deck.deal_card() for _ in range(n*2)]
        for i in range(n):
            self.players[i].init_hand([cards[i], cards[i+n]])
        self.dealer.init_hand([cards[n-1], cards[2*n-1]])

    # TODO reset

    def get_state(self) -> str:
        pass
