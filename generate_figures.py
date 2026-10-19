#!/usr/bin/env python3
"""
Generate all figures for the rebuilt retention advantage paper.

All R(t) values are computed analytically from Cepeda et al. (2008)
published model parameters. No digitized data.

Model:
    recall(t, g) = A(g) * (b*t + 1)^{-R(g)}
    A(g) = p + (1-p) * exp(-a*g)
    R(g) = 1 + c * [ln(g+1) - d]^2

Published parameters:
    b = 0.011, p = 0.760, a = 0.017, c = 0.092, d = 3.453
"""

import numpy as np
from scipy.optimize import minimize_scalar, curve_fit
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# =====================================================================
# GLOBAL STYLE
# =====================================================================
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'legend.fontsize': 10,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.spines.top': False,
    'axes.spines.right': False,
})

C_BLOCK = '#D64545'
C_DIST  = '#3B82C4'
C_MODEL = '#3D6B35'
C_DATA  = '#5B4FA0'

# =====================================================================
# CEPEDA et al. (2008) MODEL
# =====================================================================
B_PAR = 0.011
P_PAR = 0.760
A_PAR = 0.017
C_PAR = 0.092
D_PAR = 3.453

def A_func(g):
    return P_PAR + (1 - P_PAR) * np.exp(-A_PAR * g)

def R_func(g):
    return 1 + C_PAR * (np.log(g + 1) - D_PAR)**2

def recall(t, g):
    return A_func(g) * (B_PAR * t + 1)**(-R_func(g))

def optimal_recall(t, g_max=500):
    result = minimize_scalar(lambda g: -recall(t, g),
                             bounds=(0, g_max), method='bounded')
    return result.x, -result.fun

def R_ratio(t):
    """Retention advantage ratio: optimal-gap recall / massed recall."""
    _, rec_opt = optimal_recall(t)
    rec_massed = recall(t, 0)
    return rec_opt / rec_massed

# =====================================================================
# PRECOMPUTE R(t) CURVE
# =====================================================================
t_curve = np.logspace(np.log10(1), np.log10(3650), 1000)
Rt_curve = np.array([R_ratio(t) for t in t_curve])
gopt_curve = np.array([optimal_recall(t)[0] for t in t_curve])

# Key milestones
milestones_days = [1, 7, 14, 30, 60, 90, 180, 365]
milestones_labels = ['1 day', '1 week', '2 weeks', '1 month',
                     '2 months', '3 months', '6 months', '1 year']
Rt_milestones = np.array([R_ratio(t) for t in milestones_days])
gopt_milestones = np.array([optimal_recall(t)[0] for t in milestones_days])

# Paper's test delays
t_paper = np.array([7, 35, 70, 350])
Rt_paper = np.array([R_ratio(t) for t in t_paper])

# Paper's stated improvements (from text, not digitized)
paper_improvements = np.array([1.10, 1.59, 2.11, 1.77])

# =====================================================================
# FIGURE 1: CROSSOVER (illustrative, same parameters as before)
# =====================================================================
def power_law(t, m, alpha, lam):
    return m * (1 + alpha * t)**(-lam)

m_b, alpha_shared, lam_b = 0.92, 0.15, 0.42
m_d, lam_d = 0.78, 0.18

t_cross = np.linspace(0, 75, 500)
P_block = power_law(t_cross, m_b, alpha_shared, lam_b)
P_dist  = power_law(t_cross, m_d, alpha_shared, lam_d)

idx_cross = np.argmin(np.abs(P_block - P_dist))
t_star = t_cross[idx_cross]

fig, ax = plt.subplots(figsize=(7, 5))
ax.fill_between(t_cross[:idx_cross+1],
                P_dist[:idx_cross+1]*100, P_block[:idx_cross+1]*100,
                alpha=0.12, color=C_BLOCK)
ax.fill_between(t_cross[idx_cross:],
                P_block[idx_cross:]*100, P_dist[idx_cross:]*100,
                alpha=0.12, color=C_DIST)
