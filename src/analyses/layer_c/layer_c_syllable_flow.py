# layer_c_syllable_flow.py

import random, argparse, os, csv, json, hashlib
import numpy as np

VOWELS = set("aeiou")
DIGRAPHS = ["sh", "ts", "kh"]

# ---------- HASH ----------

def sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1024*1024):
            h.update(chunk)
    return h.hexdigest()

# ---------- TOKENIZE ----------

def tokenize(text):
    tokens = []
    i = 0
    while i < len(text):
        if text[i] in [" ", "|"]:
            i += 1
            continue
        if i+1 < len(text) and text[i:i+2] in DIGRAPHS:
            tokens.append(text[i:i+2])
            i += 2
        else:
            tokens.append(text[i])
            i += 1
    return tokens

def is_vowel(t):
    return any(c in VOWELS for c in t)

# ---------- NORMALIZE ----------

def normalize(t, eq_kh_k, eq_ts_s):
    if eq_kh_k and t == "kh":
        return "k"
    if eq_ts_s and t == "ts":
        return "s"
    return t

# ---------- BUILD STREAM ----------

def build_stream(text, mode, eq_kh_k, eq_ts_s):
    tokens = tokenize(text)

    stream = []
    prev_c = None
    n = len(tokens)

    for i in range(n):

        t = normalize(tokens[i], eq_kh_k, eq_ts_s)

        if is_vowel(t):

            j = i + 1
            cons = []

            while j < n:
                tj = normalize(tokens[j], eq_kh_k, eq_ts_s)
                if is_vowel(tj):
                    break
                cons.append(tj)
                j += 1

            if cons:
                stream.append(t + "".join(cons))

            else:
                if mode == "permissive" and prev_c:
                    stream.append(prev_c + t)

        else:
            prev_c = t

    return [r for r in stream if len(r) >= 2]

# ---------- METRIC ----------

def nearest_rate(stream, L):
    n = len(stream)
    matches = 0
    for i in range(n):
        for j in range(i+1, min(i+L+1, n)):
            if stream[i] == stream[j]:
                matches += 1
                break
    return matches / n if n else 0

# ---------- WINDOW ----------

def window_profile(stream, L, W, step):
    out = []
    n = len(stream)
    for i in range(0, max(1, n-W+1), step):
        seg = stream[i:i+W]
        out.append((i, nearest_rate(seg, L)))
    return out

# ---------- NULL ----------

def block_permute(stream, block, rng):
    blocks = [stream[i:i+block] for i in range(0, len(stream), block)]
    rng.shuffle(blocks)
    return [x for b in blocks for x in b]

# ---------- ANALYZE ----------

def analyze(file, args):

    with open(file, encoding="utf-8") as f:
        text = f.read()

    stream = build_stream(text, args.mode, args.eq_kh_k, args.eq_ts_s)

    obs = nearest_rate(stream, args.L)

    rng = random.Random(args.seed)

    nulls = []
    for _ in range(args.perm):
        sh = block_permute(stream, args.block, rng)
        nulls.append(nearest_rate(sh, args.L))

    mu = np.mean(nulls)
    sd = np.std(nulls)
    Z = (obs - mu) / sd if sd > 0 else 0

    book = os.path.basename(file).replace("_phonetic.txt","")

    run_dir = os.path.join(args.out_root, args.tag)
    book_dir = os.path.join(run_dir, "books", book)
    os.makedirs(book_dir, exist_ok=True)

    # ---------- CSV ----------

    summary_path = os.path.join(book_dir, f"c1_{args.tag}_summary.csv")

    with open(summary_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["book","mode","L","block","perm","seed","stream_len","obs","null_mean","Z"])
        w.writerow([book,args.mode,args.L,args.block,args.perm,args.seed,len(stream),obs,mu,Z])

    # ---------- PROFILE ----------

    prof = window_profile(stream, args.L, args.W, args.step)
    prof_path = os.path.join(book_dir, f"c1_{args.tag}_profile.csv")

    with open(prof_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pos","rate"])
        w.writerows(prof)

    # ---------- MANIFEST ----------

    manifest = {
        "book": book,
        "input_path": os.path.abspath(file),
        "sha256": sha256_of_file(file),
        "params": {
            "mode": args.mode,
            "L": args.L,
            "block": args.block,
            "perm": args.perm,
            "seed": args.seed
        },
        "stream_len": len(stream)
    }

    with open(os.path.join(book_dir, f"c1_{args.tag}_run_manifest.json"), "w", encoding="utf8") as f:
        json.dump(manifest, f, indent=2)

    # ---------- PRINT ----------

    print("="*70)
    print("BOOK:", book)
    print(f"MODE={args.mode}  L={args.L}  block={args.block}  seed={args.seed}")
    print(f"stream_len={len(stream)}")
    print(f"obs={obs:.6f}  null={mu:.6f}  Z={Z:.3f}")

    return {"book":book,"Z":Z}

# ---------- MAIN ----------

if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--mode", default="permissive")
    ap.add_argument("--L", type=int, default=20)
    ap.add_argument("--block", type=int, default=50)
    ap.add_argument("--perm", type=int, default=200)
    ap.add_argument("--W", type=int, default=1000)
    ap.add_argument("--step", type=int, default=500)
    ap.add_argument("--eq_kh_k", type=int, default=0)
    ap.add_argument("--eq_ts_s", type=int, default=0)
    ap.add_argument("--out_root", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()

    results = []

    for f in args.files:
        res = analyze(f, args)
        results.append(res)

# ---------- SORT ----------
    results_sorted = sorted(results, key=lambda x: x["book"])

# ---------- WRITE SUMMARY ALL ----------
    run_dir = os.path.join(args.out_root, args.tag)
    os.makedirs(run_dir, exist_ok=True)

    summary_all_path = os.path.join(run_dir, f"c1_{args.tag}_summary_all.csv")

    with open(summary_all_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["book", "Z"])
        for r in results_sorted:
            w.writerow([r["book"], r["Z"]])

# ---------- PRINT ----------
    print("\nTOP-LINE RESULTS")
    for r in results_sorted:
        print(f"{r['book']}  Z={r['Z']:.3f}")

    print("\nWROTE:", summary_all_path)