"""Smoke test: the numbers reported in the paper follow from the published Cepeda et al. (2008) parameters.

Independent re-implementation of the model, so it does not share code with the analysis scripts.

    python test_model.py
"""
import numpy as np
from scipy.optimize import minimize_scalar

b, p, a, c, d = 0.011, 0.760, 0.017, 0.092, 3.453


def A(g):
    return p + (1 - p) * np.exp(-a * g)


def Rg(g):
    return 1 + c * (np.log(g + 1) - d) ** 2


def recall(t, g):
    return A(g) * (b * t + 1) ** (-Rg(g))


def opt_gap(t):
    res = minimize_scalar(lambda g: -recall(t, g), bounds=(0, 500), method="bounded",
                          options={"xatol": 1e-10})
    return res.x


def ratio(t):
    return recall(t, opt_gap(t)) / recall(t, 0.0)


def crossover(g):
    """Delay at which fixed gap g overtakes massed practice (Eq. 4 with m_d/m_b = A(g))."""
    return (A(g) ** (-1 / (Rg(0) - Rg(g))) - 1) / b


if __name__ == "__main__":
    # Model structure
    assert abs(A(0) - 1.0) < 1e-12
    assert abs(Rg(0) - 2.0969) < 5e-5
    assert abs(np.exp(d) - 1 - 30.6) < 0.1

    # Table 2 values (optimal-gap ratio)
    expected = {7: 1.04, 14: 1.11, 30: 1.28, 35: 1.34, 70: 1.73, 90: 1.96, 180: 3.03, 350: 5.16}
    for t, want in expected.items():
        got = ratio(t)
        assert abs(got - want) < 0.006, f"R({t}d) = {got:.4f}, expected {want}"

    # Log-ratio decomposition is exact: ln R = ln A(g*) + [R(0) - R(g*)] ln(1 + b t)
    for t in [7, 35, 70, 350]:
        g = opt_gap(t)
        lhs = np.log(ratio(t))
        rhs = np.log(A(g)) + (Rg(0) - Rg(g)) * np.log(1 + b * t)
        assert abs(lhs - rhs) < 1e-10

    # Table 1 crossover delays
    for g, want in {1: 0.9, 7: 2.7, 21: 6.5, 30.6: 8.9, 105: 23.7}.items():
        assert abs(crossover(g) - want) < 0.06, (g, crossover(g))

    # Illustrative crossover in Figure 1: t* = (1/alpha)[(m_b/m_d)^(1/dlam) - 1]
    t_star = (1 / 0.15) * ((0.92 / 0.78) ** (1 / (0.42 - 0.18)) - 1)
    assert abs(t_star - 6.6) < 0.05

    # Monotone on [1, 3650] days
    vals = np.array([ratio(t) for t in np.arange(1, 3651, 10)])
    assert np.all(np.diff(vals) > 0), "R(t) not monotone"

    # Bahrick & Phelps (1987) cost adjustment: presentations 3.0 (zero interval) vs 5.5 (30-day)
    assert abs((3.0 / 5.5) * (0.15 / 0.06) - 1.36) < 0.005

    print("OK: Table 1 and Table 2 values, exact log-ratio decomposition, crossovers, "
          "monotonicity, and cost adjustment all reproduce")
