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
    この実験におけるパラメータ最適化問題は統計学におけるロジスティック回帰と同意の問題である。
    参考:
        津村尚志 "最近の聴覚心理実験における新しい測定法"
        Qiita   "多変量解析の超基本！知られざるロジスティック回帰分析のアルゴリズム導出"
                https://qiita.com/NaoyaOura/items/6ad5142b0306476d9293

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
    Y: float
        正答率 = C/T
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
        self.Y = 0
        self.M = 40
        self.S = 10
        self._B = np.array([-self.M / self.S, 1 / self.S], dtype=float)
        self.gradient_vec = np.zeros(shape=2, dtype=np.float)
        self.hessian_mat = np.zeros(shape=(2, 2), dtype=np.float)

    @staticmethod
    def PF(X: float, M: float, S: float) -> float:
        """
        PF: Psychometric Function
        移動音の方向弁別の実験結果がロジスティックス曲線なると仮定した心理測定関数

        Parameters
        ----------
        X: float
            刺激レベル（移動角度や移動速度など）
        M: float
            曲線の中点。最尤法によってXをMに近づけていく。
        S: float
            曲線の広がり。通常は定数で演算。

        Returns
        -------
        PF(X; M,S): float
            心理測定関数の計算結果
        """

        def _W(X: float, M: float, S: float) -> float:
            return (X - M) / S

        pf = 1 / (1 + np.exp(-_W(X, M, S)))
        return pf

    @staticmethod
    def PF_inv(Y: float, M: float, S: float) -> float:
        """
        PF_inv: Inverse Psychometric Function
        PFの逆関数。
        閾値を求めるときに使う。

        Parameters
        ----------
        Y: float
            弁別正答確率。y=PF(X;M,S)。
        M: float
            曲線の中点。最尤法によってXをMに近づけていく。
        S: float
            曲線の広がり。通常は定数で演算。

        Returns
        -------
        X: float
            刺激レベル（移動角度や移動速度など）
        """

        pf_inv = M + 2 * S * np.log(Y)
        return pf_inv

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

    def _L_B0(self) -> float:
        """
        B0によるLの偏微分
        """
        return - (self.likelihood - self.Y)

    def _L_B1(self, X: float) -> float:
        """
        B1によるLの偏微分
        """
        return - (self.likelihood - self.Y) * X

    def _L_B0B0(self) -> float:
        """
        B0によるLの2階偏微分
        """
        return self.likelihood * (1 - self.likelihood)

    def _L_B0B1(self, X: float) -> float:
        """
        B0とB1によるLの2階偏微分
        L_B1B0と等しい
        """
        return self.likelihood * (1 - self.likelihood) * X

    def _L_B1B0(self, X: float) -> float:
        """
        B1とB0によるLの2階偏微分
        L_B0B1と等しい
        """
        return self._L_B0B1(X)

    def _L_B1B1(self, X: float) -> float:
        """
        B1によるLの2階偏微分
        """
        return self.likelihood * (1 - self.likelihood) * X * X

    def update(self, is_correct: bool, X: float):
        """
        Best-PEST法のパラメータを更新する関数

        Parameters
        ----------
        is_correct: bool
            回答が正解か否か
        X: float
            刺激レベル（移動角度や移動速度など）
        """
        self.k += 1
        self.T += 1
        if is_correct:
            self.C += 1
        self.Y = self.C / self.T
        for _ in range(100):
            self.likelihood = self.PF(X, self.M, self.S)
            # self.gradient_vec += np.array([self._L_M(), self._L_S(X)])
            # self.hessian_mat += np.array([[self._L_MM(), self._L_MS(X)],
            #                               [self._L_MS(X), self._L_SS(X)]])
            self.gradient_vec = np.array([self._L_B0(), self._L_B1(X)])
            self.hessian_mat = np.array([[self._L_B0B0(), self._L_B0B1(X)],
                                         [self._L_B1B0(X), self._L_B1B1(X)]])
            dB = np.linalg.pinv(self.hessian_mat) @ self.gradient_vec.T
            # print("B:", self._B)
            self._B += dB
            # print("B:", self._B)
            # print(f"MMMM:{self.M}, SSSS:{self.S}")
            self.M = - self._B[0] / self._B[1]
            self.S = 1 / self._B[1]
            print(f"MMMM:{self.M}, SSSS:{self.S}")
        # Debug
        # print("X:", X)
        # print("C:", self.C)
        # print("T:", self.T)
        # print("Y:", self.Y)
        # print("likelihood:", self.likelihood)
        # print("B:", self._B)
        # print("gradient_vec:", self.gradient_vec)
        # print("hessan_mat:", self.hessian_mat)
        # print("dB:", dB)
        # print("plused B:", self._B)
        # print("\n\n")

# パーセプトロンは無理（入力がM, S）になってるから。本当はXからM，Sを推定しないといけない
# def update_perceptron(self, is_correct: bool, X: float, M: float, S: float):
#     # data = np.loadtxt('logistic2.csv', delimiter=',', skiprows=1)  # 学習データ読み込み
#     # x = data[:, 0:2]  # x1,x2データ
#     # t = data[:, 2]  # 分類を示すラベル
#     self.x = np.append(self.x, [[X / S, -M / S]], axis=0)
#     if is_correct:
#         np.append(self.t, [[1]], axis=0)
#     else:
#         np.append(self.t, [[0]], axis=0)
#     stdized_x = (self.x - self.x.mean(axis=0)) / self.x.std(axis=0)  # 標準正規化
#     x0 = np.ones([stdized_x.shape[0], 1])  # バイアス項作成
#     # x3 = stdized_x[:, 0, np.newaxis] ** 2  # x1を2乗した項を作成
#
#     # matrix_x = np.hstack([x0, stdized_x, x3])  # 1, x1, x2, x1^2の順
#     matrix_x = np.hstack([x0, stdized_x])  # 1, X/S, -M/S,
#     w = np.random.rand(4)  # 重み初期化
#     rate = 0.01  # 学習率
#     loop = 200000  # 更新回数
#
#     # 重み更新
#     for i in range(loop):
#         sig = 1 / (1 + np.exp(-np.dot(matrix_x, w)))  # シグモイド関数
#         w += rate * np.dot((t - sig) * sig * (1 - sig), matrix_x)  # 重み更新
#
#     print(round(-w[0] / w[2], 2), ',', round(-w[1] / w[2], 2), ',', round(-w[3] / w[2], 2))  # 重み最終値
#
#     # 描画
#     x_axis = np.linspace(start=-2, stop=1.5, num=100)
#     plt.plot(stdized_x[t == 1, 0], stdized_x[t == 1, 1], '^')  # ラベルが1のデータプロット
#     plt.plot(stdized_x[t != 1, 0], stdized_x[t != 1, 1], 'o')  # ラベルが1以外のデータプロット
#     plt.plot(x_axis, -(w[0] + w[1] * x_axis + w[3] * x_axis ** 2) / w[2])  # 境界線プロット
#     plt.grid(True)
#     plt.show()
