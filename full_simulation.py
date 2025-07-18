import random
from collections import defaultdict
from utils import plot_policy_sns
from tqdm import tqdm
from enum import Enum

from dataclasses import dataclass
# -----------------------------
# Blackjack 环境（支持 Split + Double）
# -----------------------------


@dataclass(frozen=True)
class BaseState:
    player_sum: int
    dealer_card: int
    usible_ace: bool
    splitable: bool
    can_double: bool


class Action(Enum):
    Stand = 0  # -> done with this hand
    Hit = 1  # -> hit or stand
    Double = 2  # -> done with this hand
    Split = 3  # -> hit, stand or possible split agai
    Insurance = 4  # Insurance -> hit or stand



def draw_card():
    card = random.randint(1, 13)
    return min(card, 10)

def draw_hand():
    return [draw_card(), draw_card()]

def usable_ace(hand):
    return 1 in hand and sum(hand) + 10 <= 21

def sum_hand(hand):
    s = sum(hand)
    if usable_ace(hand):
        return s + 10
    return s

def is_bust(hand):
    return sum_hand(hand) > 21

def score(hand):
    return 0 if is_bust(hand) else sum_hand(hand)

def is_pair(hand):
    return len(hand) == 2 and hand[0] == hand[1]


def can_double(hand):
    """
    判断手牌是否可以 Double（加倍）。

    规则常见约定：
    - 初始两张牌才能 Double
    - 有些赌场允许任意两张牌加倍，有些仅限特定点数范围（如 9, 10, 11）

    参数:
        hand: list[int]，玩家当前的手牌点数，如 [8, 3] 表示初始牌

    返回:
        bool: 是否可以加倍
    """
    if len(hand) != 2:
        return False

    total = sum(hand)
    # 如果有A算作11再判断
    if 1 in hand and total + 10 <= 21:
        total += 10

    # 允许加倍的总点数范围，可以根据规则定制
    return total in range(2, 21)


def is_blackjack(hand, hand_idx: int):
    return hand_idx == 0 and 1 in hand and 10 in hand

class BlackjackEnv:
    def reset(self):
        self.dealer = draw_hand()
        self.hands = [[draw_card(), draw_card()]]
        self.finished = [False]
        self.doubled = [False]
        self.current = 0
        return self._get_obs()

    def _get_obs(self):
        hand = self.hands[self.current]
        return (
            sum_hand(hand),
            self.dealer[0],
            usable_ace(hand),
            is_pair(hand) and len(self.hands) < 4,
            len(hand) == 2
        )

    def step(self, action):
        """
        执行玩家对当前手牌的一个动作，并推进游戏状态。

        参数：
            action (int): 玩家动作，0=Stand, 1=Hit, 2=Double, 3=Split

        返回：
            next_state (tuple): 当前活跃手牌的状态（或下一手牌）
            reward (float): 当前动作产生的即时奖励（大多数情况下为 0）
            done (bool): 整个游戏是否结束
            info (dict): 额外信息（此处未使用，返回空字典）
        """
        hand = self.hands[self.current]
        done = False
        reward = 0.0

        # -----------------------------
        # 动作执行
        # -----------------------------

        if action == Action.Stand:  # Stand（停牌）
            self.finished[self.current] = True

        elif action == Action.Hit:  # Hit（要牌）
            hand.append(draw_card())
            if is_bust(hand):
                self.finished[self.current] = True  # 若爆牌，结束当前手

        elif action == Action.Double:  # Double（双倍下注后只摸一张牌）
            if len(hand) == 2:
                hand.append(draw_card())
                self.finished[self.current] = True  # 不论爆不爆牌都结束
                self.doubled[self.current] = True

        elif action == Action.Split:  # Split（拆牌）
            if is_pair(hand) and len(self.hands) < 4:
                new_hand1 = [hand[0], draw_card()]
                new_hand2 = [hand[1], draw_card()]
                self.hands[self.current] = new_hand1
                self.hands.insert(self.current + 1, new_hand2)
                self.finished.insert(self.current + 1, False)
                self.doubled.insert(self.current + 1, False)
                # 拆牌后不推进 current，仍然继续操作新生成的第一手
                return self._get_obs(), 0.0, False, {}

        # -----------------------------
        # 切换到下一手未完成的牌
        # -----------------------------

        while self.current < len(self.hands) and self.finished[self.current]:
            self.current += 1

        # -----------------------------
        # 如果所有手牌已完成，进行庄家流程并计算最终奖励
        # -----------------------------

        if self.current >= len(self.hands):
            done = True  # 整个 episode 完成
            # 游戏结束，返回 None 或最后一个状态（这里选择 None）
            return None, 0.0, True, {}

        # -----------------------------
        # 返回当前状态（或 dealer 阶段后最后一个手牌状态）
        # -----------------------------

        return self._get_obs(), reward, done, {}

    def finish(self):
        """
        执行庄家流程，结算所有手牌的最终 reward。
        仅在所有手牌都完成后调用。
        """

        while sum_hand(self.dealer) < 17:
            self.dealer.append(draw_card())
        dealer_score = score(self.dealer)

        self.hand_results = []
        for idx, hand in enumerate(self.hands):
            player_score = score(hand)

            if is_bust(hand):
                result = -1.0
            else:
                result = float(player_score > dealer_score) - float(player_score < dealer_score)

            final_reward = 2 * result if self.doubled[idx] else result
            self.hand_results.append(final_reward)

        return self.hand_results

    # ====================== Utilty Functions =====================================
    def can_split(self):
        return is_pair(self.hands[self.current]) and len(self.hands) < 4

    def get_possible_actions(self):
        res = [Action.Stand, Action.Hit]
        player_hand = self.hands[self.current]
        if can_double(player_hand):
            res.append(Action.Double)
        if self.can_split():
            res.append(Action.Split)
        return res
