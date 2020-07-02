##########################################################################################################
# 方向確認用音源再生用のプログラム
#
# Takizawa Tetsu(tt20805)
# 2020
##########################################################################################################

import sys
from subprocess import Popen

usage = "usage: python direction_confirmation.py SUBJECT_DIR"
args = sys.argv[1:]
subject_dir=args[0]

def print_usage():
    print(usage)

def subprocess(cmd):
    popen = Popen(cmd.split())
    popen.wait()
    
def direction_confirm():

    if len(args) != 1:
        print("error: invalid argument")
        print_usage()

    print("\n方向確認")
    subprocess("say 方向の確認を行います")
    for i in range(13):
        subprocess("say " + str(i*30))
        subprocess("2chplay " + subject_dir +
                   "/TSP/TSP_" + str(i*30%360) + ".DSB")


if __name__ == "__main__":
    direction_confirm()
