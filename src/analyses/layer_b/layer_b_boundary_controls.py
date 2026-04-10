#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path
from statistics import mean, pstdev

DIGRAPHS = ("sh", "kh", "ts")
BOUNDARY = "|"


# -----------------------
# Tokenization
# -----------------------

def tokenize(word: str):
    out = []
    i = 0
    while i < len(word):
        two = word[i:i + 2]
        if two in DIGRAPHS:
            out.append(two)
            i += 2
        else:
            out.append(word[i])
            i += 1
    return out


# -----------------------
# Loading
# -----------------------

def load_segments(path: Path):
    words = path.read_text(encoding="utf8").split()

    segments = []
    current = []

    for w in words:
        if w == BOUNDARY:
            if current:
                segments.append(current)
            current = []
        else:
            current.extend(tokenize(w))

    if current:
        segments.append(current)

    return segments


def flatten(segments):
    return [x for s in segments for x in s]


# -----------------------
# k-grams and gap
# -----------------------

def kgram_positions(stream, k):
    pos = defaultdict(list)
    for i in range(len(stream) - k + 1):
        g = tuple(stream[i:i + k])
        pos[g].append(i)
    return pos


def collect_gaps_from_positions(pos_dict):
    gaps = []
    for positions in pos_dict.values():
        if len(positions) > 1:
            for i in range(len(positions) - 1):
                gaps.append(positions[i + 1] - positions[i])
    return gaps


def gap_metric(stream, k):
    pos = kgram_positions(stream, k)
    gaps = collect_gaps_from_positions(pos)
    return mean(gaps) if gaps else None


def gap_metric_segments(segments, k):
    """
    Proper boundary-aware gap:
    collect ALL within-segment gaps and compute global mean.
    """
    all_gaps = []

    for seg in segments:
        pos = kgram_positions(seg, k)
        gaps = collect_gaps_from_positions(pos)
        all_gaps.extend(gaps)

    return mean(all_gaps) if all_gaps else None


# -----------------------
# Null models
# -----------------------

def zscore(obs, values):
    vals = [x for x in values if x is not None]
    if not vals:
        return None, None, None
    mu = mean(vals)
    sd = pstdev(vals)
    z = None if sd == 0 else (obs - mu) / sd
    return mu, sd, z


def full_shuffle_null(stream, k, perm, seed):
    rng = random.Random(seed)
    vals = []

    for p in range(perm):
        if (p + 1) % max(1, perm // 10) == 0 or p == 0 or p + 1 == perm:
            print(f"  perm {p + 1}/{perm}")

        s = stream[:]
        rng.shuffle(s)
        vals.append(gap_metric(s, k))

    return vals


def segment_shuffle_null(segments, k, perm, seed):
    rng = random.Random(seed)
    vals = []

    for p in range(perm):
        if (p + 1) % max(1, perm // 10) == 0 or p == 0 or p + 1 == perm:
            print(f"  perm {p + 1}/{perm}")

        segs = segments[:]
        rng.shuffle(segs)
        vals.append(gap_metric(flatten(segs), k))

    return vals


# -----------------------
# Core run
# -----------------------

def run_one(file_path: Path, k: int, perm: int, seed: int):
    segments = load_segments(file_path)
    stream = flatten(segments)

    book = file_path.stem.replace("_phonetic", "")

    print("=" * 72)
    print(f"BOOK: {book}")
    print(f"k={k}  perm={perm}")

    # baseline
    gap_base = gap_metric(stream, k)
    gap_boundary = gap_metric_segments(segments, k)

    print("  computing full-shuffle null...")
    null_full = full_shuffle_null(stream, k, perm, seed)
    mu_full, sd_full, z_full = zscore(gap_base, null_full)

    print("  computing segment-shuffle null...")
    null_seg = segment_shuffle_null(segments, k, perm, seed)
    mu_seg, sd_seg, z_seg = zscore(gap_base, null_seg)

    print(f"gap baseline: {fmt(gap_base)}")
    print(f"gap boundary: {fmt(gap_boundary)}")
    print(f"Z full: {fmt(z_full)}")
    print(f"Z segment: {fmt(z_seg)}")

    return {
        "file": str(file_path),
        "book": book,
        "k": k,
        "perm": perm,
        "seed": seed,
        "gap_baseline": gap_base,
        "gap_boundary": gap_boundary,
        "null_full_mean": mu_full,
        "null_full_sd": sd_full,
        "z_full": z_full,
        "null_segment_mean": mu_seg,
        "null_segment_sd": sd_seg,
        "z_segment": z_seg,
    }

# -----------------------
# Utils
# -----------------------

def fmt(x):
    return "NA" if x is None else f"{x:.6f}"


def save_csv(path: Path, rows):
    if not rows:
        return
    with path.open("w", encoding="utf8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


# -----------------------
# Main
# -----------------------

def main():
    ap = argparse.ArgumentParser(description="Layer B boundary controls")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--perm", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--tag", default="baseline")
    args = ap.parse_args()

    run_dir = Path(args.out_dir) / args.tag
    run_dir.mkdir(parents=True, exist_ok=True)

    rows = []

    print("FILES TO PROCESS:")
    for f in args.files:
        print(" ", f)
    print()

    for f in args.files:
        res = run_one(Path(f), args.k, args.perm, args.seed)

        print("=" * 72)
        print(f"BOOK: {res['book']}")
        print(f"k={res['k']}  perm={res['perm']}")
        print(f"gap baseline: {fmt(res['gap_baseline'])}")
        print(f"gap boundary: {fmt(res['gap_boundary'])}")
        print(f"Z full: {fmt(res['z_full'])}")
        print(f"Z segment: {fmt(res['z_segment'])}")

        rows.append(res)

    save_csv(run_dir / "layer_b_boundary_controls_summary.csv", rows)

    print(f"\nWROTE: {run_dir / 'layer_b_boundary_controls_summary.csv'}")


if __name__ == "__main__":
    main()