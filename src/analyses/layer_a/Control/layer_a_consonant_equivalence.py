#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import json
import math
import random
from collections import Counter
from statistics import mean, pstdev
from typing import List, Tuple
from pathlib import Path
import sys


DIGRAPHS = ("sh", "kh", "ts")
VOWELS = {"a", "e", "i", "o", "u"}
BOUNDARY = "|"

EQUIV_MAP = {
    "f": "fv", "v": "fv",
    "k": "kq", "q": "kq",
    "s": "sz", "z": "sz",
}

def map_equiv(atom: str) -> str:
    return EQUIV_MAP.get(atom, atom)

def tokenize_word(word: str) -> List[str]:
    """Tokenize a transliterated token into phonetic atoms, keeping sh/kh/ts atomic."""
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


def corpus_name_from_path(path: str) -> str:
    stem = Path(path).stem.lower()
    if stem.endswith("_phonetic_qo"):
        stem = stem[:-12]
    elif stem.endswith("_phonetic"):
        stem = stem[:-9]
    return stem


def load_consonant_segments(path: str, respect_boundaries: bool = False) -> List[List[str]]:
    """
    Load phonetic corpus and return consonant segments.

    Baseline mode (respect_boundaries=False):
        - remove '|'
        - one continuous consonant stream

    Boundary-aware mode:
        - split on '|'
        - windows do not cross boundaries
    """
    with open(path, "r", encoding="utf8") as f:
        text = f.read().strip()

    if not text:
        return [[]]

    raw_tokens = text.split()

    if not respect_boundaries:
        stream = []
        for tok in raw_tokens:
            if tok == BOUNDARY:
                continue
            ph = tokenize_word(tok)
            cons = [map_equiv(p) for p in ph if p not in VOWELS]
            stream.extend(cons)
        return [stream]

    segments = []
    current = []

    for tok in raw_tokens:
        if tok == BOUNDARY:
            if current:
                segments.append(current)
                current = []
            continue

        ph = tokenize_word(tok)
        cons = [p for p in ph if p not in VOWELS]
        current.extend(cons)

    if current:
        segments.append(current)

    if not segments:
        segments = [[]]

    return segments


def build_windows_from_segments(segments: List[List[str]], W: int, step: int) -> List[List[str]]:
    """Build sliding windows inside each segment independently."""
    windows = []
    for seg in segments:
        if len(seg) < W:
            continue
        for i in range(0, len(seg) - W + 1, step):
            windows.append(seg[i:i + W])
    return windows


def top_families(window: List[str], top_n: int) -> Tuple[str, ...]:
    """
    Return top-N consonant atoms ranked by:
    1) descending frequency
    2) alphabetic order as deterministic tie-break
    """
    c = Counter(window)
    ranked = sorted(c.items(), key=lambda x: (-x[1], x[0]))
    return tuple(x[0] for x in ranked[:top_n])


def window_profiles(windows: List[List[str]], top_n: int) -> List[Tuple[str, ...]]:
    return [top_families(w, top_n) for w in windows]


def overlap(a: Tuple[str, ...], b: Tuple[str, ...]) -> int:
    return len(set(a) & set(b))


def global_recurrence_score(profiles: List[Tuple[str, ...]], max_lag: int) -> float:
    """Mean overlap across all pairs for lags 1..max_lag, weighted by pair count."""
    n = len(profiles)
    total_overlap = 0.0
    total_pairs = 0

    for lag in range(1, max_lag + 1):
        for i in range(n - lag):
            total_overlap += overlap(profiles[i], profiles[i + lag])
            total_pairs += 1

    return total_overlap / total_pairs if total_pairs > 0 else math.nan


def short_lag_score(profiles: List[Tuple[str, ...]], lag_from: int, lag_to: int) -> float:
    """Mean overlap across short lags, weighted by pair count."""
    n = len(profiles)
    total_overlap = 0.0
    total_pairs = 0

    for lag in range(lag_from, lag_to + 1):
        for i in range(n - lag):
            total_overlap += overlap(profiles[i], profiles[i + lag])
            total_pairs += 1

    return total_overlap / total_pairs if total_pairs > 0 else math.nan


