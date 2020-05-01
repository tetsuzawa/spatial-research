# import unittest
#
import numpy as np
import matplotlib.pyplot as plt

from best_PEST import BestPEST


# class TestBestPEST(unittest.TestCase):


def main():
    bp = BestPEST()

    M = 20
    S = 3
    r = range(1, 51)
    mock_x = list(r)
    mock_y = list(map(BestPEST.PF, map(float, r), np.full(50, M), np.full(50, S)))

    for i in range(1, 100):
        if i == 1:
            X = 50
        elif i == 2:
            X = 1
        else:
            X = bp.M

        if X < 1:
            X = 1
        elif 50 < X:
            X = 50

        is_correct = np.random.rand() < BestPEST.PF(X, M, S)
        # is_correct = BestPEST.PF(X, bp.M, bp.S) < BestPEST.PF(X, M, S)
        print(f"i:{i},\t X:{X:.3f},\t Y:{BestPEST.PF(X, bp.M, bp.S):.3f},\t mockY:{BestPEST.PF(X, M,S):.3f},\t M:{bp.M:.3f},\t S:{bp.S:.3f},\t is_correct:{is_correct}")
        bp.update(is_correct, X)
        mock_tmp_y = list(map(BestPEST.PF, map(float, r), np.full(50, bp.M), np.full(50, bp.S)))
        plt.plot(mock_x, mock_tmp_y)

    Y = 0.75
    print(f"mockの閾値 y=0.75に対するxの値は x={BestPEST.PF_inv(Y, M, S)}")
    print(f"Best-PESTの閾値 y=0.75に対するxの値は x={BestPEST.PF_inv(Y, bp.M, bp.S)}")
    print(f"Best-PESTの回答数: {bp.T}, 正答数: {bp.C}, 正答率: {bp.C / bp.T * 100:3.1f}%")

    # m31s7_8_y = list(map(BestPEST.PF, map(float, r), np.full(50, 31.4), np.full(50, 7.85)))
    # m40s7_10_y = list(map(BestPEST.PF, map(float, r), np.full(50, 40), np.full(50, 10)))
    y = list(map(BestPEST.PF, map(float, r), np.full(50, bp.M), np.full(50, bp.S)))

    plt.plot(mock_x, mock_y, "r--")
    # plt.plot(mock_x, m31s7_8_y, "y--")
    # plt.plot(mock_x, m40s7_10_y, "g--")
    plt.plot(mock_x, y, "b--")
    plt.show()


if __name__ == '__main__':
    main1()
