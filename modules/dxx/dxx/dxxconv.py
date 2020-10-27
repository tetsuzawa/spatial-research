#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# ##################################################
# 研究室で使用している音声ファイル (.DXX 形式)と.wavを変換するプログラム
#
# 作成者:瀧澤哲
# 作成年:2020
# ##################################################


import os
import sys
import argparse

import soundfile as sf
import numpy as np

import dxx


def main():
    desc = """
    .DXXや.wavを相互変換する。
    次のファイル形式のみ入出力可能。(.DSA, .DFA, .DDA, .DSB, .DFB, .DDB, .wav)
    """
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("input", help="変換元のファイル名")
    parser.add_argument("output", help="変換後のファイル名")
    args = parser.parse_args()
    input = args.input
    output = args.output

    # read input
    input_ext = os.path.splitext(input)[-1]
    if input_ext in dxx.exts:
        data = dxx.read(input)
        input_type = dxx.dtypes[dxx.exts.index(input_ext)]

    elif input_ext == ".wav":
        data = read_wav(input)
        input_type = np.int16

    else:
        print("Error: input file extension is invalid. want: .wav or .DXX, got:", input_ext, file=sys.stderr)
        parser.print_help(file=sys.stderr)
        sys.exit(1)

    # write output
    output_ext = os.path.splitext(output)[-1]
    if output_ext in dxx.exts:
        dxx.write(output, data)

    elif output_ext == ".wav":
        if input_type == np.float32 or input_type == np.float64:
            data = float_to_int16(data)
        write_wav(output, data)

    else:
        print("Error: output file extension is invalid. want: .wav or .DXX, got:", input_ext, file=sys.stderr)
        parser.print_help(file=sys.stderr)
        sys.exit(1)

    print("Successfully completed!")


def read_wav(name: str) -> np.ndarray:
    data, sr = sf.read(name, dtype="int16")
    if sr != 48000:
        print("Error: sampling rate of input data is invalid. want: 48000, got:", sr, file=sys.stderr)
        sys.exit(1)
    if data.ndim != 1:
        print("Error: number of channels of input data is invalid. want: 1, got:", data.ndim, file=sys.stderr)
        sys.exit(1)
    return data


def write_wav(name: str, data: np.ndarray):
    sf.write(file=name, data=data, samplerate=48000, subtype="PCM_16", endian="LITTLE", format="WAV")


def float_to_int16(data: np.array) -> np.array:
    amp = 2 ** 15 - 1  # default amp for .DSB
    max_data = np.abs(data).max()
    min_data = np.abs(data).min()
    data = (data - min_data) / (max_data - min_data) * amp
    return data.astype(np.int16)


def int16_to_float32(data: np.array) -> np.array:
    amp = 10000.0  # default amp for .DFB
    data = data.astype(np.float32)
    max_data = np.abs(data).max()
    min_data = np.abs(data).min()
    data = (data - min_data) / (max_data - min_data) * amp
    return data


def int16_to_float64(data: np.array) -> np.array:
    amp = 10000.0  # default amp for .DDB
    data = data.astype(np.float64)
    max_data = np.abs(data).max()
    min_data = np.abs(data).min()
    data = (data - min_data) / (max_data - min_data) * amp
    return data


if __name__ == '__main__':
    main()
