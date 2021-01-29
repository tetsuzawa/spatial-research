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
import signal

import pandas as pd
import matplotlib.pyplot as plt
import questplus as qp

# import hdi.py from current directory
from hdi import *

signal.signal(signal.SIGINT, signal.SIG_DFL)

usage = """usage: python plot_result.py <result>.csv <params>.json"""


def print_usage():
    print(usage, file=sys.stderr)


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

    # ------------------------------ 試験結果の出力 ------------------------------ #
    print(f"{num_trial}回目の回答で実験が終了しました.")
    print("パラメータ推定結果:", q.param_estimate)

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

    # 当裾
    # mean_marginal_posterior = q.marginal_posterior["mean"]
    # mean_l, mean_r = confidence_interval(mean, mean_marginal_posterior)
    # print(mean_l, mean_r)
    # axs[0].vlines(x=mean_l, ymin=0, ymax=np.max(mean_marginal_posterior), linestyles="--", )
    # axs[0].vlines(x=mean_r, ymin=0, ymax=np.max(mean_marginal_posterior), linestyles="--", )
    # sd_marginal_posterior = q.marginal_posterior["sd"]
    # sd_l, sd_r = confidence_interval(sd, sd_marginal_posterior)
    # print(sd_l, sd_r)
    # axs[1].vlines(x=sd_l, ymin=0, ymax=np.max(sd_marginal_posterior), linestyles="--", )
    # axs[1].vlines(x=sd_r, ymin=0, ymax=np.max(sd_marginal_posterior), linestyles="--", )

    # HDI (mean)
    mean_marginal_posterior = q.marginal_posterior["mean"]
    mean_marginal_posterior = mean_marginal_posterior / sum(mean_marginal_posterior)
    real_distribution = RealDistribution(mean, mean_marginal_posterior)
    hdi = HighestPosteriorDensityInterval.calculate(real_distribution, alpha=0.05)
    idx_lower = np.abs(np.asarray(mean) - hdi.lower_bound).argmin()
    idx_upper = np.abs(np.asarray(mean) - hdi.upper_bound).argmin()
    axs[0].vlines(x=hdi.lower_bound, ymin=0, ymax=np.max(mean_marginal_posterior), linestyles="--", color="black")
    axs[0].vlines(x=hdi.upper_bound, ymin=0, ymax=np.max(mean_marginal_posterior), linestyles="--", color="black")

    print("mean HDI", hdi.lower_bound, hdi.upper_bound)
    print(
        f"surface volume ratio of HDI (mean): {sum(mean_marginal_posterior[idx_lower:idx_upper]) / sum(mean_marginal_posterior)}")

    # HDI (sd)
    sd_marginal_posterior = q.marginal_posterior["sd"]
    sd_marginal_posterior = sd_marginal_posterior / sum(sd_marginal_posterior)
    real_distribution = RealDistribution(sd, sd_marginal_posterior)
    hdi = HighestPosteriorDensityInterval.calculate(real_distribution, alpha=0.05)
    idx_lower = np.abs(np.asarray(sd) - hdi.lower_bound).argmin()
    idx_upper = np.abs(np.asarray(sd) - hdi.upper_bound).argmin()
    axs[1].vlines(x=hdi.upper_bound, ymin=0, ymax=np.max(sd_marginal_posterior), linestyles="--", color="black")
    axs[1].vlines(x=hdi.lower_bound, ymin=0, ymax=np.max(sd_marginal_posterior), linestyles="--", color="black")

    print("sd HDI", hdi.lower_bound, hdi.upper_bound)
    print(
        f"surface volume ratio of HDI (sd): {sum(sd_marginal_posterior[idx_lower:idx_upper]) / sum(sd_marginal_posterior)}")
    print()

    plt.show()

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


# def confidence_interval(xs: List[int], pdf: List[float]) -> (int, int):
#     if len(xs) != len(pdf):
#         raise ValueError("length of xs and pdf must be same")
#     # cdf = []
#     # for i, v in enumerate(pdf):
#     #     if i == 0:
#     #         cdf.append(v)
#     #         continue
#     #     cdf.append(cdf[i - 1] + v)
#
#     pdf_integral = sum(pdf)
#     print(pdf_integral)
#     pdf_sum = 0
#     l, r = -1, -1
#     for i, v in enumerate(pdf):
#         if pdf_sum + v > pdf_integral * 0.025 and l < 0:
#             pdf_interpolated = np.linspace(pdf_sum, pdf_sum + v, 100)
#             for j, vv in enumerate(pdf_interpolated):
#                 if vv > pdf_integral * 0.025:
#                     l = xs[i - 1] + (xs[i] - xs[i - 1]) * j / 100
#                     break
#         if pdf_sum + v > pdf_integral * 0.975 and r < 0:
#             pdf_interpolated = np.linspace(pdf_sum, pdf_sum + v, 100)
#             for j, vv in enumerate(pdf_interpolated):
#                 if vv > pdf_integral * 0.975:
#                     r = xs[i - 1] + (xs[i] - xs[i - 1]) * j / 100
#         pdf_sum += v
#     if l < 0 or r < 0:
#         raise ValueError("failed")
#     return l, r


if __name__ == "__main__":
    main()
