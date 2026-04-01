#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import math
import random
from collections import Counter
from statistics import mean, pstdev
from typing import List, Tuple, Set


DIGRAPHS = ("sh", "kh", "ts")
VOWELS = {"a", "e", "i", "o", "u"}
BOUNDARY = "|"


# =========================================================
# PHONETIC LOADING
# =========================================================

def tokenize_word(word: str) -> List[str]:
    out = []
    i = 0
    while i < len(word):
        two = word[i:i+2]
        if two in DIGRAPHS:
            out.append(two)
            i += 2
        else:
            out.append(word[i])
            i += 1
    return out


def load_consonant_stream(path: str) -> List[str]:
    with open(path, "r", encoding="utf8") as f:
        text = f.read().strip()

    if not text:
        return []

    stream = []
    for tok in text.split():
        if tok == BOUNDARY:
            continue
        ph = tokenize_word(tok)
        cons = [p for p in ph if p not in VOWELS]
        stream.extend(cons)
    return stream


# =========================================================
# SEGMENTS (NON-OVERLAPPING)
# =========================================================

def build_segments(stream: List[str], L: int) -> List[List[str]]:
    if L <= 0:
        raise ValueError("L must be > 0")
    n_full = len(stream) // L
    return [stream[i*L:(i+1)*L] for i in range(n_full)]


# =========================================================
# DOMINANT SET
# mode = topk or freqmin
# =========================================================

def dominant_set(seg: List[str], mode: str, k: int, min_freq: int) -> Tuple[str, ...]:
    c = Counter(seg)
    ranked = sorted(c.items(), key=lambda x: (-x[1], x[0]))

    if mode == "topk":
        chosen = [x[0] for x in ranked[:k]]
    elif mode == "freqmin":
        chosen = [sym for sym, cnt in ranked if cnt >= min_freq]
    else:
        raise ValueError(f"Unknown mode: {mode}")

    return tuple(sorted(chosen))


def dominant_sets(segments: List[List[str]], mode: str, k: int, min_freq: int) -> List[Tuple[str, ...]]:
    return [dominant_set(seg, mode, k, min_freq) for seg in segments]


# =========================================================
# METRICS
# =========================================================

def jaccard(a: Set[str], b: Set[str]) -> float:
    union = a | b
    if not union:
        return math.nan
    return len(a & b) / len(union)


def adjacent_jaccard_mean(dsets: List[Tuple[str, ...]]) -> float:
    vals = []
    for i in range(len(dsets) - 1):
        a = set(dsets[i])
        b = set(dsets[i + 1])
        v = jaccard(a, b)
        if v == v:
            vals.append(v)
    return mean(vals) if vals else math.nan


def lag_jaccard_profile(dsets: List[Tuple[str, ...]], max_lag: int):
    rows = []
    n = len(dsets)
    for lag in range(1, max_lag + 1):
        vals = []
        for i in range(n - lag):
            a = set(dsets[i])
            b = set(dsets[i + lag])
            v = jaccard(a, b)
            if v == v:
                vals.append(v)
        rows.append({
            "lag": lag,
            "mean_jaccard": mean(vals) if vals else math.nan,
            "n_pairs": len(vals)
        })
    return rows


def recurrence_rate(dsets: List[Tuple[str, ...]], R: int, min_jaccard: float) -> float:
    """
    For each segment i, check whether a similar dominant set reappears
    within the next R segments.
    """
    hits = 0
    total = 0
    n = len(dsets)

    for i in range(n):
        a = set(dsets[i])
        found = False
        for j in range(i + 1, min(n, i + 1 + R)):
            b = set(dsets[j])
            v = jaccard(a, b)
            if v == v and v >= min_jaccard:
                found = True
                break
        hits += int(found)
        total += 1

    return hits / total if total > 0 else math.nan


def dominance_mass(segments: List[List[str]], dsets: List[Tuple[str, ...]]) -> float:
    vals = []
    for seg, ds in zip(segments, dsets):
        if not seg:
            continue
        d = set(ds)
        covered = sum(1 for x in seg if x in d)
        vals.append(covered / len(seg))
    return mean(vals) if vals else math.nan


# =========================================================
# NULL
# =========================================================

