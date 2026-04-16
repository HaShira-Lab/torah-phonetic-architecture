import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def parse_items(items):
    return [(i.split("=",1)[0], i.split("=",1)[1]) for i in items]


def load_rate(path):
    df = pd.read_csv(path)
    cols = {c.lower(): c for c in df.columns}

    if "rate" in cols:
        return df[cols["rate"]].to_numpy()
    elif "density" in cols:
        return df[cols["density"]].to_numpy()
    else:
        raise ValueError(f"No rate/density in {path}")


def binned_mean(arr, n_bins):
    edges = np.linspace(0, len(arr), n_bins + 1)
    out = np.zeros(n_bins)

    for i in range(n_bins):
        a = int(edges[i])
        b = int(edges[i+1])
        if b <= a:
            b = min(a+1, len(arr))
        seg = arr[a:b]
        out[i] = seg.mean() if len(seg) else np.nan

    return out


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--torah", nargs="+", required=True)
    parser.add_argument("--modern", nargs="+", required=True)
    parser.add_argument("--bins", type=int, default=120)
    parser.add_argument("--threshold", type=float, required=True)
    parser.add_argument("--out", required=True)

    args = parser.parse_args()

    torah = parse_items(args.torah)
    modern = parse_items(args.modern)
    items = torah + modern

    labels = []
    all_binned = []

    # ---------- LOAD ----------
    for name, path in items:
        arr = load_rate(path)
        b = binned_mean(arr, args.bins)
        all_binned.append(b)
        labels.append(name)

    # ---------- GLOBAL SCALE (for color only, not normalization) ----------
    global_min = min(np.nanmin(x) for x in all_binned)
    global_max = max(np.nanmax(x) for x in all_binned)

    rows = []

    for b in all_binned:
        # threshold mask
        thr = np.nanpercentile(b, 100 - args.threshold)
        mask = b >= thr

        # normalize ONLY for color mapping
        norm = (b - global_min) / (global_max - global_min + 1e-12)

        # single colormap
        colors = plt.cm.viridis(norm)

        # below threshold → white
        colors[~mask] = [1, 1, 1, 1]

        rows.append(colors[:, :3])

    data = np.stack(rows)

    # ---------- PLOT ----------
    fig, ax = plt.subplots(figsize=(13, 4.6))

    ax.imshow(data, aspect='auto', interpolation='nearest')

    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=11)

    # modern
    for i, tick in enumerate(ax.get_yticklabels()):
        if i >= len(torah):
            tick.set_color("darkred")

    ax.set_xticks(np.linspace(0, args.bins - 1, 5))
    ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"], fontsize=11)

    ax.set_xlabel("Relative position in text", fontsize=12)
    ax.set_title("Rhyme density above threshold (Layer C)", fontsize=15)

    # separators
    for y in np.arange(0.5, len(labels), 1):
        ax.axhline(y, color='white', linewidth=0.6)

    plt.tight_layout()
    plt.savefig(args.out, dpi=600)

    print(f"WROTE: {args.out}")


if __name__ == "__main__":
    main()