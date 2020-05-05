#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ##################################################
# PEST法を用いた移動音の方向弁別の閾値推定
#
# 作成者:瀧澤哲
# 作成年:2020
# ##################################################

import numpy as np


class PEST:
    _lower = False
    _upper = True

    def __init__(self, initial_dx=16, min_dx=1, Pt=0.75, W=1.0):
        self.pre_stimulation_level_direction = self._lower  # lower:False or upper:True
        self.repeated_num = 1  # 連続で同じ回答が繰り返された回数。最小値:1,
        self.dx = initial_dx  # 刺激変化幅。
        self.min_dx = min_dx  # 最小刺激変化幅。刺激幅dxが最小刺激幅min_dxとなったときに実験を終了する。
        self.doubled_dx = False
        self.switched_direction_by_doubled_dx = False
        self.T = 0  # 回答数
        self.C = 0  # 正答数
        self.W = W  # deviation limit. 1.0 <= W <= 2.0
        self.Xt = 0  # 刺激レベルの目標値Xt。これを求める。
        self.Pt = Pt  # 刺激レベルの目標値Ltに対する特定応答の出現率。閾値。強制選択法（2IFC）なら0.75, Yes/No法なら0.5。

    def update(self, is_correct, X: int) -> int:
        self.T += 1
        if is_correct:
            self.C += 1

        W = self.W
        I = self.Pt * self.T - self.C

        if np.abs(I) < W:
            self.Xt = X
            return self.Xt
        elif I <= -W:
            direction = self._lower
        elif I >= W:
            direction = self._upper
        else:
            raise ArithmeticError("Unknown arithmetic error occurred")

        self.find_dx(direction)
        self.pre_stimulation_level_direction = direction
        self.Xt = X + self.dx
        return self.Xt

    def find_dx(self, stimulation_level_direction: bool):
        # (1) 前回との刺激レベルの変化方向を比較
        if stimulation_level_direction != self.pre_stimulation_level_direction:
            if self.doubled_dx:
                self.switched_direction_by_doubled_dx = True
            self.repeated_num = 1
            self.dx = int(self.dx / 2)

        else:
            self.repeated_num += 1
            # (2)
            if self.repeated_num == 2:
                # self.dx = self.dx  # プログラム的に無駄なのでコメントアウト
                self.doubled_dx = False
            # (3)
            elif self.repeated_num >= 4:
                self.dx = 2 * self.repeated_num
                self.doubled_dx = True
            # (4)
            elif self.repeated_num == 3:
                if self.switched_direction_by_doubled_dx:
                    # self.dx = self.dx  # プログラム的に無駄なのでコメントアウト
                    self.doubled_dx = False
                else:
                    self.dx = 2 * self.repeated_num
                    self.doubled_dx = False

    def has_ended(self) -> bool:
        return self.dx == self.min_dx
