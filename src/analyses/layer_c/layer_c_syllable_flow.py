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


# -----------------------
# HASH
# -----------------------

def sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


# -----------------------
# TOKENIZATION
# -----------------------

def tokenize(text):
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


def is_vowel(t):
    return any(c in VOWELS for c in t)


# -----------------------
# STREAM (STRICT ONLY)
# -----------------------

def build_stream(text):
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

    return [r for r in stream if len(r) >= 2]


# -----------------------
# METRIC
# -----------------------

def nearest_rate(stream, L):
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


# -----------------------
# WINDOW PROFILE
# -----------------------

def window_profile(stream, L, W, step):
    out = []
    n = len(stream)

    for i in range(0, max(1, n - W + 1), step):
        seg = stream[i:i + W]
        out.append((i, nearest_rate(seg, L)))

    return out


# -----------------------
# NULL MODEL
# -----------------------

def block_permute(stream, block, rng):
    blocks = [stream[i:i + block] for i in range(0, len(stream), block)]
    rng.shuffle(blocks)
    return [x for b in blocks for x in b]


# -----------------------
# ANALYSIS
# -----------------------

def analyze(file_path, args):
    text = Path(file_path).read_text(encoding="utf-8")

    book = Path(file_path).stem.replace("_phonetic", "").replace("_qo", "")

    print("=" * 72)
    print(f"BOOK: {book}")
    print(f"L={args.L}  block={args.block}  perm={args.perm}  seed={args.seed}")

    stream = build_stream(text)
    obs = nearest_rate(stream, args.L)

    print(f"stream_len={len(stream)}")
    print("  computing null...")

    rng = random.Random(args.seed)

    nulls = []
    for p in range(args.perm):
        if (p + 1) % max(1, args.perm // 10) == 0 or p == 0 or p + 1 == args.perm:
            print(f"  perm {p + 1}/{args.perm}")

        sh = block_permute(stream, args.block, rng)
        nulls.append(nearest_rate(sh, args.L))

    mu = mean(nulls)
    sd = pstdev(nulls)
    Z = None if sd == 0 else (obs - mu) / sd

    run_dir = Path(args.out_root) / args.tag
    book_dir = run_dir / "books" / book
    book_dir.mkdir(parents=True, exist_ok=True)

    # ---------- per-book summary ----------

    summary_path = book_dir / f"c1_{args.tag}_summary.csv"

    with summary_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "book", "L", "block", "perm", "seed",
            "stream_len", "obs", "null_mean", "null_sd", "z"
        ])
        w.writerow([
            book, args.L, args.block, args.perm, args.seed,
            len(stream), obs, mu, sd, Z
        ])

    # ---------- window profile ----------

    prof = window_profile(stream, args.L, args.W, args.step)
    prof_path = book_dir / f"c1_{args.tag}_profile.csv"

    with prof_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pos", "rate"])
        w.writerows(prof)

    # ---------- manifest ----------

    manifest = {
        "book": book,
        "input_path": str(Path(file_path).resolve()),
        "sha256": sha256_of_file(file_path),
        "params": {
            "L": args.L,
            "block": args.block,
            "perm": args.perm,
            "seed": args.seed
        },
        "stream_len": len(stream)
    }

    with (book_dir / f"c1_{args.tag}_run_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # ---------- print ----------

    print("=" * 72)
    print(f"BOOK: {book}")
    print(f"L={args.L}  block={args.block}  perm={args.perm}  seed={args.seed}")
    print(f"stream_len={len(stream)}")
    print(f"obs={obs:.6f}  null={mu:.6f}  Z={Z if Z is not None else 'NA'}")

    return {
        "book": book,
        "L": args.L,
        "block": args.block,
        "perm": args.perm,
        "seed": args.seed,
        "stream_len": len(stream),
        "obs": obs,
        "null_mean": mu,
        "null_sd": sd,
        "z": Z
    }


# -----------------------
# MAIN
# -----------------------

def main():
    ap = argparse.ArgumentParser(description="Layer C1 syllable flow (strict)")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--L", type=int, default=20)
    ap.add_argument("--block", type=int, default=50)
    ap.add_argument("--perm", type=int, default=200)
    ap.add_argument("--W", type=int, default=1000)
    ap.add_argument("--step", type=int, default=500)
    ap.add_argument("--out_root", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()

    run_dir = Path(args.out_root) / args.tag
    run_dir.mkdir(parents=True, exist_ok=True)

    results = []

    print("FILES TO PROCESS:")
    for f in args.files:
        print(" ", f)
    print()

    for f in args.files:
        res = analyze(f, args)
        results.append(res)

    results_sorted = sorted(results, key=lambda x: x["book"])

    # ---------- summary all ----------

    summary_all_path = run_dir / f"c1_{args.tag}_summary_all.csv"

    with summary_all_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(results_sorted[0].keys()))
        w.writeheader()
        w.writerows(results_sorted)

    print("\nTOP-LINE RESULTS")
    for r in results_sorted:
        z_str = "NA" if r["z"] is None else f"{r['z']:.3f}"
        print(f"{r['book']}  Z={z_str}")

    print("\nWROTE:", summary_all_path)


if __name__ == "__main__":
    main()