from env import BlackjackEnv
import os
import pickle
import logging
from deck import BlackJackDeck, NormalDeck
from init_strategy import generate_basic_strategy
from episodes_generator import EpisodesGenerator
from tqdm import tqdm


def test(env: BlackjackEnv, policy: dict, num_episodes=10000):
    avg_rewards = 0

    win_rate = 0
    black_jack_rate = 0
    draw_rate = 0
    loss_rate = 0
    double_win_rate = 0
    double_loss_rate = 0

    sub_episodes_count = 0

    episodes_generator = EpisodesGenerator(0)

    for i in tqdm(range(num_episodes)):
        episodes, rewards = episodes_generator.generate_episodes(
            env, policy)  # use optimal policy

        avg_rewards += sum(rewards)
        sub_episodes_count += len(rewards)

        if not episodes[0] and rewards[0] == 1.5:
            black_jack_rate += 1
            continue
        win_rate += sum(1 for r in rewards if r == 1)
        draw_rate += sum(1 for r in rewards if r == 0)
        loss_rate += sum(1 for r in rewards if r == -1)
        double_win_rate += sum(1 for r in rewards if r == 2)
        double_loss_rate += sum(1 for r in rewards if r == -2)

    avg_rewards /= sub_episodes_count
    win_rate /= sub_episodes_count
    draw_rate /= sub_episodes_count
    loss_rate /= sub_episodes_count
    double_win_rate /= sub_episodes_count
    double_loss_rate /= sub_episodes_count
    black_jack_rate /= sub_episodes_count
    print(
        f"Finish {sub_episodes_count} sub episodes, avg rwd:{avg_rewards}, win_rate:{win_rate}")

    logging.info(
        f"Test finish with avg_rewards: {avg_rewards}, double_win_rate:{double_win_rate}, double_loss_rate:{double_loss_rate}, win_rate: {win_rate}, black_jack_rate:{black_jack_rate}, draw_rate:{draw_rate}, loss_rate:{loss_rate}")
    return avg_rewards, double_win_rate, double_loss_rate, win_rate, black_jack_rate, draw_rate, loss_rate


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
