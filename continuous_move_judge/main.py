#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import glob
import re
from subprocess import Popen

import numpy as np
import matplotlib.pyplot as plt

import psychometrics as psy

usage = "usage: python main.py subject_dir stimulation_constant_value start_position test_number"
example_1 = "example: python main.py /path/to/SUBJECTS/NAME mt05 45 3"
example_2 = "example: python main.py /path/to/SUBJECTS/NAME w12 0 8"


def print_usage():
    print(usage)
    print(example_1)
    print(example_2)
    sys.exit(1)


def main():
    # --------------- 引数の処理 -------------- #
    args = sys.argv[1:]
    if len(args) != 4:
        print_usage()

    script_dir = os.path.dirname(os.path.abspath(__file__)) + "/"  # このスクリプトのパス
    subject_dir = args[0]
    subject_name = subject_dir.split("/")[-1]
    # stimulation_var = args[1]
    stimulation_const_val = args[1]
    start_pos = args[2]
    test_number = args[3]
    # --------------- 引数の処理 -------------- #

    # --------------- 試験音の読み込み -------------- #
    os.chdir(subject_dir + "/TS/")

    # 引数の刺激条件のバリデーション
    mt_pattern = re.compile("mt\d{2}")
    w_pattern = re.compile("w\d{2}")
    if mt_pattern.match(stimulation_const_val):
        stimulation_var = "w"
    elif w_pattern.match(stimulation_const_val):
        stimulation_var = "mt"
    else:
        print("error: invalid stimulation_constant_value")
        print_usage()
        sys.exit(1)

    if stimulation_var == "w":
        # move_judge_w*_mtXX_*_{start_angle}_*.DDB を取得
        test_sounds = sorted(glob.glob(f"move_judge_w*_{stimulation_const_val}_*_{start_pos}.DSB"))
    else:
        # move_judge_wXX_mt*_*_{start_angle}_*.DDB を取得
        test_sounds = sorted(glob.glob(f"move_judge_{stimulation_const_val}_mt*_*_{start_pos}.DSB"))

    # 読み込みのエラー判定
    if len(test_sounds) == 0:
        print("試験音を読み込めませんでした。試験音のディレクトリとプログラムの引数を確認してください。")
        print_usage()
        sys.exit(1)

    # 取得した試験を[c,cc]の2列に並び替え
    test_sounds = np.array(test_sounds).reshape(-1, 2)

    # --------------- 試験音の読み込み -------------- #

    # --------------- 試験音の刺激幅を確認 -------------- #
    min_parameter = test_sounds[0, 0].replace("move_judge_", "").replace(".DSB", "")
    max_parameter = test_sounds[-1, 0].replace("move_judge_", "").replace(".DSB", "")
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
    one_level_upper_parameter = test_sounds[1, 0].replace("move_judge_", "").replace(".DSB", "")
    one_level_upper_parameter_divide = re.search("(.*)_(.*)_(.*)_(.*)", one_level_upper_parameter)
    if stimulation_var == "w":
        one_level_upper_stimulation_level = one_level_upper_parameter_divide.group(1).replace("w", "")
    else:
        one_level_upper_stimulation_level = one_level_upper_parameter_divide.group(2).replace("mt", "")
    min_dx = int(one_level_upper_stimulation_level) - int(min_stimulation_level)
    # --------------- 試験音の最小刺激幅を確認 -------------- #

    # --------------- 刺激レベルに対する試験音の辞書登録 -------------- #
    test_sounds_dict = {}
    for test_sound_both in test_sounds:
        # 時計回りの試験音だけ読み込んで刺激レベルを確認
        parameter = test_sound_both[0].replace("move_judge_", "").replace(".DSB", "")
        parameter_divide = re.search("(.*)_(.*)_(.*)_(.*)", parameter)
        if stimulation_var == "w":
            stimulation_level = parameter_divide.group(1).replace("w", "")
        else:
            stimulation_level = parameter_divide.group(2).replace("mt", "")
            # mtの場合、数字が大きいほど刺激レベルが小さくなるので、反転させる
            stimulation_level = str(int(max_stimulation_level) + int(min_stimulation_level) - int(stimulation_level))
        # 刺激レベルに対する[c,cc]の試験音の配列を登録
        test_sounds_dict[int(stimulation_level)] = test_sound_both
    # --------------- 刺激レベルに対する試験音の辞書登録 -------------- #

    # --------------- 試験音の初期刺激幅を決定 -------------- #
    # 2のべき乗にしている理由はPEST法のアルゴリズムの制約によるもの
    # 詳しくは津村尚志 "最近の聴覚心理実験における新しい測定法"（1984)を参照
    if min_dx * (2 ** 4) < len(test_sounds_dict):
        init_dx_coef = 2 ** 4
    else:
        for i in range(1, 5):
            if 2 ** i > len(test_sounds_dict):
                init_dx_coef = 2 ** (i - 1)
                break
    init_dx = min_dx * init_dx_coef
    print(f"initdx:{init_dx}")
    # --------------- 試験音の初期刺激幅を決定 -------------- #

    # --------------- 心理測定法の決定 --------------- #
    # PEST法のインスタンス生成
    destination_threshold = 0.75
    pest = psy.PEST(init_dx=init_dx, min_dx=min_dx, Pt=destination_threshold)
    # --------------- 心理測定法の決定 --------------- #

    # ----------------------------------- 試験 ----------------------------------- #
    # 試行回数T
    T = 1
    # 初期刺激レベル
    X = int(max_stimulation_level)
    # 刺激の変化を記録
    X_list = [X]
    # 試験開始
    print("試験開始")
    while True:
        # while True:
        # 試行回数読み上げ
        subprocess("say " + str(T))

        # c,ccをランダムに選択 ([0,1]から一つ選ぶ。要素は一つでも配列で返ってくるので最初の要素を取得)
        rotation_index = np.random.choice([0, 1], 1)[0]
        test_sound = test_sounds_dict[X][rotation_index]

        # 試験音再生
        subprocess("2chplay " + script_dir + subject_dir + "/TS/" + test_sound)
        # 回答の入力
        answer = input()  # 標準入力
        # 回答の入力が有効でなければもう一度再生
        if answer != "111" and answer != "000":
            continue

        # 試行回数をカウント
        T += 1

        if answer == "111":
            answer = "c"
        elif answer == "000":
            answer = "cc"

        # --------------- 試験音のパラメータ抽出 --------------- #
        # プログラム的な無駄があるが、先行研究の形式に合わせてある
        parameter = test_sounds_dict[X][rotation_index].replace("move_judge_", "").replace(".DSB", "")
        parameter_divide = re.search("(.*)_(.*)_(.*)_(.*)", parameter)
        move_width = parameter_divide.group(1).replace("w", "")
        move_time = parameter_divide.group(2).replace("mt", "")
        rotation_direction = parameter_divide.group(3)
        start_pos = parameter_divide.group(4).split(".")[0]
        # --------------- 試験音のパラメータ抽出 --------------- #

        # 正誤判定
        is_correct = answer == rotation_direction

        # 途中経過の出力
        print(f"\n刺激レベルの推定閾値: {X}")
        print(f"正誤: {is_correct}\n")

        # --------------- 結果の記録 --------------- #
        with open(script_dir + subject_dir + "/ANSWER/answer_" + subject_name + "_" + test_number + ".csv",
                  'a') as answer_file:

            is_correct_str = "1" if is_correct else "0"
            answer_file.write(test_sounds_dict[X][rotation_index] + "," + move_width + "," + move_time
                              + "," + rotation_direction + "," + start_pos + "," + str(
                answer) + "," + is_correct_str + "\n")
        # --------------- 結果の記録 --------------- #

        # 刺激レベルの更新
        X = pest.update(is_correct, X)
        X_list.append(X)

        # 試験終了判定
        if pest.has_ended():
            print("試験終了")
            break
    # ----------------------------------- 試験 ----------------------------------- #

    # --------------- 試験結果の出力 --------------- #
    print(f"{T}回目の回答で実験が終了しました.")
    print(f"刺激レベルの推定閾値: {X}")

    # 刺激レベルの軌跡
    plt.plot(list(range(1, len(X_list) + 1)), X_list, "o-")
    plt.xlabel("Numbers of trials T")
    plt.ylabel("Stimulation level X")
    plt.title("Path of stimulation level")
    plt.show()
    # --------------- 試験結果の出力 --------------- #


# コマンドの実行
def subprocess(cmd):
    popen = Popen(cmd.split())
    popen.wait()


if __name__ == '__main__':
    main()
