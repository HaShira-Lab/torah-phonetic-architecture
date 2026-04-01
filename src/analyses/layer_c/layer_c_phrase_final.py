#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import hashlib
import json
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


# ---------- NORMALIZE ----------
def normalize_tokens(tokens, eq_kh_k: int, eq_ts_s: int):
    out = []
    for t in tokens:
        if t == "d":
            t = "t"
        elif eq_kh_k and t == "kh":
            t = "k"
        elif eq_ts_s and t == "ts":
            t = "s"
        out.append(t)
    return out


# ---------- TAIL ----------
def get_tail(word: str, eq_kh_k: int, eq_ts_s: int):
    toks = tokenize(word)
    toks = normalize_tokens(toks, eq_kh_k, eq_ts_s)

    last_v = -1
    for i, t in enumerate(toks):
        if t in VOWELS:
            last_v = i

    if last_v == -1:
        return None

    tail = toks[last_v:]
    if len(tail) < 2:
        return None

    return tuple(tail)


# ---------- IO ----------
def load_tokens(path: Path):
    with path.open(encoding="utf-8") as f:
        return f.read().split()


def split_phrases(tokens):
    phrases = []
    cur = []
    for t in tokens:
        if t == "|":
            if cur:
                phrases.append(cur)
                cur = []
        else:
            cur.append(t)
    if cur:
        phrases.append(cur)
    return phrases


def corpus_name_from_path(path: Path) -> str:
    stem = path.stem.lower()
    if stem.endswith("_phonetic_qo"):
        stem = stem[:-12]
    elif stem.endswith("_phonetic"):
        stem = stem[:-9]
    return stem


# ---------- METRIC ----------
def phrase_final_tails(phrases, eq_kh_k: int, eq_ts_s: int):
    tails = []
    finals = []
    for p in phrases:
        final_word = p[-1] if p else None
        finals.append(final_word)
        tails.append(get_tail(final_word, eq_kh_k, eq_ts_s) if final_word else None)
    return finals, tails


def count_matches(tails, R: int):
    n = len(tails)
    counts = []

    for i in range(n):
        ti = tails[i]
        if ti is None:
            counts.append(None)
            continue

        c = 0
        for j in range(max(0, i - R), min(n, i + R + 1)):
            if j == i:
                continue
            if tails[j] == ti:
                c += 1
        counts.append(c)

    return counts


def compute(phrases, R: int, eq_kh_k: int, eq_ts_s: int):
    finals, tails = phrase_final_tails(phrases, eq_kh_k, eq_ts_s)
    counts = count_matches(tails, R)

    valid_counts = [c for c in counts if c is not None]
    score = float(np.mean(valid_counts)) if valid_counts else 0.0

    return {
        "n_phrases": len(phrases),
        "n_valid_final_tails": len(valid_counts),
        "final_words": finals,
        "tails": tails,
        "counts": counts,
        "score": score,
    }


# ---------- NULL ----------
def block_shuffle_phrases(phrases, block: int, rng: random.Random):
    blocks = [phrases[i:i + block] for i in range(0, len(phrases), block)]
    rng.shuffle(blocks)
    return [p for b in blocks for p in b]


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

    tokens = load_tokens(file_path)
    phrases = split_phrases(tokens)

    obs = compute(phrases, args.R, args.eq_kh_k, args.eq_ts_s)

    null_scores = []
    for _ in range(args.perm):
        sh = block_shuffle_phrases(phrases, args.block, rng)
        null_scores.append(compute(sh, args.R, args.eq_kh_k, args.eq_ts_s)["score"])

    mu = float(np.mean(null_scores))
    sd = float(np.std(null_scores))
    z = (obs["score"] - mu) / sd if sd > 0 else 0.0

    book = corpus_name_from_path(file_path)

    run_dir = Path(args.out_root) / args.tag
    book_dir = run_dir / "books" / book
    ensure_dir(book_dir)

    summary = {
        "book": book,
        "file": str(file_path),
        "R": args.R,
        "block": args.block,
        "perm": args.perm,
        "seed": args.seed,
        "eq_kh_k": args.eq_kh_k,
        "eq_ts_s": args.eq_ts_s,
        "n_phrases": obs["n_phrases"],
        "n_valid_final_tails": obs["n_valid_final_tails"],
        "score": obs["score"],
        "null_mean": mu,
        "null_sd": sd,
        "Z": z,
    }

    save_csv(book_dir / f"c4_{args.tag}_summary.csv", [summary])

    phrase_rows = []
    for i, (final_word, tail, count) in enumerate(zip(obs["final_words"], obs["tails"], obs["counts"])):
        phrase_rows.append({
            "phrase_index": i,
            "final_word": final_word,
            "tail": "" if tail is None else " ".join(tail),
            "valid_tail": int(tail is not None),
            "match_count": "" if count is None else count,
        })
    save_csv(book_dir / f"c4_{args.tag}_phrase_finals.csv", phrase_rows)

    manifest = {
        "book": book,
        "input_path": str(file_path.resolve()),
        "sha256": sha256_of_file(file_path),
        "params": {
            "R": args.R,
            "block": args.block,
            "perm": args.perm,
            "seed": args.seed,
            "eq_kh_k": args.eq_kh_k,
            "eq_ts_s": args.eq_ts_s,
            "out_root": str(Path(args.out_root).resolve()),
            "tag": args.tag,
        },
        "counts": {
            "n_phrases": obs["n_phrases"],
            "n_valid_final_tails": obs["n_valid_final_tails"],
        },
    }

    with (book_dir / f"c4_{args.tag}_run_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print("=" * 72)
    print(f"BOOK: {book}")
    print(f"R={args.R}  block={args.block}  perm={args.perm}  seed={args.seed}")
    print(f"valid_final_tails={obs['n_valid_final_tails']} / phrases={obs['n_phrases']}")
    print(f"score={obs['score']:.6f}  null={mu:.6f}  Z={z:.3f}")

    return summary


# ---------- MAIN ----------
def main():
    ap = argparse.ArgumentParser(description="Layer C4 phrase-final rhyme recurrence")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--R", type=int, default=10)
    ap.add_argument("--block", type=int, default=20)
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
            "R": r["R"],
            "block": r["block"],
            "perm": r["perm"],
            "seed": r["seed"],
            "n_phrases": r["n_phrases"],
            "n_valid_final_tails": r["n_valid_final_tails"],
            "score": r["score"],
            "null_mean": r["null_mean"],
            "Z": r["Z"],
        })

    save_csv(run_dir / f"c4_{args.tag}_summary_all.csv", results_sorted)
    save_csv(run_dir / f"c4_{args.tag}_important_summary.csv", important_rows)

    run_manifest = {
        "script": "layer_c_phrase_final.py",
        "tag": args.tag,
        "files": [str(Path(f).resolve()) for f in args.files],
        "params": {
            "R": args.R,
            "block": args.block,
            "perm": args.perm,
            "seed": args.seed,
            "eq_kh_k": args.eq_kh_k,
            "eq_ts_s": args.eq_ts_s,
        },
    }
    with (run_dir / f"c4_{args.tag}_run_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(run_manifest, f, ensure_ascii=False, indent=2)

    print("\nTOP-LINE RESULTS")
    for r in important_rows:
        print(f"{r['book']}  Z={r['Z']:.3f}")

    print(f"\nWROTE: {run_dir / f'c4_{args.tag}_summary_all.csv'}")
    print(f"WROTE: {run_dir / f'c4_{args.tag}_important_summary.csv'}")
    print(f"WROTE: {run_dir / f'c4_{args.tag}_run_manifest.json'}")


if __name__ == "__main__":
    main()