from models.player import Player
from models.deck import Deck
from models.dealer import Dealer
from enum import Enum


class Action(Enum):
    Stand = 0  # -> done with this hand
    Hit = 1  # -> hit or stand
    Split = 2  # -> hit, stand or possible split again
    Double = 3  # -> done with this hand
    Insurance = 4  # Insurance -> hit or stand


def cash_in_chips() -> int:
    # read money from terminal
    try:
        return int(input("How many chips do you want to cash in? "))
    except ValueError:
        return 0


def get_init_bet(max_bet: int):
    bet = 0
    try:
        bet = int("How many chips do you want to bet on this hand?")
    except ValueError:
        pass
    return bet if bet <= max_bet else 0


def get_action(possible_actions: list[Action]) -> Action:
    action = None
    print("Possible actions are: ", [
          f"{a.value}, {a.name}" for a in possible_actions])
    while action not in possible_actions:
        try:
            action = int(input(f"What do you want to do?"))
        except ValueError:
            pass
    return action

class State(object):
    def __init__(self):
        self.__deal_point: int = 0
        self.__player_point: int = 0

    def __str__(self):
        return f"Dealer point:{self.__deal_point},\n Player point{self.__player_point}"


class BlackJackGame(object):
    # TODO Rewards

    def __init__(self):
        self.deck = Deck(6)
        self.__init_player()
        self.dealer = Dealer()
        self.__init_hands()
        self.__is_intial: bool = True

    def __init_player(self):
        bank = cash_in_chips()
        self.player = Player(0, bank)

    def __init_hands(self):
        bet = get_init_bet(self.player.get_bank_amount())
        cards = [self.deck.deal_card() for _ in range(4)]
        self.player.init_hand([cards[0], cards[2]], bet)
        self.dealer.init_hand([cards[1], cards[3]])

    def _get_state(self) -> State:
        return State(self.player)

    def _get_possible_actions(self):
        res = [Action.Stand, Action.Hit]
        if self.__is_intial:
            res.append(Action.Double)
            if self.player.has_pair():
                res.append(Action.Split)
        if self.dealer.get_face_point() == 11:
            res.append(Action.Insurance)
            self.__is_intial = False

        return res

    def _get_reward(self):
        # blackjack
        # insurance
        insurance_reward = 0
        insurance_rate = self.player.get_insurance_rate()
        if insurance_rate > 0:
            if self.dealer.is_black_jack():
                insurance_reward = insurance_rate*2
            else:
                insurance_reward = -insurance_rate

        main_bet_reward = 0
        # blackjack
        if self.player.is_blackjack():
            if self.dealer.is_blackjack():
                main_bet_reward = 0
            else:
                main_bet_reward = 1.5
        elif self.dealer.is_blackjack():
            main_bet_reward = -1
        # bust
        elif self.player.is_bust():
            main_bet_reward = -1
        # win
        elif self.dealer.is_bust():
            main_bet_reward = 1
        elif self.player.points > self.dealer.reveal_hand():
            main_bet_reward = 1
        # lose
        elif self.player.points < self.dealer.reveal_hand():
            main_bet_reward = -1
        # push
        elif self.player.points == self.dealer.reveal_hand():
            main_bet_reward = 0
        return main_bet_reward + insurance_reward


    # setp
    def step(self, action: Action):
        if action == Action.Stand:
            self.player.stand()
        elif action == Action.Hit:
            self.player.hit(self.deck.deal_card())
        elif action == Action.Double:
            self.player.double(self.deck.deal_card())
        elif action == Action.Split:
            self.player.split()
        elif action == Action.Insurance:
            self.player.insurance()
        else:
            raise ValueError("Invalid action")

    def play(self):
        while not self.player.is_all_done():
            state = self._get_state()
            print(state)
            posible_actions = self._get_possible_actions()
            action = get_action(posible_actions)
            self.step(action)
        self.dealer.hits(self.deck)
        reward = self._get_reward()
        state = self._get_state()
        self.player.pay_out(reward)
        self.reset()
        return state, reward

    # TODO reset
    def reset(self):
        if len(self.deck.cards) < 20:
            self.deck = Deck(6)
        if self.player.get_bank_amount() == 0:
            self.__init_player()
        else:
            self.player.reset()
        self.dealer.reset()
        self.__init_hands()
        self.__is_intial: bool = True
        return self._get_state()
