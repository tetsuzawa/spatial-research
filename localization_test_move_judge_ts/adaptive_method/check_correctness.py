import sys
import glob
import os
import re
import time

import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
import psychometrics as psy
import questplus as qp

from subprocess import Popen


def main():
    resp_list = []
    problem_list = []
    correctness_list = []
    script_dir = os.path.dirname(os.path.abspath(__file__)) + "/"
    subject_dir = "SUBJECTS/TMP3"
    start_pos = "450"

    for i in range(50):
        rotation = np.random.choice([0, 1], 1)[0]
        rotation_str = "c" if rotation == 1 else "cc"
        test_sound = "move_judge_w050_mt320_" + rotation_str + "_450.DSB"
        subprocess(
            "/Users/tetsu/local/bin/2chplay " + script_dir + subject_dir + "/end_angle_" + start_pos + "/TS/" + test_sound)
        answer = input("\n回答 -> ")  # 標準入力
        if answer not in ["0", "1"]:
            continue
        resp_list.append(int(answer))
        problem_list.append(rotation)
        correctness_list.append(1 if int(answer) == rotation else 0)
        time.sleep(0.1)

    print(resp_list)
    print(problem_list)
    print(correctness_list)
    print("mean:", np.array(correctness_list).mean())


# コマンドの実行
def subprocess(cmd):
    popen = Popen(cmd.split())
    popen.wait()


if __name__ == '__main__':
    main()
