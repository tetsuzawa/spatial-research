from typing import List, Callable

import numpy as np
import scipy.optimize


class HighestPosteriorDensityInterval:
    """事後最高密度区間（HDI）を表すクラス"""

    def __init__(self, lower_bound: float, upper_bound: float):
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound

    @property
    def lower_bound(self):
        return self._lower_bound

    @property
    def upper_bound(self):
        return self._upper_bound

    @staticmethod
    def calculate(distribution: "RealDistribution", alpha=0.05) -> "HighestPosteriorDensityInterval":
        solver = Solver(distribution, alpha)
        lower_bound = solver.solve()
        upper_bound = solver.offset(lower_bound)
        return HighestPosteriorDensityInterval(lower_bound, upper_bound)

    def tolist(self):
        return [self.lower_bound, self.upper_bound]

    def __str__(self):
        return str(self.tolist())


class Solver:
    """一変数関数の最適化問題を解くクラス"""

    def __init__(self, distribution: "RealDistribution", alpha: float):
        self.distribution = distribution
        self.alpha = alpha

    def solve(self) -> float:
        fn = self._generate_objective_func()
        result = scipy.optimize.minimize_scalar(fn,
                                                bounds=(self.distribution.coords[0],
                                                        self.distribution.coords[-1]),
                                                method='bounded')
        return result.x

    def offset(self, x: float) -> float:
        q = self.distribution.cumulative_probability(x)
        return self.distribution.inverse_cumulative_probability(min([q + 1 - self.alpha, 1]))

    def _generate_objective_func(self) -> Callable[[float], float]:
        def objective_func(x: float) -> float:
            y = self.offset(x)
            d1 = self.distribution.density(y) - self.distribution.density(x)
            d2 = (self.distribution.cumulative_probability(y) - self.distribution.cumulative_probability(x)) - (
                    1 - self.alpha)
            return d1 * d1 + d2 * d2

        return objective_func


class RealDistribution:
    """確率分布を表すクラス"""

    def __init__(self, coords: List[float], distribution: List[float]):
        """length of coords and distribution must be same"""
        if len(coords) != len(distribution):
            raise ValueError("length of coords and distribution must be same")

        self._coords = coords
        self._distribution = distribution

    @property
    def coords(self):
        return self._coords

    @property
    def distribution(self):
        return self._distribution

    def density(self, x: float) -> float:
        if x < self.coords[0] or self.coords[-1] < x:
            raise ValueError(f"x must be in [{self.coords[0]}, {self.coords[-1]}]")
        adjust_val = abs(self.coords[1] - self.coords[0]) / 2
        diff = np.asarray(self.coords) - (x + adjust_val)
        idx = np.abs(diff).argmin()
        return self.distribution[idx]

    def cumulative_probability(self, x: float) -> float:
        if x < self.coords[0] or self.coords[-1] < x:
            raise ValueError(f"x must be in [{self.coords[0]}, {self.coords[-1]}]")
        # idx = np.abs(np.asarray(self.coords) - x).argmin()
        adjust_val = abs(self.coords[1] - self.coords[0]) / 2
        diff = np.asarray(self.coords) - (x + adjust_val)
        idx = np.abs(diff).argmin()
        return sum(self.distribution[:idx])

    def inverse_cumulative_probability(self, p: float) -> float:
        if p < 0 or 1 < p:
            raise ValueError(f"p must be in [0, 1]")

        cdf = [self.cumulative_probability(x) for x in self.coords]
        idx = np.abs(np.asarray(cdf) - p).argmin()
        return self.coords[idx]

    def __len__(self):
        return len(self.distribution)
