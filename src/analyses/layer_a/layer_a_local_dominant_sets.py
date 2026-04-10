#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path
from statistics import mean, pstdev
from typing import Dict, List, Sequence, Set, Tuple


DIGRAPHS = ("sh", "kh", "ts")
VOWELS = {"a", "e", "i", "o", "u"}
BOUNDARY = "|"


def tokenize_word(word: str) -> List[str]:
    """Tokenize transliterated token into phonetic atoms, keeping sh/kh/ts atomic."""
    out: List[str] = []
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


def load_consonant_stream(path: str) -> List[str]:
    """Load phonetic corpus and return continuous consonant stream with boundaries removed."""
    text = Path(path).read_text(encoding="utf8").strip()
    if not text:
        return []

    stream: List[str] = []
    for tok in text.split():
        if tok == BOUNDARY:
            continue
        atoms = tokenize_word(tok)
        consonants = [a for a in atoms if a not in VOWELS]
        stream.extend(consonants)
    return stream


def build_segments(stream: Sequence[str], L: int) -> List[List[str]]:
    """Build non-overlapping full segments of length L; discard remainder."""
    if L <= 0:
        raise ValueError("L must be > 0")
    n_full = len(stream) // L
    return [list(stream[i * L:(i + 1) * L]) for i in range(n_full)]


def dominant_set(seg: Sequence[str], mode: str, k: int, min_freq: int) -> Tuple[str, ...]:
    """
    Build dominant set for one segment.

    mode=topk   : keep top-k consonants by frequency, alphabetical tie-break
    mode=freqmin: keep all consonants with count >= min_freq
    """
    counts = Counter(seg)
    ranked = sorted(counts.items(), key=lambda x: (-x[1], x[0]))

    if mode == "topk":
        chosen = [sym for sym, _ in ranked[:k]]
    elif mode == "freqmin":
        chosen = [sym for sym, cnt in ranked if cnt >= min_freq]
    else:
        raise ValueError(f"Unknown mode: {mode}")

    return tuple(sorted(chosen))


def dominant_sets(
    segments: Sequence[Sequence[str]],
    mode: str,
    k: int,
    min_freq: int,
) -> List[Tuple[str, ...]]:
    return [dominant_set(seg, mode, k, min_freq) for seg in segments]


def jaccard(a: Set[str], b: Set[str]) -> float:
    union = a | b
    if not union:
        return math.nan
    return len(a & b) / len(union)


def adjacent_jaccard_mean(dsets: Sequence[Tuple[str, ...]]) -> float:
    vals: List[float] = []
    for i in range(len(dsets) - 1):
        v = jaccard(set(dsets[i]), set(dsets[i + 1]))
        if v == v:
            vals.append(v)
    return mean(vals) if vals else math.nan


def lag_jaccard_profile(dsets: Sequence[Tuple[str, ...]], max_lag: int) -> List[Dict]:
    rows: List[Dict] = []
    n = len(dsets)

    for lag in range(1, max_lag + 1):
        vals: List[float] = []
        for i in range(n - lag):
            v = jaccard(set(dsets[i]), set(dsets[i + lag]))
            if v == v:
                vals.append(v)

        rows.append(
            {
                "lag": lag,
                "mean_jaccard": mean(vals) if vals else math.nan,
                "n_pairs": len(vals),
            }
        )

    return rows


def recurrence_rate(dsets: Sequence[Tuple[str, ...]], R: int, min_jaccard: float) -> float:
    """
    Fraction of segments whose dominant set reappears within the next R segments
    with Jaccard >= min_jaccard.
    """
    hits = 0
    total = 0
    n = len(dsets)

    for i in range(n):
        a = set(dsets[i])
        found = False
        for j in range(i + 1, min(n, i + 1 + R)):
            v = jaccard(a, set(dsets[j]))
            if v == v and v >= min_jaccard:
                found = True
                break
        hits += int(found)
        total += 1

    return hits / total if total > 0 else math.nan


def dominance_mass(
    segments: Sequence[Sequence[str]],
    dsets: Sequence[Tuple[str, ...]],
) -> float:
    """Mean fraction of segment tokens covered by its dominant set."""
    vals: List[float] = []
    for seg, ds in zip(segments, dsets):
        if not seg:
            continue
        ds_set = set(ds)
        covered = sum(1 for x in seg if x in ds_set)
        vals.append(covered / len(seg))
    return mean(vals) if vals else math.nan


