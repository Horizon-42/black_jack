from env import BlackjackEnv, Action, BaseState, is_blackjack, draw_card, get_possible_actions
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
        episodes, rewards = self.__generate_episodes(env, policy)
        return self.__deal_with_split(env, episodes, rewards)

    def generate_episodes_with_start(self,  env: BlackjackEnv, policy: dict[BaseState, Action], state_action_start:tuple):
        start_cards, action = state_action_start
        cards = [start_cards[0], env.draw_card(), start_cards[1],
                 start_cards[2]]
        
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
        return self.__deal_with_split(env, post_episodes, rewards)


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

                possible_actions = get_possible_actions(state)

                # won't explore in greedy mode
                action = self.__action_selector(state, policy, possible_actions, self.__epsilon)

                episode.append((state, action))
                env.step(action)

                finished = env.finished[current_id]
            
            sub_episodes.append(episode)

        # 所有手牌打完后，dealer处理，返回每手 reward
        rewards = env.finish()
        return sub_episodes, rewards

    def __random_action_select(self, state:BaseState, policy:dict[BaseState, Action], possible_actions:list[Action], ep:float):
        return policy.get(state, choice(possible_actions))
    
    def __random_select_with_epsilon(self,state:BaseState, policy:dict[BaseState, Action], possible_actions:list[Action], epsilon:float):
        if state not in policy or np.random.rand() < epsilon:
            action = choice(possible_actions)
        else:
            action = policy[state]
        return action

    def __deal_with_split(self, env: BlackjackEnv, episodes: list, rewards: list[float]):
        if not env.is_split_enable():
            return episodes, rewards

        # assume only one split allowed
        if len(episodes) == 2:
            episodes[1].insert(0, episodes[0][0])

        logging.debug(episodes)
        logging.debug(rewards)
        return episodes, rewards
