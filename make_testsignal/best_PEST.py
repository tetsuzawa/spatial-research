#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ##################################################
# Best-PEST法（最尤法）を用いた移動音の方向弁別の閾値推定
#
# 作成者:瀧澤哲
# 作成年:2020
# ##################################################

import numpy as np


class BestPEST:
    """
    Best-PEST法による移動音の方向弁別実験のためのクラス。

    Attributes
    ----------
    k: int
        試行回数
    likelihood: float
        尤度
    T: int
        回答数 = 試行回数
    C: int
        正解数
    M: float
        曲線の中点。最尤法によってXをMに近づけていく。
    S: float
        曲線の広がり。通常は定数で演算。
    gradient_vec: Tuple[float, float]
        勾配ベクトル
    hessian_mat: Tuple[[float, float], [float, float]]
        ヘッシアン行列
    """

    def __init__(self):
        self.k = 0
        self.likelihood = 0
        self.T = 0
        self.C = 0
        self.M = 0.0
        self.S = 0.0
        self.gradient_vec = np.zeros(shape=2, dtype=np.float)
        self.hessian_mat = np.zeros(shape=(2, 2), dtype=np.float)

    def _PF(self, X: float) -> float:
        """
        PF: Psychometric Function
        移動音の方向弁別の実験結果がロジスティックス曲線なると仮定した心理測定関数
        参考: 津村尚志 "最近の聴覚心理実験における新しい測定法"

        Parameters
        ----------
        X: float
            刺激レベル（移動角度や移動速度など）

        Returns
        -------
        PF(X; M,S): float
            心理測定関数の計算結果
        """

        pf = 1 / (1 + np.exp((self.M - X) / self.S))
        return pf

    def _W_M(self) -> float:
        """
        MによるWの偏微分
        """
        return - 1 / self.S

    def _W_S(self, X: float) -> float:
        """
        SによるWの偏微分
        """
        return - 1 * (X - self.M) / self.S ** 2

    def _W_MM(self) -> float:
        """
        MによるのW2階偏微分
        値は0
        混乱を防ぐため定義した
        """
        return 0

    def _W_MS(self) -> float:
        """
        Wの2階偏微分
        W_SMと等しい
        """
        return 1 / self.S ** 2

    def _W_SS(self, X: float) -> float:
        """
        SによるWの2階偏微分
        """
        return 2 * (X - self.M) / self.S ** 3

    def _L_M(self) -> float:
        """
        MによるLの偏微分
        """
        t1 = self.T * self._W_M() * self.likelihood
        t2 = (self.T - self.C) * - self._W_M()
        return t1 + t2

    def _L_S(self, X: float) -> float:
        """
        SによるLの偏微分
        """
        t1 = self.T * self._W_S(X) * self.likelihood
        t2 = (self.T - self.C) * - self._W_S(X)
        return t1 + t2

    def _L_MM(self) -> float:
        """
        MによるLの2階偏微分
        """
        # 右辺各項
        t1 = 0  # 内部にW_MMが含まれるため
        t2 = self.T * self._W_M() ** 2 * self.likelihood * (1 - self.likelihood)
        t3 = 0  # 内部にW_MMが含まれるため
        return t1 + t2 + t3

    def _L_MS(self, X: float) -> float:
        """
        Lの2階偏微分
        L_SMと等しい
        """
        # 右辺各項
        t1 = self.T * self._W_MS() * self.likelihood
        t2 = self.T * self._W_M() * self._W_S(X) * self.likelihood * (1 - self.likelihood)
        t3 = (self.T - self.C) * -self._W_MS()
        return t1 + t2 + t3

    def _L_SS(self, X: float) -> float:
        """
        SによるLの2階偏微分
        """
        # 右辺各項
        t1 = self.T * self._W_SS(X) * self.likelihood
        t2 = self.T * self._W_S(X) ** 2 * self.likelihood * (1 - self.likelihood)
        t3 = (self.T - self.C) * -self._W_SS(X)
        return t1 + t2 + t3

    def update(self, is_correct: bool, X: float):
        """
        Best-PEST法のパラメータを更新する関数

        Parameters
        ----------
        is_correct: bool
            回答が正解か否か
        X: bool
            刺激レベル（移動角度や移動速度など）
        """
        self.k += 1
        self.T += 1
        if is_correct:
            self.C += 1
        self.likelihood = self._PF(X)
        self.gradient_vec += np.array([self._L_M(), self._L_S(X)])
        self.hessian_mat += np.array([[self._L_MM(), self._L_MS(X)],
                                      [self._L_MS(X), self._L_SS(X)]])
        u = np.array([self.M, self.S]).T - np.linalg.inv(self.hessian_mat) @ self.gradient_vec.T
        self.M, self.S = u
