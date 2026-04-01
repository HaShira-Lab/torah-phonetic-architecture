# layer_c_syllable_distance.py

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

def normalize(t, eq_kh_k, eq_ts_s):
    if eq_kh_k and t == "kh":
        return "k"
    if eq_ts_s and t == "ts":
        return "s"
    return t

# ---------- BUILD STREAM (FIXED) ----------
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

# ---------- METRICS ----------
def nearest_rate(stream, L):
    n = len(stream)
    matches = 0
    for i in range(n):
        for j in range(i+1, min(i+L+1, n)):
            if stream[i] == stream[j]:
                matches += 1
                break
    return matches / n if n else 0

def distance_profile(stream, Dmax):
    n = len(stream)
    out = []
    for d in range(1, Dmax+1):
        denom = n - d
        hits = sum(1 for i in range(n-d) if stream[i] == stream[i+d]) if denom>0 else 0
        rate = hits / denom if denom>0 else 0
        out.append((d, hits, denom, rate))
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
    rng = random.Random(args.seed)

    # global
    obs_global = nearest_rate(stream, args.L)
    null_global = []

    # distance
    obs_prof = distance_profile(stream, args.Dmax)
    null_by_d = {d: [] for d in range(1, args.Dmax+1)}

    for _ in range(args.perm):
        sh = block_permute(stream, args.block, rng)

        null_global.append(nearest_rate(sh, args.L))

        prof = distance_profile(sh, args.Dmax)
        for d, _, _, rate in prof:
            null_by_d[d].append(rate)

    g_mu = np.mean(null_global)
    g_sd = np.std(null_global)
    g_z = (obs_global - g_mu)/g_sd if g_sd>0 else 0

    book = os.path.basename(file).replace("_phonetic.txt","")

    run_dir = os.path.join(args.out_root, args.tag)
    book_dir = os.path.join(run_dir, "books", book)
    os.makedirs(book_dir, exist_ok=True)

    # ---------- SUMMARY ----------
    with open(os.path.join(book_dir, f"c1_2_{args.tag}_summary.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["book","Z"])
        w.writerow([book, g_z])

    # ---------- DISTANCE ----------
    rows = []
    with open(os.path.join(book_dir, f"c1_2_{args.tag}_distance.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["d","obs","null","Z"])
        for d,_,_,obs in obs_prof:
            mu = np.mean(null_by_d[d])
            sd = np.std(null_by_d[d])
            z = (obs-mu)/sd if sd>0 else 0
            w.writerow([d,obs,mu,z])
            rows.append((d,z))

    # ---------- PRINT ----------
    print("="*70)
    print("BOOK:", book)
    print(f"Z_global={g_z:.3f}")
    print("Top peaks:")
    for d,z in sorted(rows, key=lambda x:x[1], reverse=True)[:5]:
        print(f"d={d} Z={z:.2f}")

    return {"book":book,"Z":g_z}

# ---------- MAIN ----------
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--mode", default="permissive")
    ap.add_argument("--L", type=int, default=20)
    ap.add_argument("--Dmax", type=int, default=40)
    ap.add_argument("--block", type=int, default=50)
    ap.add_argument("--perm", type=int, default=200)
    ap.add_argument("--eq_kh_k", type=int, default=0)
    ap.add_argument("--eq_ts_s", type=int, default=0)
    ap.add_argument("--out_root", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()

    results = [analyze(f,args) for f in args.files]

    run_dir = os.path.join(args.out_root, args.tag)
    os.makedirs(run_dir, exist_ok=True)

    with open(os.path.join(run_dir,f"c1_2_{args.tag}_summary_all.csv"),"w",newline="") as f:
        w=csv.writer(f)
        w.writerow(["book","Z"])
        for r in sorted(results,key=lambda x:x["book"]):
            w.writerow([r["book"],r["Z"]])

    print("\nDONE")