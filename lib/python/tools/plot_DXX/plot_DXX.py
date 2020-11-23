#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ##################################################
# .DXXファイルのプロット
#
# Tetsu Takizawa (tt20805@tomakomai.kosen-ac.jp)
# 2020
# ##################################################

import argparse
import signal

import matplotlib.pyplot as plt

import dxx

signal.signal(signal.SIGINT, signal.SIG_DFL)


def main():
    desc = f"""
    .DXXの波形をプロットする。
    読み込むファイルを引数で指定して読み込む。
    usage: plot_DXX.py ./SLTF_0.DDB
    """
    # --------------- 引数の処理 -------------- #
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("data", help="読み込む音声のパス 。example: /path/to/SUBJECTS/NAME/SLTF_0.DDB")
    args = parser.parse_args()
    data = args.data
    # --------------- 引数の処理 -------------- #

    data = dxx.read(data)
    print("信号長:", len(data))

    plt.plot(data)
    plt.xlabel("Sample")
    plt.ylabel("Amplitude")
    plt.show()


if __name__ == '__main__':
    main()
