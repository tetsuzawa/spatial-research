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
    data = read(filename)
    return len(data)


def read(filename: str) -> np.ndarray:
    """.DXXファイルを読み込む関数

    example:
        import dxx
        data = dxx.read_DXX_file("example.DSB")
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
        dxx.write_DXX_file("example.DDB", data)
    """

    index = _style(filename)

    if data.dtype != dtypes[index]:
        raise BadDataStyleError(f"データの型が拡張子と一致していません。 want: {dtypes[index]}, got: {data.dtype}")

    # DXAファイル（アスキー文字列）
    if index < 3:
        # 改行区切りで保存
        data.tofile(filename, sep="\n", format=_format_specifiers[index])

    # DXBファイル（バイナリ）
    else:
        data.tofile(filename)
