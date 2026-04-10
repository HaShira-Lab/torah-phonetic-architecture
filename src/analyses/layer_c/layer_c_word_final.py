#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import hashlib
import json
import random
from pathlib import Path
from statistics import mean, pstdev

VOWELS = {"a", "e", "i", "o", "u"}
DIGRAPHS = ("sh", "kh", "ts")


# ---------- HASH ----------
def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------- TOKENIZE ----------
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


# ---------- WORD FINAL TAIL ----------
def get_tail(word: str):
    ph = tokenize(word)

    last_v = -1
    for i, x in enumerate(ph):
        if x in VOWELS:
            last_v = i

    if last_v == -1:
        return None

    # closed syllable
    if last_v < len(ph) - 1 and ph[last_v + 1] not in VOWELS:
        return (ph[last_v], ph[last_v + 1])

    # open final syllable
    if last_v > 0:
        return (ph[last_v - 1], ph[last_v])

    return None


# ---------- LOAD ----------
def load_words(path: Path):
    with path.open(encoding="utf-8") as f:
        return [w for w in f.read().split() if w != "|"]


def corpus_name(path: Path):
    stem = path.stem
    return stem.replace("_phonetic", "").replace("_qo", "")


# ---------- METRIC ----------
def compute(words, L):
    tails = [get_tail(w) for w in words]

    matches = 0
    comparisons = 0
    valid = sum(1 for t in tails if t is not None)

    n = len(words)
    for i in range(n):
        ti = tails[i]
        if ti is None:
            continue

        for j in range(i + 1, min(i + L + 1, n)):
            tj = tails[j]
            if tj is None:
                continue
            comparisons += 1
            if ti == tj:
                matches += 1

    rate = matches / comparisons if comparisons else 0.0

    return {
        "n_words": n,
        "n_valid_tails": valid,
        "matches": matches,
        "comparisons": comparisons,
        "rate": rate,
    }


# ---------- NULL ----------
def block_shuffle(words, block, rng):
    blocks = [words[i:i + block] for i in range(0, len(words), block)]
    rng.shuffle(blocks)
    return [w for b in blocks for w in b]


# ---------- ANALYZE ----------
def analyze_one(file_path: Path, args):
    rng = random.Random(args.seed)

    words = load_words(file_path)
    obs = compute(words, args.L)

    print("=" * 72)
    print(f"BOOK: {corpus_name(file_path)}")
    print(f"L={args.L}  block={args.block}  perm={args.perm}  seed={args.seed}")
    print(f"words={obs['n_words']}  valid_tails={obs['n_valid_tails']}")
    print("  computing null...")

    null_rates = []
    for p in range(args.perm):
        if (p + 1) % max(1, args.perm // 10) == 0 or p == 0 or p + 1 == args.perm:
            print(f"  perm {p + 1}/{args.perm}")

        sh = block_shuffle(words, args.block, rng)
        r = compute(sh, args.L)
        null_rates.append(r["rate"])

    mu = mean(null_rates)
    sd = pstdev(null_rates)
    z = None if sd == 0 else (obs["rate"] - mu) / sd

    book = corpus_name(file_path)

    run_dir = Path(args.out_root) / args.tag
    book_dir = run_dir / "books" / book
    book_dir.mkdir(parents=True, exist_ok=True)

    res = {
        "book": book,
        "L": args.L,
        "block": args.block,
        "perm": args.perm,
        "seed": args.seed,
        "n_words": obs["n_words"],
        "n_valid_tails": obs["n_valid_tails"],
        "matches": obs["matches"],
        "comparisons": obs["comparisons"],
        "rate": obs["rate"],
        "null_mean": mu,
        "null_sd": sd,
        "Z": z,
    }

    with (book_dir / f"c2_{args.tag}_summary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(res.keys()))
        w.writeheader()
        w.writerow(res)

    manifest = {
        "book": book,
        "input_path": str(file_path.resolve()),
        "sha256": sha256_of_file(file_path),
        "params": vars(args),
    }

    with (book_dir / f"c2_{args.tag}_run_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"rate={obs['rate']:.6f}  null={mu:.6f}  Z={z if z is not None else 'NA'}")

    return res


# ---------- MAIN ----------
def main():
    ap = argparse.ArgumentParser(description="Layer C2 word-final rhyme concentration")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--L", type=int, default=40)
    ap.add_argument("--block", type=int, default=50)
    ap.add_argument("--perm", type=int, default=200)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out_root", required=True)
    ap.add_argument("--tag", required=True)
    args = ap.parse_args()

    results = []
    for f in args.files:
        results.append(analyze_one(Path(f), args))

    results = sorted(results, key=lambda x: x["book"])

    run_dir = Path(args.out_root) / args.tag
    run_dir.mkdir(parents=True, exist_ok=True)

    with (run_dir / f"c2_{args.tag}_summary_all.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)

    print("\nTOP-LINE RESULTS")
    for r in results:
        z = "NA" if r["Z"] is None else f"{r['Z']:.3f}"
        print(f"{r['book']}  Z={z}")


if __name__ == "__main__":
    main()