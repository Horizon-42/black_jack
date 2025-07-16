# Record the S, A, R sequence
# compute the Reward using discount rate G or simple sum of all future rewards
import numpy as np
from .player import Player
from .utils import Action, BaseState
from .deck import Deck
import pickle

import logging
import os
from collections import defaultdict
from dataclasses import dataclass
from random import choice


@dataclass
class EpisodeHistory:
    state_action_history: list[tuple]
    terminal_return: float


class Agent(Player):
    """
    Smart player that can learn policies
    """

    def __init__(self, name: str, bank: float = 1e100):
        super().__init__(42, bank)
        self.name = name

        self.policy: dict[BaseState, Action] = {}  # state -> action mapping
        self.Q: dict[BaseState, dict[Action, float]
                     ] = defaultdict(lambda: defaultdict(float))
        # state-action -> count mapping, count how many times the agent has taken this action in this state
        self.state_action_count: dict[BaseState,
                                      dict[Action, int]] = defaultdict(lambda: defaultdict(int))
        self.state_action_space: dict[BaseState,
                                      list[Action]] = defaultdict(set)

        # record the state-action pairs for each episode
        self.current_hand_history: EpisodeHistory = EpisodeHistory([], 0)
        self.all_histories: list[EpisodeHistory] = []

    def done_with_hand(self):
        super().done_with_hand()
        # deal with episode history
        self.all_histories.append(self.current_hand_history)
        self.current_hand_history = EpisodeHistory([], 0)

    def clear_episode_history(self):
        """
        Clear the episode history.
        This is called at the end of each episode.
        """
        self.current_hand_history = EpisodeHistory([], 0)
        self.all_histories = []

    def first_play(self, state: BaseState, init_action: Action, deck: Deck) -> bool:
        possible_actions = self.__get_possible_actions(state)
        if state not in self.state_action_space:
            self.state_action_space[state] = set(possible_actions)
        if init_action not in possible_actions:
            return False

        self.__play(state, init_action, deck)

        return True

    def play(self, state: BaseState, deck: Deck):
        """
        Play the game with the given state.
        Choose an action based on the policy or explore.
        """
        possible_actions = self.__get_possible_actions(state)
        if state not in self.state_action_space:
            self.state_action_space[state] = set(possible_actions)

        if state not in self.policy:
            # If we don't have a policy, choose a random action
            action = choice(possible_actions)
        else:
            # Otherwise, follow the policy
            action = self.policy[state]

        self.__play(state, action, deck)


    def set_episodes_return(self, rewards: list[float]):
        """
        Set the return for the current episode.
        This is called at the end of the episode.
        Win 1, lose -1, draw 0.
        """
        for i, reward in enumerate(rewards):
            self.all_histories[i].terminal_return = reward

    def learn_exploring_starts(self):
        # Use first-visit Monte Carlo method to update the policy

        # iterate over the state-action pairs in the episode
        # run the iteration in reverse order to compute the return
        for history in self.all_histories:
            state_action_histroy = history.state_action_history
            episode_return = history.terminal_return
            first_vist = set()
            for state, action in state_action_histroy:
                if (state, action) in first_vist:
                    continue
                first_vist.add((state, action))
                # Update the state-action count
                self.state_action_count[state][action] += 1
                # Update the Q value using the return
                self.Q[state][action] += (episode_return -
                                          self.Q[state][action]) / self.state_action_count[state][action]

                # Update the policy, equal to argmax_a Q(s, a)
                if state not in self.policy or self.Q[state][action] > self.Q[state][self.policy[state]]:
                    self.policy[state] = action
                # if state not in self.policy:
                #     self.policy[state] = action
                # else:
                # self.policy[state] = self.__get_max_q_acion(state)

    def learn_epsilon_greedy(self, epsilon=0.01):
        # Use first-visit Monte Carlo method to update the policy
        # Because we have split hands, we may meet the same state-action pair multiple times in an episode

        # iterate over the state-action pairs in the episode
        # run the iteration in reverse order to compute the return
        for history in self.all_histories:
            state_action_histroy = history.state_action_history
            episode_return = history.terminal_return
            first_visit = set()  # to keep track of the first visit state-action pairs
            for state, action in state_action_histroy:
                if (state, action) in first_visit:
                    continue
                first_visit.add((state, action))
                # Update the state-action count
                self.state_action_count[state][action] += 1
                # Update the Q value using the return
                self.Q[state][action] += (episode_return -
                                          self.Q[state][action]) / self.state_action_count[state][action]

                greedy_action = self.__get_max_q_acion(state)

                if np.random.rand() < (1-epsilon):
                    self.policy[state] = greedy_action
                else:
                    self.policy[state] = choice(
                        list(self.state_action_space[state]))

    # ============================== Helper methods ==============================
    def __get_max_q_acion(self, state: BaseState):
        return max(self.Q[state].items(), key=lambda item: item[1])[0]

    def __get_possible_actions(self, state: BaseState) -> list[Action]:
        actions = [Action.Stand, Action.Hit]
        if state.splitable:
            actions.append(Action.Split)
        if self.can_double():
            actions.append(Action.Double)
        return actions

    def __play(self, state: BaseState, action: Action, deck: Deck):
        """
        Add state action pair to history, then run action
        """
        self.current_hand_history.state_action_history.append(
            (state, action))
        # Transition to the next state based on the action
        if action == Action.Stand:
            self.stand()
        elif action == Action.Hit:
            self.hit(deck.deal_card())
        elif action == Action.Double:
            self.double(deck.deal_card())
        elif action == Action.Split:
            self.split(deck.deal_card(), deck.deal_card())
        elif action == Action.Insurance:
            self.insurance()
        else:
            raise ValueError("Invalid action")

        logging.debug(
            f"Agent Chose action {action} in state {state}")

        # judge if hit 21 or bust
        if not self.is_all_done() and self.get_hand().points >= 21:
            self.done_with_hand()


    def __del__(self):
        logging.info(f"Saving agent policy and Q values to disk")
        # Save the policy and Q values to disk using pickle
        save_dir = f"results/agent_{self.name}/"
        os.makedirs(save_dir, exist_ok=True)
        with open(os.path.join(save_dir, "policy.pkl"), "wb") as f:
            pickle.dump(dict(self.policy), f)
        with open(os.path.join(save_dir, "Q.pkl"), "wb") as f:
            self.Q = dict(self.Q)
            for k in self.Q:
                self.Q[k] = dict(self.Q[k])
            pickle.dump(dict(self.Q), f)
