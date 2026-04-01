#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import hashlib
import json
import os
import random
from pathlib import Path

import numpy as np

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


# ---------- TAIL ----------
def get_tail(word: str):
    ph = tokenize(word)
    last_v = -1
    for i, x in enumerate(ph):
        if x in VOWELS:
            last_v = i
    if last_v == -1:
        return None
    tail = ph[last_v:]
    if len(tail) < 2:
        return None
    return tuple(tail)


# ---------- NORMALIZE ----------
def normalize_tail(tail, eq_kh_k: int, eq_ts_s: int):
    if tail is None:
        return None
    out = []
    for x in tail:
        if x == "d":
            x = "t"
        elif eq_kh_k and x == "kh":
            x = "k"
        elif eq_ts_s and x == "ts":
            x = "s"
        out.append(x)
    return tuple(out)


# ---------- LOAD ----------
def load_words(path: Path):
    with path.open(encoding="utf-8") as f:
        return [w for w in f.read().split() if w != "|"]


def corpus_name_from_path(path: Path) -> str:
    stem = path.stem.lower()
    if stem.endswith("_phonetic_qo"):
        stem = stem[:-12]
    elif stem.endswith("_phonetic"):
        stem = stem[:-9]
    return stem


# ---------- METRIC ----------
def compute(words, L: int, eq_kh_k: int, eq_ts_s: int):
    tails = [normalize_tail(get_tail(w), eq_kh_k, eq_ts_s) for w in words]

    matches = 0
    comparisons = 0
    valid_words = sum(1 for t in tails if t is not None)

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
        "n_valid_tails": valid_words,
        "matches": matches,
        "comparisons": comparisons,
        "rate": rate,
    }


# ---------- NULL ----------
def block_shuffle(words, block: int, rng: random.Random):
    blocks = [words[i:i + block] for i in range(0, len(words), block)]
    rng.shuffle(blocks)
    return [w for b in blocks for w in b]


# ---------- IO ----------
def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def save_csv(path: Path, rows):
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


# ---------- ANALYZE ----------
def analyze_one(file_path: Path, args):
    rng = random.Random(args.seed)

    words = load_words(file_path)
    obs = compute(words, args.L, args.eq_kh_k, args.eq_ts_s)

    null_rates = []
    for _ in range(args.perm):
        sh = block_shuffle(words, args.block, rng)
        r = compute(sh, args.L, args.eq_kh_k, args.eq_ts_s)
        null_rates.append(r["rate"])

    mu = float(np.mean(null_rates))
    sd = float(np.std(null_rates))
    z = (obs["rate"] - mu) / sd if sd > 0 else 0.0

    book = corpus_name_from_path(file_path)

    run_dir = Path(args.out_root) / args.tag
    book_dir = run_dir / "books" / book
    ensure_dir(book_dir)

    res = {
        "book": book,
        "file": str(file_path),
        "L": args.L,
        "block": args.block,
        "perm": args.perm,
        "seed": args.seed,
        "eq_kh_k": args.eq_kh_k,
        "eq_ts_s": args.eq_ts_s,
        "n_words": obs["n_words"],
        "n_valid_tails": obs["n_valid_tails"],
        "matches": obs["matches"],
        "comparisons": obs["comparisons"],
        "rate": obs["rate"],
        "null_mean": mu,
        "null_sd": sd,
        "Z": z,
    }

    save_csv(book_dir / f"c2_{args.tag}_summary.csv", [res])

    manifest = {
        "book": book,
        "input_path": str(file_path.resolve()),
        "sha256": sha256_of_file(file_path),
        "params": {
            "L": args.L,
            "block": args.block,
            "perm": args.perm,
            "seed": args.seed,
            "eq_kh_k": args.eq_kh_k,
            "eq_ts_s": args.eq_ts_s,
            "out_root": str(Path(args.out_root).resolve()),
            "tag": args.tag,
        },
        "counts": {
            "n_words": obs["n_words"],
            "n_valid_tails": obs["n_valid_tails"],
        },
    }

    with (book_dir / f"c2_{args.tag}_run_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print("=" * 72)
    print(f"BOOK: {book}")
    print(f"L={args.L}  block={args.block}  perm={args.perm}  seed={args.seed}")
    print(f"valid_tails={obs['n_valid_tails']} / words={obs['n_words']}")
    print(f"matches={obs['matches']} / comparisons={obs['comparisons']}")
    print(f"rate={obs['rate']:.6f}  null={mu:.6f}  Z={z:.3f}")

    return res


# ---------- MAIN ----------
def main():
    ap = argparse.ArgumentParser(description="Layer C2 word-final rhyme concentration")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--L", type=int, default=40)
    ap.add_argument("--block", type=int, default=50)
    ap.add_argument("--perm", type=int, default=200)
    ap.add_argument("--eq_kh_k", type=int, default=0)
    ap.add_argument("--eq_ts_s", type=int, default=0)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out_root", required=True)
    ap.add_argument("--tag", required=True)
    args = ap.parse_args()

    results = []
    for fp in args.files:
        results.append(analyze_one(Path(fp), args))

    results_sorted = sorted(results, key=lambda x: x["book"])
    run_dir = Path(args.out_root) / args.tag
    ensure_dir(run_dir)

    important_rows = []
    for r in results_sorted:
        important_rows.append({
            "book": r["book"],
            "L": r["L"],
            "block": r["block"],
            "perm": r["perm"],
            "seed": r["seed"],
            "matches": r["matches"],
            "comparisons": r["comparisons"],
            "rate": r["rate"],
            "null_mean": r["null_mean"],
            "Z": r["Z"],
        })

    save_csv(run_dir / f"c2_{args.tag}_summary_all.csv", results_sorted)
    save_csv(run_dir / f"c2_{args.tag}_important_summary.csv", important_rows)

    run_manifest = {
        "script": "layer_c_word_final.py",
        "tag": args.tag,
        "files": [str(Path(f).resolve()) for f in args.files],
        "params": {
            "L": args.L,
            "block": args.block,
            "perm": args.perm,
            "seed": args.seed,
            "eq_kh_k": args.eq_kh_k,
            "eq_ts_s": args.eq_ts_s,
        },
    }
    with (run_dir / f"c2_{args.tag}_run_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(run_manifest, f, ensure_ascii=False, indent=2)

    print("\nTOP-LINE RESULTS")
    for r in important_rows:
        print(f"{r['book']}  Z={r['Z']:.3f}")

    print(f"\nWROTE: {run_dir / f'c2_{args.tag}_summary_all.csv'}")
    print(f"WROTE: {run_dir / f'c2_{args.tag}_important_summary.csv'}")
    print(f"WROTE: {run_dir / f'c2_{args.tag}_run_manifest.json'}")


if __name__ == "__main__":
    main()