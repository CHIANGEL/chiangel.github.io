#!/usr/bin/env python3
"""Generate data-driven result figures for the PerFusion KDD 2026 poster."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "figures" / "perfusion_poster"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

NAVY = "#17233C"
BLUE = "#3E5F8A"
TEAL = "#2A9D8F"
CORAL = "#E76F51"
GOLD = "#E9C46A"
GRAY = "#AEB8C8"
GRID = "#DCE2EC"


def configure() -> None:
    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 16,
            "axes.titlesize": 20,
            "axes.titleweight": "bold",
            "axes.labelsize": 16,
            "xtick.labelsize": 14,
            "ytick.labelsize": 15,
            "figure.dpi": 180,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.spines.left": False,
            "axes.grid": True,
            "grid.alpha": 1.0,
            "grid.color": GRID,
            "grid.linestyle": "-",
            "axes.axisbelow": True,
        }
    )


def online_impact() -> None:
    labels = [
        "Search CTR",
        "Recommendation CTR",
        "Conversion rate",
        "Return rate",
    ]
    values = [17.81, 13.35, 17.27, -7.90]
    colors = [TEAL, BLUE, CORAL, GOLD]

    fig, ax = plt.subplots(figsize=(10.2, 4.7))
    y = np.arange(len(labels))
    bars = ax.barh(y, values, color=colors, height=0.58, edgecolor="none")
    ax.axvline(0, color=NAVY, linewidth=1.3)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(-10.5, 20.5)
    ax.set_xticks([-10, 0, 10, 20], ["-10%", "0", "+10%", "+20%"])
    ax.set_title("AIGI vs. human-designed items in the same stores", loc="left", color=NAVY, pad=15)
    ax.set_xlabel("Relative change", color=NAVY, labelpad=8)
    ax.tick_params(axis="both", colors=NAVY, length=0)
    ax.spines["bottom"].set_color(GRID)

    for bar, value in zip(bars, values):
        if value >= 0:
            x, ha, label, label_color = value + 0.55, "left", f"+{value:.2f}%", NAVY
        else:
            x, ha, label, label_color = value / 2, "center", f"{value:.1f}%", NAVY
        ax.text(
            x,
            bar.get_y() + bar.get_height() / 2,
            label,
            va="center",
            ha=ha,
            fontsize=16,
            fontweight="bold",
            color=label_color,
        )

    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    fig.savefig(OUT_DIR / "fig_online_impact.pdf", transparent=True)
    fig.savefig(OUT_DIR / "fig_online_impact.png", transparent=True)
    plt.close(fig)


def reward_model_comparison() -> None:
    models = [
        "Aesthetics",
        "CLIP-H",
        "ImageReward",
        "HPSv1",
        "HPSv2",
        "PickScore",
        "PerFusionRM",
    ]
    gauc = [0.5000, 0.7060, 0.6115, 0.5030, 0.6420, 0.5820, 0.9564]
    colors = [GRAY] * 6 + [CORAL]

    fig, ax = plt.subplots(figsize=(10.2, 5.4))
    y = np.arange(len(models))
    bars = ax.barh(y, gauc, color=colors, height=0.58, edgecolor="none")
    ax.set_yticks(y, models)
    ax.invert_yaxis()
    ax.set_xlim(0.45, 1.02)
    ax.set_xticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    ax.set_title("Industrial user-preference estimation", loc="left", color=NAVY, pad=15)
    ax.set_xlabel("Group-wise AUC (GAUC)", color=NAVY, labelpad=8)
    ax.tick_params(axis="both", colors=NAVY, length=0)
    ax.spines["bottom"].set_color(GRID)

    for bar, value in zip(bars, gauc):
        ax.text(
            value + 0.008,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.4f}",
            va="center",
            ha="left",
            fontsize=14,
            fontweight="bold" if value == max(gauc) else "normal",
            color=NAVY,
        )

    ax.text(
        0.955,
        5.46,
        "+35.47% vs. best baseline",
        ha="right",
        va="bottom",
        fontsize=15,
        fontweight="bold",
        color=CORAL,
    )

    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    fig.savefig(OUT_DIR / "fig_reward_model_gauc.pdf", transparent=True)
    fig.savefig(OUT_DIR / "fig_reward_model_gauc.png", transparent=True)
    plt.close(fig)


def main() -> None:
    configure()
    online_impact()
    reward_model_comparison()
    print(f"Generated result figures in {OUT_DIR}")


if __name__ == "__main__":
    main()
