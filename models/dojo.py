from .agent import Agent
from .deck import Deck
from .hand import PlayerHand, Hand
from .dealer import Dealer
from .card import Card, Rank, Suit, get_random_card
from .utils import BaseState, Action

from enum import Enum
from random import choice, choices
from itertools import product

import logging


class LearnMode(Enum):
    MCES = "MCES"
    MCE = "MCE"  # exploring with epsilon greedy

# TODO put back, card counting


class Dojo:
    """
    The Dojo class is responsible for managing the training environment for the agent.
    """

    def __init__(self, agent: Agent):
        self.agent = agent
        self.agent.clear_episode_history()

        # deck initialization
        self.deck = Deck(8)

        # init dealer
        self.dealer = Dealer()

    def train_exploring_starts(self, episodes: int = -1):
        """
        Train the agent using exploring starts.
        This method generates a set of starting hands and trains the agent on them.
        """
        starts = self.__generate_exploring_starts()
        logging.info(
            f"Training with exploring starts, running total {len(starts)} episodes...")

        avg_reward = 0
        win_rate = 0
        sub_episode_count = 0  # related to split

        i = 0
        for start_cards, start_action in starts:
            self.__refill_deck()

            self.agent.clear_episode_history()
            self.agent.set_bank_amount(1e10)  # reset bank amount

            self.dealer.reset()

            self.__init_hands(
                [start_cards[0], get_random_card(), start_cards[1], start_cards[2]])
            self.agent.first_play(
                self.__build_current_state(), start_action, self.deck)
            i += 1

            # run the game until the player has no hands left
            while not self.agent.is_all_done():
                self.agent.play(self.__build_current_state(), self.deck)

            self.dealer.hits(self.deck)

            # compute the rewards, insurance are ignored
            rewards = self.__compute_reward()
            self.agent.set_episodes_return(rewards)

            sub_episode_count += len(rewards)
            avg_reward += sum(rewards)
            win_rate += sum(1 for r in rewards if r > 0)

            logging.info(
                f"Episode {i} finished with rewards {rewards}")
            self.agent.learn_exploring_starts()

        avg_reward /= sub_episode_count
        win_rate /= sub_episode_count

        logging.info(
            f"Training finished, total episodes:{sub_episode_count}, average reward: {avg_reward}, win rate: {win_rate}.")
        return avg_reward, win_rate

    def train_exploring_greedy(self, episodes: int, epsilon: float = 0.001):
        """
        Train the agent using exploring starts.
        This method generates a set of starting hands and trains the agent on them.
        """
        logging.info(
            f"Training MC epsilon greedy, running total {episodes} episodes...")

        avg_reward = 0
        win_rate = 0
        sub_episode_count = 0  # related to split

        for i in range(episodes):
            self.__refill_deck()

            self.agent.clear_episode_history()
            self.agent.set_bank_amount(1e10)  # reset bank amount

            self.dealer.reset()

            self.__init_hands(
                [self.deck.deal_card() for _ in range(4)])

            # run the game until the player has no hands left
            while not self.agent.is_all_done():
                self.agent.play(self.__build_current_state(), self.deck)

            self.dealer.hits(self.deck)

            # compute the rewards, insurance are ignored
            rewards = self.__compute_reward()
            self.agent.set_episodes_return(rewards)

            sub_episode_count += len(rewards)
            avg_reward += sum(rewards)
            win_rate += sum(1 for r in rewards if r > 0)

            logging.info(
                f"Episode {i} finished with rewards {rewards}")
            self.agent.learn_epsilon_greedy(epsilon)

        avg_reward /= sub_episode_count
        win_rate /= sub_episode_count

        logging.info(
            f"Training finished, total episodes:{sub_episode_count}, average reward: {avg_reward}, win rate: {win_rate}.")
        return avg_reward, win_rate

    def train(self, episodes: int = 1000, start_mode: LearnMode = LearnMode.MCES, epsilon=0.001):
        """
        Train the agent for a given number of episodes.
        :param episodes: Number of training episodes.
        :param deck_init_mode: Mode to initialize the deck.
        """
        if start_mode == LearnMode.MCES:
            self.train_exploring_starts(episodes)
        elif start_mode == LearnMode.MCE:
            self.train_exploring_greedy(episodes, epsilon)
        else:
            pass

    def test(self, episodes: int = 1000, verbose=False):
        """
        Test the agent for a given number of episodes.
        :param episodes: Number of testing episodes.
        """
        logging.info(f"Testing agent for {episodes} episodes...")
        avg_reward = 0
        win_rate = 0
        sub_episode_count = 0

        for _ in range(episodes):
            self.__refill_deck()

            self.agent.clear_episode_history()
            self.agent.set_bank_amount(1e10)
            self.dealer.reset()

            # deal initial cards
            self.__init_hands([self.deck.deal_card() for _ in range(4)])
            # run the game until the player has no hands left
            while not self.agent.is_all_done():
                if self.agent.get_hand().points >= 21:
                    self.agent.done_with_hand()
                    continue
                self.agent.play(self.__build_current_state(), self.deck)
            self.dealer.hits(self.deck)
            if verbose:
                self.__print_final_state()

            # compute the reward
            rewards = self.__compute_reward()
            if verbose:
                print(f"Gain reward:{sum(rewards)}")
                print("=======================")

            sub_episode_count += len(rewards)
            avg_reward += sum(rewards)
            win_rate += sum(1 for r in rewards if r > 0)

        avg_reward /= sub_episode_count
        win_rate /= sub_episode_count

        logging.info(
            f"Testing finished, total episodes:{sub_episode_count}, average reward: {avg_reward}, win rate: {win_rate}.")
        return avg_reward, win_rate


    # ============================== Helper methods ==============================

    def __init_hands(self, cards: list[Card]):
        """
        Initialize the player and dealer hands with the given start cards.
        """
        self.agent.init_hand(
            [cards[0], cards[2]], 1)
        self.dealer.init_hand(
            [cards[1], cards[3]])


    def __generate_exploring_starts(self):
        start_state_actions: list[tuple[tuple, Action]] = []

        delear_up_cards: list[Card] = [
            Card(choice([suit for suit in Suit]), rank) for rank in Rank]

        # agent cards
        # have useable ace
        player_first_cards = [Card(choice([suit for suit in Suit]), Rank.ACE)]
        # second card can be any rank, maximum sum 21, two aces count as 12
        player_second_cards = [Card(choice([suit for suit in Suit]), rank)
                               for rank in Rank]

        soft_start_cards = [(player_first_card, player_second_card, delar_card)
                            for player_first_card, player_second_card, delar_card in product(
            player_first_cards, player_second_cards, delear_up_cards)]
        soft_actions = [Action.Stand, Action.Hit, Action.Double]
        start_state_actions.extend(
            [(state, action) for state, action in product(soft_start_cards, soft_actions)])

        # have pair
        player_first_cards = [
            Card(choice([suit for suit in Suit]), rank) for rank in Rank]
        split_cards = [(player_first_card, player_first_card, delar_card)
                       for player_first_card, delar_card in product(player_first_cards, delear_up_cards)]
        ten_points_cards = [Card(choice([suit for suit in Suit]), rank) for rank in [
            Rank.TEN, Rank.JACK, Rank.KING, Rank.QUEEN]]
        split_cards.extend([(player_1st_card, player_2ed_card, dealer_card)
                           for player_1st_card, player_2ed_card, dealer_card
                           in product(ten_points_cards, ten_points_cards, delear_up_cards)])
        split_actions = [Action.Split, Action.Stand, Action.Hit, Action.Double]

        start_state_actions.extend(
            [(state, action) for state, action in product(split_cards, split_actions)])


        # have no useable ace, no pair
        player_first_cards = [Card(choice([suit for suit in Suit]), rank)
                              for rank in Rank if rank != Rank.ACE]
        player_second_cards = [Card(choice([suit for suit in Suit]), rank)
                               for rank in Rank if rank != Rank.ACE]
        hard_cards = [(player_first_card, player_second_card, delar_card) for
                      player_first_card, player_second_card, delar_card in product(
            player_first_cards, player_second_cards, delear_up_cards)]
        hard_actions = [Action.Stand, Action.Hit, Action.Double]
        start_state_actions.extend(
            [(state, action) for state, action in product(hard_cards, hard_actions)])

        # remove duplicates
        return start_state_actions

    def __build_current_state(self) -> BaseState:
        """
        Build the base state from the current player and dealer hands.
        """
        try:
            return BaseState(
                player_sum=self.agent.get_hand().points,
                dealer_card=self.dealer.get_face_point(),
                usible_ace=self.agent.get_hand().is_soft,
                splitable=self.agent.can_split()
            )
        except ValueError as e:
            logging.error(f"Error building state: {e}")
            raise ValueError("Cannot build state from current hands.")

    def __refill_deck(self):
        """
        Refill the deck if it is empty.
        """
        if len(self.deck.cards) < 30:
            self.deck = Deck(8)
            logging.debug("Deck refilled.")

    def __get_hand_reward(self, player_hand: PlayerHand) -> float:
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

    def __compute_reward(self):
        """
        Compute the reward
        """
        rewards = [self.__get_hand_reward(hand)
                   for hand in self.agent.get_all_hands()]
        # disable insurance
        rewards.append(0)
        self.agent.pay_out(rewards)
        return rewards[:-1]

    def __print_final_state(self):
        print("\nFinal state:")
        print("Dealer's hand:", self.dealer.get_hand())
        print("Player's hands:")
        for hand in self.agent.get_all_hands():
            print(hand)
