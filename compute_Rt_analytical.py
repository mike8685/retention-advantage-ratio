#!/usr/bin/env python3
"""
Compute R(t) analytically from Cepeda et al. (2008) published retention surface model.

Model (from paper, Figure 4 parameters):
    recall(t, g) = A(g) * (b*t + 1)^{-R(g)}
    A(g) = p + (1 - p) * exp(-a * g)
    R(g) = 1 + c * [ln(g + 1) - d]^2

Published fitted parameters:
    b = 0.011
    p = 0.760
    a = 0.017
    c = 0.092
    d = 3.453

R(t) = max_g recall(t, g) / recall(t, 0)
"""

import numpy as np
from scipy.optimize import minimize_scalar
import matplotlib.pyplot as plt

# --- Published parameters ---
b = 0.011
p = 0.760
a_param = 0.017
c = 0.092
d = 3.453

def A(g):
    """Initial learning strength as function of gap."""
    return p + (1 - p) * np.exp(-a_param * g)

def R(g):
    """Decay rate as function of gap."""
    return 1 + c * (np.log(g + 1) - d)**2

def recall(t, g):
    """Recall probability at retention interval t with spacing gap g."""
    return A(g) * (b * t + 1)**(-R(g))

def recall_neg(g, t):
    """Negative recall for minimization."""
    return -recall(t, g)

# --- Compute R(t) across a range of retention intervals ---
t_values = np.logspace(np.log10(1), np.log10(365 * 10), 1000)

# Also compute at specific points matching the paper's test delays
t_specific = np.array([7, 35, 70, 350])

print("=" * 70)
print("CEPEDA et al. (2008) MODEL: ANALYTICAL R(t) COMPUTATION")
print("=" * 70)
print(f"\nPublished parameters: b={b}, p={p}, a={a_param}, c={c}, d={d}")
print(f"\nA(0) = {A(0):.4f}")
print(f"R(0) = {R(0):.4f}")
print(f"\nNote: A(0) = p + (1-p)*exp(0) = p + (1-p) = 1.0 (perfect initial recall)")
print(f"Note: R(0) = 1 + c*(ln(1) - d)^2 = 1 + c*d^2 = 1 + {c}*{d}^2 = {R(0):.4f}")

# --- Massed recall at each t ---
print("\n" + "-" * 70)
print("MASSED (gap=0) RECALL AT EACH TEST DELAY")
print("-" * 70)
for t in t_specific:
    r = recall(t, 0)
    print(f"  t = {t:>4d} days: recall(t, 0) = {r:.4f}")

# --- Optimal gap and recall at each t ---
print("\n" + "-" * 70)
print("OPTIMAL GAP AND RECALL AT EACH TEST DELAY")
print("-" * 70)

R_t_specific = []
for t in t_specific:
    # Optimize over g in [0, 500] days
    result = minimize_scalar(recall_neg, bounds=(0, 500), args=(t,), method='bounded')
    g_opt = result.x
    recall_opt = -result.fun
    recall_massed = recall(t, 0)
    R_ratio = recall_opt / recall_massed
    R_t_specific.append(R_ratio)
    
    # Also check the gaps actually tested at this RI (Cepeda et al., 2008, Table 1)
    tested_gaps = {7: [0, 1, 2, 7, 21, 105], 35: [0, 1, 4, 7, 11, 21, 105],
                   70: [0, 1, 7, 14, 21, 105], 350: [0, 1, 7, 21, 35, 70, 105]}
    discrete_gaps = tested_gaps.get(t, [0, 1, 2, 4, 7, 11, 14, 21, 35, 70, 105])
    discrete_recalls = [recall(t, g) for g in discrete_gaps]
    best_discrete_idx = np.argmax(discrete_recalls)
    best_discrete_gap = discrete_gaps[best_discrete_idx]
    best_discrete_recall = discrete_recalls[best_discrete_idx]
    
    print(f"\n  t = {t:>4d} days:")
    print(f"    Massed recall:          {recall_massed:.4f}")
    print(f"    Continuous optimal gap:  {g_opt:.1f} days")
    print(f"    Recall at optimal gap:   {recall_opt:.4f}")
    print(f"    R(t):                    {R_ratio:.3f}")
    print(f"    Best discrete gap:       {best_discrete_gap} days (recall = {best_discrete_recall:.4f})")
    print(f"    R(t) using discrete gap: {best_discrete_recall / recall_massed:.3f}")
    
    # Check against paper's stated improvements
    improvement_pct = (best_discrete_recall - recall_massed) / recall_massed * 100
    print(f"    Discrete improvement:    {improvement_pct:.1f}%")

