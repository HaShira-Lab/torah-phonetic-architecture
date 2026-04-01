#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, pstdev

DIGRAPHS = ("sh", "kh", "ts")
BOUNDARY = "|"
VOWELS = {"a", "e", "i", "o", "u"}


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def tokenize_word(word: str):
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


def corpus_name_from_path(path: Path) -> str:
    stem = path.stem.lower()
    if stem.endswith("_phonetic_qo"):
        stem = stem[:-12]
    elif stem.endswith("_phonetic"):
        stem = stem[:-9]
    return stem


def load_stream(path: Path):
    text = path.read_text(encoding="utf8").strip()
    tokens = text.split()

    stream = []
    lexical_tokens = 0
    boundary_count = 0

    for tok in tokens:
        if tok == BOUNDARY:
            boundary_count += 1
            continue
        lexical_tokens += 1
        stream.extend(tokenize_word(tok))

    return stream, lexical_tokens, boundary_count


def normalize_phoneme(ph: str, mode: str):
    if mode == "exact":
        return ph
    mapping = {
        "d": "t",
        "z": "s",
        "q": "k",
        "v": "b",
    }
    return mapping.get(ph, ph)


def normalize_stream(stream, mode: str):
    return [normalize_phoneme(x, mode) for x in stream]


def is_anchor(ph: str) -> bool:
    return ph not in VOWELS


def build_anchor_events(stream):
    events = []
    pos = defaultdict(list)

    if len(stream) < 3:
        return events, pos

    for i in range(1, len(stream) - 1):
        c = stream[i]
        if not is_anchor(c):
            continue
        event = (c, stream[i - 1], stream[i + 1])
        pos[event].append(len(events))
        events.append(event)

    return events, pos


