"""Smoke test: headline numbers in the paper follow from the published Cepeda et al. (2008) parameters.

Independent re-implementation of the model, so it does not share code with the analysis scripts.

    python test_model.py
"""
import numpy as np
from scipy.optimize import minimize_scalar

b, p, a, c, d = 0.011, 0.760, 0.017, 0.092, 3.453


def recall(t, g):
    A = p + (1 - p) * np.exp(-a * g)
    R = 1 + c * (np.log(g + 1) - d) ** 2
    return A * (b * t + 1) ** (-R)


def rar(t):
    res = minimize_scalar(lambda g: -recall(t, g), bounds=(0, 500), method="bounded",
                          options={"xatol": 1e-10})
    return recall(t, res.x) / recall(t, 0.0), res.x


if __name__ == "__main__":
    assert abs(recall(0, 0.0) - 1.0) < 1e-12                         # A(0) = 1
    assert abs((1 + c * d**2) - 2.0969) < 5e-5                       # R(0)
    assert abs(np.exp(d) - 1 - 30.6) < 0.1                           # g*
    expected = {1: 1.00, 7: 1.04, 30: 1.28, 365: 5.35}
    for t, want in expected.items():
        got, _ = rar(t)
        assert abs(got - want) < 0.005, f"R({t}d) = {got:.4f}, expected {want}"
    ts = np.arange(1, 3651)
    vals = np.array([rar(t)[0] for t in ts[::10]])
    assert np.all(np.diff(vals) > 0), "R(t) not monotone"
    print("OK: R(1d)=1.00, R(1wk)=1.04, R(1mo)=1.28, R(1yr)=5.35; monotone on [1, 3650] days")