print("\n" + "-" * 70)
print("COMPARISON WITH PAPER'S STATED IMPROVEMENTS")
print("-" * 70)
paper_improvements = [10, 59, 111, 77]  # percent
paper_best_gaps = [1, 11, 21, 21]  # days (from paper)
print(f"{'RI':>6} | {'Paper gap':>9} | {'Paper %':>8} | {'Model %':>8} | {'Model/Data lnR':>14}")
print("-" * 55)
for t, pg, pi in zip(t_specific, paper_best_gaps, paper_improvements):
    recall_massed = recall(t, 0)
    recall_at_paper_gap = recall(t, pg)
    model_improvement = (recall_at_paper_gap - recall_massed) / recall_massed * 100
    ln_ratio = np.log(1 + model_improvement / 100) / np.log(1 + pi / 100)
    print(f"{t:>4}d | {pg:>7}d | {pi:>7}% | {model_improvement:>7.1f}% | {ln_ratio:>14.2f}")

# --- Full R(t) curve ---
print("\n" + "-" * 70)
print("FULL R(t) CURVE (continuous optimization)")
print("-" * 70)

R_t_full = []
g_opt_full = []
for t in t_values:
    result = minimize_scalar(recall_neg, bounds=(0, 1000), args=(t,), method='bounded')
    g_opt = result.x
    recall_opt = -result.fun
    recall_massed = recall(t, 0)
    R_ratio = recall_opt / recall_massed
    R_t_full.append(R_ratio)
    g_opt_full.append(g_opt)

R_t_full = np.array(R_t_full)
g_opt_full = np.array(g_opt_full)

# Print at key milestones
milestones = [1, 7, 14, 30, 60, 90, 180, 365, 365*2, 365*5, 365*10]
milestone_labels = ['1d', '1wk', '2wk', '1mo', '2mo', '3mo', '6mo', '1yr', '2yr', '5yr', '10yr']
print(f"{'Time':>6} | {'R(t)':>8} | {'g_opt':>8} | {'Monotonic?':>10}")
print("-" * 45)
prev_R = 0
for t, label in zip(milestones, milestone_labels):
    result = minimize_scalar(recall_neg, bounds=(0, 1000), args=(t,), method='bounded')
    g_opt = result.x
    R_ratio = -result.fun / recall(t, 0)
    mono = "YES" if R_ratio > prev_R else "NO <<<" 
    print(f"{label:>6} | {R_ratio:>8.3f} | {g_opt:>7.1f}d | {mono:>10}")
    prev_R = R_ratio

# --- Check: is R(t) monotonically increasing? ---
diffs = np.diff(R_t_full)
monotonic = np.all(diffs >= 0)
print(f"\nIs R(t) monotonically increasing over [{t_values[0]:.0f}, {t_values[-1]:.0f}] days? {monotonic}")
if not monotonic:
    first_decrease = np.where(diffs < 0)[0]
    if len(first_decrease) > 0:
        idx = first_decrease[0]
        print(f"  First decrease at t ≈ {t_values[idx]:.1f} days")
        print(f"  R({t_values[idx]:.1f}) = {R_t_full[idx]:.4f}")
        print(f"  R({t_values[idx+1]:.1f}) = {R_t_full[idx+1]:.4f}")

# --- Try fitting sqrt model to the CORRECT R(t) values ---
from scipy.optimize import curve_fit

def sqrt_model(t, a, b):
    return a + b * np.sqrt(t)

def log_model(t, a, b):
    return a + b * np.log(t)

def power_model(t, a, b):
    return a * t**b

# Sample R(t) at many points for fitting
t_sample = np.array([7, 14, 30, 60, 90, 180, 365, 730, 1825])
R_sample = []
for t in t_sample:
    result = minimize_scalar(recall_neg, bounds=(0, 1000), args=(t,), method='bounded')
    R_sample.append(-result.fun / recall(t, 0))
R_sample = np.array(R_sample)

print("\n" + "-" * 70)
print("MODEL FITTING TO ANALYTICAL R(t)")
print("-" * 70)

try:
    popt_sqrt, _ = curve_fit(sqrt_model, t_sample, R_sample)
    pred_sqrt = sqrt_model(t_sample, *popt_sqrt)
    ss_res = np.sum((R_sample - pred_sqrt)**2)
    ss_tot = np.sum((R_sample - np.mean(R_sample))**2)
    r2_sqrt = 1 - ss_res / ss_tot
    print(f"Sqrt: R(t) = {popt_sqrt[0]:.4f} + {popt_sqrt[1]:.4f} * sqrt(t), R² = {r2_sqrt:.4f}")
except:
    print("Sqrt model fitting failed")

try:
    popt_log, _ = curve_fit(log_model, t_sample, R_sample)
    pred_log = log_model(t_sample, *popt_log)
    ss_res = np.sum((R_sample - pred_log)**2)
    ss_tot = np.sum((R_sample - np.mean(R_sample))**2)
    r2_log = 1 - ss_res / ss_tot
    print(f"Log:  R(t) = {popt_log[0]:.4f} + {popt_log[1]:.4f} * ln(t), R² = {r2_log:.4f}")
except:
    print("Log model fitting failed")

