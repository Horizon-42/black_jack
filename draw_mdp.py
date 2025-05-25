from graphviz import Digraph

def draw_mdp(states, actions, transitions, rewards, start_state=None, terminal_states=None):
    dot = Digraph(comment='MDP State Transition Diagram', format='png')
    dot.attr(rankdir='LR') # 从左到右布局

    # 添加状态节点
    for s in states:
        if s == start_state:
            dot.node(str(s), f'S{s}', shape='doublecircle', style='filled', fillcolor='lightblue')
        elif terminal_states and s in terminal_states:
            dot.node(str(s), f'S{s}', shape='octagon', style='filled', fillcolor='lightgreen')
        else:
            dot.node(str(s), f'S{s}', shape='circle')

    # 添加转移边
    for (s, a, next_s), prob in transitions.items():
        # 为动作创建一个中间节点，以便更好地显示奖励和概率
        action_node_name = f'S{s}_A{a}'
        dot.node(action_node_name, f'A{a}', shape='box', style='filled', fillcolor='lightgray', width='0.3', height='0.3')
        dot.edge(str(s), action_node_name, label=f'Action {a}')

        reward_val = rewards.get((s, a, next_s), 0) # 获取奖励，如果没有定义则为0
        dot.edge(action_node_name, str(next_s), label=f'p={prob:.2f}\nR={reward_val}', fontsize='10')

    return dot

# 示例MDP数据
states = [0, 1, 2, 3]
actions = ['move_left', 'move_right']
# transitions: (state, action, next_state) -> probability
transitions = {
    (0, 'move_right', 1): 0.8,
    (0, 'move_right', 0): 0.2, # 失败转移
    (1, 'move_left', 0): 0.9,
    (1, 'move_left', 1): 0.1,
    (1, 'move_right', 2): 1.0,
    (2, 'move_right', 3): 0.7,
    (2, 'move_right', 2): 0.3,
    (3, 'move_left', 2): 0.5,
    (3, 'move_left', 3): 0.5,
}
# rewards: (state, action, next_state) -> reward
rewards = {
    (0, 'move_right', 1): -1,
    (1, 'move_right', 2): -1,
    (2, 'move_right', 3): 10, # 达到目标状态奖励
    (3, 'move_left', 2): -1,
}
start_state = 0
terminal_states = [3]

# 绘制图
mdp_graph = draw_mdp(states, actions, transitions, rewards, start_state, terminal_states)
mdp_graph.render('my_mdp_diagram', view=True) # 生成 PNG 文件并打开