def block_shuffle(stream: Sequence[str], block: int, rng: random.Random) -> List[str]:
    """
    Block-permutation null:
    - split into full non-overlapping blocks of size `block`
    - shuffle full blocks
    - preserve internal order inside each block
    - keep trailing remainder in place
    """
    if len(stream) <= 1:
        return list(stream)

    if block <= 1:
        shuffled = list(stream)
        rng.shuffle(shuffled)
        return shuffled

    n_full = (len(stream) // block) * block
    blocks = [list(stream[i:i + block]) for i in range(0, n_full, block)]
    tail = list(stream[n_full:])

    rng.shuffle(blocks)

    out: List[str] = []
    for b in blocks:
        out.extend(b)
    out.extend(tail)
    return out


def zscore(obs: float, arr: Sequence[float]) -> Tuple[float, float, float]:
    vals = [x for x in arr if x == x]
    if not vals:
        return math.nan, math.nan, math.nan
    mu = mean(vals)
    sd = pstdev(vals)
    z = math.nan if sd == 0 else (obs - mu) / sd
    return mu, sd, z


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
    seed: int,
) -> Tuple[Dict, List[Dict]]:
    corpus = corpus_name_from_path(path)
    stream = load_consonant_stream(path)

    if not stream:
        raise ValueError(f"No consonant stream extracted from file: {path}")

    segments = build_segments(stream, L)
    if len(segments) < max(2, max_lag + 1):
        raise ValueError(
            f"Too few full segments for analysis in {path}: {len(segments)}. "
            f"Need at least {max(2, max_lag + 1)}."
        )

    dsets = dominant_sets(segments, mode, k, min_freq)

    obs_adj = adjacent_jaccard_mean(dsets)
    obs_rec = recurrence_rate(dsets, R, min_jaccard)
    obs_mass = dominance_mass(segments, dsets)
    obs_lag = lag_jaccard_profile(dsets, max_lag)

    rng = random.Random(seed)
    null_adj: List[float] = []
    null_rec: List[float] = []
    null_mass: List[float] = []
    lag_null = {lag: [] for lag in range(1, max_lag + 1)}

    for p in range(perm):
        if (p + 1) % max(1, perm // 10) == 0 or p == 0 or p + 1 == perm:
            print(f"  perm {p + 1}/{perm}")

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

    lag_rows: List[Dict] = []
    for row in obs_lag:
        lag = row["lag"]
        mu_l, sd_l, z_l = zscore(row["mean_jaccard"], lag_null[lag])
        lag_rows.append(
            {
                "corpus": corpus,
                "file_path": str(Path(path).resolve()),
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
                "lag": lag,
                "mean_jaccard_obs": row["mean_jaccard"],
                "mean_jaccard_null_mean": mu_l,
                "mean_jaccard_null_sd": sd_l,
                "z_lag_jaccard": z_l,
                "n_pairs": row["n_pairs"],
            }
        )

    summary = {
        "corpus": corpus,
        "file_path": str(Path(path).resolve()),
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
        "z_adjacent_jaccard": z_adj,
        "recurrence_rate_obs": obs_rec,
        "recurrence_rate_null_mean": mu_rec,
        "recurrence_rate_null_sd": sd_rec,
        "z_recurrence_rate": z_rec,
        "dominance_mass_obs": obs_mass,
        "dominance_mass_null_mean": mu_mass,
        "dominance_mass_null_sd": sd_mass,
        "z_dominance_mass": z_mass,
    }

    return summary, lag_rows


def write_csv(path: Path, rows: List[Dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, obj: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def print_summary(summary: Dict) -> None:
    print("=" * 72)
    ordered_keys = [
        "corpus",
        "stream_len",
        "n_segments",
        "L",
        "mode",
        "k",
        "min_freq",
        "max_lag",
        "R",
        "min_jaccard",
        "block",
        "perm",
        "seed",
        "adjacent_jaccard_obs",
        "adjacent_jaccard_null_mean",
        "adjacent_jaccard_null_sd",
        "z_adjacent_jaccard",
        "recurrence_rate_obs",
        "recurrence_rate_null_mean",
        "recurrence_rate_null_sd",
        "z_recurrence_rate",
        "dominance_mass_obs",
        "dominance_mass_null_mean",
        "dominance_mass_null_sd",
        "z_dominance_mass",
    ]
    for key in ordered_keys:
        print(f"{key}: {summary[key]}")
    print()


def main() -> None:
    ap = argparse.ArgumentParser(description="Layer A+ — Local Dominant Consonant Sets")
    ap.add_argument("files", nargs="+", help="Explicit list of input phonetic files")
    ap.add_argument("--out_dir", required=True, help="Output root directory")
    ap.add_argument("--tag", default="baseline", help="Run tag")
    ap.add_argument("--L", type=int, default=150, help="Non-overlapping segment length")
    ap.add_argument("--mode", choices=["topk", "freqmin"], default="topk")
    ap.add_argument("--k", type=int, default=3, help="Used when mode=topk")
    ap.add_argument("--min_freq", type=int, default=2, help="Used when mode=freqmin")
    ap.add_argument("--max_lag", type=int, default=10)
    ap.add_argument("--R", type=int, default=5, help="Recurrence horizon in segments")
    ap.add_argument("--min_jaccard", type=float, default=0.5)
    ap.add_argument("--block", type=int, default=80)
    ap.add_argument("--perm", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()

    out_root = Path(args.out_dir)
    run_dir = out_root / args.tag
    run_dir.mkdir(parents=True, exist_ok=True)

    print("FILES TO PROCESS:")
    for f in args.files:
        print(" ", f)
    print()

    summaries: List[Dict] = []
    lag_rows_all: List[Dict] = []

    for f in args.files:
        try:
            print(f"Processing: {f}")
            summary, lag_rows = analyze_file(
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
                seed=args.seed,
            )
            print_summary(summary)
            summaries.append(summary)
            lag_rows_all.extend(lag_rows)

            corpus_dir = run_dir / "books" / summary["corpus"]
            write_csv(corpus_dir / f"layer_a_plus_{args.tag}_summary.csv", [summary])

        except Exception as e:
            print(f"ERROR while processing {f}: {e}")
            print()

    if not summaries:
        print("No successful outputs were produced.")
        sys.exit(1)

    important_rows: List[Dict] = []
    for s in summaries:
        important_rows.append(
            {
                "corpus": s["corpus"],
                "z_adjacent_jaccard": s["z_adjacent_jaccard"],
                "z_recurrence_rate": s["z_recurrence_rate"],
                "z_dominance_mass": s["z_dominance_mass"],
                "n_segments": s["n_segments"],
                "L": s["L"],
                "mode": s["mode"],
                "k": s["k"],
                "min_freq": s["min_freq"],
                "max_lag": s["max_lag"],
                "R": s["R"],
                "min_jaccard": s["min_jaccard"],
                "block": s["block"],
                "perm": s["perm"],
                "seed": s["seed"],
            }
        )

    summaries_sorted = sorted(summaries, key=lambda x: x["corpus"])
    lag_rows_sorted = sorted(lag_rows_all, key=lambda x: (x["corpus"], x["lag"]))
    important_sorted = sorted(important_rows, key=lambda x: x["corpus"])

    write_csv(run_dir / f"layer_a_plus_{args.tag}_summary_all.csv", summaries_sorted)
    write_csv(run_dir / f"layer_a_plus_{args.tag}_lag_profile_all.csv", lag_rows_sorted)
    write_csv(run_dir / f"layer_a_plus_{args.tag}_important_summary.csv", important_sorted)

    manifest = {
        "script": "layer_a_local_dominant_sets.py",
        "tag": args.tag,
        "files": [str(Path(f).resolve()) for f in args.files],
        "params": {
            "L": args.L,
            "mode": args.mode,
            "k": args.k,
            "min_freq": args.min_freq,
            "max_lag": args.max_lag,
            "R": args.R,
            "min_jaccard": args.min_jaccard,
            "block": args.block,
            "perm": args.perm,
            "seed": args.seed,
        },
        "outputs": {
            "summary_all_csv": str((run_dir / f"layer_a_plus_{args.tag}_summary_all.csv").resolve()),
            "lag_profile_all_csv": str((run_dir / f"layer_a_plus_{args.tag}_lag_profile_all.csv").resolve()),
            "important_summary_csv": str((run_dir / f"layer_a_plus_{args.tag}_important_summary.csv").resolve()),
            "run_manifest_json": str((run_dir / f"layer_a_plus_{args.tag}_run_manifest.json").resolve()),
        },
    }
    write_json(run_dir / f"layer_a_plus_{args.tag}_run_manifest.json", manifest)

    print("=" * 72)
    print("TOP-LINE RESULTS")
    for row in important_sorted:
        print(
            f"{row['corpus']}: "
            f"z_adj={row['z_adjacent_jaccard']:.3f}  "
            f"z_rec={row['z_recurrence_rate']:.3f}  "
            f"z_mass={row['z_dominance_mass']:.3f}"
        )

    print()
    print(f"WROTE: {run_dir / f'layer_a_plus_{args.tag}_summary_all.csv'}")
    print(f"WROTE: {run_dir / f'layer_a_plus_{args.tag}_lag_profile_all.csv'}")
    print(f"WROTE: {run_dir / f'layer_a_plus_{args.tag}_important_summary.csv'}")
    print(f"WROTE: {run_dir / f'layer_a_plus_{args.tag}_run_manifest.json'}")


if __name__ == "__main__":
    main()