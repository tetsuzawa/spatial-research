#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

##########################################################################################################
# 被験者選定の音像定位実験用Pythonスクリプト
# SUBJECTS/HOGEHOGE/TS内の試験音ファイルを読み込みランダムに呈示
# 再生したDSBファイルと被験者の回答をSUBJECTS/HOGEHOGE/ANSWER内のCSVファイルに出力
#
# ex : python3 localization_test_subchoise.py HOGEHOGE TIMEs(1,2,3....)
#
# Ryota Shimokawara (sr17805@tomakomai.kosen-ac.jp)
# 2018
##########################################################################################################
# 一部ディレクトリの修正(2019.6.24)
# 前後誤知覚率,平均定位誤差,標本標準偏差の算出を追加(2019.7.10)
#
# Shimizu Yuya(sy19807@)
# 2019
##########################################################################################################

import glob
import sys
import random
import os
import re
from subprocess import Popen
from datetime import datetime

args = sys.argv[1:]
subject_dir = args[0]
times = args[1]

def main():
    global subject_dir
    global times

    # 試験音のシャッフル
    test_sounds = []
    for i in range(5):
        TSs = glob.glob(subject_dir + "/TS/*")
        for string in TSs:
            test_sounds.append(string.replace(subject_dir+"/TS/", ""))
    random.shuffle(test_sounds)

    # シャッフル後の順番の記憶
    with open(subject_dir+"/ANSWER/random_"+times+".txt", mode='w') as random_file:
        for i in range(len(test_sounds)):
            random_file.write(test_sounds[i]+"\n")

    # 方向の確認
    direction_confirm()

    # 試験
    print("\n試験開始")
    for test_num in range(len(test_sounds)):
        while True:
            subprocess("say " + str(test_num+1))  # 試験番号読み上げ
            subprocess("2chplay " + subject_dir +
                       "/TS/" + test_sounds[test_num])  # 試験音再生
            answer = input()  # 標準入力
            print(f"\ninput: {answer}\n")

            # 方向の抜き出し
            temp = (test_sounds[test_num]).split("_", 1)
            temp = re.findall(r'([0-9]*)', str(temp[1]))
            test_direction = temp[0]

            # 方向の確認
            if answer == "222":
                direction_confirm()
            elif answer == "000":
                continue

            # 回答の入力
            elif int(answer) % 10 == 0 and int(answer) <= 180 and int(answer) >= 0:

                if test_num == 0:  # 表の各項目の書込み
                    with open(subject_dir+"/ANSWER/answer_"+times+".csv", 'a') as answer_file:
                        answer_file.write("file_name" + "," + "correct_direction" +
                                          "," + "answer_direction" + "," + "data_time" + "\n")

                with open(subject_dir+"/ANSWER/answer_"+times+".csv", 'a') as answer_file:
                    answer_file.write(test_sounds[test_num] + "," + str(test_direction) + "," + str(
                        answer) + "," + datetime.now().strftime("%H:%M:%S") + "\n")
                break

    subprocess("say お疲れさまでした 以上で試験は終了です")


def subprocess(cmd):
    popen = Popen(cmd.split())
    popen.wait()

# 方向の確認


def direction_confirm():
    global subject_dir

    print("\n方向確認")
    subprocess("say 方向の確認を行います")
    for i in range(7):
        subprocess("say " + str(i*30))
        subprocess("2chplay " + subject_dir +
                   "/TSP/TSP_" + str(i*30) + ".DSB")


if __name__ == "__main__":
    main()