def block_shuffle(stream: List[str], block: int, rng: random.Random) -> List[str]:
    if len(stream) <= 1:
        return stream[:]

    if block <= 1:
        s = stream[:]
        rng.shuffle(s)
        return s

    blocks = [stream[i:i+block] for i in range(0, len(stream), block)]
    rng.shuffle(blocks)

    out = []
    for b in blocks:
        out.extend(b)
    return out


def zscore(obs: float, arr: List[float]):
    vals = [x for x in arr if x == x]
    if not vals:
        return math.nan, math.nan, math.nan
    mu = mean(vals)
    sd = pstdev(vals)
    z = math.nan if sd == 0 else (obs - mu) / sd
    return mu, sd, z


# =========================================================
# ANALYSIS
# =========================================================

def analyze_file(
    path: str,
    L: int,
    mode: str,
    k: int,
    min_freq: int,
    max_lag: int,
    R: int,
    min_jaccard: float,
    block: int,
    perm: int,
    seed: int
):
    stream = load_consonant_stream(path)
    segments = build_segments(stream, L)
    dsets = dominant_sets(segments, mode, k, min_freq)

    if len(segments) < max(2, max_lag + 1):
        raise ValueError(f"Too few full segments for analysis: {len(segments)}")

    obs_adj = adjacent_jaccard_mean(dsets)
    obs_rec = recurrence_rate(dsets, R, min_jaccard)
    obs_mass = dominance_mass(segments, dsets)
    obs_lag = lag_jaccard_profile(dsets, max_lag)

    rng = random.Random(seed)

    null_adj = []
    null_rec = []
    null_mass = []
    lag_null = {lag: [] for lag in range(1, max_lag + 1)}

    for p in range(perm):
        if (p + 1) % max(1, perm // 10) == 0 or p == 0 or p + 1 == perm:
            print(f"  perm {p+1}/{perm}")

        shuf = block_shuffle(stream, block, rng)
        shuf_segments = build_segments(shuf, L)
        shuf_dsets = dominant_sets(shuf_segments, mode, k, min_freq)

        null_adj.append(adjacent_jaccard_mean(shuf_dsets))
        null_rec.append(recurrence_rate(shuf_dsets, R, min_jaccard))
        null_mass.append(dominance_mass(shuf_segments, shuf_dsets))

        lp = lag_jaccard_profile(shuf_dsets, max_lag)
        for row in lp:
            lag_null[row["lag"]].append(row["mean_jaccard"])

    mu_adj, sd_adj, z_adj = zscore(obs_adj, null_adj)
    mu_rec, sd_rec, z_rec = zscore(obs_rec, null_rec)
    mu_mass, sd_mass, z_mass = zscore(obs_mass, null_mass)

    lag_rows = []
    for row in obs_lag:
        mu_l, sd_l, z_l = zscore(row["mean_jaccard"], lag_null[row["lag"]])
        lag_rows.append({
            "file": path,
            "L": L,
            "mode": mode,
            "k": k if mode == "topk" else "",
            "min_freq": min_freq if mode == "freqmin" else "",
            "max_lag": max_lag,
            "R": R,
            "min_jaccard": min_jaccard,
            "block": block,
            "perm": perm,
            "seed": seed,
            "lag": row["lag"],
            "mean_jaccard_obs": row["mean_jaccard"],
            "mean_jaccard_null_mean": mu_l,
            "mean_jaccard_null_sd": sd_l,
            "Z_lag_jaccard": z_l,
            "n_pairs": row["n_pairs"]
        })

    summary = {
        "file": path,
        "stream_len": len(stream),
        "n_segments": len(segments),
        "L": L,
        "mode": mode,
        "k": k if mode == "topk" else "",
        "min_freq": min_freq if mode == "freqmin" else "",
        "max_lag": max_lag,
        "R": R,
        "min_jaccard": min_jaccard,
        "block": block,
        "perm": perm,
        "seed": seed,
        "adjacent_jaccard_obs": obs_adj,
        "adjacent_jaccard_null_mean": mu_adj,
        "adjacent_jaccard_null_sd": sd_adj,
        "Z_adjacent_jaccard": z_adj,
        "recurrence_rate_obs": obs_rec,
        "recurrence_rate_null_mean": mu_rec,
        "recurrence_rate_null_sd": sd_rec,
        "Z_recurrence_rate": z_rec,
        "dominance_mass_obs": obs_mass,
        "dominance_mass_null_mean": mu_mass,
        "dominance_mass_null_sd": sd_mass,
        "Z_dominance_mass": z_mass
    }

    return summary, lag_rows


# =========================================================
# IO
# =========================================================

def write_csv(path: str, rows: List[dict]):
    if not path or not rows:
        return
    with open(path, "w", newline="", encoding="utf8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def print_summary(s: dict):
    print("=" * 72)
    for k, v in s.items():
        print(f"{k}: {v}")


# =========================================================
# MAIN
# =========================================================

def main():
    ap = argparse.ArgumentParser(description="Layer A+ — Local Dominant Consonant Sets")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--L", type=int, default=150, help="Non-overlapping segment length")
    ap.add_argument("--mode", choices=["topk", "freqmin"], default="topk")
    ap.add_argument("--k", type=int, default=3, help="Used in mode=topk")
    ap.add_argument("--min_freq", type=int, default=2, help="Used in mode=freqmin")
    ap.add_argument("--max_lag", type=int, default=10)
    ap.add_argument("--R", type=int, default=5, help="Recurrence horizon in segments")
    ap.add_argument("--min_jaccard", type=float, default=0.5)
    ap.add_argument("--block", type=int, default=80)
    ap.add_argument("--perm", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--csv", default="ldcs_summary.csv")
    ap.add_argument("--lag_csv", default="ldcs_lag_profile.csv")
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--tag", default="baseline")
    args = ap.parse_args()

    summaries = []
    lag_rows_all = []

    print("FILES TO PROCESS:")
    for f in args.files:
        print(" ", f)

    for f in args.files:
        print(f"\nProcessing: {f}")
        s, lag_rows = analyze_file(
            path=f,
            L=args.L,
            mode=args.mode,
            k=args.k,
            min_freq=args.min_freq,
            max_lag=args.max_lag,
            R=args.R,
            min_jaccard=args.min_jaccard,
            block=args.block,
            perm=args.perm,
            seed=args.seed
        )
        print_summary(s)
        summaries.append(s)
        lag_rows_all.extend(lag_rows)

        from pathlib import Path
        import json
        import os

        out_root = Path(args.out_dir)
        run_dir = out_root / args.tag
        run_dir.mkdir(parents=True, exist_ok=True)

        books_dir = run_dir / "books"
        books_dir.mkdir(exist_ok=True)

        # per-book
        for s in summaries:
            corpus = Path(s["file"]).stem.replace("_phonetic", "")
            cdir = books_dir / corpus
            cdir.mkdir(exist_ok=True)

            write_csv(
                cdir / f"layer_a_plus_{args.tag}_summary.csv",
                [s]
            )

        # combined
        write_csv(
            run_dir / f"layer_a_plus_{args.tag}_summary_all.csv",
            summaries
        )

        write_csv(
            run_dir / f"layer_a_plus_{args.tag}_lag_profile_all.csv",
            lag_rows_all
        )

        # important summary
        important = []
        for s in summaries:
            important.append({
                "corpus": Path(s["file"]).stem.replace("_phonetic", ""),
                "z_adjacent": s["Z_adjacent_jaccard"],
                "z_recurrence": s["Z_recurrence_rate"],
                "z_mass": s["Z_dominance_mass"],
                "n_segments": s["n_segments"]
            })

        write_csv(
            run_dir / f"layer_a_plus_{args.tag}_important_summary.csv",
            important
        )

        # manifest
        manifest = vars(args)
        manifest["files"] = args.files

        with open(run_dir / f"layer_a_plus_{args.tag}_run_manifest.json", "w", encoding="utf8") as f:
            json.dump(manifest, f, indent=2)

        print(f"\nWROTE: {run_dir}")

    print(f"\nWROTE: {args.csv}")
    print(f"WROTE: {args.lag_csv}")

    print("\nTOP-LINE RESULTS")
    for s in summaries:
        corpus = Path(s["file"]).stem.replace("_phonetic", "")
        print(
            f"{corpus}: "
            f"z_adj={s['Z_adjacent_jaccard']:.3f}  "
            f"z_rec={s['Z_recurrence_rate']:.3f}  "
            f"z_mass={s['Z_dominance_mass']:.3f}"
        )

if __name__ == "__main__":
    main()