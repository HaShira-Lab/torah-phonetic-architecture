# src\figures\fig1_layer_a_delta.py

import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def main(input_csv, output_png):

    # очистка
    plt.clf()
    plt.close('all')

    df = pd.read_csv(input_csv)

    order = ["genesis", "exodus", "leviticus", "numbers", "deuteronomy", "hagamad"]
    df["corpus"] = pd.Categorical(df["corpus"], categories=order, ordered=True)
    df = df.sort_values("corpus")

    x = np.arange(len(order))

    # --- Δ ---
    delta = df["global_overlap_obs"] - df["global_overlap_null_mean"]

    # --- ERROR BARS ---
    # 
    if "global_overlap_null_sd" in df.columns:
        err = df["global_overlap_null_sd"]
    else:
        err = None  # fallback

    # цвета 
    colors = ["#2E7D32"]*5 + ["#444444"]

    # фигура 
    fig, ax = plt.subplots(figsize=(3.6, 3.4))

    ax.bar(
        x,
        delta,
        color=colors,
        yerr=err,
        capsize=3
    )

    # baseline
    ax.axhline(0, linewidth=1)

    # оси
    ax.set_xticks(x)
    ax.set_xticklabels(order, rotation=25, ha="right", fontsize=7)

    ax.set_ylabel("Δ (observed − null)", fontsize=9)
    # ax.set_xlabel("Corpus", fontsize=9)

    # заголовок 
    ax.set_title(
        "Layer A: Consonantal structure\n(Δ overlap)",
        fontsize=9,
        pad=10
    )

    # сетка
    ax.grid(axis='y', linestyle='--', alpha=0.3)

    # layout
    plt.tight_layout(rect=[0,0,1,0.95])

    # сохранить
    os.makedirs(os.path.dirname(output_png), exist_ok=True)
    plt.savefig(output_png, dpi=300)
    plt.close()

    print("WROTE:", output_png)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python fig1_layer_a_delta_final.py input.csv output.png")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])