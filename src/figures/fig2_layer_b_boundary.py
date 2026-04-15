# src\figures\fig2_layer_b_boundary.py

import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def main(input_csv, output_png):

    plt.clf()
    plt.close('all')

    df = pd.read_csv(input_csv)

    order = ["genesis","exodus","leviticus","numbers","deuteronomy","hagamad"]

    df["book"] = pd.Categorical(df["book"], categories=order, ordered=True)
    df = df.sort_values("book")

    x = np.arange(len(df))
    labels = df["book"].values

    # ---  Δ  ---
    y = df["gap_baseline"] - df["null_segment_mean"]

    # --- error bars ---
    err = df["null_segment_sd"].values

    colors = ["#2E7D32"]*5 + ["#444444"]

    fig, ax = plt.subplots(figsize=(3.6, 3.4))

    ax.bar(
        x,
        y,
        color=colors,
        yerr=err,
        capsize=3
    )

    ax.axhline(0, linewidth=1)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=7)

    ax.set_ylabel("Δ gap (baseline − segment null)", fontsize=9)
    # ax.set_xlabel("Corpus", fontsize=9)

    ax.set_title(
        "Layer B: Boundary effect\n(segment control)",
        fontsize=9,
        pad=10
    )

    ax.grid(axis='y', linestyle='--', alpha=0.3)

    plt.tight_layout(rect=[0,0,1,0.95])

    os.makedirs(os.path.dirname(output_png), exist_ok=True)
    plt.savefig(output_png, dpi=300)
    plt.close()

    print("WROTE:", output_png)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python fig2_layer_b_boundary_final.py input.csv output.png")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])