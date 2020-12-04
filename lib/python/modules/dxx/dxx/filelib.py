# -*- coding: utf-8 -*-

# ##################################################
# 研究室で使用している音声ファイル (.DXX 形式)を扱うライブラリ
#
# 作成者:瀧澤哲
# 作成年:2020
# ##################################################

import os

import numpy as np

exts = [".DSA", ".DFA", ".DDA", ".DSB", ".DFB", ".DDB"]
dtypes = [np.int16, np.float32, np.float64, np.int16, np.float32, np.float64]
dtype_byte_width = [2, 4, 8, 2, 4, 8]
_format_specifiers = ["%d", "%e", "%e"]


class BadDataStyleError(Exception):
    """ファイル形式が適切でないことを知らせる例外クラス"""
    pass


def _style(name: str):
    """ファイルの拡張子を確認する関数。拡張子が不適切であれば例外を発生させる。"""
    name_ext = os.path.splitext(name)[1]

    if not name_ext in exts:
        raise BadDataStyleError(f"ファイルの拡張子が不適切です。 want: {exts}, got: {name_ext}")

    return exts.index(name_ext)


def len_file(filename: str) -> int:
    """データの長さを確認する関数

    example:
        import dxx
        num_sample = dxx.len_file("example.DSB")
    """
    index = _style(filename)
    byte_width = dtype_byte_width[index]
    return int(os.path.getsize(filename) / byte_width)


def read(filename: str) -> np.ndarray:
    """.DXXファイルを読み込む関数

    example:
        import dxx
        data = dxx.read("example.DSB")
    """

    index = _style(filename)

    # DXAファイル（アスキー文字列）
    if index < 3:
        with open(filename, "r") as f:
            data = np.fromfile(f, dtypes[index], -1)
        return data

    # DXBファイル（バイナリ）
    else:
        with open(filename, "rb") as f:
            data = np.fromfile(f, dtypes[index], -1)
        return data


def write(filename: str, data: np.ndarray):
    """.DXXファイルを書き込む関数

    example:
        import dxx
        data = np.random.rand(1024)
        dxx.write("example.DDB", data)
    """

    index = _style(filename)

    data_type = data.dtype
    output_type = dtypes[index]
    if (data_type == np.float32 or data_type == np.float64) and output_type == np.int16:
        data = _float_to_int16(data)
    elif data_type == np.int16 and output_type == np.float32:
        data = _int16_to_float32(data)
    elif data_type == np.int16 and output_type == np.float64:
        data = _int16_to_float64(data)
    else:
        BadDataStyleError(f"want: np.int16 or np.float32 or np.float64, got: ", data_type)

    # DXAファイル（アスキー文字列）
    if index < 3:
        # 改行区切りで保存
        data.tofile(filename, sep="\n", format=_format_specifiers[index])

    # DXBファイル（バイナリ）
    else:
        data.tofile(filename)


def _float_to_int16(data: np.ndarray) -> np.ndarray:
    amp = 2 ** 15 - 1  # default amp for .DSB
    max_data = np.abs(data).max()
    min_data = np.abs(data).min()
    data = (data - min_data) / (max_data - min_data) * amp
    return data.astype(np.int16)


def _int16_to_float32(data: np.ndarray) -> np.ndarray:
    amp = 10000.0  # default amp for .DFB
    data = data.astype(np.float32)
    max_data = np.abs(data).max()
    min_data = np.abs(data).min()
    data = (data - min_data) / (max_data - min_data) * amp
    return data


def _int16_to_float64(data: np.ndarray) -> np.ndarray:
    amp = 10000.0  # default amp for .DDB
    data = data.astype(np.float64)
    max_data = np.abs(data).max()
    min_data = np.abs(data).min()
    data = (data - min_data) / (max_data - min_data) * amp
    return data
