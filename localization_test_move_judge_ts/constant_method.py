#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ##################################################
# 恒常法を用いた音の最小知覚移動角度の心理測定実験
#
# Tetsu Takizawa (tt20805@tomakomai.kosen-ac.jp)
# 2020
# ##################################################

import sys
import os
import glob
import re
from subprocess import Popen

import numpy as np

usage = f"usage: python constant.py subject_dir test_number"
example_1 = "example: python constant.py /path/to/SUBJECTS/NAME 1"


def print_usage():
    print(usage)
    print(example_1)


# コマンドの実行
def subprocess(cmd):
    popen = Popen(cmd.split())
    popen.wait()


def main():
    # --------------- 引数の処理 -------------- #
    args = sys.argv[1:]
    if len(args) != 2:
        print_usage()
        sys.exit(1)

    script_dir = os.path.dirname(os.path.abspath(__file__)) + "/"  # このスクリプトのパス
    subject_dir = args[0]
    subject_name = subject_dir.split("/")[-1]
    test_number = args[1]
    # --------------- 引数の処理 -------------- #

    # --------------- 試験音の読み込み -------------- #
    os.chdir(subject_dir + "/TS/")
    test_sounds = glob.glob("*")

    # 読み込みのエラー判定
    if len(test_sounds) == 0:
        print("試験音を読み込めませんでした。試験音のディレクトリとプログラムの引数を確認してください。")
        print_usage()
        sys.exit(1)

    # 試験音のシャッフル
    np.random.shuffle(test_sounds)

    # シャッフル後の順番の記憶
    with open(script_dir + subject_dir + "/ANSWER/random_" + subject_name + "_" + test_number + ".txt",
              'w') as random_file:
        for i in range(len(test_sounds)):
            random_file.write(test_sounds[i] + "\n")

    # --------------- 試験音の読み込み -------------- #

    # ----------------------------------- 試験 ----------------------------------- #
    print("試験開始")
    for num in range(len(test_sounds)):
        while True:
            # 試行回数読み上げ
            subprocess("say " + str(num + 1))
            # 試験音再生
            subprocess("2chplay " + script_dir + subject_dir + "/TS/" + test_sounds[num])
            # 回答の入力
            answer = input()  # 標準入力

            if answer == "111":
                answer_rotation = "c"
            elif answer == "000":
                answer_rotation = "cc"
            else:
                # 回答の入力が有効でなければもう一度再生
                continue

            # --------------- 試験音のパラメータ抽出 --------------- #
            parameter = test_sounds[num].replace("move_judge_", "").replace(".DSB", "")
            parameter_divide = re.search("(.*)_(.*)_(.*)_(.*)", parameter)
            move_width = parameter_divide.group(1).replace("w", "")
            move_time = parameter_divide.group(2).replace("mt", "")
            rotation_direction = parameter_divide.group(3)
            start_pos = parameter_divide.group(4).split(".")[0]
            is_correct = "1" if rotation_direction == answer_rotation else "0"
            # --------------- 試験音のパラメータ抽出 --------------- #

            # -------------------- 結果の記録 -------------------- #
            with open(script_dir + subject_dir + "/ANSWER/answer_" + subject_name + "_" + test_number + ".csv",
                      'a') as answer_file:

                answer_file.write(test_sounds[num] + "," + move_width + "," + move_time
                                  + "," + rotation_direction + "," + start_pos + "," + answer_rotation + "," + is_correct + "\n")
            # -------------------- 結果の記録 -------------------- #

            # 途中経過の出力
            print(f"正誤: {is_correct}\n")
            # 次の試験音へ
            break
    # ----------------------------------- 試験 ----------------------------------- #

    # --------------- 終了処理 --------------- #
    print(f"実験終了")
    subprocess("say お疲れさまでした")
    # --------------- 終了処理 --------------- #


if __name__ == '__main__':
    main()
