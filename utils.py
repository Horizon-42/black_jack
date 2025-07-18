import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from env import BaseState, Action
from enum import Enum


class ChartName(Enum):
    HardTotals = "Hard Totals"
    SoftTotals = "Soft Totals"
    Split = "Split"


def get_split_policy_q_matrices(Q: dict, policy: dict, can_double: bool = True):
    splitable_player_sums = range(22, 2, -2)
    splitable_player_sum_labels = [
        f"{s//2}, {s//2}" for s in splitable_player_sums]
    splitable_player_sum_labels[0] = 'A, A'  # for 22, which is a pair of aces

    dealer_cards = range(2, 12)

    split_policy = np.zeros(
        shape=(len(splitable_player_sums), len(dealer_cards)))
    split_policy_labels = np.array(
        ['']*len(splitable_player_sums)*len(dealer_cards)).reshape(-1, len(dealer_cards))

    split_policy_values = np.zeros(
        (len(splitable_player_sums), len(dealer_cards)))
    for i, player_sum in enumerate(splitable_player_sums):
        has_ace = False
        if player_sum == 22:
            # player has a usable ace
            has_ace = True
            player_sum = 12
        for j, dealer_card_value in enumerate(dealer_cards):
            state = BaseState(
                player_sum=player_sum,
                dealer_card=dealer_card_value,
                usible_ace=has_ace,
                splitable=True,
                can_double=can_double
            )
            action = policy.get(state)
            if action is None:
                continue
            split_policy[i, j] = action == Action.Split
            split_policy_labels[i, j] = 'Y' if split_policy[i, j] else 'N'
            if state in Q and action in Q[state]:
                split_policy_values[i, j] = Q[state][action]

    return split_policy, split_policy_labels, split_policy_values, splitable_player_sum_labels, dealer_cards


def plot_split_policy(policy: dict):
    split_policy, split_policy_labels, _, splitable_player_sum_labels, dealer_cards = get_split_policy_q_matrices({
    }, policy)

    plt.figure(figsize=(10, 6))
    ax = sns.heatmap(split_policy, annot=split_policy_labels, fmt='', cmap='coolwarm', cbar=True,
                     xticklabels=dealer_cards, yticklabels=splitable_player_sum_labels)

    plt.title('Policy for Split Action')
    plt.xlabel('Dealer Card')
    plt.ylabel('Player Sum (Splitable)')
    plt.xticks(ticks=np.arange(len(dealer_cards)), labels=dealer_cards)
    plt.yticks(ticks=np.arange(len(splitable_player_sum_labels)),
               labels=splitable_player_sum_labels)
    plt.tight_layout()

    plt.show()


def get_hard_total_matrices(Q: dict, policy: dict, cand_double=True):
    hard_player_sums = range(20, 4, -1)  # remind AA count as 12 here
    dealer_cards = range(2, 12)

    hard_policy = np.zeros((len(hard_player_sums), len(dealer_cards)))
    hard_policy_labels = np.array(
        ['']*len(hard_player_sums)*len(dealer_cards)).reshape(-1, len(dealer_cards))
    hard_policy_values = np.zeros((len(hard_player_sums), len(dealer_cards)))
    for i, player_sum in enumerate(hard_player_sums):
        for j, dealer_card_value in enumerate(dealer_cards):
            state = BaseState(
                player_sum=player_sum,
                dealer_card=dealer_card_value,
                usible_ace=False,
                splitable=False,  # split rule has higher order
                can_double=cand_double,
            )
            action = policy.get(state)
            if action is None:
                continue
            hard_policy[i, j] = action.value
            # use first letter of action name
            hard_policy_labels[i, j] = action.name[0]
            if state in Q and action in Q[state]:
                hard_policy_values[i, j] = Q[state][action]

    return hard_policy, hard_policy_labels, hard_policy_values, hard_player_sums, dealer_cards


def plot_hard_total_policy(policy: dict):

    hard_policy, hard_policy_labels, _, hard_player_sums, dealer_cards = get_hard_total_matrices({
    }, policy)

    hard_player_sums = range(20, 4, -1)  # remind AA count as 12 here
    dealer_cards = range(2, 12)

    plt.figure(figsize=(10, 6))
    ax = sns.heatmap(hard_policy, annot=hard_policy_labels, fmt='', cmap='coolwarm', cbar=True,
                     xticklabels=dealer_cards, yticklabels=hard_player_sums)
    plt.title('Policy for Hard Totals')
    plt.xlabel('Dealer Card')
    plt.ylabel('Player Sum (Hard)')
    plt.xticks(ticks=np.arange(len(dealer_cards)), labels=dealer_cards)
    plt.yticks(ticks=np.arange(len(hard_player_sums)), labels=hard_player_sums)
    plt.tight_layout()

    plt.show()


