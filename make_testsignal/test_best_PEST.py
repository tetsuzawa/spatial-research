# import unittest
#
import numpy as np
import matplotlib.pyplot as plt

from best_PEST import BestPEST


# class TestBestPEST(unittest.TestCase):


def main():
    bp = BestPEST()

    M = 20
    S = 1
    r = range(1, 50)
    mock_x = list(r)
    mock_y = list(map(BestPEST.PF, map(float, r), np.full(50, M), np.full(50, S)))

    for i in r:
        if i == 1:
            X = 50
        elif i == 2:
            X = 1
        else:
            X = bp.M

        print(f"M:{bp.M}, S:{bp.S}")
        is_correct = np.random.rand() < BestPEST.PF(X, M, S)
        bp.update(is_correct, X)

    Y = 0.75
    print(f"mockの閾値 y=0.75に対するxの値は x={BestPEST.PF_inv(Y, M, S)}")
    print(f"Best-PESTの閾値 y=0.75に対するxの値は x={BestPEST.PF_inv(Y, bp.M, bp.S)}")
    print(f"Best-PESTの回答数: {bp.T}, 正答数: {bp.C}, 正答率: {bp.C / bp.T*100:3.1f}%")

    y = list(map(BestPEST.PF, map(float, r), np.full(50, bp.M), np.full(50, bp.S)))

    plt.plot(mock_x, mock_y, "r--")
    plt.plot(mock_x, y, "b--")
    plt.show()


if __name__ == '__main__':
    main()