try:
    popt_pow, _ = curve_fit(power_model, t_sample, R_sample, p0=[1, 0.3])
    pred_pow = power_model(t_sample, *popt_pow)
    ss_res = np.sum((R_sample - pred_pow)**2)
    ss_tot = np.sum((R_sample - np.mean(R_sample))**2)
    r2_pow = 1 - ss_res / ss_tot
    print(f"Power: R(t) = {popt_pow[0]:.4f} * t^{popt_pow[1]:.4f}, R² = {r2_pow:.4f}")
except:
    print("Power model fitting failed")

print(f"\nSample points used for fitting:")
for t, r in zip(t_sample, R_sample):
    print(f"  t = {t:>5d} days: R(t) = {r:.4f}")


# =====================================================================
# PLOTS
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

# --- Plot 1: R(t) from analytical model ---
fig, ax = plt.subplots(figsize=(7, 5))

ax.plot(t_values, R_t_full, color='#3D6B35', linewidth=3, 
        label=r'$\mathcal{R}(t)$ from published model')

# Mark the paper's test delays
R_t_sp = np.array(R_t_specific)
ax.scatter(t_specific, R_t_sp, s=120, color='#5B4FA0', edgecolors='black',
           linewidth=1.2, zorder=4, label='At study test delays')

ax.axhline(y=1, color='gray', linestyle='--', linewidth=1, alpha=0.7)
ax.text(2, 1.02, r'$\mathcal{R} = 1$ (equal performance)', fontsize=9, color='gray')

ax.set_xlabel('Retention Interval (days)')
ax.set_ylabel(r'Retention Advantage Ratio $\mathcal{R}(t)$')
ax.set_title(r'$\mathcal{R}(t)$ Computed Analytically from Cepeda et al. (2008) Model')
ax.set_xlim(0, 400)
ax.legend(loc='upper left', framealpha=0.9)

fig.savefig('Rt_analytical.png', dpi=300)
plt.close()

# --- Plot 2: R(t) on log scale, extended range ---
fig, ax = plt.subplots(figsize=(7, 5))

ax.semilogx(t_values, R_t_full, color='#3D6B35', linewidth=3,
            label=r'$\mathcal{R}(t)$ from published model')
ax.scatter(t_specific, R_t_sp, s=120, color='#5B4FA0', edgecolors='black',
           linewidth=1.2, zorder=4, label='At study test delays')

ax.axhline(y=1, color='gray', linestyle='--', linewidth=1, alpha=0.7)

# Add milestone labels
for t, label, R_val in zip(milestones[:8], milestone_labels[:8], 
    [None]*len(milestones)):
    result = minimize_scalar(recall_neg, bounds=(0, 1000), args=(t,), method='bounded')
    rv = -result.fun / recall(t, 0)

ax.set_xlabel('Retention Interval (days, log scale)')
ax.set_ylabel(r'Retention Advantage Ratio $\mathcal{R}(t)$')
ax.set_title(r'$\mathcal{R}(t)$ Over Extended Range (Log Scale)')
ax.legend(loc='upper left', framealpha=0.9)

fig.savefig('Rt_analytical_log.png', dpi=300)
plt.close()

# --- Plot 3: Optimal gap as function of t ---
fig, ax = plt.subplots(figsize=(7, 5))

ax.plot(t_values, g_opt_full, color='#D64545', linewidth=2.5)
ax.set_xlabel('Retention Interval (days)')
ax.set_ylabel('Optimal Spacing Gap (days)')
ax.set_title('Optimal Gap Grows with Retention Interval')
ax.set_xlim(0, 400)

fig.savefig('optimal_gap.png', dpi=300)
plt.close()

# --- Plot 4: Recall surface slice ---
fig, ax = plt.subplots(figsize=(7, 5))

gaps_plot = np.linspace(0, 120, 500)
colors = ['#7B2D8E', '#2B5EA7', '#1A9E76', '#6B8E23']
for t, color, label in zip([7, 35, 70, 350], colors, 
    ['7-day delay', '35-day delay', '70-day delay', '350-day delay']):
    recalls = [recall(t, g) for g in gaps_plot]
    ax.plot(gaps_plot, recalls, color=color, linewidth=2, label=label)

ax.set_xlabel('Spacing Gap (days)')
ax.set_ylabel('Predicted Recall')
ax.set_title('Cepeda et al. (2008) Fitted Model Predictions')
ax.legend(loc='upper right', framealpha=0.9)
ax.set_xlim(0, 120)
ax.set_ylim(0, 1.0)

fig.savefig('model_predictions.png', dpi=300)
plt.close()

print("\n" + "=" * 70)
print("FIGURES SAVED")
print("=" * 70)
print("  Rt_analytical.png - R(t) from model (linear scale)")
print("  Rt_analytical_log.png - R(t) from model (log scale)")
print("  optimal_gap.png - Optimal gap vs retention interval")
print("  model_predictions.png - Recall surface slices")
