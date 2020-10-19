#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import os
import glob
from subprocess import Popen

import numpy as np


def main():
    args = sys.argv
    if len(args) != 3:
        print("usage: localization_test.py subject times")
        sys.exit()

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) + '/'  # このスクリプトのパス
    subject = args[1]
    times = args[2]

    # コマンドの実行
    def subprocess(cmd):
        popen = Popen(cmd.split())
        popen.wait()

    # 試験音のシャッフル
    os.chdir(subject + "/TS/")
    test_sounds = glob.glob("*")
    np.random.shuffle(test_sounds)

    # シャッフル後の順番の記憶
    with open(SCRIPT_DIR + subject + "/ANSWER/random_" + subject + "_" + times + ".txt", 'w') as random_file:
        for i in range(len(test_sounds)): random_file.write(test_sounds[i] + "\n")

    # 試験
    for test_num in range(len(test_sounds)):
        while True:
            subprocess("say " + str(test_num + 1))  # 試験番号読み上げ
            subprocess("2chplay " + SCRIPT_DIR + subject + "/TS/" + test_sounds[test_num])  # 試験音再生
            answer = int(input())  # 標準入力

            # 回答の入力
            if answer == 111 or answer == 000:
                with open(SCRIPT_DIR + subject + "/ANSWER/answer_" + subject + "_" + times + ".csv",
                          'a') as answer_file:
                    if answer == 111:
                        answer = "c"
                    elif answer == 000:
                        answer = "cc"

                    # 試験音のパラメータ抽出 ###################################################
                    parameter = test_sounds[test_num].replace("move_judge_", "").replace(".DSB", "")
                    parameter_divide = re.search("(.*)_(.*)_(.*)_(.*)", parameter)
                    move_width = parameter_divide.group(1).replace("w", "")
                    move_time = parameter_divide.group(2).replace("mt", "")
                    rotation_direction = parameter_divide.group(3)
                    start_pos = parameter_divide.group(4).split(".")[0]
                    is_correct = "1" if rotation_direction == answer else "0"
                    ########################################################################

                    answer_file.write(test_sounds[test_num] + "," + move_width + "," + move_time
                                      + "," + start_pos + "," + rotation_direction + "," + str(
                        answer) + "," + is_correct + "\n")
                    break


if __name__ == '__main__':
    main()
