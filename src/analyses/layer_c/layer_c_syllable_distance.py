#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import json
import random
import hashlib
from pathlib import Path
from statistics import mean, pstdev

VOWELS = set("aeiou")
DIGRAPHS = ("sh", "ts", "kh")


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def tokenize(text: str):
    tokens = []
    i = 0
    while i < len(text):
        if text[i] in (" ", "|"):
            i += 1
            continue
        two = text[i:i + 2]
        if two in DIGRAPHS:
            tokens.append(two)
            i += 2
        else:
            tokens.append(text[i])
            i += 1
    return tokens


def is_vowel(token: str) -> bool:
    return any(c in VOWELS for c in token)


def build_stream(text: str):
    tokens = tokenize(text)
    stream = []
    n = len(tokens)

    for i in range(n):
        t = tokens[i]

        if is_vowel(t):
            j = i + 1
            cons = []

            while j < n:
                tj = tokens[j]
                if is_vowel(tj):
                    break
                cons.append(tj)
                j += 1

            if cons:
                stream.append(t + "".join(cons))

    return [unit for unit in stream if len(unit) >= 2]


def nearest_rate(stream, L: int) -> float:
    n = len(stream)
    if n == 0:
        return 0.0

    matches = 0
    for i in range(n):
        for j in range(i + 1, min(i + L + 1, n)):
            if stream[i] == stream[j]:
                matches += 1
                break

    return matches / n


def distance_profile(stream, dmax: int):
    n = len(stream)
    rows = []

    for d in range(1, dmax + 1):
        denom = n - d
        if denom <= 0:
            hits = 0
            rate = 0.0
        else:
            hits = sum(1 for i in range(denom) if stream[i] == stream[i + d])
            rate = hits / denom

        rows.append({
            "d": d,
            "hits": hits,
            "denom": max(0, denom),
            "obs_rate": rate,
        })

    return rows


def block_permute(stream, block: int, rng: random.Random):
    blocks = [stream[i:i + block] for i in range(0, len(stream), block)]
    rng.shuffle(blocks)
    return [x for b in blocks for x in b]


def analyze(file_path: Path, args):
    text = file_path.read_text(encoding="utf-8")
    book = file_path.stem.replace("_phonetic", "").replace("_qo", "")

    print("=" * 72)
    print(f"BOOK: {book}")
    print(f"L={args.L}  Dmax={args.Dmax}  block={args.block}  perm={args.perm}  seed={args.seed}")

    stream = build_stream(text)
    print(f"stream_len={len(stream)}")
    print("  computing null...")

    obs_global = nearest_rate(stream, args.L)
    obs_profile = distance_profile(stream, args.Dmax)

    rng = random.Random(args.seed)
    null_global = []
    null_by_d = {d: [] for d in range(1, args.Dmax + 1)}

    for p in range(args.perm):
        if (p + 1) % max(1, args.perm // 10) == 0 or p == 0 or p + 1 == args.perm:
            print(f"  perm {p + 1}/{args.perm}")

        shuffled = block_permute(stream, args.block, rng)

        null_global.append(nearest_rate(shuffled, args.L))

        shuffled_profile = distance_profile(shuffled, args.Dmax)
        for row in shuffled_profile:
            null_by_d[row["d"]].append(row["obs_rate"])

    global_mu = mean(null_global)
    global_sd = pstdev(null_global)
    global_z = None if global_sd == 0 else (obs_global - global_mu) / global_sd

    run_dir = Path(args.out_root) / args.tag
    book_dir = run_dir / "books" / book
    book_dir.mkdir(parents=True, exist_ok=True)

    summary_row = {
        "book": book,
        "L": args.L,
        "Dmax": args.Dmax,
        "block": args.block,
        "perm": args.perm,
        "seed": args.seed,
        "stream_len": len(stream),
        "obs_global": obs_global,
        "null_global_mean": global_mu,
        "null_global_sd": global_sd,
        "z_global": global_z,
    }

    with (book_dir / f"c1_2_{args.tag}_summary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary_row.keys()))
        w.writeheader()
        w.writerow(summary_row)

    distance_rows = []
    for row in obs_profile:
        d = row["d"]
        mu = mean(null_by_d[d])
        sd = pstdev(null_by_d[d])
        z = None if sd == 0 else (row["obs_rate"] - mu) / sd

        distance_rows.append({
            "d": d,
            "hits": row["hits"],
            "denom": row["denom"],
            "obs_rate": row["obs_rate"],
            "null_mean": mu,
            "null_sd": sd,
            "z": z,
        })

    with (book_dir / f"c1_2_{args.tag}_distance.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(distance_rows[0].keys()))
        w.writeheader()
        w.writerows(distance_rows)

    manifest = {
        "book": book,
        "input_path": str(file_path.resolve()),
        "sha256": sha256_of_file(file_path),
        "params": {
            "L": args.L,
            "Dmax": args.Dmax,
            "block": args.block,
            "perm": args.perm,
            "seed": args.seed,
        },
        "stream_len": len(stream),
    }

    with (book_dir / f"c1_2_{args.tag}_run_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"obs_global={obs_global:.6f}  null={global_mu:.6f}  Z={global_z if global_z is not None else 'NA'}")
    print("Top peaks:")
    top_peaks = sorted(distance_rows, key=lambda x: float("-inf") if x["z"] is None else x["z"], reverse=True)[:5]
    for row in top_peaks:
        z_str = "NA" if row["z"] is None else f"{row['z']:.2f}"
        print(f"d={row['d']}  Z={z_str}")

    return summary_row


def main():
    ap = argparse.ArgumentParser(description="Layer C1.2 syllabic rhyme distance spectrum (strict)")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--L", type=int, default=20)
    ap.add_argument("--Dmax", type=int, default=40)
    ap.add_argument("--block", type=int, default=50)
    ap.add_argument("--perm", type=int, default=200)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out_root", required=True)
    ap.add_argument("--tag", required=True)
    args = ap.parse_args()

    run_dir = Path(args.out_root) / args.tag
    run_dir.mkdir(parents=True, exist_ok=True)

    print("FILES TO PROCESS:")
    for f in args.files:
        print(" ", f)
    print()

    results = []
    for f in args.files:
        results.append(analyze(Path(f), args))

    results_sorted = sorted(results, key=lambda x: x["book"])

    summary_all_path = run_dir / f"c1_2_{args.tag}_summary_all.csv"
    with summary_all_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(results_sorted[0].keys()))
        w.writeheader()
        w.writerows(results_sorted)

    run_manifest = {
        "script": "layer_c_syllable_distance.py",
        "tag": args.tag,
        "files": [str(Path(f).resolve()) for f in args.files],
        "params": {
            "L": args.L,
            "Dmax": args.Dmax,
            "block": args.block,
            "perm": args.perm,
            "seed": args.seed,
        },
        "outputs": {
            "summary_all_csv": str(summary_all_path.resolve()),
        },
    }

    with (run_dir / f"c1_2_{args.tag}_run_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(run_manifest, f, indent=2)

    print("\nTOP-LINE RESULTS")
    for r in results_sorted:
        z_str = "NA" if r["z_global"] is None else f"{r['z_global']:.3f}"
        print(f"{r['book']}  Z_global={z_str}")

    print("\nWROTE:", summary_all_path)


if __name__ == "__main__":
    main()