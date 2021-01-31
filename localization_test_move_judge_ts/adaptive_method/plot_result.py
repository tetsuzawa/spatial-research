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
from typing import List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import questplus as qp
import arviz as az
from scipy import interpolate

# import hdi.py from current directory
from hdi import *

signal.signal(signal.SIGINT, signal.SIG_DFL)

plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['xtick.top'] = True
plt.rcParams['ytick.right'] = True
plt.rcParams['font.size'] = 11
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['figure.dpi'] = 200

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
    fig, axs = plt.subplots(2, 2)

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
        axs[0, 0].plot(mean, q.marginal_posterior["mean"], color="blue", alpha=num_trial / num_trials)
        axs[0, 0].set_xlabel("Mean μ")
        axs[0, 0].set_ylabel("Probability")
        axs[0, 0].set_title("Posterior PDF (μ)")

        axs[0, 1].plot(sd, q.marginal_posterior["sd"], color="green", alpha=num_trial / num_trials)
        axs[0, 1].set_xlabel("Standard deviation σ")
        axs[0, 1].set_ylabel("Probability")
        axs[0, 1].set_title("Posterior PDF (sd)")

        pf_most_probable = np.squeeze(qp.qp.psychometric_function.norm_cdf(
            intensity=intensity,
            mean=q.param_estimate["mean"],
            sd=q.param_estimate["sd"],
            lapse_rate=q.param_estimate["lapse_rate"],
            lower_asymptote=lower_asymptote,
        ))
        axs[1, 0].plot(pf_most_probable, color="red", alpha=num_trial / num_trials)
        axs[1, 0].set_xlabel("Intensity")
        axs[1, 0].set_ylabel("Probability")
        axs[1, 0].set_ylim([0.5, 1.0])
        axs[1, 0].set_title("Psychometric Function")

        axs[1, 1].plot(lapse_rate, q.marginal_posterior["lapse_rate"], color="yellow", alpha=num_trial / num_trials)
        axs[1, 1].set_xlabel("Lapse rate λ")
        axs[1, 1].set_ylabel("Probability")
        axs[1, 1].set_title("Posterior PDF (λ)")

        # 試行回数をカウント
        num_trial += 1

    # ------------------------------ 試験結果の出力 ------------------------------ #
    print(f"{num_trial}回目の回答で実験が終了しました.")
    print("パラメータ推定結果:", q.param_estimate)

    fig.suptitle("Tracks of estimation")
    plt.tight_layout()
    fig.savefig(f"track_{result_file_name.split('.')[0]}.png")
    plt.show()

    fig, axs = plt.subplots(2, 2)

    axs[0, 0].plot(mean, q.marginal_posterior["mean"], color="blue")
    axs[0, 0].vlines(x=q.param_estimate["mean"], ymin=0, ymax=np.max(q.marginal_posterior["mean"]), linestyles="--",
                     color="red")
    axs[0, 0].set_xlabel("Mean μ")
    axs[0, 0].set_ylabel("Probability")
    axs[0, 0].set_title("Posterior PDF (μ)")

    axs[0, 1].plot(sd, q.marginal_posterior["sd"], color="green")
    axs[0, 1].vlines(x=q.param_estimate["sd"], ymin=0, ymax=np.max(q.marginal_posterior["sd"]), linestyles="--",
                     color="red")
    axs[0, 1].set_xlabel("Standard deviation σ")
    axs[0, 1].set_ylabel("Probability")
    axs[0, 1].set_title("Posterior PDF (σ)")

    pf_most_probable = np.squeeze(qp.qp.psychometric_function.norm_cdf(
        intensity=intensity,
        mean=q.param_estimate["mean"],
        sd=q.param_estimate["sd"],
        lapse_rate=q.param_estimate["lapse_rate"],
        lower_asymptote=lower_asymptote,
    ))

    axs[1, 0].plot(pf_most_probable, color="red", label="Estimated PF")
    axs[1, 0].set_xlabel("Intensity")
    axs[1, 0].set_ylabel("Probability")
    axs[1, 0].set_ylim([0.5, 1.0])
    axs[1, 0].set_title("Psychometric Function")

    axs[1, 1].plot(lapse_rate, q.marginal_posterior["lapse_rate"], color="yellow")
    axs[1, 1].vlines(x=q.param_estimate["lapse_rate"], ymin=0, ymax=np.max(q.marginal_posterior["lapse_rate"]),
                     linestyles="--",
                     color="red")
    axs[1, 1].set_xlabel("Lapse rate λ")
    axs[1, 1].set_ylabel("Probability")
    axs[1, 1].set_title("Posterior PDF (λ)")

    # HDI (mean)
    mean_marginal_posterior = q.marginal_posterior["mean"]
    mean_marginal_posterior = mean_marginal_posterior / sum(mean_marginal_posterior)
    hdi = find_hdi(mean, q.marginal_posterior["mean"].tolist())
    axs[0, 0].vlines(x=hdi.lower_bound, ymin=0, ymax=np.max(mean_marginal_posterior), linestyles="--", color="dimgrey")
    axs[0, 0].vlines(x=hdi.upper_bound, ymin=0, ymax=np.max(mean_marginal_posterior), linestyles="--", color="dimgrey")
    mean_hdi = hdi.tolist()

    print("mean HDI", hdi.lower_bound, hdi.upper_bound)

    # HDI (sd)
    sd_marginal_posterior = q.marginal_posterior["sd"]
    sd_marginal_posterior = sd_marginal_posterior / sum(sd_marginal_posterior)
    hdi = find_hdi(sd, q.marginal_posterior["sd"].tolist())
    axs[0, 1].vlines(x=hdi.upper_bound, ymin=0, ymax=np.max(sd_marginal_posterior), linestyles="--", color="dimgrey")
    axs[0, 1].vlines(x=hdi.lower_bound, ymin=0, ymax=np.max(sd_marginal_posterior), linestyles="--", color="dimgrey")
    sd_hdi = hdi.tolist()

    print("sd HDI", hdi.lower_bound, hdi.upper_bound)

    # HDI (lapse rate)
    lapse_rate_marginal_posterior = q.marginal_posterior["lapse_rate"]
    lapse_rate_marginal_posterior = lapse_rate_marginal_posterior / sum(lapse_rate_marginal_posterior)
    hdi = find_hdi(lapse_rate, q.marginal_posterior["lapse_rate"].tolist())
    axs[1, 1].vlines(x=hdi.upper_bound, ymin=0, ymax=np.max(lapse_rate_marginal_posterior), linestyles="--",
                     color="dimgrey")
    axs[1, 1].vlines(x=hdi.lower_bound, ymin=0, ymax=np.max(lapse_rate_marginal_posterior), linestyles="--",
                     color="dimgrey")
    lapse_rate_hdi = hdi.tolist()

    print("lapse rate HDI", hdi.lower_bound, hdi.upper_bound)

    # plot credible interval of PF
    pfs = []
    for m in mean_hdi:
        for s in sd_hdi:
            for l in lapse_rate_hdi:
                pf = np.squeeze(qp.qp.psychometric_function.norm_cdf(
                    intensity=intensity,
                    mean=m,
                    sd=s,
                    lapse_rate=l,
                    lower_asymptote=lower_asymptote,
                ))
                pfs.append(pf.values.tolist())

    pf_lower = np.amin(pfs, axis=0)
    pf_upper = np.amax(pfs, axis=0)
    axs[1, 0].plot(intensity, pf_lower, linestyle="--", color="dimgrey")
    axs[1, 0].plot(intensity, pf_upper, linestyle="--", color="dimgrey", label="95% Credible interval")
    axs[1, 0].legend()

    plt.tight_layout()
    fig.savefig(f"estimation_{result_file_name.split('.')[0]}.png")
    plt.show()

    fig, axs = plt.subplots(1, 2)

    # 刺激量の軌跡
    axs[0].plot(list(range(1, len(stim_history) + 1)), stim_history, "o-")
    axs[0].set_xlabel("Numbers of trials")
    axs[0].set_ylabel("Intensity")
    axs[0].set_title("Track of intensity")

    # エントロピーの軌跡
    axs[1].plot(list(range(1, len(entropy_history) + 1)), entropy_history, "o-")
    axs[1].set_xlabel("Numbers of trials")
    axs[1].set_ylabel("Entropy")
    axs[1].set_title("Track of entropy")
    plt.tight_layout()
    fig.savefig(f"entropy_{result_file_name.split('.')[0]}.png")
    plt.show()

    print("stim history", stim_history)
    print("result history", result_history)
    print("entropy history", entropy_history)
    # ------------------------------ 試験結果の出力 ------------------------------ #


def find_hdi(xs: List, probability: List, samples=10000) -> HighestPosteriorDensityInterval:
    if len(xs) != len(probability):
        raise ValueError(f"length of xs and probability must same. xs:{len(xs)}, probability:{len(probability)}")

    latent_xs = np.linspace(min(xs), max(xs), 1000)
    fitted_probability_func = interpolate.interp1d(xs, probability)
    fitted_probability = fitted_probability_func(latent_xs)
    fitted_probability = fitted_probability / fitted_probability.sum()
    # data = np.random.choice(a=xs, size=samples, p=probability)
    data = np.random.choice(a=latent_xs, size=samples, p=fitted_probability)
    hdi = az.hdi(data, hdi_prob=0.95)
    return HighestPosteriorDensityInterval(*hdi)


if __name__ == "__main__":
    main()
