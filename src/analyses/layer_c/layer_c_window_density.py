# layer_c_window_density.py

import argparse, random, os, csv
import numpy as np
import matplotlib.pyplot as plt

VOWELS = set("aeiou")
DIGRAPHS = ["sh","ts","kh"]

# ---------- TOKENIZE ----------
def tokenize(text):
    tokens=[]
    i=0
    while i<len(text):
        if text[i] in [" ","|"]:
            i+=1; continue
        if i+1<len(text) and text[i:i+2] in DIGRAPHS:
            tokens.append(text[i:i+2]); i+=2
        else:
            tokens.append(text[i]); i+=1
    return tokens

def is_vowel(t):
    return any(c in VOWELS for c in t)

# ---------- STREAM ----------
def build_stream(text, mode="permissive"):
    tokens = tokenize(text)
    stream=[]
    prev_c=None

    for i in range(len(tokens)):
        t=tokens[i]

        if is_vowel(t):
            j=i+1; cons=[]
            while j<len(tokens):
                if is_vowel(tokens[j]): break
                cons.append(tokens[j]); j+=1

            if cons:
                stream.append(t+"".join(cons))
            elif mode=="permissive" and prev_c:
                stream.append(prev_c+t)
        else:
            prev_c=t

    return stream

# ---------- SUPPORT ----------
def support_array(stream,L):
    n=len(stream)
    sup=[0]*n
    for i in range(n):
        for j in range(i+1,min(i+L+1,n)):
            if stream[i]==stream[j]:
                sup[i]=1; break
    return sup

# ---------- WINDOWS ----------
def window_density(stream,L,W,step):
    sup = support_array(stream,L)
    res=[]

    for start in range(0,len(stream)-W,step):
        window = sup[start:start+W]
        res.append(sum(window)/len(window))

    return res

# ---------- NULL ----------
def block_shuffle(stream,block,rng):
    blocks=[stream[i:i+block] for i in range(0,len(stream),block)]
    rng.shuffle(blocks)
    return [x for b in blocks for x in b]

# ---------- SMOOTH ----------
def smooth(x, k=5):
    if k <= 1:
        return x
    return np.convolve(x, np.ones(k)/k, mode='same')

# ---------- ANALYZE ----------
def analyze(file,args):

    text=open(file,encoding="utf-8").read()
    stream = build_stream(text, args.mode)

    obs = window_density(stream,args.L,args.W,args.step)

    mean_obs = np.mean(obs)
    var_obs = np.var(obs)
    min_obs = np.min(obs)

    low_frac = np.mean([x < args.threshold for x in obs])

    rng=random.Random(args.seed)

    null_means=[]; null_vars=[]; null_mins=[]

    for _ in range(args.perm):
        sh = block_shuffle(stream,args.block,rng)
        w = window_density(sh,args.L,args.W,args.step)

        null_means.append(np.mean(w))
        null_vars.append(np.var(w))
        null_mins.append(np.min(w))

    def z(obs,arr):
        mu=np.mean(arr); sd=np.std(arr)
        return (obs-mu)/sd if sd>0 else 0

    z_mean = z(mean_obs,null_means)
    z_var  = z(var_obs,null_vars)
    z_min  = z(min_obs,null_mins)

    name=os.path.basename(file).replace("_phonetic.txt","")
    outdir=os.path.join(args.out_root,args.tag,name)
    os.makedirs(outdir,exist_ok=True)

    # CSV
    with open(os.path.join(outdir,"windows.csv"),"w",newline="") as f:
        w=csv.writer(f)
        w.writerow(["idx","rate"])
        for i,x in enumerate(obs):
            w.writerow([i,x])

    # plot (normalized x)
    x = np.linspace(0,1,len(obs))
    y_s = smooth(obs, args.smooth)

    # plt.figure(figsize=(12,4))
    # plt.plot(x, obs, alpha=0.4)
    # plt.plot(x, y_s)
    # plt.axhline(args.threshold, linestyle="--")
    # plt.title(name)
    # plt.savefig(os.path.join(outdir,"plot.png"))
    # plt.close()

    print("="*60)
    print(name)
    print(f"mean={mean_obs:.3f} Z={z_mean:.2f}")
    print(f"var={var_obs:.5f} Z={z_var:.2f}")
    print(f"min={min_obs:.3f} Z={z_min:.2f}")
    print(f"low_frac={low_frac:.3f}")

# ---------- MAIN ----------
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("files",nargs="+")
    ap.add_argument("--L",type=int,default=20)
    ap.add_argument("--W",type=int,default=800)
    ap.add_argument("--step",type=int,default=200)
    ap.add_argument("--block",type=int,default=50)
    ap.add_argument("--perm",type=int,default=200)
    ap.add_argument("--seed",type=int,default=1)
    ap.add_argument("--mode",choices=["permissive","strict"],default="permissive")
    ap.add_argument("--threshold",type=float,default=0.15)
    ap.add_argument("--smooth",type=int,default=5)
    ap.add_argument("--out_root",required=True)
    ap.add_argument("--tag",required=True)
    args=ap.parse_args()

    for f in args.files:
        analyze(f,args)