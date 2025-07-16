from models.agent import Agent
from models.dojo import Dojo, StartMode
from models.utils import Action, BaseState
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    agent = Agent(id = 42, bank=10000)
    dojo = Dojo(agent)

    # Train the agent with exploring starts
    dojo.train(episodes=1000, start_mode=StartMode.Exploring)
    print("Training completed.")