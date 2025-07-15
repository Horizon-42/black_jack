# Record the S, A, R sequence
# compute the Reward using discount rate G or simple sum of all future rewards
import numpy as np
from player import Player
from utils import Action, State


class Agent(Player):
    """
    Smart player that can learn policies
    """

    def __init__(self, name: str, bank: float = 1e100):
        super().__init__(name, bank)

        self.policy: dict[State, Action] = {}  # state -> action mapping
        self.Q: dict[tuple, float] = {}  # state-action -> value mapping
        # state-action -> count mapping, count how many times the agent has taken this action in this state
        self.state_action_count: dict[tuple, int] = {}

        # record the state-action pairs for each episode
        self.episode_state_action_history = []
        self.episode_return = 0  # Since we only have rewards at the end state

    def play(self, state: State, possible_actions: list[Action]) -> Action:
        """
        Play the game with the given state.
        Choose an action based on the policy or explore.
        """
        if state not in self.policy:
            # If we don't have a policy, choose a random action
            action = possible_actions[np.random.randint(len(possible_actions))]
        else:
            # Otherwise, follow the policy
            action = self.policy[state]

        self.episode_state_action_history.append((state, action))
        return action

    def set_episode_return(self, reward: float):
        """
        Set the return for the current episode.
        This is called at the end of the episode.
        Win 1, lose -1, draw 0.
        """
        self.episode_return = reward

    def learn_exploring_starts(self):
        # Because we won't have same state-action pairs in the episode,
        # the first visit and the every visit will be the same.

        # iterate over the state-action pairs in the episode
        # run the iteration in reverse order to compute the return
        for action, state in self.episode_state_action_history[::-1]:
            # Update the state-action count
            if (state, action) not in self.state_action_count:
                self.state_action_count[(state, action)] = 0
            self.state_action_count[(state, action)] += 1

            # Update the Q value
            if (state, action) not in self.Q:
                self.Q[(state, action)] = 0.0

            # Update the Q value using the return
            self.Q[(state, action)] += (self.episode_return -
                                        self.Q[(state, action)]) / self.state_action_count[(state, action)]

            # Update the policy
            self.policy[state] = max(self.Q.items(), key=lambda x: x[1])[
                0] if state in self.policy else action
