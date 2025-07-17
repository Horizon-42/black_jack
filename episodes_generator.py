from env import BlackjackEnv, Action, BaseState, is_blackjack, draw_card
from enum import Enum
from random import choice
import numpy as np
import logging

class GenerateMode(Enum):
    Greedy = 1
    Episilon = 2


class EpisodesGenerator:
    def __init__(self, epsilon:float):
        self.__epsilon = epsilon

        if epsilon>0:
            self.__action_selector = self.__random_select_with_epsilon
        else:
            self.__action_selector = self.__random_action_select

    def generate_episodes(self,  env: BlackjackEnv, policy: dict[BaseState, Action]):
        """
        Normal Generate, include greedy and e-greedy
        """
        env.reset()
        return self.__generate_episodes(env, policy)

    def generate_episodes_with_start(self,  env: BlackjackEnv, policy: dict[BaseState, Action], state_action_start:tuple):
        start_cards, action = state_action_start
        cards = [start_cards[0], draw_card(), start_cards[1], start_cards[2]]
        
        env.reset(cards)
        start_state = env.get_state()
        # process action
        env.step(action)

        post_episodes, rewards = self.__generate_episodes(env, policy)
        if not post_episodes:
            # only one action episode
            post_episodes.append([(start_state, action)])
        else:
            post_episodes[0].insert(0, (start_state, action))
        return post_episodes, rewards


    # ======================= Utility ==============================
    def __generate_episodes(self, env: BlackjackEnv, policy: dict[BaseState, Action]):
        sub_episodes = []

        # hands will expand during the split
        while env.current < len(env.hands):
            current_id  = env.current # record current id cause it will update in step
            hand = env.hands[current_id]
            finished = env.finished[current_id]
            episode = []

            if is_blackjack(hand, current_id):
                sub_episodes.append([])
                env.current += 1 # move to next hand
                continue

            while not finished:
                state = env.get_state()

                possible_actions = env.get_possible_actions()

                # won't explore in greedy mode
                action = self.__action_selector(state, policy, possible_actions, self.__epsilon)

                logging.debug(f"running...{state}, {action}")
                episode.append((state, action))
                env.step(action)

                finished = env.finished[current_id]
            
            sub_episodes.append(episode)

        # 所有手牌打完后，dealer处理，返回每手 reward
        rewards = env.finish()
        # 对split的return进行特殊处理，每个split动作的收益是其之后所有手收益之和
        if (len(rewards) > 1):
            for i in range(len(rewards)-2, -1, -1):
                rewards[i] += rewards[i+1]


        logging.debug(sub_episodes)
        logging.debug(rewards)
        return sub_episodes, rewards

    def __random_action_select(self, state:BaseState, policy:dict[BaseState, Action], possible_actions:list[Action], ep:float):
        return policy.get(state, choice(possible_actions))
    
    def __random_select_with_epsilon(self,state:BaseState, policy:dict[BaseState, Action], possible_actions:list[Action], epsilon:float):
        if state not in policy or np.random.rand() < epsilon:
            action = choice(possible_actions)
        else:
            action = policy[state]
        return action