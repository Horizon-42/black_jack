import random
from collections import defaultdict
from utils import plot_policy_sns
# -----------------------------
# Blackjack 环境（支持 Split + Double）
# -----------------------------

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

        if action == 0:  # Stand（停牌）
            self.finished[self.current] = True

        elif action == 1:  # Hit（要牌）
            hand.append(draw_card())
            if is_bust(hand):
                self.finished[self.current] = True  # 若爆牌，结束当前手

        elif action == 2:  # Double（双倍下注后只摸一张牌）
            if len(hand) == 2:
                hand.append(draw_card())
                self.finished[self.current] = True  # 不论爆不爆牌都结束
                self.doubled[self.current] = True

        elif action == 3:  # Split（拆牌）
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
# -----------------------------
# Monte Carlo with Split + Double
# -----------------------------

ACTIONS = {
    0: "Stand",
    1: "Hit",
    2: "Double",
    3: "Split"
}

def generate_sub_episodes(env:BlackjackEnv, policy, epsilon=0.1):
    env.reset()
    sub_episodes = []

    for i in range(len(env.hands)):
        env.current = i
        hand = env.hands[i]
        finished = env.finished[i]
        episode = []

        while not finished:
            state = (
                sum_hand(hand),
                env.dealer[0],
                usable_ace(hand),
                is_pair(hand) and len(env.hands) < 4,
                len(hand) == 2
            )

            if random.random() < epsilon or state not in policy:
                action = random.choice([0, 1, 2, 3])
            else:
                action = policy[state]

            episode.append((state, action))
            next_state, _, done, _ = env.step(action)

            finished = env.finished[i]
            hand = env.hands[i]

        sub_episodes.append(episode)

    # 所有手牌打完后，dealer处理，返回每手 reward
    rewards = env.finish()
    return sub_episodes, rewards

def mc_control(num_episodes=200000):
    Q = defaultdict(lambda: [0.0] * 4)
    returns_sum = defaultdict(lambda: [0.0] * 4)
    returns_count = defaultdict(lambda: [0] * 4)
    policy = {}

    avg_rewards = 0
    win_rate = 0
    sub_episodes_count = 0
    for i in range(num_episodes):
        sub_episodes, rewards = generate_sub_episodes(env, policy)

        print(rewards)
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
                    best_action = max(range(4), key=lambda a: Q[state][a])
                    policy[state] = best_action

    avg_rewards /= sub_episodes_count
    win_rate /= sub_episodes_count
    print(f"Finish {sub_episodes_count} sub episodes, avg rwd:{avg_rewards}, win_rate:{win_rate}")
    return policy, Q

# -----------------------------
# 策略可视化（仅打印部分）
# -----------------------------

def print_policy(policy):
    print(f"{'P_sum':>6} {'D_card':>7} {'UsAce':>6} {'Split':>6} {'Double':>7} {'Action':>10}")
    for state in sorted(policy.keys())[:50]:  # 只显示前 50 条
        psum, dcard, usace, split, doub = state
        action = ACTIONS[policy[state]]
        print(f"{psum:>6} {dcard:>7} {str(usace):>6} {str(split):>6} {str(doub):>7} {action:>10}")

# -----------------------------
# Run
# -----------------------------

if __name__ == "__main__":
    env:BlackjackEnv = BlackjackEnv()
    policy, Q = mc_control()
    print("训练完成。示例策略如下：\n")
    print_policy(policy)

    # print(policy)

    # plot_policy_sns(policy)

