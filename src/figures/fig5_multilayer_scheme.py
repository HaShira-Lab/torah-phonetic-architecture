#!/usr/bin/env python3
"""
fig4_multilayer_scheme.py

Run style:
    python src\figures\fig4_multilayer_scheme.py results\figures\fig4_multilayer_scheme.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


BOX_FACE = "#e8eef7"
BOX_EDGE = "#415a77"
ARROW_COLOR = "#415a77"
TEXT_COLOR = "#111111"


def add_box(ax, x, y, w, h, layer, desc, right_label):
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.012,rounding_size=0.02",
        linewidth=2.2,
        edgecolor=BOX_EDGE,
        facecolor=BOX_FACE,
        zorder=2,
    )
    ax.add_patch(box)

    # Layer title
    ax.text(
        x + w / 2,
        y + h * 0.68,
        layer,
        ha="center",
        va="center",
        fontsize=22,
        fontweight="bold",
        color=TEXT_COLOR,
        zorder=3,
    )

    # Description
    ax.text(
        x + w / 2,
        y + h * 0.34,
        desc,
        ha="center",
        va="center",
        fontsize=14.5,
        color=TEXT_COLOR,
        linespacing=1.15,
        zorder=3,
    )

    # Right-side connector and label
    y_mid = y + h / 2
    x0 = x + w + 0.015
    x1 = x0 + 0.03
    ax.plot(
        [x0, x1],
        [y_mid, y_mid],
        color=BOX_EDGE,
        linewidth=2.0,
        solid_capstyle="round",
        zorder=1,
    )
    ax.text(
        x1 + 0.03,
        y_mid,
        right_label,
        ha="left",
        va="center",
        fontsize=16,
        color=TEXT_COLOR,
        linespacing=1.15,
        zorder=3,
    )


def build_figure():
    fig, ax = plt.subplots(figsize=(12, 10), dpi=300)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Layout
    x = 0.18
    w = 0.40
    h = 0.16

    y_a = 0.66
    y_b = 0.39
    y_c = 0.12

    # Title
    ax.text(
        0.5,
        0.94,
        "A multi-layer model of phonetic organization",
        ha="center",
        va="center",
        fontsize=27,
        color=TEXT_COLOR,
    )

    # Boxes
    add_box(
        ax, x, y_a, w, h,
        "Layer A",
        "Consonantal clustering\n(local substrate)",
        "recurrent\nconsonantal\nregimes",
    )
    add_box(
        ax, x, y_b, w, h,
        "Layer B",
        "Boundary-aligned phonetic chains\n(structural alignment)",
        "segmentation-\naligned\nphonetic chains",
    )
    add_box(
        ax, x, y_c, w, h,
        "Layer C",
        "Syllabic / rhyme correspondence\n(long-range patterning)",
        "distributed\nsyllabic / rhyme\ncorrespondence",
    )

    # Vertical arrows
    center_x = x + w / 2
    ax.annotate(
        "",
        xy=(center_x, y_b + h + 0.01),
        xytext=(center_x, y_a - 0.01),
        arrowprops=dict(arrowstyle="-|>", lw=2.4, color=ARROW_COLOR, mutation_scale=18),
        zorder=1,
    )
    ax.annotate(
        "",
        xy=(center_x, y_c + h + 0.01),
        xytext=(center_x, y_b - 0.01),
        arrowprops=dict(arrowstyle="-|>", lw=2.4, color=ARROW_COLOR, mutation_scale=18),
        zorder=1,
    )

    # Footer
    ax.text(
        0.5,
        0.045,
        "Interaction across layers yields structured large-scale phonetic organization.",
        ha="center",
        va="center",
        fontsize=18.5,
        color=TEXT_COLOR,
    )

    return fig


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "output_png",
        help="Output PNG path, e.g. results\\figures\\fig4_multilayer_scheme.png",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    out_path = Path(args.output_png)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fig = build_figure()
    fig.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    print(f"WROTE: {out_path}")


if __name__ == "__main__":
    main()