from models.agent import Agent
from models.dojo import Dojo, LearnMode
from models.utils import Action, BaseState
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    agent = Agent(name="MCES10", bank=10000)
    dojo = Dojo(agent)

    # Train the agent with exploring starts
    dojo.train(episodes=100000, start_mode=LearnMode.MCES, epsilon=0.03)
    print("Training completed.")

    avg_rwd, avg_win_rate = dojo.test(episodes=10000)
