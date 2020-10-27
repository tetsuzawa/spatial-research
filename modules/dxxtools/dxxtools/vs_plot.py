#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import signal

import matplotlib.pyplot as plt
import dxx

signal.signal(signal.SIGINT, signal.SIG_DFL)


def main():
    desc = "vs_plot shows wave of .DXX"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("filename", help="filename to analyze")
    args = parser.parse_args()
    filename = args.filename

    data = dxx.read(filename)

    plt.plot(data)
    plt.show()


if __name__ == "__main__":
    main()
