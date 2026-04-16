import sys
import os
import pandas as pd
import matplotlib.pyplot as plt


def load_one(csv_path: str, label: int) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    cols = {c.lower(): c for c in df.columns}

    book_col = cols.get("book")
    obs_col = cols.get("score") or cols.get("obs")
    null_col = cols.get("null_mean")

    if book_col is None or obs_col is None or null_col is None:
        raise ValueError(
            f"Expected columns book/score/null_mean in file: {csv_path}. "
            f"Found: {list(df.columns)}"
        )

    delta = df[obs_col] - df[null_col]

    out = pd.DataFrame({
        "corpus": df[book_col].astype(str).str.strip().str.lower(),
        "L": label,
        "delta": delta,
    })
    return out


def main(csv_l10, csv_l20, csv_l40, output_png):
    df = pd.concat(
        [
            load_one(csv_l10, 10),
            load_one(csv_l20, 20),
            load_one(csv_l40, 40),
        ],
        ignore_index=True,
    )

    corpus_order = [
        "genesis",
        "exodus",
        "leviticus",
        "numbers",
        "deuteronomy",
        "hagamad",
    ]

    plt.figure(figsize=(8.5, 5.5))

    for corpus in corpus_order:
        sub = df[df["corpus"] == corpus].sort_values("L")
        if sub.empty:
            continue
        plt.plot(sub["L"], sub["delta"], marker="o", linewidth=2, label=corpus)

    plt.xlabel("Scale (L)")
    plt.ylabel("Δ (Observed − Null)")
    plt.title("Layer C: Multi-scale syllabic correspondence")

    plt.xticks([10, 20, 40])
    plt.grid(axis="y")
    plt.legend()

    os.makedirs(os.path.dirname(output_png), exist_ok=True)
    plt.savefig(output_png, bbox_inches="tight", dpi=300)
    plt.close()

    print("WROTE:", output_png)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(
            "Usage: python fig3_layer_c_flow_delta.py "
            "<csv_L10> <csv_L20> <csv_L40> <output_png>"
        )
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])