from models.agent import Agent
from models.dojo import Dojo, LearnMode
from models.utils import Action, BaseState
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    learn_mode = LearnMode.MCES

    agent = Agent(name=f"{learn_mode.name}1", bank=10000)
    dojo = Dojo(agent)

    # Train the agent with exploring starts
    dojo.train(episodes=100000, start_mode=learn_mode, epsilon=0.5)
    print("Training completed.")

    avg_rwd, avg_win_rate = dojo.test(episodes=10000)
