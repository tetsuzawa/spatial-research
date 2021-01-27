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
from typing import List, Callable

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import questplus as qp
import scipy.optimize

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

    # HPD
    mean_marginal_posterior = q.marginal_posterior["mean"]
    mean_marginal_posterior = mean_marginal_posterior / sum(mean_marginal_posterior)
    real_distribution = RealDistribution(mean, mean_marginal_posterior)
    hpd = HighestPosteriorDensityInterval.calculate(real_distribution, alpha=0.05)
    mean_l, mean_r = hpd.lower_bound, hpd.upper_bound
    print("mean HPD", mean_l, mean_r)
    idx_l = np.abs(np.asarray(mean) - mean_l).argmin()
    idx_r = np.abs(np.asarray(mean) - mean_r).argmin()
    print(
        f"sum cdf: {sum(mean_marginal_posterior)}, lower:{sum(mean_marginal_posterior[:idx_l])}, upper:{sum(mean_marginal_posterior[:idx_r])}, confidence surface {sum(mean_marginal_posterior[idx_l:idx_r]) / sum(mean_marginal_posterior)}")
    axs[0].vlines(x=mean_l, ymin=0, ymax=np.max(mean_marginal_posterior), linestyles="--", color="black")
    axs[0].vlines(x=mean_r, ymin=0, ymax=np.max(mean_marginal_posterior), linestyles="--", color="black")

    sd_marginal_posterior = q.marginal_posterior["sd"]
    sd_marginal_posterior = sd_marginal_posterior / sum(sd_marginal_posterior)
    real_distribution = RealDistribution(sd, sd_marginal_posterior)
    hpd = HighestPosteriorDensityInterval.calculate(real_distribution, alpha=0.05)
    sd_l, sd_r = hpd.lower_bound, hpd.upper_bound
    print("sd HPD", sd_l, sd_r)
    idx_l = np.abs(np.asarray(sd) - sd_l).argmin()
    idx_r = np.abs(np.asarray(sd) - sd_r).argmin()
    print(
        f"sum cdf: {sum(sd_marginal_posterior)}, lower:{sum(sd_marginal_posterior[:idx_l])}, upper:{sum(sd_marginal_posterior[:idx_r])}, confidence surface {sum(sd_marginal_posterior[idx_l:idx_r]) / sum(sd_marginal_posterior)}")
    axs[1].vlines(x=sd_l, ymin=0, ymax=np.max(sd_marginal_posterior), linestyles="--", color="black")
    axs[1].vlines(x=sd_r, ymin=0, ymax=np.max(sd_marginal_posterior), linestyles="--", color="black")

    print()
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


class HighestPosteriorDensityInterval:
    def __init__(self, lower_bound: float, upper_bound: float):
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound

    @property
    def lower_bound(self):
        return self._lower_bound

    @property
    def upper_bound(self):
        return self._upper_bound

    @staticmethod
    def calculate(distribution: "RealDistribution", alpha=0.05) -> "HighestPosteriorDensityInterval":
        solver = Solver(distribution, alpha)
        lower_bound = solver.solve()
        upper_bound = solver.offset(lower_bound)
        return HighestPosteriorDensityInterval(lower_bound, upper_bound)

    def __str__(self):
        return str([self.lower_bound, self.upper_bound])


class Solver:
    def __init__(self, distribution: "RealDistribution", alpha: float):
        self.distribution = distribution
        self.alpha = alpha

    def solve(self) -> float:
        fn = self.pdf()
        result = scipy.optimize.minimize_scalar(fn,
                                                bounds=(self.distribution.xs[0],
                                                        self.distribution.xs[-1]),
                                                method='bounded')
        return result.x

    def offset(self, x: float) -> float:
        q = self.distribution.cumulative_probability(x)
        return self.distribution.inverse_cumulative_probability(min([q + 1 - self.alpha, 1]))

    def pdf(self) -> Callable[[float], float]:
        def objective_func(x: float) -> float:
            y = self.offset(x)
            d1 = self.distribution.density(y) - self.distribution.density(x)
            d2 = (self.distribution.cumulative_probability(y) - self.distribution.cumulative_probability(x)) - (
                    1 - self.alpha)
            return d1 * d1 + d2 * d2

        return objective_func


class RealDistribution:
    def __init__(self, xs: List[float], distribution: List[float]):
        """length of xs and distribution must be same"""
        if len(xs) != len(distribution):
            raise ValueError("length of xs and distribution must be same")

        self._xs = xs
        self._distribution = distribution

    @property
    def xs(self):
        return self._xs

    @property
    def distribution(self):
        return self._distribution

    def density(self, x: float) -> float:
        if x < self.xs[0] or self.xs[-1] < x:
            raise ValueError(f"x must be in [{self.xs[0]}, {self.xs[-1]}]")
        adjust_val = abs(self.xs[1] - self.xs[0]) / 2
        diff = np.asarray(self.xs) - (x + adjust_val)
        idx = np.abs(diff).argmin()
        return self.distribution[idx]

    def cumulative_probability(self, x: float) -> float:
        if x < self.xs[0] or self.xs[-1] < x:
            raise ValueError(f"x must be in [{self.xs[0]}, {self.xs[-1]}]")
        # idx = np.abs(np.asarray(self.xs) - x).argmin()
        adjust_val = abs(self.xs[1] - self.xs[0]) / 2
        diff = np.asarray(self.xs) - (x + adjust_val)
        idx = np.abs(diff).argmin()
        return sum(self.distribution[:idx])

    def inverse_cumulative_probability(self, p: float) -> float:
        if p < 0 or 1 < p:
            raise ValueError(f"p must be in [0, 1]")

        cdf = [self.cumulative_probability(x) for x in self.xs]
        idx = np.abs(np.asarray(cdf) - p).argmin()
        return self.xs[idx]

    def __len__(self):
        return len(self.distribution)


if __name__ == "__main__":
    main()
