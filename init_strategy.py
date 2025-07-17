from env import BaseState, Action
from collections import defaultdict
import os
import pickle

def generate_basic_strategy():
    polocy:dict[BaseState, Action] = {}

    dealer_cards = range(2, 12)

    # Hard standing
    for player_sum in range(4, 13):
        for dealer_card in dealer_cards:
            for splitable in [True, False]:
                for can_double in [True, False]:
                    polocy[
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
                    polocy[
                        BaseState(
                            player_sum=12,
                            dealer_card=dealer_card,
                            usible_ace=False,
                            splitable=splitable,
                            can_double=can_double
                        )
                    ] = Action.Stand
    
    for player_sum in range(13, 20):
        for dealer_card in dealer_cards:
            for splitable in [True, False]:
                for can_double in [True, False]:
                    polocy[
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
                    polocy[
                        BaseState(
                            player_sum=player_sum,
                            dealer_card=dealer_card,
                            usible_ace=False,
                            splitable=splitable,
                            can_double=can_double
                        )
                    ] = Action.Hit
    


            