def lag_profile(profiles: List[Tuple[str, ...]], max_lag: int):
    rows = []
    n = len(profiles)

    for lag in range(1, max_lag + 1):
        vals = []
        for i in range(n - lag):
            vals.append(overlap(profiles[i], profiles[i + lag]))

        rows.append({
            "lag": lag,
            "mean_overlap": mean(vals) if vals else math.nan,
            "n_pairs": len(vals),
        })

    return rows


def block_shuffle_segment(segment: List[str], block_size: int, rng: random.Random) -> List[str]:
    """Shuffle a segment in non-overlapping blocks."""
    if len(segment) <= 1:
        return segment[:]

    if block_size <= 1:
        s = segment[:]
        rng.shuffle(s)
        return s

    blocks = [segment[i:i + block_size] for i in range(0, len(segment), block_size)]
    rng.shuffle(blocks)

    out = []
    for b in blocks:
        out.extend(b)
    return out


def block_shuffle_segments(segments: List[List[str]], block_size: int, rng: random.Random) -> List[List[str]]:
    return [block_shuffle_segment(seg, block_size, rng) for seg in segments]


def zscore(obs: float, arr: List[float]):
    vals = [x for x in arr if x == x]
    if not vals:
        return math.nan, math.nan, math.nan
    mu = mean(vals)
    sd = pstdev(vals)
    z = math.nan if sd == 0 else (obs - mu) / sd
    return mu, sd, z


def null_distribution(
    segments: List[List[str]],
    W: int,
    step: int,
    top_n: int,
    max_lag: int,
    block: int,
    perm: int,
    seed: int,
    short_lag_to: int,
    progress_every: int = 100,
):
    rng = random.Random(seed)
    global_vals = []
    short_vals = []
    lag_null = {lag: [] for lag in range(1, max_lag + 1)}

    for p in range(perm):
        if progress_every > 0 and ((p + 1) % progress_every == 0 or p == 0 or p + 1 == perm):
            print(f"  perm {p + 1}/{perm}")

        shuf_segments = block_shuffle_segments(segments, block, rng)
        wins = build_windows_from_segments(shuf_segments, W, step)
        profs = window_profiles(wins, top_n)

        g = global_recurrence_score(profs, max_lag)
        s = short_lag_score(profs, 1, min(short_lag_to, max_lag))
        lp = lag_profile(profs, max_lag)

        global_vals.append(g)
        short_vals.append(s)

        for row in lp:
            lag_null[row["lag"]].append(row["mean_overlap"])

    return global_vals, short_vals, lag_null