def get_soft_total_matrices(Q: dict, policy: dict, can_double: bool = True):
    # split situation
    soft_plyer_sums = range(20, 11, -1)  # remind AA count as 12 here
    dealer_cards = range(2, 12)
    soft_player_sum_labels = [f"A, {s-11}" for s in soft_plyer_sums]

    soft_policy = np.zeros((len(soft_plyer_sums), len(dealer_cards)))
    soft_policy_labels = np.array(
        ['']*len(soft_plyer_sums)*len(dealer_cards)).reshape(len(soft_plyer_sums), len(dealer_cards))

    soft_policy_values = np.zeros((len(soft_plyer_sums), len(dealer_cards)))
    for i, player_sum in enumerate(soft_plyer_sums):
        for j, dealer_card_value in enumerate(dealer_cards):
            state = BaseState(
                player_sum=player_sum,
                dealer_card=dealer_card_value,
                usible_ace=True,
                splitable=False,
                can_double=can_double
            )
            action = policy.get(state)
            if action is None:
                continue
            soft_policy[i, j] = action.value
            # use first letter of action name
            soft_policy_labels[i, j] = action.name[0]
            if state in Q and action in Q[state]:
                soft_policy_values[i, j] = Q[state][action]

    return soft_policy, soft_policy_labels, soft_policy_values, soft_player_sum_labels, dealer_cards


def plot_soft_total_policy(policy: dict):
    soft_policy, soft_policy_labels, _, soft_player_sum_labels, dealer_cards = get_soft_total_matrices({
    }, policy)

    plt.figure(figsize=(10, 6))
    ax = sns.heatmap(soft_policy, annot=soft_policy_labels, fmt='', cmap='coolwarm', cbar=True,
                     xticklabels=dealer_cards, yticklabels=soft_player_sum_labels)
    plt.title('Policy for Soft Totals')
    plt.xlabel('Dealer Card')
    plt.ylabel('Player Sum (Soft)')
    plt.xticks(ticks=np.arange(len(dealer_cards)), labels=dealer_cards)
    plt.yticks(ticks=np.arange(len(soft_player_sum_labels)),
               labels=soft_player_sum_labels)
    plt.tight_layout()
    plt.show()


def plot_policy_and_Q(Q: dict, policy: dict, chart_name: ChartName, can_double: bool):

    if chart_name == ChartName.Split:
        policy_mat, policy_labels, q, y_tics, x_tics = get_split_policy_q_matrices(
            Q, policy, can_double)
    elif chart_name == ChartName.HardTotals:
        policy_mat, policy_labels, q, y_tics, x_tics = get_hard_total_matrices(
            Q, policy, can_double)
    elif chart_name == ChartName.SoftTotals:
        policy_mat, policy_labels, q, y_tics, x_tics = get_soft_total_matrices(
            Q, policy, can_double)

    plt.figure(figsize=(10, 6))
    ax = sns.heatmap(policy_mat, annot=policy_labels, fmt='', cmap='coolwarm', cbar=True,
                     xticklabels=x_tics, yticklabels=y_tics)
    plt.title(f'Policy for {chart_name.value}')
    plt.xlabel('Dealer Card')
    plt.ylabel('Player Sum')
    plt.xticks(ticks=np.arange(len(x_tics)), labels=x_tics)
    plt.yticks(ticks=np.arange(len(y_tics)), labels=y_tics)
    plt.tight_layout()

    plt.figure(figsize=(10, 6))
    sns.heatmap(q, annot=True, fmt=".2f", cmap='coolwarm', cbar=True,
                xticklabels=x_tics, yticklabels=y_tics)
    plt.title(f'Q-values for {chart_name.value} via Policy')
    plt.xlabel('Dealer Card')
    plt.ylabel('Player Sum')
    plt.xticks(ticks=np.arange(len(x_tics)), labels=x_tics)
    plt.yticks(ticks=np.arange(len(y_tics)), labels=y_tics)
    plt.tight_layout()

    plt.show()
