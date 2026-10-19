# The Retention Advantage Ratio

**Velle Logos Educational Research**

Code and manuscript for:

> Wish, M. (2025). *The Retention Advantage Ratio: A Time-Indexed Framework for Evaluating Distributed Practice Efficiency*. Velle Logos Educational Research.

---

## Overview

This repository contains the complete, reproducible pipeline for the paper. All R(t) values are derived **analytically** from the published fitted parameters of Cepeda et al. (2008)—no data digitization, no raw data access required.

**Model source:** Cepeda, N. J., Vul, E., Rohrer, D., Wixted, J. T., & Pashler, H. (2008). Spacing effects in learning: A temporal ridgeline of optimal retention. *Psychological Science*, 19, 1095–1102. https://doi.org/10.1111/j.1467-9280.2008.02209.x

**Published parameters used (Figure 4 of Cepeda et al., 2008):**

| Parameter | Value | Role |
|-----------|-------|------|
| b | 0.011 | Shared temporal scaling |
| p | 0.760 | Permastore asymptote |
| a | 0.017 | Gap-strength decay |
| c | 0.092 | Decay-rate curvature |
| d | 3.453 | Optimal decay-rate gap (log scale) |

---

## Repository Structure

```
.
├── main_rebuilt.tex          # LaTeX manuscript (two-column journal format)
├── generate_figures.py       # Generates all 4 figures (PDF output)
├── compute_Rt_analytical.py  # Standalone R(t) computation with diagnostics
├── test_model.py             # Smoke test: independent check of headline numbers
├── requirements.txt          # Pinned Python dependencies
├── CITATION.cff              # Citation metadata (used by Zenodo)
├── LICENSE                   # MIT (code)
└── README.md                 # This file
```

---

## Reproducing the Figures

### Setup

```bash
pip install -r requirements.txt
```

The pinned versions are those used for the preprint. The scripts were also verified on newer numpy, scipy and matplotlib. Check the numbers with `python test_model.py`.

### Generate all figures

```bash
python generate_figures.py
```

This produces four PDF files in the working directory:

| File | Figure | Description |
|------|--------|-------------|
| `figure1_crossover.pdf` | Fig. 1 | Illustrative retention crossover under power law |
| `figure2_model_surface.pdf` | Fig. 2 | Model-predicted recall as a function of spacing gap |
| `figure3_Rt_analytical.pdf` | Fig. 3 | R(t) derived analytically from Cepeda et al. (2008) |
| `figure4_model_vs_data.pdf` | Fig. 4 | Model-derived vs. data-implied R(t) |

It also prints two tables to stdout:
- R(t) at key retention intervals (1 day through 1 year)
- Comparison of model-derived vs. paper-stated percentage improvements

### Diagnostic script

```bash
python compute_Rt_analytical.py
```

Runs full diagnostics: verifies model structure (A(0) = 1.0, R(g) minimum at g* = exp(d)−1 ≈ 30.6 days), checks monotonicity over [1, 3650] days, fits sqrt/log/power approximations to R(t), and saves PNG versions of the figures.

---

## Compiling the Manuscript

```bash
pdflatex main_rebuilt.tex
pdflatex main_rebuilt.tex  # run twice for cross-references
```

Figures must be generated first (see above). The `.tex` file references `figure1_crossover.pdf` through `figure4_model_vs_data.pdf` by filename in the working directory.

**Requirements:** A standard TeX distribution (TeX Live, MiKTeX, or MacTeX) with the following packages: `amsmath`, `amssymb`, `graphicx`, `booktabs`, `hyperref`, `geometry`, `titlesec`.

---

## Key Analytical Results

| Retention Interval | Optimal Gap (days) | Massed Recall | Optimal Recall | R(t) |
|---|---|---|---|---|
| 1 day | 0.5 | 0.977 | 0.978 | 1.00 |
| 1 week | 5.0 | 0.856 | 0.893 | 1.04 |
| 1 month | 12.2 | 0.550 | 0.704 | 1.28 |
| 3 months | 18.4 | 0.236 | 0.463 | 1.96 |
| 6 months | 21.5 | 0.101 | 0.307 | 3.03 |
| 1 year | 23.7 | 0.034 | 0.182 | 5.35 |

All values computed via continuous optimization over g ∈ [0, 500] days.

---

## Caveat

R(1 year) = 5.35 is a model extrapolation. At 350 days the fitted surface overpredicts the ratio implied by the Cepeda et al. data (about 1.77), largely because of floor effects in the data. Read the long-horizon values as model-implied, not observed.

---

## Preprint Version

The commit tagged `v1.0-preprint` corresponds exactly to the submitted preprint. To reproduce that version:

```bash
git checkout v1.0-preprint
```

---

## License

Code: MIT License  
Manuscript text: © Michael Wish, Velle Logos Educational Research. All rights reserved pending peer review.
