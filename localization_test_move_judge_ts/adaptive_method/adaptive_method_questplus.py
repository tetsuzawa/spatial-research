#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ##################################################
# 適応法を用いた音の最小知覚移動角度の心理測定実験
#
# Tetsu Takizawa (tt20805@tomakomai.kosen-ac.jp)
# 2020
# ##################################################

import sys
import glob
import os
import re

import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
import psychometrics as psy
import questplus as qp

from subprocess import Popen

usage = "usage: python adaptive_method.py subject_dir stimulation_constant_value start_position test_number"
example_1 = "example: python adaptive_method.py /path/to/SUBJECTS/NAME mt040 45 3"
example_2 = "example: python adaptive_method.py /path/to/SUBJECTS/NAME w012 0 8"


def print_usage():
    print(usage)
    print(example_1)
    print(example_2)


def main():
    # --------------- 引数の処理 -------------- #
    args = sys.argv[1:]
    if len(args) != 4:
        print_usage()
        sys.exit(1)

    script_dir = os.path.dirname(os.path.abspath(__file__)) + "/"  # このスクリプトのパス
    subject_dir = args[0]
    subject_name = subject_dir.split("/")[-1]
    stimulation_const_val = args[1]
    start_pos = args[2]
    test_number = args[3]
    # --------------- 引数の処理 -------------- #

    # --------------- 試験音の読み込み -------------- #
    os.chdir(subject_dir + "/end_angle_" + start_pos + "/TS/")

    # 引数の刺激条件のバリデーション
    mt_pattern = re.compile("mt\d{3}")
    w_pattern = re.compile("w\d{3}")
    if mt_pattern.match(stimulation_const_val):
        stimulation_var = "w"
    elif w_pattern.match(stimulation_const_val):
        stimulation_var = "mt"
    else:
        print("error: invalid stimulation_constant_value")
        print_usage()
        sys.exit(1)

    print(stimulation_const_val)
    if stimulation_var == "w":
        # move_judge_w*_mtXX_*_{start_angle}_*.DDB を取得
        test_sounds = sorted(
            glob.glob(f"move_judge_w*_{stimulation_const_val}_*_{start_pos}.DSB"))
    else:
        # move_judge_wXX_mt*_*_{start_angle}_*.DDB を取得
        test_sounds = sorted(
            glob.glob(f"move_judge_{stimulation_const_val}_mt*_*_{start_pos}.DSB"))

    # 読み込みのエラー判定
    if len(test_sounds) == 0:
        print("試験音を読み込めませんでした。試験音のディレクトリとプログラムの引数を確認してください。読み込み条件:", stimulation_const_val)
        print_usage()
        sys.exit(1)

    # 取得した試験を[c,cc]の2列に並び替え
    test_sounds = np.array(test_sounds).reshape(-1, 2)

    # --------------- 試験音の読み込み -------------- #

    # --------------- 試験音の刺激幅を確認 -------------- #
    min_parameter = test_sounds[0, 0].replace(
        "move_judge_", "").replace(".DSB", "")
    max_parameter = test_sounds[-1,
                                0].replace("move_judge_", "").replace(".DSB", "")
    min_parameter_divide = re.search("(.*)_(.*)_(.*)_(.*)", min_parameter)
    max_parameter_divide = re.search("(.*)_(.*)_(.*)_(.*)", max_parameter)
    if stimulation_var == "w":
        min_stimulation_level = min_parameter_divide.group(1).replace("w", "")
        max_stimulation_level = max_parameter_divide.group(1).replace("w", "")
    else:
        min_stimulation_level = min_parameter_divide.group(2).replace("mt", "")
        max_stimulation_level = max_parameter_divide.group(2).replace("mt", "")
    # --------------- 試験音の刺激幅を確認 -------------- #

    # --------------- 試験音の最小刺激幅を確認 -------------- #
    one_level_upper_parameter = test_sounds[1, 0].replace(
        "move_judge_", "").replace(".DSB", "")
    one_level_upper_parameter_divide = re.search(
        "(.*)_(.*)_(.*)_(.*)", one_level_upper_parameter)
    if stimulation_var == "w":
        one_level_upper_stimulation_level = one_level_upper_parameter_divide.group(
            1).replace("w", "")
    else:
        one_level_upper_stimulation_level = one_level_upper_parameter_divide.group(
            2).replace("mt", "")
    min_dx = int(one_level_upper_stimulation_level) - int(min_stimulation_level)
    # --------------- 試験音の最小刺激幅を確認 -------------- #

    # --------------- 刺激レベルに対する試験音の辞書登録 -------------- #
    test_sounds_dict = {}
    for test_sound_both in test_sounds:
        # 時計回りの試験音だけ読み込んで刺激レベルを確認
        parameter = test_sound_both[0].replace(
            "move_judge_", "").replace(".DSB", "")
        parameter_divide = re.search("(.*)_(.*)_(.*)_(.*)", parameter)
        if stimulation_var == "w":
            stimulation_level = parameter_divide.group(1).replace("w", "")
        else:
            stimulation_level = parameter_divide.group(2).replace("mt", "")
            # mtの場合、数字が大きいほど刺激レベルが小さくなるので、反転させる
            stimulation_level = str(
                int(max_stimulation_level) + int(min_stimulation_level) - int(stimulation_level))
        # 刺激レベルに対する[c,cc]の試験音の配列を登録
        test_sounds_dict[int(stimulation_level)] = test_sound_both
    # --------------- 刺激レベルに対する試験音の辞書登録 -------------- #

    # --------------- 試験音の初期刺激幅を決定 -------------- #
    # 2のべき乗にしている理由はPEST法のアルゴリズムの制約によるもの
    # 詳しくは津村尚志 "最近の聴覚心理実験における新しい測定法"（1984)を参照
    # if 2 ** 4 < len(test_sounds_dict):
    #     init_dx_coef = 2 ** 4
    # else:
    #     for i in range(1, 5):
    #         if 2 ** i > len(test_sounds_dict):
    #             init_dx_coef = 2 ** (i - 1)
    #             break
    # init_dx = min_dx * init_dx_coef
    # print(f"initdx:{init_dx}")
    # --------------- 試験音の初期刺激幅を決定 -------------- #

    # --------------- 心理測定法の決定 --------------- #
    # destination_threshold = 0.75

    # Stimulus domain.
    # intensities = np.arange(start=-3.5, stop=-0.5 + 0.25, step=0.25)
    intensities = np.array(list(test_sounds_dict.keys())) / 10.0

    stim_domain = dict(intensity=intensities)

    # Parameter domain.
    # mean = orientation.copy()
    mean = np.arange(1, 8, 1)
    # beta
    # slope = 3.5
    # sd = 8
    sd = np.arange(3, 15, 0.5)
    # bias (if 2-AFC then 1/2)
    lower_asymptote = 1 / 2
    # lapse_rate = 1 / 2
    # rate of mistake
    lapse_rate = np.arange(0, 0.05, 0.01)
    # lower_asymptote = np.arange(0, 0.05, 0.01)

    param_domain = dict(mean=mean,
                        sd=sd,
                        lower_asymptote=lower_asymptote,
                        lapse_rate=lapse_rate)

    # mean_fitted = scipy.stats.norm.pdf(mean, loc=17.84, scale=8.38)
    # mean_fitted /= mean_fitted.sum()
    # sd_fitted = scipy.stats.norm.pdf(sd, loc=10.83, scale=2.78)
    # sd_fitted /= sd_fitted.sum()
    # prior_param_domain = dict(mean=mean_fitted, sd=sd_fitted)

    # Outcome (response) domain.
    responses = ["Correct", "Incorrect"]
    outcome_domain = dict(response=responses)

    # Further parameters.
    func = "norm_cdf"
    stim_scale = "linear"
    stim_selection_method = "min_entropy"
    # param_estimation_method = "mode"
    param_estimation_method = "mean"

    # Initialize the QUEST+ staircase.
    q = qp.QuestPlus(stim_domain=stim_domain,
                     func=func,
                     stim_scale=stim_scale,
                     param_domain=param_domain,
                     outcome_domain=outcome_domain,
                     stim_selection_method=stim_selection_method,
                     param_estimation_method=param_estimation_method,
                     # prior=prior_param_domain,
                     )
    # --------------- 心理測定法の決定 --------------- #

    # ----------------------------------- 試験 ----------------------------------- #
    # 試行回数T
    T = 1
    # 総試行回数
    T_end = 100
    # 初期刺激レベル
    # X = int(max_stimulation_level)
    # 刺激の変化を記録
    X_list = []
    result_list = []
    entropy_list = []
    # 試験開始
    print("試験開始")

    fig, axs = plt.subplots(1, 4)

    while T <= T_end:
        next_stim = q.next_stim
        print("next_stim:", next_stim)
        eps = np.random.choice(range(-3 * min_dx, (3 + 1) * min_dx, min_dx), 1)[0]
        eps /= 10
        print("eps:", eps)
        if next_stim["intensity"] + eps in np.array(list(test_sounds_dict.keys()))/10:
            next_stim["intensity"] += eps
        X = next_stim["intensity"]
        print("next_stim:", next_stim)
        X = int(X * 10)
        X_list.append(X)
        entropy_list.append(q.entropy)
        # 試行回数読み上げ
        subprocess("say " + str(T))

        # c,ccをランダムに選択 ([0,1]から一つ選ぶ。要素は一つでも配列で返ってくるので最初の要素を取得)
        rotation_index = np.random.choice([0, 1], 1)[0]
        test_sound = test_sounds_dict[X][rotation_index]

        # 試験音再生
        subprocess(
            "/Users/tetsu/local/bin/2chplay " + script_dir + subject_dir + "/end_angle_" + start_pos + "/TS/" + test_sound)
        # print("/Users/tetsu/local/bin/2chplay" + script_dir + subject_dir + "/end_angle_" + start_pos + "/TS/" + test_sound)
        # 回答の入力
        answer = input("\n回答 -> ")  # 標準入力

        if answer == "1":
            answer_rotation = "c"
        elif answer == "0":
            answer_rotation = "cc"
        else:
            # 回答の入力が有効でなければもう一度再生
            continue

        # 試行回数をカウント
        T += 1

        # --------------- 試験音のパラメータ抽出 --------------- #
        # プログラム的な無駄があるが、先行研究の形式に合わせてある
        parameter = test_sounds_dict[X][rotation_index].replace(
            "move_judge_", "").replace(".DSB", "")
        parameter_divide = re.search("(.*)_(.*)_(.*)_(.*)", parameter)
        move_width = parameter_divide.group(1).replace("w", "")
        move_time = parameter_divide.group(2).replace("mt", "")
        rotation_direction = parameter_divide.group(3)
        start_pos = parameter_divide.group(4).split(".")[0]
        # --------------- 試験音のパラメータ抽出 --------------- #

        # 正誤判定
        is_correct = answer_rotation == rotation_direction
        result = "Correct" if is_correct else "Incorrect"
        result_list.append(result)

        # 途中経過の出力

        print(f"\n刺激レベルX: {next_stim}")
        print(f"正誤: {is_correct}\n")

        # --------------- 結果の記録 --------------- #
        with open(
                script_dir + subject_dir + "/end_angle_" + start_pos + "/ANSWER/answer_" + subject_name + "_" + stimulation_const_val + "_" + start_pos + "_" + test_number + ".csv",
                "a") as answer_file:

            is_correct_str = "1" if is_correct else "0"
            answer_file.write(test_sounds_dict[X][rotation_index] + "," + move_width + "," + move_time
                              + "," + start_pos + "," + rotation_direction + "," + answer_rotation + "," + is_correct_str + "\n")
        # --------------- 結果の記録 --------------- #

        # 刺激レベルの更新
        q.update(stim=next_stim, outcome=dict(response=result))

        print(f"\n刺激レベルの推定閾値 mean: {q.param_estimate['mean']}, sd:{q.param_estimate['sd']}")
        print(f"entropy: {q.entropy}")

        # 試験終了判定
        # if pest.has_ended():
        #     print("試験終了")
        #     break
        # print(f"T={T}, likelihoods={q.likelihoods}")
        # likelihoods = q.likelihoods
        # print(f"T={T}, likelihoods[mean]={q.likelihoods['mean']}")
        # print(likelihoods)

        axs[0].plot(mean, q.marginal_posterior["mean"], color="blue", alpha=T / T_end, label=T)
        axs[0].set_xlabel("mean")
        axs[0].set_ylabel("probability")

        axs[1].plot(sd, q.marginal_posterior["sd"], color="green", alpha=T / T_end, label=T)
        axs[1].set_xlabel("sd")
        axs[1].set_ylabel("probability")

        pf_most_probable = np.squeeze(qp.qp.psychometric_function.norm_cdf(
            intensity=intensities,
            mean=q.param_estimate['mean'],
            sd=q.param_estimate['sd'],
            # lapse_rate=lapse_rate,
            lapse_rate=q.param_estimate['lapse_rate'],
            # lapse_rate=lapse_rate[q.marginal_posterior["lapse_rate"].argmax()],
            lower_asymptote=lower_asymptote,
            # lower_asymptote=lower_asymptote[q.marginal_posterior["lower_asymptote"].argmax()],
        ))
        axs[2].plot(pf_most_probable, color="red", alpha=T / T_end, label=T)
        axs[2].set_xlabel("psychometric function")
        axs[2].set_ylabel("probability")

        axs[3].plot(intensities, q.expected_entropies, color="yellow", alpha=T / T_end, label=T)
        axs[3].set_xlabel("intensity")
        axs[3].set_ylabel("EH")
        # plt.legend()
        # plt.show()

        # ----------------------------------- 試験 ----------------------------------- #
    plt.legend()
    plt.show()

    fig, axs = plt.subplots(1, 4)
    axs[0].plot(mean, q.marginal_posterior["mean"])
    axs[0].set_xlabel("mean")
    axs[0].set_ylabel("probability")

    axs[1].plot(sd, q.marginal_posterior["sd"])
    axs[1].set_xlabel("sd")
    axs[1].set_ylabel("probability")

    pf_most_probable = np.squeeze(qp.qp.psychometric_function.norm_cdf(
        intensity=intensities,
        mean=q.param_estimate['mean'],
        sd=q.param_estimate['sd'],
        # lapse_rate=lapse_rate,
        lapse_rate=q.param_estimate['lapse_rate'],
        # lapse_rate=lapse_rate[q.marginal_posterior["lapse_rate"].argmax()],
        lower_asymptote=lower_asymptote,
        # lower_asymptote=lower_asymptote[q.marginal_posterior["lower_asymptote"].argmax()],
    ))
    axs[2].plot(pf_most_probable)
    axs[2].set_xlabel("psychometric function")
    axs[2].set_ylabel("probability")

    axs[3].plot(intensities, q.expected_entropies)
    axs[3].set_xlabel("intensity")
    axs[3].set_ylabel("expected_entropies")
    plt.show()

    for k, v in q.marginal_posterior.items():
        print("marginal_posterior, k", k, "v", v)
        plt.plot(param_domain[k], v, label=k)
        plt.legend()
        plt.show()

    # --------------- 試験結果の出力 --------------- #
    print(f"{T}回目の回答で実験が終了しました.")
    # print(f"刺激レベルの推定閾値: {X}")

    for param_name, value in q.param_estimate.items():
        print(f"param_estimate, {param_name}: {value:.3f}")

    # 刺激レベルの軌跡
    plt.plot(list(range(1, len(X_list) + 1)), X_list, "o-")
    plt.xlabel("Numbers of trials T")
    plt.ylabel("Stimulation level X")
    plt.title("Path of stimulation level")
    plt.show()

    # エントロピーの軌跡
    plt.plot(list(range(1, len(X_list) + 1)), entropy_list, "o-")
    plt.xlabel("Numbers of trials T")
    plt.ylabel("Entropy")
    plt.title("Path of Entoropy")
    plt.show()

    print("X_list", X_list)
    print("result_list", result_list)
    print("q.resp_history", q.resp_history)
    print("q.stim_history", q.stim_history)
    print("entropy_list", entropy_list)

    # with open(
    #         script_dir + subject_dir + "/end_angle_" + start_pos + "/ANSWER/answer_" + subject_name + "_" + stimulation_const_val + "_" + start_pos + "_" + test_number + "questplus.json",
    #         "w") as qp_json_file:
    #     qp_json_file.write(q.to_json())

    # --------------- 試験結果の出力 --------------- #


# コマンドの実行
def subprocess(cmd):
    popen = Popen(cmd.split())
    popen.wait()


def norm_cdf(x, mu, sd_, gamma, delta):
    """mu: mean, sd_: standard diviation, gamma: lower_asymptote, delta: lapse_rate
    """
    norm = scipy.stats.norm(loc=mu, scale=sd_)
    return gamma + (1 - gamma - delta) * norm.cdf(x)


if __name__ == "__main__":
    main()
