#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import glob
import re
from subprocess import Popen

import psychometrics as psy

usage = "usage: main.py subject_dir start_position stimulation_variable stimulation_constant_value test_number"
example_1 = "example: main.py ../SUBJECTS/NAME 45 w mt5 3"
example_2 = "example: main.py ../SUBJECTS/NAME 0 mt w12 8"


def main():
    args = sys.argv
    if len(args) != 6:
        print(usage)
        print(example_1)
        print(example_2)
        sys.exit(1)

    script_dir = os.path.dirname(os.path.abspath(__file__)) + "/"  # このスクリプトのパス
    subject = args[1]
    start_pos = args[2]
    stimulation_var = args[3]
    stimulation_const_val = args[4]
    test_number = args[5]

    # 試験音の読み込み
    os.chdir(subject + "/TS/")
    if stimulation_var == "w":
        # move_judge_w*_mtXX_*_{start_angle}_*.DDB を取得
        test_sounds = sorted(glob.glob(f"move_judge_w*_{stimulation_const_val}_*_{start_pos}_*.DDB"))
    elif stimulation_var == "mt":
        # move_judge_wXX_mt*_*_{start_angle}_*.DDB を取得
        test_sounds = sorted(glob.glob(f"move_judge_{stimulation_const_val}_mt*_*_{start_pos}_*.DDB"))
    else:
        print("error: invalid stimulation_variable")
        print(usage)
        print(example_1)
        print(example_2)
        sys.exit(1)


    # --------------- 試験音の刺激幅を確認 -------------- #
    min_parameter = test_sounds[0].replace("move_judge_", "").replace(".DSB", "")
    max_parameter = test_sounds[-1].replace("move_judge_", "").replace(".DSB", "")
    min_parameter_divide = re.search("(.*)_(.*)_(.*)_(.*)", min_parameter)
    max_parameter_divide = re.search("(.*)_(.*)_(.*)_(.*)", max_parameter)
    if stimulation_var == "w":
        min_var = min_parameter_divide.group(1).replace("w", "")
        max_var = max_parameter_divide.group(1).replace("w", "")
    elif stimulation_var == "mt":
        min_var = min_parameter_divide.group(2).replace("mt", "")
        max_var = max_parameter_divide.group(2).replace("mt", "")
    # --------------- 試験音の刺激幅を確認 -------------- #

    # --------------- 試験音の最小刺激幅を確認 -------------- #
    one_level_upper_parameter = test_sounds[1].replace("move_judge_", "").replace(".DSB", "")
    one_level_upper_parameter_divide = re.search("(.*)_(.*)_(.*)_(.*)", min_parameter)
    if stimulation_var == "w":
        one_level_upper_var = min_parameter_divide.group(1).replace("w", "")
    elif stimulation_var == "mt":
        one_level_upper_var = min_parameter_divide.group(2).replace("mt", "")
    dx = int(one_level_upper_var)-int(min_var)
    # --------------- 試験音の最小刺激幅を確認 -------------- #

    # --------------- 心理測定法の決定 ---------------#
    # PEST法のインスタンス生成
    pest = psy.PEST()
    # --------------- 心理測定法の決定 ---------------#

    # 試行回数T
    T = 0
    # 実験開始
    print("実験開始")
    while True:
        T += 1
        while True:
            # 試行回数読み上げ
            subprocess("say " + str(T + 1))
            # 試験音再生
            subprocess("2chplay " + script_dir + subject + "/TS/" + test_sounds[test_num])
            answer = int(input())  # 標準入力

            # 刺激レベルの更新
            X = pest.update(is_correct, X)
            X_list.append(X)

            # 実験終了判定
            if pest.has_ended():
                print("実験終了")
                break


# コマンドの実行
def subprocess(cmd):
    popen = Popen(cmd.split())
    popen.wait()


if __name__ == '__main__':
    main()
