#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse, random, csv, json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, pstdev

DIGRAPHS = ("sh","kh","ts")
BOUNDARY = "|"

# -----------------------

def tokenize(w):
    out=[]; i=0
    while i<len(w):
        if w[i:i+2] in DIGRAPHS:
            out.append(w[i:i+2]); i+=2
        else:
            out.append(w[i]); i+=1
    return out

def load(path):
    words = Path(path).read_text(encoding="utf8").split()

    segs=[]; cur=[]
    for w in words:
        if w==BOUNDARY:
            if cur: segs.append(cur)
            cur=[]
        else:
            cur.extend(tokenize(w))
    if cur: segs.append(cur)

    return segs

def flatten(segs):
    return [x for s in segs for x in s]

# -----------------------

def kgrams(stream,k):
    grams=[]; pos=defaultdict(list)
    for i in range(len(stream)-k+1):
        g=tuple(stream[i:i+k])
        grams.append(g)
        pos[g].append(i)
    return grams,pos

def gap_metric(stream,k):
    grams,pos=kgrams(stream,k)

    gaps=[]
    for g,p in pos.items():
        if len(p)>1:
            for i in range(len(p)-1):
                gaps.append(p[i+1]-p[i])

    return mean(gaps) if gaps else None

def z(obs,vals):
    vals=[x for x in vals if x is not None]
    if not vals: return None
    mu=mean(vals); sd=pstdev(vals)
    return (obs-mu)/sd if sd>0 else None

def fmt(x):
    return "NA" if x is None else f"{x:.6f}"

# -----------------------

def run_one(file,k,perm,seed):

    segs = load(file)
    stream = flatten(segs)

    # baseline
    gap_base = gap_metric(stream,k)

    # boundary-aware
    bound_vals=[gap_metric(s,k) for s in segs]
    gap_boundary = mean([x for x in bound_vals if x is not None])

    # full shuffle
    rng=random.Random(seed)
    null_full=[]
    for _ in range(perm):
        s=stream[:]
        rng.shuffle(s)
        null_full.append(gap_metric(s,k))
    z_full = z(gap_base,null_full)

    # segment shuffle
    rng=random.Random(seed)
    null_seg=[]
    for _ in range(perm):
        s2=segs[:]
        rng.shuffle(s2)
        null_seg.append(gap_metric(flatten(s2),k))
    z_seg = z(gap_base,null_seg)

    return {
        "file": file,
        "gap": gap_base,
        "gap_boundary": gap_boundary,
        "z_full": z_full,
        "z_segment": z_seg
    }

# -----------------------

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--k",type=int,default=3)
    ap.add_argument("--perm",type=int,default=1000)
    ap.add_argument("--seed",type=int,default=1)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--tag", default="baseline")
    args=ap.parse_args()

    run_dir = Path(args.out_dir)/args.tag
    run_dir.mkdir(parents=True,exist_ok=True)

    rows=[]

    for f in args.files:
        res = run_one(f,args.k,args.perm,args.seed)

        print("\nFILE:",res["file"])
        print("gap baseline:",fmt(res["gap"]))
        print("gap boundary:",fmt(res["gap_boundary"]))
        print("Z full:",fmt(res["z_full"]))
        print("Z segment:",fmt(res["z_segment"]))

        rows.append(res)

    # save summary
    with open(run_dir/"boundary_controls_summary.csv","w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

    print("\nWROTE:", run_dir/"boundary_controls_summary.csv")

if __name__=="__main__":
    main()