import argparse
import os
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime

# =========================
# CONSTANTS
# =========================

HEBREW_LETTERS = set("אבגדהוזחטיכלמנסעפצקרשתךםןףץ")
FINAL_TO_BASE = {"ך": "כ", "ם": "מ", "ן": "נ", "ף": "פ", "ץ": "צ"}

DAGESH = "\u05BC"
SHEVA = "\u05B0"
SHIN_DOT = "\u05C1"
SIN_DOT = "\u05C2"

SOF_PASUQ = "\u05C3"
ATNAH = "\u0591"
ZAQEF_KATAN = "\u0594"
MAQAF = "\u05BE"

GUTTURALS = {"א", "ה", "ח", "ע"}

# =========================
# HASH
# =========================

def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

# =========================
# VOWELS
# =========================

def build_vowel_map(qamats_o=False):
    return {
        "\u05B1": "e",
        "\u05B2": "a",
        "\u05B3": "a",
        "\u05B4": "i",
        "\u05B5": "e",
        "\u05B6": "e",
        "\u05B7": "a",
        "\u05B8": "o" if qamats_o else "a",
        "\u05B9": "o",
        "\u05BB": "u",
    }

# =========================
# CORE
# =========================

def transliterate_word(token, VOWELS):
    base = "".join(FINAL_TO_BASE.get(ch, ch) for ch in token if ch in HEBREW_LETTERS)

    if base == "יהוה":
        return "adonai"
    if base in {"אלהים", "אלוהים"}:
        return "elohim"

    units = re.findall(r"[אבגדהוזחטיכלמנסעפצקרשת][^\s]*", token)
    if not units:
        return ""

    out = []
    for ch in token:
        if ch in VOWELS:
            out.append(VOWELS[ch])
        elif ch in HEBREW_LETTERS:
            out.append({
                "ב":"v","כ":"kh","פ":"f","ש":"sh","צ":"ts",
                "ק":"q","ח":"h","ט":"t","ת":"t",
                "ג":"g","ד":"d","ז":"z","ל":"l",
                "מ":"m","נ":"n","ס":"s","ר":"r"
            }.get(ch,""))
    return "".join(out)

# =========================
# BUILD
# =========================

def process_file(inp, outp, mode, qamats_o):
    VOWELS = build_vowel_map(qamats_o)

    with open(inp, encoding="utf-8") as f:
        text = f.read()

    text = text.replace(MAQAF, " ")
    text = re.sub(r"\d+", " ", text)

    words = re.split(r"\s+", text)

    out = []
    for w in words:
        if any(x in w for x in [SOF_PASUQ, ATNAH, ZAQEF_KATAN]):
            out.append("|")

        phon = transliterate_word(w, VOWELS)
        if phon:
            out.append(phon)

    result = " ".join(out)

    with open(outp, "w", encoding="utf-8") as f:
        f.write(result)

    meta = {
        "mode": mode,
        "qamats": "o" if qamats_o else "a",
        "input_sha256": sha256(inp),
        "output_sha256": sha256(outp),
        "timestamp": datetime.utcnow().isoformat()
    }

    with open(outp + ".meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

# =========================
# VERIFY
# =========================

def verify(outdir):
    errors = []
    for root, _, files in os.walk(outdir):
        for f in files:
            if not f.endswith(".txt"):
                continue
            p = os.path.join(root, f)
            meta = p + ".meta.json"
            if not os.path.exists(meta):
                errors.append(p)
    return errors

# =========================
# MAIN
# =========================

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--torah_in", required=True)
    parser.add_argument("--modern_in", required=True)
    parser.add_argument("--out", required=True)

    args = parser.parse_args()

    torah_out = Path(args.out) / "torah"
    modern_out = Path(args.out) / "modern"

    torah_out.mkdir(parents=True, exist_ok=True)
    modern_out.mkdir(parents=True, exist_ok=True)

    # Torah
    for f in os.listdir(args.torah_in):
        if not f.endswith(".txt"):
            continue
        inp = os.path.join(args.torah_in, f)
        base = f.replace("_raw.txt","")

        process_file(inp, torah_out / f"{base}_phonetic.txt", "torah", False)

    # Modern (1 файл)
    for f in os.listdir(args.modern_in):
        if not f.endswith(".txt"):
            continue
        inp = os.path.join(args.modern_in, f)
        base = f.replace("_raw.txt","")

        process_file(inp, modern_out / f"{base}_phonetic.txt", "modern", False)

    errs = verify(args.out)

    print("DONE")
    print("Errors:", len(errs))

if __name__ == "__main__":
    main()