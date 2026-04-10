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


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


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


def get_tail(word: str):
    toks = tokenize(word)

    last_v = -1
    for i, t in enumerate(toks):
        if t in VOWELS:
            last_v = i

    if last_v == -1:
        return None

    # closed final syllable: V + first following consonant
    if last_v < len(toks) - 1 and toks[last_v + 1] not in VOWELS:
        return (toks[last_v], toks[last_v + 1])

    # open final syllable: previous consonant + V
    if last_v == len(toks) - 1 and last_v > 0 and toks[last_v - 1] not in VOWELS:
        return (toks[last_v - 1], toks[last_v])

    return None


def load_tokens(path: Path):
    with path.open(encoding="utf-8") as f:
        return f.read().split()


def split_phrases(tokens):
    phrases = []
    current = []

    for tok in tokens:
        if tok == "|":
            if current:
                phrases.append(current)
            current = []
        else:
            current.append(tok)

    if current:
        phrases.append(current)

    return phrases


def corpus_name(path: Path):
    return path.stem.replace("_phonetic", "").replace("_qo", "")


def phrase_final_tails(phrases):
    final_words = []
    tails = []

    for phrase in phrases:
        final_word = phrase[-1] if phrase else None
        final_words.append(final_word)
        tails.append(get_tail(final_word) if final_word else None)

    return final_words, tails


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


def compute(phrases, R: int):
    final_words, tails = phrase_final_tails(phrases)
    counts = count_matches(tails, R)

    valid_counts = [c for c in counts if c is not None]
    score = mean(valid_counts) if valid_counts else 0.0

    return {
        "n_phrases": len(phrases),
        "n_valid_final_tails": len(valid_counts),
        "final_words": final_words,
        "tails": tails,
        "counts": counts,
        "score": score,
    }


def block_shuffle_phrases(phrases, block: int, rng: random.Random):
    blocks = [phrases[i:i + block] for i in range(0, len(phrases), block)]
    rng.shuffle(blocks)
    return [phrase for block_item in blocks for phrase in block_item]


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def save_csv(path: Path, rows):
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def analyze_one(file_path: Path, args):
    rng = random.Random(args.seed)

    tokens = load_tokens(file_path)
    phrases = split_phrases(tokens)
    obs = compute(phrases, args.R)

    book = corpus_name(file_path)

    print("=" * 72)
    print(f"BOOK: {book}")
    print(f"R={args.R}  block={args.block}  perm={args.perm}  seed={args.seed}")
    print(f"phrases={obs['n_phrases']}  valid_final_tails={obs['n_valid_final_tails']}")
    print("  computing null...")

    null_scores = []
    for p in range(args.perm):
        if (p + 1) % max(1, args.perm // 10) == 0 or p == 0 or p + 1 == args.perm:
            print(f"  perm {p + 1}/{args.perm}")

        shuffled = block_shuffle_phrases(phrases, args.block, rng)
        null_scores.append(compute(shuffled, args.R)["score"])

    mu = mean(null_scores)
    sd = pstdev(null_scores)
    z = None if sd == 0 else (obs["score"] - mu) / sd

    run_dir = Path(args.out_root) / args.tag
    book_dir = run_dir / "books" / book
    ensure_dir(book_dir)

    summary = {
        "book": book,
        "R": args.R,
        "block": args.block,
        "perm": args.perm,
        "seed": args.seed,
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
            "out_root": str(Path(args.out_root).resolve()),
            "tag": args.tag,
        },
        "counts": {
            "n_phrases": obs["n_phrases"],
            "n_valid_final_tails": obs["n_valid_final_tails"],
        },
    }

    with (book_dir / f"c4_{args.tag}_run_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    z_str = "NA" if z is None else f"{z:.3f}"
    print(f"score={obs['score']:.6f}  null={mu:.6f}  Z={z_str}")

    return summary


def main():
    ap = argparse.ArgumentParser(description="Layer C4 phrase-final rhyme recurrence")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--R", type=int, default=10)
    ap.add_argument("--block", type=int, default=20)
    ap.add_argument("--perm", type=int, default=200)
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
        },
    }

    with (run_dir / f"c4_{args.tag}_run_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(run_manifest, f, indent=2)

    print("\nTOP-LINE RESULTS")
    for r in important_rows:
        z_str = "NA" if r["Z"] is None else f"{r['Z']:.3f}"
        print(f"{r['book']}  Z={z_str}")

    print(f"\nWROTE: {run_dir / f'c4_{args.tag}_summary_all.csv'}")
    print(f"WROTE: {run_dir / f'c4_{args.tag}_important_summary.csv'}")
    print(f"WROTE: {run_dir / f'c4_{args.tag}_run_manifest.json'}")


if __name__ == "__main__":
    main()