def compute_metrics(stream):
    events, pos = build_anchor_events(stream)
    total = len(events)

    if total == 0:
        return {
            "stream_len": len(stream),
            "total_events": 0,
            "types_total": 0,
            "types_repeated": 0,
            "token_repeat_fraction": 0.0,
            "type_repeat_fraction": 0.0,
            "mean_gap": None,
            "median_gap": None,
            "n_gaps": 0,
        }

    counts = Counter(events)
    repeated_types = [g for g, c in counts.items() if c > 1]
    repeated_token_count = sum(c for c in counts.values() if c > 1)

    gaps = []
    for g in repeated_types:
        positions = pos[g]
        for i in range(len(positions) - 1):
            gaps.append(positions[i + 1] - positions[i])

    return {
        "stream_len": len(stream),
        "total_events": total,
        "types_total": len(counts),
        "types_repeated": len(repeated_types),
        "token_repeat_fraction": repeated_token_count / total,
        "type_repeat_fraction": len(repeated_types) / len(counts),
        "mean_gap": mean(gaps) if gaps else None,
        "median_gap": sorted(gaps)[len(gaps) // 2] if gaps else None,
        "n_gaps": len(gaps),
    }


def block_shuffle_stream(stream, block_size: int, rng: random.Random):
    if block_size <= 1 or len(stream) <= block_size:
        out = stream[:]
        rng.shuffle(out)
        return out

    blocks = [stream[i:i + block_size] for i in range(0, len(stream), block_size)]
    rng.shuffle(blocks)

    shuffled = []
    for b in blocks:
        shuffled.extend(b)
    return shuffled


def null_distribution(stream, block_size: int, n_perm: int, seed: int):
    rng = random.Random(seed)

    token_vals = []
    type_vals = []
    gap_vals = []

    for p in range(n_perm):
        if (p + 1) % max(1, n_perm // 10) == 0 or p == 0 or p + 1 == n_perm:
            print(f"  perm {p + 1}/{n_perm}")

        shuf = block_shuffle_stream(stream, block_size, rng)
        m = compute_metrics(shuf)

        token_vals.append(m["token_repeat_fraction"])
        type_vals.append(m["type_repeat_fraction"])
        gap_vals.append(m["mean_gap"] if m["mean_gap"] is not None else math.nan)

    return {
        "token_repeat_fraction": token_vals,
        "type_repeat_fraction": type_vals,
        "mean_gap": gap_vals,
    }


def zscore(obs, values):
    vals = [x for x in values if x == x]
    if not vals:
        return None, None, None
    mu = mean(vals)
    sd = pstdev(vals)
    z = None if sd == 0 else (obs - mu) / sd
    return mu, sd, z


def fmt(x):
    if x is None:
        return "NA"
    return f"{x:.6f}"


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def save_csv(path: Path, rows):
    if not rows:
        return
    with path.open("w", encoding="utf8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def run_one(file_path: Path, mode: str, block_size: int, n_perm: int, seed: int):
    raw_stream, lexical_tokens, boundary_count = load_stream(file_path)
    stream = normalize_stream(raw_stream, mode)

    obs = compute_metrics(stream)
    nulls = null_distribution(stream, block_size, n_perm, seed)

    mu_tok, sd_tok, z_tok = zscore(obs["token_repeat_fraction"], nulls["token_repeat_fraction"])
    mu_typ, sd_typ, z_typ = zscore(obs["type_repeat_fraction"], nulls["type_repeat_fraction"])
    mu_gap, sd_gap, z_gap = (
        zscore(obs["mean_gap"], nulls["mean_gap"])
        if obs["mean_gap"] is not None else (None, None, None)
    )

    return {
        "file": str(file_path),
        "book": corpus_name_from_path(file_path),
        "mode": mode,
        "block_size": block_size,
        "n_perm": n_perm,
        "seed": seed,
        "lexical_tokens": lexical_tokens,
        "boundary_count_removed": boundary_count,
        **obs,
        "null_token_repeat_mean": mu_tok,
        "null_token_repeat_sd": sd_tok,
        "z_token_repeat": z_tok,
        "null_type_repeat_mean": mu_typ,
        "null_type_repeat_sd": sd_typ,
        "z_type_repeat": z_typ,
        "null_mean_gap_mean": mu_gap,
        "null_mean_gap_sd": sd_gap,
        "z_mean_gap": z_gap,
    }


def print_result(res: dict):
    print("=" * 72)
    print(f"BOOK: {res['book']}")
    print(f"MODE={res['mode']}  block={res['block_size']}  perm={res['n_perm']}")
    print(f"STREAM_LEN={res['stream_len']}  TOTAL_EVENTS={res['total_events']}  TYPES={res['types_total']}")
    print(
        f"[TOKEN] obs={fmt(res['token_repeat_fraction'])}  "
        f"null={fmt(res['null_token_repeat_mean'])}  Z={fmt(res['z_token_repeat'])}"
    )
    print(
        f"[TYPE ] obs={fmt(res['type_repeat_fraction'])}  "
        f"null={fmt(res['null_type_repeat_mean'])}  Z={fmt(res['z_type_repeat'])}"
    )
    print(
        f"[GAP  ] obs={fmt(res['mean_gap'])}  "
        f"null={fmt(res['null_mean_gap_mean'])}  Z={fmt(res['z_mean_gap'])}"
    )


def main():
    ap = argparse.ArgumentParser(description="Layer B anchor participation test")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--mode", choices=["exact", "equiv"], default="exact")
    ap.add_argument("--block", type=int, default=80)
    ap.add_argument("--perm", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--tag", default="baseline")
    ap.add_argument("--out_dir", required=True)
    args = ap.parse_args()

    out_root = Path(args.out_dir)
    run_dir = out_root / args.tag
    books_root = run_dir / "books"

    ensure_dir(run_dir)
    ensure_dir(books_root)

    summary_rows = []
    important_rows = []

    print("FILES TO PROCESS:")
    for fp in args.files:
        print(" ", fp)
    print()

    for fp in args.files:
        file_path = Path(fp)
        book = corpus_name_from_path(file_path)

        book_dir = books_root / book
        ensure_dir(book_dir)

        res = run_one(
            file_path=file_path,
            mode=args.mode,
            block_size=args.block,
            n_perm=args.perm,
            seed=args.seed,
        )
        print_result(res)

        summary_rows.append(res)
        important_rows.append({
            "book": res["book"],
            "mode": res["mode"],
            "block_size": res["block_size"],
            "n_perm": res["n_perm"],
            "z_token_repeat": res["z_token_repeat"],
            "z_type_repeat": res["z_type_repeat"],
            "z_mean_gap": res["z_mean_gap"],
            "token_repeat_fraction": res["token_repeat_fraction"],
            "type_repeat_fraction": res["type_repeat_fraction"],
            "mean_gap": res["mean_gap"],
        })

        save_csv(book_dir / f"layer_b_anchor_{args.tag}_metrics.csv", [res])

        log = {
            "book": book,
            "input_path": str(file_path.resolve()),
            "sha256": sha256_of_file(file_path),
            "tag": args.tag,
            "params": {
                "mode": args.mode,
                "block": args.block,
                "perm": args.perm,
                "seed": args.seed,
                "out_dir": str(out_root.resolve()),
            },
            "stream_info": {
                "lexical_tokens": res["lexical_tokens"],
                "boundary_count_removed": res["boundary_count_removed"],
                "phoneme_stream_len": res["stream_len"],
                "digraphs_atomic": list(DIGRAPHS),
            },
        }
        with (book_dir / f"layer_b_anchor_{args.tag}_run_manifest.json").open("w", encoding="utf8") as f:
            json.dump(log, f, ensure_ascii=False, indent=2)

    summary_rows_sorted = sorted(summary_rows, key=lambda x: x["book"])
    important_rows_sorted = sorted(important_rows, key=lambda x: x["book"])

    save_csv(run_dir / f"layer_b_anchor_{args.tag}_summary_all.csv", summary_rows_sorted)
    save_csv(run_dir / f"layer_b_anchor_{args.tag}_important_summary.csv", important_rows_sorted)

    manifest = {
        "script": "layer_b_anchor_participation.py",
        "tag": args.tag,
        "files": [str(Path(f).resolve()) for f in args.files],
        "params": {
            "mode": args.mode,
            "block": args.block,
            "perm": args.perm,
            "seed": args.seed,
        },
    }
    with (run_dir / f"layer_b_anchor_{args.tag}_run_manifest.json").open("w", encoding="utf8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print("\nTOP-LINE RESULTS")
    for row in important_rows_sorted:
        print(
            f"{row['book']}  "
            f"z_token={fmt(row['z_token_repeat'])}  "
            f"z_type={fmt(row['z_type_repeat'])}  "
            f"z_gap={fmt(row['z_mean_gap'])}"
        )

    print(f"\nWROTE: {run_dir / f'layer_b_anchor_{args.tag}_summary_all.csv'}")
    print(f"WROTE: {run_dir / f'layer_b_anchor_{args.tag}_important_summary.csv'}")
    print(f"WROTE: {run_dir / f'layer_b_anchor_{args.tag}_run_manifest.json'}")


if __name__ == "__main__":
    main()