# -----------------------------
# Monte Carlo with Split + Double
# -----------------------------


def generate_sub_episodes(env: BlackjackEnv, policy, epsilon=0.01, learning=True):
    env.reset()
    sub_episodes = []

    for i in range(len(env.hands)):
        env.current = i
        hand = env.hands[i]
        finished = env.finished[i]
        episode = []

        if is_blackjack(hand, i):
            continue

        while not finished:
            state = BaseState(
                sum_hand(hand),
                env.dealer[1],  # deal 第二张牌是明牌
                usable_ace(hand),
                env.can_split(),
                can_double(hand)
            )
            # print(f"Current hand idx:{env.current}")
            # print(state)

            if (learning and random.random() < epsilon) or (state not in policy):
                action = random.choice(env.get_possible_actions())
                # print(ACTIONS[action], "chosed randomly")
            else:
                action = policy[state]
                # print(ACTIONS[action], "chosed by policy")

            # print(ACTIONS[action])

            episode.append((state, action))
            next_state, _, done, _ = env.step(action)

            finished = env.finished[i]
            hand = env.hands[i]

        sub_episodes.append(episode)

    # 所有手牌打完后，dealer处理，返回每手 reward
    rewards = env.finish()
    return sub_episodes, rewards


def mc_control(num_episodes=200000, epsilon=0.01):
    Q: dict[BaseState, dict[Action, float]] = defaultdict(
        lambda: defaultdict(float))
    returns_sum: dict[BaseState, dict[Action, float]] = defaultdict(
        lambda: defaultdict(float))
    returns_count: dict[BaseState, dict[Action, int]
                        ] = defaultdict(lambda: defaultdict(float))
    policy: dict[BaseState, Action] = {}

    avg_rewards = 0
    win_rate = 0
    sub_episodes_count = 0
    for i in tqdm(range(num_episodes)):
        sub_episodes, rewards = generate_sub_episodes(env, policy, epsilon)

        avg_rewards += sum(rewards)
        win_rate +=sum(1 for r in rewards if r >0)
        sub_episodes_count+=len(rewards)

        for episode, reward in zip(sub_episodes, rewards):
            visited = set()
            for state, action in episode:
                if (state, action) not in visited:
                    visited.add((state, action))
                    returns_sum[state][action] += reward
                    returns_count[state][action] += 1
                    Q[state][action] = returns_sum[state][action] / returns_count[state][action]
                    best_action = max(
                        Q[state], key=lambda a: Q[state][a])
                    policy[state] = best_action

    avg_rewards /= sub_episodes_count
    win_rate /= sub_episodes_count
    print(f"Finish {sub_episodes_count} sub episodes, avg rwd:{avg_rewards}, win_rate:{win_rate}")
    return policy, Q


def test(env: BlackjackEnv, policy: dict, num_episodes=10000):
    avg_rewards = 0
    win_rate = 0
    sub_episodes_count = 0

    for i in range(num_episodes):
        _, rewards = generate_sub_episodes(
            env, policy, learning=False)  # use optimal policy

        avg_rewards += sum(rewards)
        win_rate += sum(1 for r in rewards if r > 0)
        sub_episodes_count += len(rewards)

    avg_rewards /= sub_episodes_count
    win_rate /= sub_episodes_count
    print(
        f"Finish {sub_episodes_count} sub episodes, avg rwd:{avg_rewards}, win_rate:{win_rate}")


if __name__ == "__main__":
    env:BlackjackEnv = BlackjackEnv()
    policy, Q = mc_control(epsilon=0.1)
    print("Finish training.")

    test(env=BlackjackEnv(), policy=policy)

