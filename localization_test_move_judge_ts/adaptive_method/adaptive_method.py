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
import re
import json
from typing import List, Dict
from subprocess import Popen

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import questplus as qp

usage = """usage: python adaptive_method.py subject_dir stimulation_constant_value start_position test_number
example: python adaptive_method.py /path/to/SUBJECTS/NAME mt040 45 3
example: python adaptive_method.py /path/to/SUBJECTS/NAME w012 0 8"""


def print_usage():
    print(usage, sys.stderr)


def main():
    # --------------- 引数の処理 -------------- #
    args = sys.argv[1:]
    if len(args) != 4:
        print_usage()
        sys.exit(1)

    subject_dir = args[0]
    subject_name = subject_dir.split("/")[-1]
    stim_const_val = args[1]
    start_pos = args[2]
    test_number = args[3]
    # --------------- 引数の処理 -------------- #

    # 引数の刺激条件のバリデーション
    mt_pattern = re.compile("mt\d{3}")  # mtXXX (mt + 3桁の数字))
    w_pattern = re.compile("w\d{3}")
    if mt_pattern.match(stim_const_val):
        stim_var = "w"
    elif w_pattern.match(stim_const_val):
        stim_var = "mt"
    else:
        print("error: invalid stimulation_constant_value", file=sys.stderr)
        print_usage()
        sys.exit(1)

    TS_dir = subject_dir + "/end_angle_" + start_pos + "/TS/"
    ANSWER_dir = subject_dir + "/end_angle_" + start_pos + "/ANSWER/"

    # 試験音の読み込み
    test_sounds = glob_test_sounds(TS_dir, start_pos, stim_const_val, stim_var)

    # 取得した試験を[c,cc]の2列に並び替え
    test_sounds = np.array(test_sounds).reshape(-1, 2)

    # 試験音の最小刺激幅を確認
    stim_spacing = check_stimulation_spacing(test_sounds, stim_var)

    # 刺激量に対する試験音の辞書作成
    test_sounds_dict = make_test_sounds_dict(test_sounds, stim_var)

    # --------------- 心理測定法の決定 --------------- #

    # 刺激ドメイン (単位を合わせるために10で割る)
    intensity = np.array(list(test_sounds_dict.keys())) / 10.0
    stim_domain = dict(intensity=intensity)

    # パラメータドメイン
    mean = intensity.copy()
    sd = np.arange(0.5, 20, 0.5)
    # bias (if 2-AFC then 1/2)
    lower_asymptote = 1 / 2
    # rate of mistake
    lapse_rate = np.arange(0, 0.05, 0.01)
    param_domain = dict(mean=mean,
                        sd=sd,
                        lower_asymptote=lower_asymptote,
                        lapse_rate=lapse_rate)

    # 事前確率密度ドメイン
    # mean_fitted = scipy.stats.norm.pdf(mean, loc=17.84, scale=8.38)
    # mean_fitted /= mean_fitted.sum()
    # sd_fitted = scipy.stats.norm.pdf(sd, loc=10.83, scale=2.78)
    # sd_fitted /= sd_fitted.sum()
    # prior = dict(mean=mean_fitted, sd=sd_fitted)
    prior = None

    # 結果ドメイン
    # Outcome (response) domain.
    response = ["Correct", "Incorrect"]
    outcome_domain = dict(response=response)

    # その他のパラメータ
    func = "norm_cdf"
    stim_scale = "linear"
    stim_selection_method = "min_entropy"
    param_estimation_method = "mean"

    # Initialize the QUEST+ staircase.
    qp_params = dict(stim_domain=stim_domain,
                     param_domain=param_domain,
                     outcome_domain=outcome_domain,
                     prior=prior,
                     func=func,
                     stim_scale=stim_scale,
                     stim_selection_method=stim_selection_method,
                     param_estimation_method=param_estimation_method)
    q = qp.QuestPlus(**qp_params)

    # QUEST+ パラメータの保存
    qp_params_file_name = ANSWER_dir + "qp_params_" + subject_name + "_" + stim_const_val + "_" + start_pos + "_" + test_number + ".json"
    with open(qp_params_file_name, 'w') as f:
        json.dump(qp_params, f, indent=2, cls=JSONEncoderNDArray)

    print("intensitiy:", intensity)
    print("mean:", mean)
    print("sd:", sd)
    # --------------- 心理測定法の決定 --------------- #

    # ----------------------------------- 試験 ----------------------------------- #
    # 試行回数T
    num_trial = 1
    # 総試行回数
    num_trials = 100

    # 刺激の過程を記録
    stim_history = []
    response_history = []
    entropy_history = []

    # 刺激の10％をランダムにずらす
    stim_range = int(len(intensity) * 0.1)
    print("stim_range:", stim_range)
    stim_jitters = list(range(-stim_range * stim_spacing, (stim_range + 1) * stim_spacing, stim_spacing))

    # 結果記録用データフレーム
    df = pd.DataFrame(
        columns=["num_trial", "test_sound", "move_width", "move_time", "start_pos", "rotation_direction",
                 "answer_rotation", "response", "mean_estimation", "sd_estimation", "lapse_rate_estimation",
                 "entropy"])

    # 推定過程表示用のfigure
    fig, axs = plt.subplots(1, 3)

    # 試験開始
    print("\n************************* 試験開始 *************************")

    # 試験音のロック用フラグ（聞き直しの際に試験音が変わることを防ぐため）
    test_sound_selected = False

    try:
        while num_trial <= num_trials:
            if not test_sound_selected:
                stim = q.next_stim["intensity"]
                stim_jitter = np.random.choice(stim_jitters) / 10.0
                print("stim jitter:", stim_jitter)
                if int((stim + stim_jitter) * 10) in test_sounds_dict.keys():
                    stim += stim_jitter
                print("original stim:", q.next_stim["intensity"], "stim with jitter:", stim)

                # 刺激の単位合わせ
                stim = int(stim * 10)

                # c,ccをランダムに選択
                rotation_index = np.random.choice([0, 1])
                test_sound = test_sounds_dict[stim][rotation_index]
                # 試験音のロック
                test_sound_selected = True

            # 試行回数読み上げ
            subprocess("say " + str(num_trial))
            # 試験音再生
            subprocess("2chplay " + TS_dir + test_sound)

            # 回答の入力
            answer = input("\n回答 -> ")

            if answer == "1":
                answer_rotation = "c"
            elif answer == "0":
                answer_rotation = "cc"
            else:
                # 回答の入力が有効でなければもう一度再生
                continue

            # 試験音のロック解除
            test_sound_selected = False

            # 試験音のパラメータ抽出
            # プログラム的な無駄があるが、先行研究の形式に合わせてある
            parameter = test_sounds_dict[stim][rotation_index].replace("move_judge_", "").replace(".DSB", "")
            parameter_divide = re.search("(.*)_(.*)_(.*)_(.*)", parameter)
            move_width = parameter_divide.group(1).replace("w", "")
            move_time = parameter_divide.group(2).replace("mt", "")
            rotation = parameter_divide.group(3)
            start_pos = parameter_divide.group(4).split(".")[0]

            # 正誤判定
            response = "Correct" if answer_rotation == rotation else "Incorrect"

            stim_history.append(stim)
            response_history.append(response)
            entropy_history.append(q.entropy)

            # 刺激量の更新
            q.update(stim=dict(intensity=stim / 10), outcome=dict(response=response))

            # 結果の書き込み
            series = pd.Series(
                [num_trial, test_sound, move_width, move_time, start_pos, rotation, answer_rotation, response,
                 q.param_estimate["mean"], q.param_estimate["sd"], q.param_estimate["lapse_rate"], q.entropy],
                index=df.columns)
            df = df.append(series, ignore_index=True)

            # 試行回数をカウント
            num_trial += 1

            # 途中経過の出力
            print("試行回数:", num_trial)
            print("刺激量X:", stim / 10)
            print("正誤:", response)
            print("\nパラメータ推定値:", q.param_estimate)
            print("エントロピー:", q.entropy)
            print("-------------------------------------------------------\n")

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

    except KeyboardInterrupt:
        print("KeyboardInterrupt", file=sys.stderr)
    except Exception as e:
        result_file_name = ANSWER_dir + "answer_" + subject_name + "_" + stim_const_val + "_" + start_pos + "_" + test_number + ".csv"
        df.to_csv(result_file_name, index=False)
        raise e
    finally:
        result_file_name = ANSWER_dir + "answer_" + subject_name + "_" + stim_const_val + "_" + start_pos + "_" + test_number + ".csv"
        df.to_csv(result_file_name, index=False)
    # ----------------------------------- 試験 ----------------------------------- #

    print("\n************************* 試験終了 *************************")

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
    print("result history", response_history)
    print("entropy history", entropy_history)

    # ------------------------------ 試験結果の出力 ------------------------------ #


