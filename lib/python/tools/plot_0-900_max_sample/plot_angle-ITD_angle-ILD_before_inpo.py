#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import signal
import argparse

import pandas as pd
import matplotlib.pyplot as plt

signal.signal(signal.SIGINT, signal.SIG_DFL)


def main():
    parser = argparse.ArgumentParser(description="plot ILDs and ITDs")
    parser.add_argument("ILDs", help="ILDs csv file", default="ILDs.csv")
    parser.add_argument("ITDs", help="ITDs csv file", default="ITDs.csv")
    parser.add_argument("start_angle", help="start angle to analyze", type=int, default=0)
    parser.add_argument("end_angle", help="end angle to analyze", type=int, default=3600)
    parser.add_argument("step", help="step", type=int, default=1)
    args = parser.parse_args()
    ILDs = args.ILDs
    ITDs = args.ITDs
    start = args.start_angle
    end = args.end_angle
    step = args.step

    df_ILD = pd.read_csv(ILDs, header=None).iloc[:, 0]
    df_ITD = pd.read_csv(ITDs, header=None).iloc[:, 0]

    r = range(start, end, step)

    if step == 1:
        df_ILD = df_ILD[start:end]
        df_ITD = df_ITD[start:end]
    else:
        df_ILD = df_ILD[start:end:step]
        df_ITD = df_ITD[start:end:step]

    plot_format = "-"

    print(len(list(r)))
    print(len(df_ILD))
    print(len(df_ITD))

    fig = plt.figure()
    ax1 = fig.add_subplot(1, 2, 1)
    ax1.plot(r, df_ILD, plot_format)
    ax1.set_xlabel("Angle [deg]")
    ax1.set_ylabel("ILD")
    ax1.grid()

    ax2 = fig.add_subplot(1, 2, 2)
    ax2.plot(r, df_ITD, plot_format)
    ax2.set_xlabel("Angle [deg]")
    ax2.set_ylabel("ITD")
    ax2.grid()

    plt.show()


if __name__ == '__main__':
    main()