ax.plot(t_cross, P_block*100, color=C_BLOCK, lw=2.5, label='Blocked/Massed')
ax.plot(t_cross, P_dist*100, color=C_DIST, lw=2.5, label='Distributed/Spaced')
ax.plot(t_star, P_block[idx_cross]*100, 'ko', ms=10, zorder=5)
ax.annotate(f'$t^* \\approx {t_star:.1f}$ days',
            xy=(t_star, P_block[idx_cross]*100),
            xytext=(t_star+8, P_block[idx_cross]*100+8),
            fontsize=12, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
ax.text(0.97, 0.05, r'$P(t) = m(1+\alpha t)^{-\lambda}$',
        transform=ax.transAxes, fontsize=12, ha='right', va='bottom',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                  edgecolor='gray', alpha=0.9))
ax.set_xlabel('Retention Interval (days)')
ax.set_ylabel('Recall Probability (%)')
ax.set_title('Retention Crossover: Why Testing Time Matters')
ax.set_ylim(0, 100); ax.set_xlim(0, 75)
ax.legend(loc='upper right', framealpha=0.9)
fig.savefig('figure1_crossover.pdf')
plt.close()


# =====================================================================
# FIGURE 2: MODEL-PREDICTED RECALL SURFACE (from published parameters)
# =====================================================================
gaps_plot = np.linspace(0, 120, 500)
colors_delay = ['#7B2D8E', '#2B5EA7', '#1A9E76', '#6B8E23']

fig, ax = plt.subplots(figsize=(7, 5))
for t_val, color, label in zip([7, 35, 70, 350], colors_delay,
    ['7-day delay', '35-day delay', '70-day delay', '350-day delay']):
    rec = np.array([recall(t_val, g) for g in gaps_plot])
    ax.plot(gaps_plot, rec, color=color, lw=2, label=label)
    # Mark optimal
    g_opt, r_opt = optimal_recall(t_val)
    ax.plot(g_opt, r_opt, 'o', color=color, ms=8, markeredgecolor='white',
            markeredgewidth=1, zorder=5)

ax.set_xlabel('Spacing Gap (days)')
ax.set_ylabel('Predicted Recall Probability')
ax.set_title('Cepeda et al. (2008) Fitted Model\n'
             r'$\mathrm{recall}(t,g) = A(g)\,(bt+1)^{-R(g)}$')
ax.legend(loc='upper right', framealpha=0.9)
ax.set_xlim(0, 120); ax.set_ylim(0, 1.0)
ax.text(0.03, 0.03,
        f'$b = {B_PAR}$, $p = {P_PAR}$, $a = {A_PAR}$\n'
        f'$c = {C_PAR}$, $d = {D_PAR}$',
        transform=ax.transAxes, fontsize=9, va='bottom',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#F5F5F5',
                  edgecolor='gray', alpha=0.9))
fig.savefig('figure2_model_surface.pdf')
plt.close()


# =====================================================================
# FIGURE 3: R(t) FROM ANALYTICAL MODEL (the main figure)
# =====================================================================
fig, ax = plt.subplots(figsize=(7, 5))

# Main curve
ax.plot(t_curve, Rt_curve, color=C_MODEL, lw=3, zorder=2,
        label=r'$\mathcal{R}(t)$ from published model')

# Milestone markers
for t_m, R_m, lab in zip(milestones_days, Rt_milestones, milestones_labels):
    ax.plot(t_m, R_m, 'o', color=C_DATA, ms=8,
            markeredgecolor='black', markeredgewidth=1, zorder=4)

# Annotate select milestones
annotations = [
    (7, Rt_milestones[1], '1 wk', (15, -5)),
    (30, Rt_milestones[3], '1 mo', (15, -5)),
    (90, Rt_milestones[5], '3 mo', (15, 5)),
    (365, Rt_milestones[7], '1 yr', (-35, 10)),
]
for tx, rx, lab, (dx, dy) in annotations:
    ax.annotate(f'{lab}\n$\\mathcal{{R}}={rx:.2f}$',
                xy=(tx, rx), xytext=(tx+dx, rx+dy*0.03),
                fontsize=9, color=C_DATA,
                arrowprops=dict(arrowstyle='->', color='gray',
                                lw=0.8, connectionstyle='arc3,rad=0.1'))

# Reference line
ax.axhline(y=1, color='gray', ls='--', lw=1, alpha=0.7)
ax.text(5, 1.05, r'$\mathcal{R}=1$ (equal performance)',
        fontsize=9, color='gray')

# Region beyond the longest tested retention interval (350 days)
ax.axvspan(350, 400, color='gray', alpha=0.15, lw=0)
ax.text(375, 5.7, 'beyond\ntested RI', fontsize=8, color='dimgray',
        ha='center', va='top')

