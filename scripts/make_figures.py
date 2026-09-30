"""Generate the paper's figures. Every number is either analytic or a seeded Monte Carlo simulation."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "paper" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURF, "axes.facecolor": SURF,
    "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlecolor": INK, "legend.frameon": False,
    "lines.linewidth": 2,
})
Z = 1.959964; ZB = 0.841621  # alpha=.05 two-sided, power=.80
rng = np.random.default_rng(20260930)

# Figure 2: CI half-width and minimum detectable effect vs n
n = np.unique(np.logspace(np.log10(50), np.log10(5000), 60).astype(int))
fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.2))
for p, c in [(0.5, S1), (0.7, S2), (0.9, S3)]:
    hw = 100 * Z * np.sqrt(p * (1 - p) / n)
    a.plot(n, hw, color=c, label=f"accuracy = {p:.0%}")
a.set_xscale("log"); a.set_xlabel("number of eval items (n)"); a.set_ylabel("95% CI half-width (pp)")
a.set_title("A. Uncertainty of a single score"); a.legend(loc="upper right"); a.set_xlim(50, 5000)
p = 0.7
for rho, c, lab in [(0.0, S1, "unpaired (ρ = 0)"), (0.5, S2, "paired, ρ = 0.5"), (0.8, S3, "paired, ρ = 0.8")]:
    mde = 100 * (Z + ZB) * np.sqrt(2 * p * (1 - p) * (1 - rho) / n)
    b.plot(n, mde, color=c, label=lab)
b.set_xscale("log"); b.set_xlabel("number of eval items (n)"); b.set_ylabel("min. detectable difference (pp)")
b.set_title("B. Comparing two models (80% power, α = 0.05)"); b.legend(loc="upper right"); b.set_xlim(50, 5000)
fig.tight_layout(); fig.savefig(OUT / "fig2_power.png", dpi=200); plt.close(fig)

# Figure 3: clustered standard errors — design effect
icc = np.linspace(0, 0.5, 100)
fig, ax = plt.subplots(figsize=(6.4, 4.2))
for m, c in [(3, S1), (10, S2), (30, S3)]:
    inf = np.sqrt(1 + (m - 1) * icc)
    ax.plot(icc, inf, color=c, label=f"{m} items per cluster")
ax.set_xlabel("intra-cluster correlation (ICC)"); ax.set_ylabel("SE inflation vs. naive i.i.d. SE (×)")
ax.set_title("Naive SEs understate uncertainty for clustered items"); ax.legend(loc="upper left"); ax.set_xlim(0, 0.5)
fig.tight_layout(); fig.savefig(OUT / "fig3_cluster.png", dpi=200); plt.close(fig)

# Figure 4: judge-noise attenuation (Monte Carlo)
pA, pB, N, R = 0.70, 0.75, 1000, 2000
accs = np.linspace(0.55, 1.0, 19)
means, lo, hi = [], [], []
for acc in accs:
    ta = rng.random((R, N)) < pA; tb = rng.random((R, N)) < pB
    fa = rng.random((R, N)) > acc; fb = rng.random((R, N)) > acc
    d = 100 * ((tb ^ fb).mean(1) - (ta ^ fa).mean(1))
    means.append(d.mean()); lo.append(np.percentile(d, 2.5)); hi.append(np.percentile(d, 97.5))
fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.fill_between(accs, lo, hi, color=S1, alpha=0.18, lw=0, label="95% of simulated runs")
ax.plot(accs, means, "o", color=S1, ms=6, mec=SURF, mew=2, label="simulated mean")
ax.plot(accs, (2 * accs - 1) * 100 * (pB - pA), color=S2, label="analytic: (2a − 1)·Δ")
ax.axhline(5, color=INK2, lw=1, ls="--"); ax.text(0.56, 5.3, "true Δ = 5 pp", color=INK2, fontsize=10)
ax.axhline(0, color=GRID, lw=1)
ax.set_xlabel("judge agreement with ground truth (a)"); ax.set_ylabel("measured B − A difference (pp)")
ax.set_title("A noisy judge shrinks real differences"); ax.legend(loc="upper left")
fig.tight_layout(); fig.savefig(OUT / "fig4_judge.png", dpi=200); plt.close(fig)

# Numbers quoted in the text
for nn in (100, 400, 1000):
    print(f"n={nn}: CI half-width at p=.7 = {100*Z*np.sqrt(.21/nn):.1f}pp; MDE unpaired={100*(Z+ZB)*np.sqrt(.42/nn):.1f}pp, paired rho=.5={100*(Z+ZB)*np.sqrt(.21/nn):.1f}pp")
i = int(np.argmin(abs(accs - 0.8)))
print(f"judge a=0.80: simulated mean diff {means[i]:.2f}pp, 95% band [{lo[i]:.2f},{hi[i]:.2f}]")
print("detect rate at a=.8 vs 1.0 is visible from band crossing zero:", lo[i] > 0, lo[-1] > 0)
