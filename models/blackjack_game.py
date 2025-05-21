from player import Player
from card import Card
from hand import Hand
from deck import Deck
from dealer import Dealer


class BlackJackGame(object):
    players: list[Player]
    dealer: Dealer
    deck: Deck

    def __init__(self, player_num: int = 1):
        self.deck = Deck()
        self.deck.shuffle()
        # to do or not?
        self.deck.burn_out()

        # init hand for players
        for _ in range(player_num):
            self.players.append(
                Player(self.deck.deal_card(), self.deck.deal_card()))
        # init hand for dealer
        self.dealer = Dealer(self.deck.deal_card(), self.deck.deal_card())

    def get_state(self) -> str:
        pass
