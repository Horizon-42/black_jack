from models.agent import Agent
from models.dojo import Dojo, StartMode
from models.utils import Action, BaseState
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    agent = Agent(name="MCES3", bank=10000)
    dojo = Dojo(agent)

    # Train the agent with exploring starts
    dojo.train(episodes=1000000, start_mode=StartMode.Exploring)
    print("Training completed.")

    avg_rwd, avg_win_rate, avg_lose_rate = dojo.test(episodes=1000)