# Info box
ax.text(0.03, 0.97,
        'Computed from the descriptive surface\nof Cepeda et al. (2008); values near\n350 days exceed the data (Fig. 4)',
        transform=ax.transAxes, fontsize=9, va='top',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#E8F5E9',
                  edgecolor='#4CAF50', alpha=0.9))

ax.set_xlabel('Retention Interval (days)')
ax.set_ylabel(r'Retention Advantage Ratio $\mathcal{R}(t)$')
ax.set_title(r'$\mathcal{R}(t)$: Optimal Spacing Advantage Grows with Retention Interval')
ax.set_xlim(0, 400)
ax.set_ylim(0.8, 6.0)
ax.legend(loc='lower right', framealpha=0.9)

fig.savefig('figure3_Rt_analytical.pdf')
plt.close()


# =====================================================================
# FIGURE 4: MODEL-DERIVED vs RAW-DATA-IMPLIED R(t)
# =====================================================================
fig, ax = plt.subplots(figsize=(7, 5))

# Model curve (clipped to study range)
mask = t_curve <= 400
ax.plot(t_curve[mask], Rt_curve[mask], color=C_MODEL, lw=3, zorder=2,
        label=r'Model-derived $\mathcal{R}(t)$')

# Model values at paper's test delays
ax.scatter(t_paper, Rt_paper, s=120, color=C_MODEL, edgecolors='black',
           lw=1.2, zorder=4, marker='D',
           label='Model at study test delays')

# Raw data-implied R(t) from stated improvements
ax.scatter(t_paper, paper_improvements, s=120, color=C_DATA,
           edgecolors='black', lw=1.2, zorder=4, marker='o',
           label='Data-implied (stated improvements)')

# Connect the data points to show the non-monotonicity
ax.plot(t_paper, paper_improvements, '--', color=C_DATA, lw=1.5, alpha=0.5)

# Annotate the divergence at 350 days
ax.annotate('Model massed recall\nnear floor (0.036):\nratio unstable',
            xy=(350, paper_improvements[3]),
            xytext=(225, 2.9),
            fontsize=9, color=C_DATA, fontstyle='italic',
            arrowprops=dict(arrowstyle='->', color=C_DATA, lw=1.2))

ax.axhline(y=1, color='gray', ls='--', lw=1, alpha=0.7)

ax.set_xlabel('Retention Interval (days)')
ax.set_ylabel(r'Retention Advantage Ratio $\mathcal{R}(t)$')
ax.set_title('Model-Derived vs. Data-Implied Retention Advantage')
ax.set_xlim(0, 400)
ax.set_ylim(0.8, 6.0)
ax.legend(loc='upper left', framealpha=0.9, fontsize=9)

# Caveat box
ax.text(0.97, 0.05,
        'Model and data agree on growth\n'
        'through 70 days; at 350 days the\n'
        'model ratio is about 3x the data',
        transform=ax.transAxes, fontsize=8.5, ha='right', va='bottom',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFF9C4',
                  edgecolor='#FBC02D', alpha=0.8))

fig.savefig('figure4_model_vs_data.pdf')
plt.close()


# =====================================================================
# FIGURE 5: LOG-RATIO DECOMPOSITION
#   ln R(t; g) = ln A(g) + [R(0) - R(g)] * ln(1 + b t)
# Each fixed gap is a straight line in x = ln(1 + b t):
#   intercept = ln A(g) <= 0 (initial-strength cost)
#   slope     = R(0) - R(g) (decay-rate benefit)
# =====================================================================
fig, ax = plt.subplots(figsize=(7, 5))
t_lin = np.linspace(0, 350, 400)
x_lin = np.log(1 + B_PAR * t_lin)
gap_set = [1, 7, 21, 105]
gap_cols = ['#9C6ADE', '#3B82C4', '#3D6B35', '#C77C02']
for g, col in zip(gap_set, gap_cols):
    lnA = np.log(A_func(g))
    slope = R_func(0) - R_func(g)
    ax.plot(x_lin, lnA + slope * x_lin, color=col, lw=2,
            label=f'gap {g} d: intercept {lnA:.3f}, slope {slope:.2f}')
ax.axhline(0, color='gray', ls='--', lw=1)
ticks_t = [7, 35, 70, 180, 350]
ax_top = ax.secondary_xaxis('top',
                            functions=(lambda x: x, lambda x: x))