def run_file(path, W, step, top_n, max_lag, block, perm, seed, respect_boundaries, short_lag_to):
    corpus = corpus_name_from_path(path)
    segments = load_consonant_segments(path, respect_boundaries=respect_boundaries)
    stream_len = sum(len(seg) for seg in segments)
    seg_lens = [len(s) for s in segments if len(s) > 0]

    wins = build_windows_from_segments(segments, W, step)

    print("=" * 72)
    print(f"CORPUS             = {corpus}")
    print(f"FILE               = {path}")
    print(f"respect_boundaries = {int(respect_boundaries)}")
    print(f"segments           = {len(segments)}")
    print(f"stream_len         = {stream_len}")
    if seg_lens:
        print(f"segment_len_minmax = {min(seg_lens)} .. {max(seg_lens)}")
    else:
        print("segment_len_minmax = 0 .. 0")
    print(f"W / step           = {W} / {step}")
    print(f"top_n              = {top_n}")
    print(f"max_lag            = {max_lag}")
    print(f"block / perm       = {block} / {perm}")
    print(f"seed               = {seed}")

    if stream_len == 0:
        raise ValueError(f"No consonant stream extracted from file: {path}")

    if len(wins) == 0:
        raise ValueError(
            f"No windows formed for file {path}. "
            f"Try smaller --W or disable --respect_boundaries."
        )

    profs = window_profiles(wins, top_n)

    obs_global = global_recurrence_score(profs, max_lag)
    obs_short = short_lag_score(profs, 1, min(short_lag_to, max_lag))
    lp_obs = lag_profile(profs, max_lag)

    print(f"n_windows          = {len(wins)}")
    print("Building null...")

    null_global, null_short, lag_null = null_distribution(
        segments=segments,
        W=W,
        step=step,
        top_n=top_n,
        max_lag=max_lag,
        block=block,
        perm=perm,
        seed=seed,
        short_lag_to=short_lag_to,
        progress_every=max(1, perm // 10),
    )

    mu_g, sd_g, z_g = zscore(obs_global, null_global)
    mu_s, sd_s, z_s = zscore(obs_short, null_short)

    lag_rows = []
    for row in lp_obs:
        lag = row["lag"]
        mu_l, sd_l, z_l = zscore(row["mean_overlap"], lag_null.get(lag, []))
        lag_rows.append({
            "corpus": corpus,
            "file_path": str(Path(path).resolve()),
            "respect_boundaries": int(respect_boundaries),
            "stream_len": stream_len,
            "n_segments": len(segments),
            "n_windows": len(wins),
            "W": W,
            "step": step,
            "top_n": top_n,
            "max_lag": max_lag,
            "block": block,
            "perm": perm,
            "seed": seed,
            "short_lag_to": short_lag_to,
            "lag": lag,
            "mean_overlap_obs": row["mean_overlap"],
            "mean_overlap_null_mean": mu_l,
            "mean_overlap_null_sd": sd_l,
            "z_lag_overlap": z_l,
            "n_pairs": row["n_pairs"],
        })

    best = max(lp_obs, key=lambda x: x["mean_overlap"]) if lp_obs else None
    best_lag = best["lag"] if best else math.nan
    best_overlap = best["mean_overlap"] if best else math.nan

    summary = {
        "corpus": corpus,
        "file_path": str(Path(path).resolve()),
        "respect_boundaries": int(respect_boundaries),
        "stream_len": stream_len,
        "n_segments": len(segments),
        "n_windows": len(wins),
        "W": W,
        "step": step,
        "top_n": top_n,
        "max_lag": max_lag,
        "block": block,
        "perm": perm,
        "seed": seed,
        "short_lag_to": short_lag_to,
        "global_overlap_obs": obs_global,
        "global_overlap_null_mean": mu_g,
        "global_overlap_null_sd": sd_g,
        "z_global_overlap": z_g,
        "short_overlap_obs": obs_short,
        "short_overlap_null_mean": mu_s,
        "short_overlap_null_sd": sd_s,
        "z_short_overlap": z_s,
        "best_lag": best_lag,
        "best_lag_overlap": best_overlap,
    }

    return summary, lag_rows


def print_summary(res: dict):
    print("-" * 72)
    print("RESULT")
    ordered_keys = [
        "corpus",
        "respect_boundaries",
        "stream_len",
        "n_segments",
        "n_windows",
        "W",
        "step",
        "top_n",
        "max_lag",
        "block",
        "perm",
        "seed",
        "short_lag_to",
        "global_overlap_obs",
        "global_overlap_null_mean",
        "global_overlap_null_sd",
        "z_global_overlap",
        "short_overlap_obs",
        "short_overlap_null_mean",
        "short_overlap_null_sd",
        "z_short_overlap",
        "best_lag",
        "best_lag_overlap",
    ]
    for k in ordered_keys:
        print(f"{k}: {res[k]}")
    print()


def write_csv(path: Path, rows: List[dict]):
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf8") as out:
        w = csv.DictWriter(out, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def write_json(path: Path, obj: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def main():
    ap = argparse.ArgumentParser(
        description="Layer A consonant-unit top-N recurrence (locked baseline logic)"
    )
    ap.add_argument("files", nargs="+", help="Input phonetic files (explicit list)")
    ap.add_argument("--out_dir", required=True, help="Output directory")
    ap.add_argument("--tag", default="baseline", help="Run tag (lower-case recommended)")
    ap.add_argument("--W", type=int, default=150)
    ap.add_argument("--step", type=int, default=25)
    ap.add_argument("--top_n", type=int, default=3)
    ap.add_argument("--max_lag", type=int, default=20)
    ap.add_argument("--short_lag_to", type=int, default=5)
    ap.add_argument("--block", type=int, default=80)
    ap.add_argument("--perm", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--respect_boundaries", type=int, choices=[0, 1], default=0)
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    run_dir = out_dir / args.tag
    run_dir.mkdir(parents=True, exist_ok=True)

    print("FILES TO PROCESS:")
    for f in args.files:
        print(" ", f)
    print()

    summary_rows = []
    lag_rows_all = []

    for f in args.files:
        try:
            summary, lag_rows = run_file(
                path=f,
                W=args.W,
                step=args.step,
                top_n=args.top_n,
                max_lag=args.max_lag,
                block=args.block,
                perm=args.perm,
                seed=args.seed,
                respect_boundaries=bool(args.respect_boundaries),
                short_lag_to=args.short_lag_to,
            )
            print_summary(summary)
            summary_rows.append(summary)
            lag_rows_all.extend(lag_rows)

            corpus = summary["corpus"]
            corpus_dir = run_dir / "books" / corpus
            write_csv(corpus_dir / f"layer_a_{args.tag}_summary.csv", [summary])
            write_csv(corpus_dir / f"layer_a_{args.tag}_lag_profile.csv", lag_rows)

        except Exception as e:
            print(f"ERROR while processing {f}: {e}")
            print()

    if not summary_rows:
        print("No successful outputs were produced.")
        sys.exit(1)

    important_rows = []
    for row in summary_rows:
        important_rows.append({
            "corpus": row["corpus"],
            "z_global_overlap": row["z_global_overlap"],
            "z_short_overlap": row["z_short_overlap"],
            "best_lag": row["best_lag"],
            "best_lag_overlap": row["best_lag_overlap"],
            "n_windows": row["n_windows"],
            "stream_len": row["stream_len"],
            "respect_boundaries": row["respect_boundaries"],
            "W": row["W"],
            "step": row["step"],
            "top_n": row["top_n"],
            "max_lag": row["max_lag"],
            "block": row["block"],
            "perm": row["perm"],
            "seed": row["seed"],
        })

    summary_rows_sorted = sorted(summary_rows, key=lambda x: x["corpus"])
    lag_rows_sorted = sorted(lag_rows_all, key=lambda x: (x["corpus"], x["lag"]))
    important_rows_sorted = sorted(important_rows, key=lambda x: x["corpus"])

    write_csv(run_dir / f"layer_a_{args.tag}_summary_all.csv", summary_rows_sorted)
    write_csv(run_dir / f"layer_a_{args.tag}_lag_profile_all.csv", lag_rows_sorted)
    write_csv(run_dir / f"layer_a_{args.tag}_important_summary.csv", important_rows_sorted)

    manifest = {
        "script": "layer_a_consonant_family.py",
        "tag": args.tag,
        "files": [str(Path(f).resolve()) for f in args.files],
        "params": {
            "W": args.W,
            "step": args.step,
            "top_n": args.top_n,
            "max_lag": args.max_lag,
            "short_lag_to": args.short_lag_to,
            "block": args.block,
            "perm": args.perm,
            "seed": args.seed,
            "respect_boundaries": args.respect_boundaries,
        },
        "outputs": {
            "summary_all_csv": str((out_dir / f"layer_a_{args.tag}_summary_all.csv").resolve()),
            "lag_profile_all_csv": str((out_dir / f"layer_a_{args.tag}_lag_profile_all.csv").resolve()),
            "important_summary_csv": str((out_dir / f"layer_a_{args.tag}_important_summary.csv").resolve()),
        },
    }
    write_json(out_dir / f"layer_a_{args.tag}_run_manifest.json", manifest)

    print("=" * 72)
    print("TOP-LINE RESULTS")
    for row in important_rows_sorted:
        print(
            f"{row['corpus']}: "
            f"z_global={row['z_global_overlap']:.3f}  "
            f"z_short={row['z_short_overlap']:.3f}  "
            f"best_lag={row['best_lag']}  "
            f"best_overlap={row['best_lag_overlap']:.3f}"
        )

    print()
    print(f"WROTE: {out_dir / f'layer_a_{args.tag}_summary_all.csv'}")
    print(f"WROTE: {out_dir / f'layer_a_{args.tag}_lag_profile_all.csv'}")
    print(f"WROTE: {out_dir / f'layer_a_{args.tag}_important_summary.csv'}")
    print(f"WROTE: {out_dir / f'layer_a_{args.tag}_run_manifest.json'}")


if __name__ == "__main__":
    main()