def subprocess(cmd):
    """コマンドの実行"""
    popen = Popen(cmd.split())
    popen.wait()


def glob_test_sounds(target_dir: str, start_pos: str, stim_const_val: str, stim_var: str) -> List[str]:
    """指定した条件の試験音をすべて読み込む"""
    if stim_var == "w":
        # move_judge_w*_mtXX_*_{start_angle}_*.DDB を取得
        test_sounds = sorted(
            glob.glob(f"{target_dir}move_judge_w*_{stim_const_val}_*_{start_pos}.DSB"))
    else:
        # move_judge_wXX_mt*_*_{start_angle}_*.DDB を取得
        test_sounds = sorted(
            glob.glob(f"{target_dir}move_judge_{stim_const_val}_mt*_*_{start_pos}.DSB"))

    # 読み込みのエラー判定
    if len(test_sounds) == 0:
        print("試験音を読み込めませんでした。試験音のディレクトリとプログラムの引数を確認してください。ディレクトリ:" + target_dir + "読み込み条件:", stim_const_val,
              file=sys.stderr)
        print_usage()
        sys.exit(1)

    print(f"試験音を{len(test_sounds)}個読み込みました")

    # 取得した試験音のファイル名からtarget_dir部分を削除
    test_sounds = [test_sound.replace(target_dir, "") for test_sound in test_sounds]
    return test_sounds


