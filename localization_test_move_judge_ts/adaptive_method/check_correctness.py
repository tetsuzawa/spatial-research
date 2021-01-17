import os
import time
from subprocess import Popen

import numpy as np


def main():
    answer_history = []
    rotation_history = []
    result_history = []
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
        answer_history.append(int(answer))
        rotation_history.append(rotation)
        result_history.append(1 if int(answer) == rotation else 0)
        time.sleep(0.1)

    print(answer_history)
    print(rotation_history)
    print(result_history)
    print("mean:", np.array(result_history).mean())


# コマンドの実行
def subprocess(cmd):
    popen = Popen(cmd.split())
    popen.wait()


if __name__ == '__main__':
    main()
