from train_mc import BlackjackEnv, BaseState, Action, test
import os
import pickle
import logging
from deck import BlackJackDeck



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    deck = BlackJackDeck()
    env: BlackjackEnv = BlackjackEnv()

    name = "MCE3"
    save_dir = f"results/agent_{name}/"

    with open(f"{save_dir}/policy.pkl", "rb") as f:
        policy = pickle.load(f)
    with open(f"{save_dir}/Q.pkl", "rb") as f:
        Q = pickle.load(f)

    test(env=env, policy=policy, num_episodes=10000)
