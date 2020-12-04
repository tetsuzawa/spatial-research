#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ##################################################
# .DXXファイルのLR比較プロット
#
# Tetsu Takizawa (tt20805@tomakomai.kosen-ac.jp)
# 2020
# ##################################################

import signal

import numpy as np
import matplotlib.pyplot as plt
import dxx

signal.signal(signal.SIGINT, signal.SIG_DFL)


def main():
    # r = range(0, 105, 1)  # 0度から10度
    # r = range(0, 105, 5)  # 0度から10度
    # r = range(0, 305, 5)  # 0度から30度
    # r = range(900,1005,5)  # 90度から100度
    # r = range(0, 905, 5)  # 0度から90度
    r = range(0, 905, 50)  # 0度から90度
    # r = range(2700, 3555, 50)  # 0度から90度
    # r = range(0, 1005, 1)  # 0度から90度
    sounds = []
    for i in r:
        sounds.append(dxx.read(f"SLTF_{i}_R.DDB"))

    arg_maxs = []
    maxs = []

    for sound in sounds:
        arg_maxs.append(np.argmax(sound))
        maxs.append(np.max(sound))
        # maxs.append(np.max(sound))

    fig = plt.figure()
    ax1 = fig.add_subplot(1, 3, 1)
    ax1.plot(r, arg_maxs, "o")
    #ax1.plot(r, arg_maxs, "-o")
    ax1.set_xlabel("Angle [deg]")
    ax1.set_ylabel("Sample")

    # max_max = np.max(maxs)
    # for i, m in enumerate(maxs):
    #     maxs[i] = 20 * np.log10(m/max_max)

    ax2 = fig.add_subplot(1, 3, 2)
    ax2.plot(r, maxs, "o")
    #ax2.plot(r, maxs, "-o")
    ax2.set_xlabel("Angle [deg]")
    ax2.set_ylabel("Amplitude")
    ax2.grid()

    ax3 = fig.add_subplot(1, 3, 3)
    ax3.plot(arg_maxs, maxs, "o")
    #ax3.plot(arg_maxs, maxs, "-o")
    ax3.set_xlabel("Sample")
    ax3.set_ylabel("Amplitude")
    ax3.grid()

    # fig.show()
    plt.show()


if __name__ == '__main__':
    main()
