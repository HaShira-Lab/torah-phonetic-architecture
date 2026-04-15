import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib as mpl


def load_rate(path):
    df = pd.read_csv(path)
    cols = {c.lower(): c for c in df.columns}

    if "rate" in cols:
        return df[cols["rate"]].to_numpy()
    elif "density" in cols:
        return df[cols["density"]].to_numpy()
    else:
        raise ValueError(f"No rate/density column in {path}")


def downsample(arr, factor=3):
    n = len(arr) // factor
    if n == 0:
        return arr
    return arr[: n * factor].reshape(n, factor).mean(axis=1)


def smooth(arr, k=2):
    if k <= 1 or len(arr) < 2:
        return arr
    pad = k // 2
    arr_padded = np.pad(arr, pad, mode="edge")
    out = np.convolve(arr_padded, np.ones(k) / k, mode="valid")
    return out[: len(arr)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--files", nargs="+", required=True)
    parser.add_argument("--labels", nargs="+", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    if len(args.files) != len(args.labels):
        raise ValueError("files and labels must match")

    full_series = []
    boundaries = []

    pos = 0
    for path in args.files:
        arr = load_rate(path)
        arr = downsample(arr, factor=3)
        arr = smooth(arr, k=2)

        full_series.append(arr)
        boundaries.append(pos)
        pos += len(arr)

    full_series = np.concatenate(full_series)
    boundaries.append(len(full_series))

    min_v = np.nanmin(full_series)
    max_v = np.nanmax(full_series)
    norm = (full_series - min_v) / (max_v - min_v + 1e-12)
    norm = np.power(norm, 0.9)

    colors = cm.viridis_r(norm)[:, :3]
    data = colors.reshape(1, -1, 3)

    fig, ax = plt.subplots(figsize=(7, 2.2))

    ax.imshow(
        data,
        aspect="auto",
        interpolation="bilinear"
    )

    ax.set_yticks([])
    ax.set_xticks([])
    ax.set_title("Distribution of local rhyme density across the Torah", fontsize=10)

    # boundaries
    for b in boundaries:
        ax.axvline(b - 0.5, color="black", linewidth=1.2)

    # pointers + labels
    for i in range(len(args.labels)):
        start = boundaries[i]
        end = boundaries[i + 1]

        x0 = start - 0.5
        text_x = (start + end) / 2

        # short vertical down from boundary
        ax.plot(
            [x0, x0],
            [0, -0.10],
            color="black",
            linewidth=1,
            transform=ax.get_xaxis_transform(),
            clip_on=False
        )

        # diagonal toward label
        ax.plot(
            [x0, text_x],
            [-0.10, -0.30],
            color="black",
            linewidth=1,
            transform=ax.get_xaxis_transform(),
            clip_on=False
        )

        # label
        ax.text(
            text_x,
            -0.34,
            args.labels[i],
            ha="center",
            va="top",
            fontsize=8,
            transform=ax.get_xaxis_transform()
        )

    cbar = plt.colorbar(
        mpl.cm.ScalarMappable(cmap=cm.viridis_r),
        ax=ax,
        orientation="horizontal",
        fraction=0.06,
        pad=0.38
    )
    cbar.set_label("Relative rhyme density (low → high)", fontsize=9)
    cbar.set_ticks([])

    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.0)

    plt.subplots_adjust(bottom=0.35)
    plt.tight_layout()
    plt.savefig(args.out, dpi=600)
    print(f"WROTE: {args.out}")


if __name__ == "__main__":
    main()