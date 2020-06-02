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
format_specifiers = ["%d", "%e", "%e"]


class BadDataStyleError(Exception):
    """ファイル形式が適切でないことを知らせる例外クラス"""
    pass


def style(name: str):
    """ファイルの拡張子を確認する関数。拡張子が不適切であれば例外を発生させる。"""
    name_ext = os.path.splitext(name)[1]

    if not name_ext in exts:
        raise BadDataStyleError(f"ファイルの拡張子が不適切です。 want: {exts}, got: {name_ext}")

    return exts.index(name_ext)


def len_file(name: str) -> int:
    """データの長さを確認する関数

    example:
        num_sample = len_file("example.DSB")
    """
    data = read_DXX_file(name)
    return len(data)


def read_DXX_file(name: str) -> np.ndarray:
    """.DXXファイルを読み込む関数

    example:
        data = read_DXX_file("example.DSB")
    """

    index = style(name)

    # DXAファイル（アスキー文字列）
    if index < 3:
        with open(name, "r") as f:
            data = np.fromfile(f, dtypes[index], -1)
        return data

    # DXBファイル（バイナリ）
    else:
        with open(name, "rb") as f:
            data = np.fromfile(f, dtypes[index], -1)
        return data


def write_DXX_file(name: str, data: np.ndarray):
    """.DXXファイルを書き込む関数

    example:
        write_DXX_file("example.DDB", data)
    """

    index = style(name)

    if data.dtype != dtypes[index]:
        raise BadDataStyleError(f"データの型が拡張子と一致していません。 want: {dtypes[index]}, got: {data.dtype}")

    # DXAファイル（アスキー文字列）
    if index < 3:
        # 改行区切りで保存
        data.tofile(name, sep="\n", format=format_specifiers[index])

    # DXBファイル（バイナリ）
    else:
        data.tofile(name)
