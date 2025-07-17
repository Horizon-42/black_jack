from train_mc import BlackjackEnv, BaseState, Action, test
import os
import pickle
import logging
from deck import BlackJackDeck



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filename="test.log")

    env: BlackjackEnv = BlackjackEnv()

    name = "MCES0"
    save_dir = f"results/agent_{name}/"

    with open(f"{save_dir}/policy.pkl", "rb") as f:
        policy = pickle.load(f)
    with open(f"{save_dir}/Q.pkl", "rb") as f:
        Q = pickle.load(f)

    test(env=env, policy=policy, num_episodes=100)
