from player import Player
from card import Card
from hand import Hand
from deck import Deck
from dealer import Dealer


def get_bank_money(player_id: int) -> int:
    # read money from terminal
    try:
        return int(input("Please input your bank money amout, only number: "))
    except ValueError:
        return 0

class BlackJackGame(object):
    players: list[Player]
    dealer: Dealer
    deck: Deck

    def __init__(self, player_num=1):
        self.deck = Deck(6)
        self.__init_players(player_num)
        self.dealer = Dealer()
        self.__init_hands()

    def __init_players(self, player_num: int = 1):
        for i in range(player_num):
            # input from terminal
            bank = get_bank_money(i)
            if bank > 0:
                self.players.append(Player(bank))

    def __init_hands(self):
        n = len(self.players)+1
        if n == 1:
            raise ValueError("No player!")
        cards = [self.deck.deal_card() for _ in range(n*2)]
        for i in range(n):
            self.players[i].init_hand([cards[i], cards[i+n]])
        self.dealer.init_hand([cards[n-1], cards[2*n-1]])

    def get_state(self) -> str:
        pass
