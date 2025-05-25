from models.player import Player
from models.deck import Deck
from models.dealer import Dealer
from models.hand import PlayerHand, Hand
from enum import Enum


class Action(Enum):
    Stand = 0  # -> done with this hand
    Hit = 1  # -> hit or stand
    Split = 2  # -> hit, stand or possible split again
    Double = 3  # -> done with this hand
    Insurance = 4  # Insurance -> hit or stand


class Interaction(object):
    @staticmethod
    def cash_in_chips() -> int:
        # read money from terminal
        try:
            return int(input("How many chips do you want to cash in?\n"))
        except ValueError:
            return 0

    @staticmethod
    def get_init_bet(max_bet: int):
        bet = 0
        while bet <= 0 or bet > max_bet:
            try:
                bet = int(
                    input("How many chips do you want to bet on this hand?\n"))
            except ValueError:
                print("Please enter a valid bet amount.")
        return bet

    @staticmethod
    def get_action(possible_actions: list[Action]) -> Action:
        action = None
        print("Possible actions are: ", [
            f"{a.value}, {a.name}" for a in possible_actions])
        while action not in possible_actions:
            try:
                action = Action(int(input(f"What do you want to do?\n")))
            except ValueError:
                pass
        return action

class State(object):
    def __init__(self, dealer_hand: Hand, player_hand: PlayerHand):
        self.__dealer_hand: Hand = dealer_hand
        self.__player_hand: PlayerHand = player_hand

    def __str__(self):
        res = ""
        res += f"Dealer's hand: {self.__dealer_hand},\n"
        res += f"Player's hand: {self.__player_hand}\n"
        return res


class BlackJackGame(object):
    def __init__(self):
        self.deck = Deck(6)
        self.__init_player()
        self.dealer = Dealer()
        self.__init_hands()
        self.__can_insure: bool = True

        self.state_action_history = []

    def __init_player(self):
        bank = Interaction.cash_in_chips()
        self.player = Player(0, bank)

    def __init_hands(self):
        bet = Interaction.get_init_bet(self.player.get_bank_amount())
        cards = [self.deck.deal_card() for _ in range(4)]
        self.player.init_hand([cards[0], cards[2]], bet)
        self.dealer.init_hand([cards[1], cards[3]])

    def _get_state(self) -> State:
        return State(dealer_hand=self.dealer.get_hand(),
                     player_hand=self.player.get_hand())

    def _print_final_state(self):
        print("\nFinal state:")
        print("Dealer's hand:", self.dealer.get_hand())
        print("Player's hands:")
        for hand in self.player.get_all_hands():
            print(hand)

    def _get_possible_actions(self) -> list[Action]:
        # no possible actions if player's hand is bust or has 21 points
        if self.player.get_hand().points >= 21:
            return []
        res = [Action.Stand, Action.Hit]
        if self.__can_insure and self.dealer.get_face_point() == 11:
            res.append(Action.Insurance)
            self.__can_insure = False
        if self.player.can_double():
            res.append(Action.Double)
            if self.player.has_pair():
                res.append(Action.Split)
        # sort actions by their value
        res.sort(key=lambda x: x.value)
        return res

    def _get_insurance_reward(self) -> float:
        # insurance
        insurance_reward = 0
        insurance_rate = self.player.get_insurance_rate()
        if insurance_rate > 0:
            if self.dealer.is_blackjack():
                insurance_reward = insurance_rate*2
            else:
                insurance_reward = -insurance_rate
        return insurance_reward

    def _get_hand_reward(self, player_hand: PlayerHand) -> float:
        main_bet_reward = 0
        # blackjack
        if player_hand.is_blackjack():
            if self.dealer.is_blackjack():
                main_bet_reward = 0
            else:
                main_bet_reward = 1.5
        elif self.dealer.is_blackjack():
            main_bet_reward = -1
        # bust
        elif player_hand.is_bust():
            main_bet_reward = -1
        # win
        elif self.dealer.is_bust():
            main_bet_reward = 1
        elif player_hand.points > self.dealer.reveal_hand():
            main_bet_reward = 1
        # lose
        elif player_hand.points < self.dealer.reveal_hand():
            main_bet_reward = -1
        # push
        elif player_hand.points == self.dealer.reveal_hand():
            main_bet_reward = 0
        # double
        if player_hand.doubled:
            main_bet_reward *= 2
        return main_bet_reward


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


    def round(self):
        while not self.player.is_all_done():
            state = self._get_state()
            print("\nCurrent state:")
            print(state)
            posible_actions = self._get_possible_actions()
            action = None
            if not posible_actions:
                print("No possible actions, player done with this hand.")
                self.player.done_with_hand()
                continue
            action = Interaction.get_action(posible_actions)
            # Record the state-action pair
            self.state_action_history.append((state, action))
            self.step(action)
        #
        print("\nPlayer done, dealer hits...")
        self.dealer.hits(self.deck)
        # calculate rewards
        self._print_final_state()

        player_hands = self.player.get_all_hands()
        rewards = [self._get_hand_reward(hand) for hand in player_hands]
        rewards.append(self._get_insurance_reward())
        print(f"\nPlayer's bank: {self.player.get_bank_amount()}, ", end="")
        print(f"with bet {self.player.get_all_bets()}, ", end="")
        print(f"insurance {self.player.get_insurance_amount()}")
        print("Rewards:", rewards)
        print("Total reward:", sum(rewards))
        print(f"Gain: {self.player.pay_out(rewards)}")
        print("Player's bank:", self.player.get_bank_amount())
        print("Round ended.\n\n")
        return state, rewards

    def play(self):
        while True:
            print("Starting a new round...")
            self.round()
            if self.player.get_bank_amount() <= 0:
                print("Player has no more chips, game over!")
                break
            self.reset()
        print("Game ended.")

    def reset(self):
        if len(self.deck.cards) < 20:
            self.deck = Deck(6)
        if self.player.get_bank_amount() == 0:
            self.__init_player()

        self.dealer.reset()
        self.__init_hands()
        self.__can_insure: bool = True
        return self._get_state()
