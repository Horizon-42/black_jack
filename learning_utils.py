from env import Action, BaseState
from copy import deepcopy

def add_double_in(pre_trained_policy:dict[BaseState, Action]):
    policy = deepcopy(pre_trained_policy)
    for s in pre_trained_policy:
        ns = BaseState(
            s.player_sum,
            s.dealer_card,
            s.usible_ace,
            s.splitable,
            True
        )
        policy[ns] = pre_trained_policy[s]
    return policy