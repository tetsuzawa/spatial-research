#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ##################################################
# .DXXファイルのLR比較プロット
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
    desc = """
    伝達関数のLRの波形を比較する。(.DSA, .DFA, .DDA, .DSB, .DFB, .DDB)形式のみ対応。
    読み込む伝達関数を引数で指定して読み込む。
    """
    # --------------- 引数の処理 -------------- #
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("L", help="読み込む伝達関数のパス (L)。例: /path/to/SUBJECTS/NAME/SLTF_0_L.DDB")
    parser.add_argument("R", help="読み込む伝達関数のパス (R)。例: /path/to/SUBJECTS/NAME/SLTF_0_R.DDB")
    parser.add_argument("--sample", help="プロットする伝達関数のサンプル数 例: 2048", type=int)
    args = parser.parse_args()
    file_L = args.L
    file_R = args.R
    sample = args.sample
    # --------------- 引数の処理 -------------- #

    data_L = dxx.read_DXX_file(file_L)
    data_R = dxx.read_DXX_file(file_R)
    print("Lの信号長:", len(data_L))
    print("Rの信号長:", len(data_R))

    plt.plot(data_L[:sample], alpha=0.5, label="L")
    plt.plot(data_R[:sample], alpha=0.5, label="R")
    plt.xlabel("Sample")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.show()


if __name__ == '__main__':
    main()
