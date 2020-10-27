#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

import numpy as np
import dxx


def main():
    desc = "upsample .DXX by de"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("input", help="変換元のファイル名")
    parser.add_argument("output", help="変換後のファイル名")
    parser.add_argument("multiple", type=int, help="何倍にアップサンプリングするか")
    args = parser.parse_args()
    input = args.input
    output = args.output
    multiple = args.multiple

    x = dxx.read(input)
    fft_points = len(x)
    fft_points_expd = len(x) * multiple
    X = np.fft.fft(x)
    Y = np.zeros(fft_points_expd, dtype=np.complex128)

    for i in range(0, int(fft_points / 2)):
        Y[i] = X[i]
        Y[fft_points_expd - 1 - i] = X[fft_points - 1 - i]

    y = np.fft.ifft(Y)
    dxx.write(output, y.real)


if __name__ == "__main__":
    main()
