import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_policy_sns(policy):
    player_sum = np.arange(4, 22)  # 玩家点数，建议包括低点数
    dealer_show = np.arange(1, 11) # 庄家明牌 1~10
    actions = {0: 'Stand', 1: 'Hit', 2: 'Double', 3: 'Split'}

    # 先创建空DataFrame存动作编码，行是player_sum，列是dealer_show
    usable_df = pd.DataFrame(index=player_sum, columns=dealer_show, dtype=int)
    unusable_df = pd.DataFrame(index=player_sum, columns=dealer_show, dtype=int)

    # 填充DataFrame
    for ps in player_sum:
        for ds in dealer_show:
            for ua in [True, False]:
                action = policy.get((ps, ds, ua), -1)  # -1 表示无效动作
                if ua:
                    usable_df.at[ps, ds] = action
                else:
                    unusable_df.at[ps, ds] = action

    # 创建一个颜色映射，基于动作
    # 用一个简单的色盘，顺序对应动作编码0-3
    palette = sns.color_palette("Set2", n_colors=4)
    cmap = sns.color_palette(palette, as_cmap=True)

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    sns.heatmap(usable_df, ax=axes[0], cmap=palette, cbar=False,
                linewidths=0.5, linecolor='gray', square=True,
                xticklabels=True, yticklabels=True)

    sns.heatmap(unusable_df, ax=axes[1], cmap=palette, cbar=False,
                linewidths=0.5, linecolor='gray', square=True,
                xticklabels=True, yticklabels=True)

    axes[0].set_title('Usable Ace')
    axes[1].set_title('No Usable Ace')

    for ax in axes:
        ax.set_xlabel('Dealer Showing')
        ax.set_ylabel('Player Sum')
        ax.set_xticklabels(dealer_show)
        ax.set_yticklabels(player_sum)

    # 为了更好显示动作，标注动作名称
    for ax, df in zip(axes, [usable_df, unusable_df]):
        for y in range(df.shape[0]):
            for x in range(df.shape[1]):
                val = df.iat[y, x]
                if val in actions:
                    ax.text(x + 0.5, y + 0.5, actions[val],
                            ha='center', va='center', fontsize=8, color='black')

    plt.tight_layout()
    plt.show()
