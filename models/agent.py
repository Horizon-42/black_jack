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

class Agent(Player):
    """
    Smart player that can learn policies
    """

    def __init__(self, name: str, bank: float = 1e100):
        super().__init__(42, bank)
        self.name = name

        self.policy: dict[BaseState, Action] = {}  # state -> action mapping
        self.Q: dict[tuple, float] = defaultdict(
            float)  # state-action -> Q value mapping
        # state-action -> count mapping, count how many times the agent has taken this action in this state
        self.state_action_count: dict[tuple, int] = defaultdict(int)

        # record the state-action pairs for each episode
        self.episode_state_action_history = []
        self.episode_return = 0  # Since we only have rewards at the end state

    def clear_episode_history(self):
        """
        Clear the episode history.
        This is called at the end of each episode.
        """
        self.episode_state_action_history.clear()
        self.episode_return = 0

    def play(self, state: BaseState, deck: Deck) -> Action:
        """
        Play the game with the given state.
        Choose an action based on the policy or explore.
        """
        possible_actions = self.__get_possible_actions(state)
        if state not in self.policy:
            # If we don't have a policy, choose a random action
            action = possible_actions[np.random.randint(len(possible_actions))]
        else:
            # Otherwise, follow the policy
            action = self.policy[state]

        self.episode_state_action_history.append((state, action))

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

        return action

    def set_episode_return(self, reward: float):
        """
        Set the return for the current episode.
        This is called at the end of the episode.
        Win 1, lose -1, draw 0.
        """
        self.episode_return = reward

    def learn_exploring_starts(self):
        # Use first-visit Monte Carlo method to update the policy
        # Because we have split hands, we may meet the same state-action pair multiple times in an episode

        # iterate over the state-action pairs in the episode
        # run the iteration in reverse order to compute the return
        first_visit = set()  # to keep track of the first visit state-action pairs
        for state, action in self.episode_state_action_history[::-1]:
            if (state, action) in first_visit:
                continue
            first_visit.add((state, action))
            # Update the state-action count
            self.state_action_count[(state, action)] += 1
            # Update the Q value using the return
            self.Q[(state, action)] += (self.episode_return -
                                        self.Q[(state, action)]) / self.state_action_count[(state, action)]

            # Update the policy, equal to argmax_a Q(s, a)
            if state not in self.policy or self.Q[(state, action)] > self.Q[(state, self.policy[state])]:
                self.policy[state] = action

    # ============================== Helper methods ==============================
    def __get_possible_actions(self, state: BaseState) -> list[Action]:
        actions = [Action.Stand, Action.Hit]
        if state.splitable:
            actions.append(Action.Split)
        if self.can_double():
            actions.append(Action.Double)
        return actions

    def __del__(self):
        logging.info(f"Saving agent policy and Q values to disk")
        # Save the policy and Q values to disk using pickle
        save_dir = f"results/agent_{self.name}/"
        os.makedirs(save_dir, exist_ok=True)
        with open(os.path.join(save_dir, "policy.pkl"), "wb") as f:
            pickle.dump(dict(self.policy), f)
        with open(os.path.join(save_dir, "Q.pkl"), "wb") as f:
            pickle.dump(dict(self.Q), f)
