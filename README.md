# The Retention Advantage Ratio

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23484598.svg)](https://doi.org/10.5281/zenodo.23484598)

Code and manuscript for:

> Wish, M. J. (2026). *The Retention Advantage Ratio: A Time-Indexed Framework for Evaluating Distributed Practice Efficiency* (Version 1.1) [Preprint]. Zenodo. https://doi.org/10.5281/zenodo.23484598

Preprint, not peer reviewed. The PDF is `retention-advantage-ratio-preprint.pdf`.

---

## Overview

The paper treats the ratio R(t) = P_distributed(t) / P_blocked(t) as a function of retention interval and analyzes it on the log scale. Under a power law of forgetting with a shared time scale, the log-ratio splits exactly into an initial-strength term (constant) and a decay-rate term that grows linearly in ln(1 + αt). The framework is applied to the retention surface fitted by Cepeda et al. (2008), including where that application fails.

All model values are computed from the published parameters; no data are digitized.

**Model source:** Cepeda, N. J., Vul, E., Rohrer, D., Wixted, J. T., & Pashler, H. (2008). Spacing effects in learning: A temporal ridgeline of optimal retention. *Psychological Science*, 19, 1095–1102. https://doi.org/10.1111/j.1467-9280.2008.02209.x

| Parameter | Value | Role |
|-----------|-------|------|
| b | 0.011 | Shared temporal scaling |
| p | 0.760 | Asymptote of initial recall as gap grows |
| a | 0.017 | Rate at which initial recall falls with gap |
| c | 0.092 | Curvature of the decay-rate function |
| d | 3.453 | Log-gap at which decay is slowest (gap ≈ 30.6 days) |

---

## Key results

| Retention interval | Model R(t) | Data-implied R(t) |
|---|---|---|
| 7 days | 1.04 | 1.10 |
| 35 days | 1.34 | 1.59 |
| 70 days | 1.73 | 2.11 |
| 350 days | 5.16 | 1.77 |

Data-implied values come from the improvements Cepeda et al. (2008) report for the best tested gap (10%, 59%, 111%, 77%).

**Caveat.** Model and data agree through 70 days. At 350 days the model ratio is about three times the data, because the model's massed-practice recall there is 0.036 and small errors in a near-floor denominator inflate the ratio. Long-delay model ratios are not empirical estimates.

---

## Repository structure

```
.
├── main_rebuilt.tex                       # LaTeX manuscript
├── retention-advantage-ratio-preprint.pdf # Compiled manuscript
├── generate_figures.py                    # Figures 1-5 (PDF)
├── compute_Rt_analytical.py               # R(t) computation with diagnostics
├── test_model.py                          # Independent check of the paper's numbers
├── requirements.txt                       # Pinned Python dependencies
├── CITATION.cff                           # Citation metadata (used by Zenodo)
├── LICENSE                                # MIT (code)
└── README.md
```

---

## Reproducing

```bash
pip install -r requirements.txt
python test_model.py          # checks every computed number in the paper
python generate_figures.py    # writes figure1_crossover.pdf ... figure5_log_decomposition.pdf
pdflatex main_rebuilt.tex && pdflatex main_rebuilt.tex
```

The pinned versions are those used for the original preprint; the scripts also run on current numpy, scipy, and matplotlib. Figures must be generated before compiling the manuscript.

---

## Versions

- **v1.1.0** (October 2026): log-ratio reframing; corrected crossover formula, citations, DOIs, and the Bahrick and Phelps cost adjustment; long-delay model values qualified. The manuscript ends with a full list of changes.
- **v1.0.1** (October 2026): first Zenodo archive of the original preprint.
- **v1.0-preprint**: original manuscript as first submitted.

---

## License

Code: MIT License.
Manuscript text and figures: © Michael J. Wish, released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
