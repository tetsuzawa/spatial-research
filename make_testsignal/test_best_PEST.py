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

    def PF(X: float, M: float, S: float) -> float:
        pf = 1 / (1 + np.exp(-W(X, M, S)))
        return pf

    def W(X: float, M: float, S: float) -> float:
        return (X - M) / S

    def inv_PF(Y: float, M: float, S: float) -> float:
        return M + 2 * S * np.log(Y)

    r = range(1, 50)
    mock_x = list(r)
    mock_y = list(map(PF, map(float, r), np.full(50, M), np.full(50, S)))

    for i in r:
        if i == 1:
            X = 50
        elif i == 2:
            X = 1
        else:
            X = bp.M

        is_correct = np.random.rand() < PF(X, M, S)
        bp.update(is_correct, X)

    Y = 0.75
    print(f"mockの閾値 y=0,75に対するxの値は x={inv_PF(Y, M, S)}")
    print(f"Best-PESTの閾値 y=0,75に対するxの値は x={inv_PF(Y, bp.M, bp.S)}")

    y = list(map(PF, map(float, r), np.full(50, bp.M), np.full(50, bp.S)))

    plt.plot(mock_x, mock_y, "r--")
    plt.plot(mock_x, y, "b--")
    plt.show()


if __name__ == '__main__':
    main()
