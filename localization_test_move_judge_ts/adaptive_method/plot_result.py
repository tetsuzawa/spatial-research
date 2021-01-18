#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ##################################################
# 適応法を用いた音の最小知覚移動角度の心理測定実験
#
# Tetsu Takizawa (tt20805@tomakomai.kosen-ac.jp)
# 2020
# ##################################################

import sys
import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import questplus as qp

usage = """usage: python plot_result.py <result>.csv <params>.json"""


def print_usage():
    print(usage, sys.stderr)


def main():
    # 引数の処理
    args = sys.argv
    if len(args) != 3:
        print_usage()
        sys.exit(1)

    result_file_name = args[1]
    qp_params_file_name = args[2]

    # 推定結果csvの読み込み
    df = pd.read_csv(result_file_name)

    # QUEST+パラメータの読み込み
    with open(qp_params_file_name) as f:
        qp_params = json.load(f)
    print(qp_params)

    stim_domain = qp_params["stim_domain"]
    param_domain = qp_params["param_domain"]

    # Initialize the QUEST+ staircase.
    q = qp.QuestPlus(**qp_params)

    intensity = stim_domain["intensity"]
    mean = param_domain["mean"]
    sd = param_domain["sd"]
    lower_asymptote = param_domain["lower_asymptote"]
    lapse_rate = param_domain["lapse_rate"]

    print("intensity:", intensity)
    print("mean:", mean)
    print("sd:", sd)
    # --------------- 心理測定法の決定 --------------- #

    # 試行回数T
    num_trial = 1
    # 総試行回数
    num_trials = len(df)
    print("num_trials", num_trials)

    # 刺激の過程を記録
    stim_history = []
    result_history = []
    entropy_history = []

    # 推定過程表示用のfigure
    fig, axs = plt.subplots(1, 3)

    while num_trial <= num_trials:
        # エントロピーを内部で計算
        _ = q.next_stim["intensity"]
        stim = int(df.at[num_trial - 1, "move_width"]) / 10
        print("stim", stim)

        # 刺激の単位合わせ
        stim = int(stim * 10)

        # 正誤判定
        result = df.at[num_trial - 1, "response"]

        stim_history.append(stim)
        result_history.append(result)
        entropy_history.append(q.entropy)

        # 刺激量の更新
        q.update(stim=dict(intensity=float(stim / 10)), outcome=dict(response=result))

        # 途中経過のプロット
        axs[0].plot(mean, q.marginal_posterior["mean"], color="blue", alpha=num_trial / num_trials)
        axs[0].set_xlabel("mean")
        axs[0].set_ylabel("Probability")
        axs[0].set_title("Posterior PDF (mean)")

        axs[1].plot(sd, q.marginal_posterior["sd"], color="green", alpha=num_trial / num_trials)
        axs[1].set_xlabel("sd")
        axs[1].set_ylabel("Probability")
        axs[1].set_title("Posterior PDF (sd)")

        pf_most_probable = np.squeeze(qp.qp.psychometric_function.norm_cdf(
            intensity=intensity,
            mean=q.param_estimate["mean"],
            sd=q.param_estimate["sd"],
            lapse_rate=q.param_estimate["lapse_rate"],
            lower_asymptote=lower_asymptote,
        ))
        axs[2].plot(pf_most_probable, color="red", alpha=num_trial / num_trials)
        axs[2].set_xlabel("intensity")
        axs[2].set_ylabel("Probability")
        axs[2].set_title("PF(x)")

        # 試行回数をカウント
        num_trial += 1

    fig.suptitle("Tracks of estimation")
    plt.show()

    fig, axs = plt.subplots(1, 3)
    axs[0].plot(mean, q.marginal_posterior["mean"], color="blue")
    axs[0].set_xlabel("mean")
    axs[0].set_ylabel("Probability")
    axs[0].set_title("Posterior PDF (mean)")

    axs[1].plot(sd, q.marginal_posterior["sd"], color="green")
    axs[1].set_xlabel("sd")
    axs[1].set_ylabel("Probability")
    axs[1].set_title("Posterior PDF (sd)")

    pf_most_probable = np.squeeze(qp.qp.psychometric_function.norm_cdf(
        intensity=intensity,
        mean=q.param_estimate["mean"],
        sd=q.param_estimate["sd"],
        lapse_rate=q.param_estimate["lapse_rate"],
        lower_asymptote=lower_asymptote,
    ))

    axs[2].plot(pf_most_probable, color="red")
    axs[2].set_xlabel("intensity")
    axs[2].set_ylabel("Probability")
    axs[2].set_title("PF(x)")

    fig.suptitle("Posterior PDF")
    plt.show()

    # ------------------------------ 試験結果の出力 ------------------------------ #
    print(f"{num_trial}回目の回答で実験が終了しました.")
    print("パラメータ推定結果:", q.param_estimate)

    fig, axs = plt.subplots(1, 2)

    # 刺激量の軌跡
    axs[0].plot(list(range(1, len(stim_history) + 1)), stim_history, "o-")
    axs[0].set_xlabel("Numbers of trials T")
    axs[0].set_ylabel("Stimulation level X")
    axs[0].set_title("Path of stimulation level")

    # エントロピーの軌跡
    axs[1].plot(list(range(1, len(entropy_history) + 1)), entropy_history, "o-")
    axs[1].set_xlabel("Numbers of trials T")
    axs[1].set_ylabel("Entropy")
    axs[1].set_title("Path of Entropy")
    plt.show()

    print("stim history", stim_history)
    print("result history", result_history)
    print("entropy history", entropy_history)
    # ------------------------------ 試験結果の出力 ------------------------------ #


if __name__ == "__main__":
    main()