ax_top.set_xticks([np.log(1 + B_PAR * t) for t in ticks_t])
ax_top.set_xticklabels([f'{t} d' for t in ticks_t])
ax_top.set_xlabel('Retention interval')
ax.set_xlabel(r'$\ln(1 + bt)$')
ax.set_ylabel(r'$\ln \mathcal{R}(t; g)$')
ax.legend(loc='upper left', fontsize=8.5, framealpha=0.9)
fig.savefig('figure5_log_decomposition.pdf')
plt.close()


# =====================================================================
# PRINT TABLE DATA FOR PAPER
# =====================================================================
print("=" * 70)
print("TABLE: R(t) AT KEY RETENTION INTERVALS")
print("=" * 70)
print(f"{'Interval':>12} | {'g_opt (days)':>12} | {'Massed':>8} | {'Optimal':>8} | {'R(t)':>8}")
print("-" * 60)
for t_m, lab in zip(milestones_days, milestones_labels):
    g_opt, rec_opt = optimal_recall(t_m)
    rec_m = recall(t_m, 0)
    Rt = rec_opt / rec_m
    print(f"{lab:>12} | {g_opt:>11.1f} | {rec_m:>8.4f} | {rec_opt:>8.4f} | {Rt:>8.3f}")

print("\n" + "=" * 70)
print("TABLE: COMPARISON WITH PAPER'S STATED IMPROVEMENTS")
print("=" * 70)
print(f"{'RI':>6} | {'Paper best gap':>14} | {'Paper improv.':>13} | "
      f"{'Model R(t)':>10} | {'Data R(t)':>10}")
print("-" * 65)
paper_gaps = [1, 11, 21, 21]
for t_val, pg, pi, Rt_m in zip(t_paper, paper_gaps, 
    [10, 59, 111, 77], Rt_paper):
    data_Rt = 1 + pi/100
    print(f"{t_val:>4}d | {pg:>12}d | {pi:>11}% | "
          f"{Rt_m:>10.3f} | {data_Rt:>10.2f}")

print("\n" + "=" * 70)
print("MODEL STRUCTURE VERIFICATION")
print("=" * 70)
print(f"A(0) = {A_func(0):.4f} (should be 1.0)")
print(f"R(0) = {R_func(0):.4f} (massed decay rate)")
print(f"R(g) minimized at g = exp(d)-1 = {np.exp(D_PAR)-1:.1f} days")
print(f"  R at minimum = {R_func(np.exp(D_PAR)-1):.4f} (should be 1.0)")
print(f"  A at that gap = {A_func(np.exp(D_PAR)-1):.4f}")

# Verify the R(g) minimum is at g = exp(d) - 1
g_minR = np.exp(D_PAR) - 1
print(f"\nAt g = exp(d)-1 = {g_minR:.1f} days:")
print(f"  R(g) = {R_func(g_minR):.6f}")
print(f"  ln(g+1) = {np.log(g_minR+1):.6f}, d = {D_PAR}")
print(f"  [ln(g+1) - d]^2 = {(np.log(g_minR+1) - D_PAR)**2:.2e}")

print("\n" + "=" * 70)
print("KEY FINDING: MONOTONICITY")
print("=" * 70)
diffs = np.diff(Rt_curve)
print(f"R(t) monotonically increasing over [1, 3650] days: {np.all(diffs >= 0)}")
print(f"R(1 day)   = {R_ratio(1):.4f}")
print(f"R(1 week)  = {R_ratio(7):.4f}")
print(f"R(1 month) = {R_ratio(30):.4f}")
print(f"R(1 year)  = {R_ratio(365):.4f}")

print("\n" + "=" * 70)
print("WHY THE MODEL OVERPREDICTS AT 350 DAYS")
print("=" * 70)
print("The model's massed recall at 350 days is very low:")
print(f"  recall(350, 0) = {recall(350, 0):.4f}")
print(f"  recall(350, g_opt={optimal_recall(350)[0]:.1f}) = {optimal_recall(350)[1]:.4f}")
print("Small denominators amplify the ratio.")
print("The raw data would have floor effects moderating this.")
print(f"\nFor comparison, at 70 days:")
print(f"  recall(70, 0) = {recall(70, 0):.4f}")
print(f"  recall(70, g_opt={optimal_recall(70)[0]:.1f}) = {optimal_recall(70)[1]:.4f}")

print("\nFIGURES SAVED: figure1-4")
