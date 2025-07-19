from env import Action, BaseState

def add_double_in(pre_trained_policy:dict[BaseState, Action]):
    policy = pre_trained_policy
    for s in pre_trained_policy:
        ns = s
        ns.can_double = True
        policy[ns] = pre_trained_policy[s]
    return policy