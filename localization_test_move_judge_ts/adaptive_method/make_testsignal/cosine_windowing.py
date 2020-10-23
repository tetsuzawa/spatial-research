#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys

import dxx
import numpy as np


def cosine_windowing(input: str, sampling_freq: float, start_point: int, window_len: float, output: str):
    length = dxx.len_file(input)
    window_len = int(window_len * sampling_freq)
    print(f"signal:{input} \nsignal length:{length} ,window length:{window_len}[sample]\n", file=sys.stderr)

    x = dxx.read_DXX_file(input)

    for i in range(start_point, start_point + window_len):
        x[i] = x[i] * np.sin(float(i - start_point) / window_len * np.pi / 2.0)

    for i in range(length - window_len, length):
        x[i] = x[i] * np.cos(float(i - (length - window_len)) / window_len * np.pi / 2.0)

    dxx.write_DXX_file(output, x)


if __name__ == "__main__":
    desc = "multiply start of signal and end by cosine_window"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("input", help="input file")
    parser.add_argument("sampling_freq", type=float, help="sampling frequency [kHz]")
    parser.add_argument("start_point", type=int, help="start point of convolution")
    parser.add_argument("window_len", type=float, help="the length of cosine window")
    parser.add_argument("output", help="output file")
    args = parser.parse_args()

    cosine_windowing(args.input, args.sampling_freq, args.start_point, args.window_len, args.output)