def min_max_stimulation_level(test_sounds: np.ndarray, stim_var: str) -> (int, int):
    """最低と最高の刺激量を確認する"""
    min_parameter = test_sounds[0, 0].replace("move_judge_", "").replace(".DSB", "")
    max_parameter = test_sounds[-1, 0].replace("move_judge_", "").replace(".DSB", "")
    min_parameter_divide = re.search("(.*)_(.*)_(.*)_(.*)", min_parameter)
    max_parameter_divide = re.search("(.*)_(.*)_(.*)_(.*)", max_parameter)
    if stim_var == "w":
        min_stim_level = min_parameter_divide.group(1).replace("w", "")
        max_stim_level = max_parameter_divide.group(1).replace("w", "")
    else:
        min_stim_level = min_parameter_divide.group(2).replace("mt", "")
        max_stim_level = max_parameter_divide.group(2).replace("mt", "")
    return min_stim_level, max_stim_level


def check_stimulation_spacing(test_sounds: np.ndarray, stim_var: str) -> int:
    """刺激量の間隔を確認する"""
    min_parameter = test_sounds[0, 0].replace("move_judge_", "").replace(".DSB", "")
    one_level_upper_parameter = test_sounds[1, 0].replace("move_judge_", "").replace(".DSB", "")
    min_parameter_divide = re.search("(.*)_(.*)_(.*)_(.*)", min_parameter)
    one_level_upper_parameter_divide = re.search("(.*)_(.*)_(.*)_(.*)", one_level_upper_parameter)
    if stim_var == "w":
        min_stim_level = min_parameter_divide.group(1).replace("w", "")
        one_level_upper_stim_level = one_level_upper_parameter_divide.group(1).replace("w", "")
    else:
        min_stim_level = min_parameter_divide.group(2).replace("mt", "")
        one_level_upper_stim_level = one_level_upper_parameter_divide.group(2).replace("mt", "")
    stim_spacing = int(one_level_upper_stim_level) - int(min_stim_level)
    return stim_spacing


def make_test_sounds_dict(test_sounds: np.ndarray, stim_var) -> Dict[int, str]:
    """刺激量に対する試験音の辞書作成"""
    min_stim_level, max_stim_level = min_max_stimulation_level(test_sounds, stim_var)
    test_sounds_dict = {}
    for test_sound_both in test_sounds:
        # 時計回りの試験音だけ読み込んで刺激量を確認
        parameter = test_sound_both[0].replace("move_judge_", "").replace(".DSB", "")
        parameter_divide = re.search("(.*)_(.*)_(.*)_(.*)", parameter)
        if stim_var == "w":
            stim_level = parameter_divide.group(1).replace("w", "")
        else:
            stim_level = parameter_divide.group(2).replace("mt", "")
            # mtの場合、数字が大きいほど刺激量が小さくなるので、反転させる
            stim_level = str(
                int(max_stim_level) + int(min_stim_level) - int(stim_level))
        # 刺激量に対する[c,cc]の試験音の配列を登録
        test_sounds_dict[int(stim_level)] = test_sound_both
    return test_sounds_dict


class JSONEncoderNDArray(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(JSONEncoderNDArray, self).default(obj)


if __name__ == "__main__":
    main()
