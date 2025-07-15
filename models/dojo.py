from .blackjack_game import BlackJackGame
from .agent import Agent
from .deck import Deck
from .hand import PlayerHand, Hand
from .dealer import Dealer


class Dojo(BlackJackGame):
    """
    The Dojo class is a specialized version of the BlackJackGame that allows for
    training agents in a controlled environment.
    """

    def __init__(self, agent: Agent):
        super().__init__()
        self.agent = agent
        self.agent.episode_state_action_history = []
        self.agent.episode_return = 0

    def reset(self):
        """
        Reset the game state for a new episode.
        """
        self.deck = Deck(6)
        self.__init_player()
        self.dealer = Dealer()
        self.__init_hands()
        self.agent.episode_state_action_history.clear()
        self.agent.episode_return = 0