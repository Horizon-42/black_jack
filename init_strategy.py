import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from env import BaseState, Action
from collections import defaultdict
import os
import pickle
from utils import plot_split_policy

def generate_basic_strategy():
    policy: dict[BaseState, Action] = {}

    dealer_cards = range(2, 12)

    # Hard standing
    for player_sum in range(4, 13):
        for dealer_card in dealer_cards:
            for splitable in [True, False]:
                for can_double in [True, False]:
                    policy[
                        BaseState(
                            player_sum=player_sum,
                            dealer_card=dealer_card,
                            usible_ace=False,
                            splitable=splitable,
                            can_double=can_double
                        )
                    ] = Action.Hit
    for dealer_card in [4,5,6]:
        for splitable in [True, False]:
                for can_double in [True, False]:
                    policy[
                        BaseState(
                            player_sum=12,
                            dealer_card=dealer_card,
                            usible_ace=False,
                            splitable=splitable,
                            can_double=can_double
                        )
                    ] = Action.Stand
    
    for player_sum in range(13, 21):
        for dealer_card in dealer_cards:
            for splitable in [True, False]:
                for can_double in [True, False]:
                    policy[
                        BaseState(
                            player_sum=player_sum,
                            dealer_card=dealer_card,
                            usible_ace=False,
                            splitable=splitable,
                            can_double=can_double
                        )
                    ] = Action.Stand
    
    for player_sum in range(13, 17):
        for dealer_card in range(7, 12):
            for splitable in [True, False]:
                for can_double in [True, False]:
                    policy[
                        BaseState(
                            player_sum=player_sum,
                            dealer_card=dealer_card,
                            usible_ace=False,
                            splitable=splitable,
                            can_double=can_double
                        )
                    ] = Action.Hit
    
    # Soft Standing
    for player_sum in range(12, 21):
        for dealer_card in range(2, 12):
            if player_sum > 18:
                for can_double in [True, False]:
                    policy[
                        BaseState(
                            player_sum=player_sum,
                            dealer_card=dealer_card,
                            usible_ace=True,
                            splitable=False,  # AA always split
                            can_double=can_double
                        )
                    ] = Action.Stand
            elif player_sum == 18:
                if dealer_card in [9, 10]:
                    for can_double in [True, False]:
                        policy[
                            BaseState(
                                player_sum=player_sum,
                                dealer_card=dealer_card,
                                usible_ace=True,
                                splitable=False,  # AA always split
                                can_double=can_double
                            )
                        ] = Action.Hit
                else:
                    for can_double in [True, False]:
                        policy[
                            BaseState(
                                player_sum=player_sum,
                                dealer_card=dealer_card,
                                usible_ace=True,
                                splitable=False,  # AA always split
                                can_double=can_double
                            )
                        ] = Action.Stand
            else:
                for can_double in [True, False]:
                    policy[
                        BaseState(
                            player_sum=player_sum,
                            dealer_card=dealer_card,
                            usible_ace=True,
                            splitable=False,  # AA always split
                            can_double=can_double
                        )
                    ] = Action.Hit

    # Hard Doubling
    # This policy will overwrite the standing rule
    for player_sum in range(9, 12):
        for dealer_card in range(2, 7):
            policy[
                BaseState(
                    player_sum=player_sum,
                    dealer_card=dealer_card,
                    usible_ace=False,
                    splitable=False,  # AA always split
                    can_double=True
                )
            ] = Action.Double
    for dealer_card in range(7, 12):
        policy[
            BaseState(
                player_sum=11,
                dealer_card=dealer_card,
                usible_ace=False,
                splitable=False,  # AA always split
                can_double=True
            )
        ] = Action.Double

    for dealer_card in range(7, 10):
        policy[
            BaseState(
                player_sum=10,
                dealer_card=dealer_card,
                usible_ace=False,
                splitable=False,  # AA always split
                can_double=True
            )
        ] = Action.Double

    # Soft Doubling
    for player_sum in range(12, 19):
        for dealer_card in range(5, 7):
            policy[
                BaseState(
                    player_sum=player_sum,
                    dealer_card=dealer_card,
                    usible_ace=True,
                    splitable=False,  # AA always split
                    can_double=True
                )
            ] = Action.Double
    for player_sum in range(13, 19):
        policy[
            BaseState(
                player_sum=player_sum,
                dealer_card=4,
                usible_ace=True,
                splitable=False,  # AA always split
                can_double=True
            )
        ] = Action.Double

    for player_sum in range(17, 19):
        policy[
            BaseState(
                player_sum=player_sum,
                dealer_card=3,
                usible_ace=True,
                splitable=False,  # AA always split
                can_double=True
            )
        ] = Action.Double
    policy[
        BaseState(
            player_sum=17,
            dealer_card=2,
            usible_ace=True,
            splitable=False,  # AA always split
            can_double=True
        )
    ] = Action.Double

    # Pair Spliting
    for dealer_card in dealer_cards:
        # AA
        for can_double in [True, False]:
            policy[
                BaseState(
                    player_sum=12,
                    dealer_card=dealer_card,
                    usible_ace=True,
                    splitable=True,
                    can_double=can_double
                )
            ] = Action.Split
        # 10 10
        for can_double in [True, False]:
            policy[
                BaseState(
                    player_sum=20,
                    dealer_card=dealer_card,
                    usible_ace=False,
                    splitable=True,
                    can_double=can_double
                )
            ] = policy[
                BaseState(
                    player_sum=20,
                    dealer_card=dealer_card,
                    usible_ace=False,
                    splitable=False,
                    can_double=can_double
                )
            ]

    for dealer_card in range(2, 8):
        for player_sum in [4, 6, 12, 14, 16, 18]:
            for can_double in [True, False]:
                policy[
                    BaseState(
                        player_sum=player_sum,
                        dealer_card=dealer_card,
                        usible_ace=False,
                        splitable=True,
                        can_double=can_double
                    )
                ] = Action.Split
    # special deal with 9 9
    for can_double in [True, False]:
        policy[
            BaseState(
                player_sum=18,
                dealer_card=7,
                usible_ace=False,
                splitable=True,
                can_double=can_double
            )
        ] = policy[
            BaseState(
                player_sum=18,
                dealer_card=7,
                usible_ace=False,
                splitable=False,
                can_double=can_double
            )
        ]

    for player_sum in [8, 10]:
        for dealer_card in dealer_cards:
            for can_double in [True, False]:
                policy[
                    BaseState(
                        player_sum=player_sum,
                        dealer_card=dealer_card,
                        usible_ace=False,
                        splitable=True,
                        can_double=can_double
                    )
                ] = policy[
                    BaseState(
                        player_sum=player_sum,
                        dealer_card=dealer_card,
                        usible_ace=False,
                        splitable=False,
                        can_double=can_double
                    )
                ]
    # special trate for 4 4
    for can_double in [True, False]:
        policy[
            BaseState(
                player_sum=8,
                dealer_card=5,
                usible_ace=False,
                splitable=True,
                can_double=can_double
            )
        ] = Action.Split

    for dealer_card in range(8, 12):
        for player_sum in range(4, 20, 2):
            for can_double in [True, False]:
                if player_sum == 16:
                    policy[
                        BaseState(
                            player_sum=player_sum,
                            dealer_card=dealer_card,
                            usible_ace=False,
                            splitable=True,
                            can_double=can_double
                        )
                    ] = Action.Split
                else:
                    policy[
                        BaseState(
                            player_sum=player_sum,
                            dealer_card=dealer_card,
                            usible_ace=False,
                            splitable=True,
                            can_double=can_double
                        )
                    ] = policy[
                        BaseState(
                            player_sum=player_sum,
                            dealer_card=dealer_card,
                            usible_ace=False,
                            splitable=False,
                            can_double=can_double
                        )
                    ]
    for can_double in [True, False]:
        policy[
            BaseState(
                player_sum=14,
                dealer_card=8,
                usible_ace=False,
                splitable=True,
                can_double=can_double
            )
        ] = Action.Split

        for dcard in [8, 9]:
            policy[
                BaseState(
                    player_sum=18,
                    dealer_card=dcard,
                    usible_ace=False,
                    splitable=True,
                    can_double=can_double
                )
            ] = Action.Split

    return policy


if __name__ == "__main__":
    from init_strategy import generate_basic_strategy
# plotting

    policy = generate_basic_strategy()

    plot_split_policy(policy)
