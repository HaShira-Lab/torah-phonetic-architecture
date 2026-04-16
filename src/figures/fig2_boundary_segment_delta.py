import sys
import os
import pandas as pd
import matplotlib.pyplot as plt

def main(input_csv, output_png):
    df = pd.read_csv(input_csv)

    # порядок книг
    order = ["genesis", "exodus", "leviticus", "numbers", "deuteronomy", "hagamad"]
    df["book"] = pd.Categorical(df["book"], categories=order, ordered=True)
    df = df.sort_values("book")

    # Δ между baseline и segment-null
    delta = df["gap_baseline"] - df["null_segment_mean"]

    plt.figure(figsize=(8,5))
    plt.bar(df["book"], delta)

    plt.xlabel("Corpus")
    plt.ylabel("Δ gap (baseline − segment-null)")
    plt.title("Layer B: Boundary effect (segment control)")

    plt.xticks(rotation=30)
    plt.grid(axis='y')

    os.makedirs(os.path.dirname(output_png), exist_ok=True)
    plt.savefig(output_png, bbox_inches='tight', dpi=300)
    plt.close()

    print("WROTE:", output_png)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python fig2_boundary_segment_delta.py input.csv output.png")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])