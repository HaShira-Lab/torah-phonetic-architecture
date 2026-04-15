# src\figures\fig3_layer_c_flow_bars.py

import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def main(input_csv, output_png):

    # 
    plt.clf()
    plt.close('all')

    # --- данные ---
    df = pd.read_csv(input_csv)
    df["delta"] = df["obs"] - df["null_mean"]

    order = ["genesis","exodus","leviticus","numbers","deuteronomy","hagamad"]
    df = df.set_index("book").reindex(order)

    x = np.arange(len(order))
    y = df["delta"].values
    err = df["null_sd"].values

    colors = ["#2E7D32"]*5 + ["#444444"]

    # --- фигура ---
    fig, ax = plt.subplots(figsize=(3.6, 3.4))

    ax.bar(
        x,
        y,
        color=colors,
        yerr=err,
        capsize=3
    )

    # baseline
    ax.axhline(0, linewidth=1)

    # --- оси ---
    ax.set_xticks(x)
    ax.set_xticklabels(order, rotation=25, ha="right", fontsize=6.5)

    ax.set_ylabel("Δ (observed − null)", fontsize=9)
    # ax.set_xlabel("Corpus", fontsize=9)

    # --- ЗАГОЛОВОК ---
    ax.set_title(
        "Layer C: Syllabic correspondence\n(Δ, L = 20)",
        fontsize=9,
        pad=10
    )

    # --- сетка ---
    ax.grid(axis='y', linestyle='--', alpha=0.3)

    # --- layout ---
    plt.tight_layout(rect=[0,0,1,0.95])

    # --- сохранить ---
    os.makedirs(os.path.dirname(output_png), exist_ok=True)
    plt.savefig(output_png, dpi=300)
    plt.close()

    print("WROTE:", output_png)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python fig3_layer_c_flow_L20_final.py input.csv output.png")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])