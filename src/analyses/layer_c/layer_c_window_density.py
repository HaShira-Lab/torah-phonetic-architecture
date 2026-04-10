#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import json
import hashlib
from pathlib import Path
from statistics import mean, pstdev

VOWELS = {"a","e","i","o","u"}
DIGRAPHS = ("sh","kh","ts")


# ---------- HASH ----------
def sha256_of_file(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------- TOKEN ----------
def tokenize(word):
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


# ---------- RHYME UNITS ----------
def extract_units(word):
    ph = tokenize(word)
    units = []
    n = len(ph)

    for i, t in enumerate(ph):

        if t not in VOWELS:
            continue

        # --- CLOSED ---
        if i < n - 1:
            j = i + 1
            cons = []

            while j < n:
                if ph[j] in VOWELS:
                    break
                cons.append(ph[j])
                j += 1

            if cons:
                units.append(tuple([t] + cons))

        # --- OPEN (word-final vowel) ---
        elif i == n - 1 and i > 0:
            if ph[i - 1] not in VOWELS:
                units.append((ph[i - 1], t))

    return units

# ---------- LOAD ----------
def load_words(path):
    with path.open(encoding="utf-8") as f:
        return [w for w in f.read().split() if w != "|"]


# ---------- STREAM ----------
def build_stream(words):
    stream = []
    for w in words:
        stream.extend(extract_units(w))
    return stream


# ---------- WINDOW DENSITY ----------
def window_density(stream, L, W, step):
    N = len(stream)
    out = []

    for start in range(0, N - W + 1, step):   # FIX
        window = stream[start:start+W]

        matches = 0
        total_pairs = 0

        for i in range(len(window)):
            for j in range(i+1, min(i + L + 1, len(window))):  # FIX
                total_pairs += 1
                if window[i] == window[j]:
                    matches += 1

        rate = matches / total_pairs if total_pairs else 0.0
        out.append(rate)

    return out


# ---------- IO ----------
def ensure_dir(p):
    p.mkdir(parents=True, exist_ok=True)


def save_csv(path, rows):
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def corpus_name(path):
    return path.stem.lower().replace("_phonetic","").replace("_qo","")


# ---------- ANALYZE ----------
def analyze_one(file_path, args):
    words = load_words(file_path)
    stream = build_stream(words)

    book = corpus_name(file_path)

    print("="*72)
    print(f"BOOK: {book}")
    print(f"L={args.L}  W={args.W}  step={args.step}")
    print(f"stream_len={len(stream)}")

    wd = window_density(stream, args.L, args.W, args.step)

    res = {
        "book": book,
        "mean": mean(wd) if wd else 0.0,
        "var": pstdev(wd)**2 if wd else 0.0,
        "min": min(wd) if wd else 0.0,
        "max": max(wd) if wd else 0.0,
        "n_windows": len(wd)
    }

    run_dir = Path(args.out_root) / args.tag
    book_dir = run_dir / "books" / book
    ensure_dir(book_dir)

    # windows
    rows = [{"window_index": i, "rate": wd[i]} for i in range(len(wd))]
    save_csv(book_dir / "windows.csv", rows)

    # summary
    save_csv(book_dir / "summary.csv", [res])

    # manifest
    manifest = {
        "book": book,
        "input_path": str(Path(file_path).resolve()),
        "sha256": sha256_of_file(file_path),
        "params": vars(args),
        "stream_len": len(stream)
    }

    with (book_dir / "run_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"mean={res['mean']:.6f}  var={res['var']:.6f}  windows={res['n_windows']}")

    return res


# ---------- MAIN ----------
def main():
    ap = argparse.ArgumentParser(description="Layer C — windowed rhyme density (visual)")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--L", type=int, required=True)
    ap.add_argument("--W", type=int, required=True)
    ap.add_argument("--step", type=int, required=True)
    ap.add_argument("--out_root", required=True)
    ap.add_argument("--tag", required=True)
    args = ap.parse_args()

    results = []
    for f in args.files:
        results.append(analyze_one(Path(f), args))

    run_dir = Path(args.out_root) / args.tag
    ensure_dir(run_dir)

    save_csv(run_dir / "summary_all.csv", results)

    print("\nDONE")


if __name__ == "__main__":
    main()