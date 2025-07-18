from train_mc import BlackjackEnv, BaseState, Action, test, draw_card
import os
import pickle
import logging
from deck import BlackJackDeck, NormalDeck
from init_strategy import generate_basic_strategy


def test_basic_strategy(deck_num: int = 6):
    env: BlackjackEnv = BlackjackEnv(
        given_draw_card=NormalDeck(deck_num).deal_card)

    policy = generate_basic_strategy()

    avg_rewards, double_win_rate, double_loss_rate, win_rate, black_jack_rate, draw_rate, loss_rate = test(
        env=env, policy=policy, num_episodes=1000000)
    print(f"avg_rewards:{avg_rewards}")
    print(f"double_win_rate:{double_win_rate}")
    print(f"double_loss_rate:{double_loss_rate}")
    print(f"win_rate:{win_rate}")
    print(f"black_jack_rate:{black_jack_rate}")
    print(f"draw_rate:{draw_rate}")
    print(f"loss_rate:{loss_rate}")

    expetation = double_win_rate*2 + double_loss_rate * \
        (-2) + win_rate*1+black_jack_rate*1.5+loss_rate*(-1)
    print(f"Expetation of basic strategy is {expetation}")



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename="test.log")

    deck_num = 1

    test_basic_strategy()

    env: BlackjackEnv = BlackjackEnv(
        given_draw_card=NormalDeck(deck_num).deal_card)

    name = "MCE_WITH_BASIC"
    save_dir = f"results/agent_{name}/"

    with open(f"{save_dir}/policy.pkl", "rb") as f:
        policy = pickle.load(f)
    with open(f"{save_dir}/Q.pkl", "rb") as f:
        Q = pickle.load(f)

    avg_rewards, double_win_rate, double_loss_rate, win_rate, black_jack_rate, draw_rate, loss_rate = test(
        env=env, policy=policy, num_episodes=1000000)
    print(f"avg_rewards:{avg_rewards}")
    print(f"double_win_rate:{double_win_rate}")
    print(f"double_loss_rate:{double_loss_rate}")
    print(f"win_rate:{win_rate}")
    print(f"black_jack_rate:{black_jack_rate}")
    print(f"draw_rate:{draw_rate}")
    print(f"loss_rate:{loss_rate}")

    expetation = double_win_rate*2 + double_loss_rate * \
        (-2) + win_rate*1+black_jack_rate*1.5+loss_rate*(-1)
    print(f"Expetation of this agent {name} is {expetation}")
