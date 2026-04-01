import sys
import re
import hashlib
import os
import json
import datetime

# =========================
# PATHS
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../../"))

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
ZAQEF = "\u0595"
MAQAF = "\u05BE"

GUTTURALS = {"א", "ה", "ח", "ע"}

# =========================
# CLI FLAGS
# =========================

qamats_as_o = "--qamats-o" in sys.argv

# =========================
# VOWELS (dynamic)
# =========================

def build_vowel_map():
    return {
        "\u05B1": "e",
        "\u05B2": "a",
        "\u05B3": "a",
        "\u05B4": "i",
        "\u05B5": "e",
        "\u05B6": "e",
        "\u05B7": "a",
        "\u05B8": "o" if qamats_as_o else "a",  # ← ключ
        "\u05B9": "o",
        "\u05BB": "u",
    }

VOWELS = build_vowel_map()

KEEP_MARKS = set(VOWELS) | {
    DAGESH, SHEVA, SHIN_DOT, SIN_DOT,
    SOF_PASUQ, ATNAH, ZAQEF_KATAN, ZAQEF
}
VOCALIZATION_MARKS = set(VOWELS) | {DAGESH, SHEVA, SHIN_DOT, SIN_DOT}

# =========================
# UTIL
# =========================

def sha256(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def letters_only(s: str) -> str:
    return "".join(FINAL_TO_BASE.get(ch, ch) for ch in s if ch in HEBREW_LETTERS)

# =========================
# PARSING
# =========================

def parse_units(token: str):
    units = []
    i = 0
    while i < len(token):
        ch = token[i]
        if ch in HEBREW_LETTERS:
            base = FINAL_TO_BASE.get(ch, ch)
            marks = []
            j = i + 1
            while j < len(token) and token[j] not in HEBREW_LETTERS and token[j] != MAQAF:
                if token[j] in KEEP_MARKS:
                    marks.append(token[j])
                j += 1
            units.append((base, marks))
            i = j
        else:
            i += 1
    return units

def token_has_vocalization(token: str) -> bool:
    return any(ch in VOCALIZATION_MARKS for ch in token)

def unit_info(unit):
    letter, marks = unit
    return {
        "letter": letter,
        "marks": marks,
        "dagesh": DAGESH in marks,
        "sheva": SHEVA in marks,
        "shin_dot": SHIN_DOT in marks,
        "sin_dot": SIN_DOT in marks,
        "vowel_marks": [m for m in marks if m in VOWELS],
    }

def own_vowel(letter: str, info: dict) -> str:
    if letter == "ו" and info["dagesh"] and not info["vowel_marks"]:
        return "u"
    for m in info["marks"]:
        if m in VOWELS:
            return VOWELS[m]
    return ""

# =========================
# CONSONANTS
# =========================

def map_consonant(letter: str, info: dict, idx: int, n: int, ownv: str) -> str:
    if letter in ("א", "ע"):
        return ""

    if letter == "ה":
        if idx == n - 1:
            return ""
        return "h"

    if letter == "ב":
        return "b" if info["dagesh"] else "v"
    if letter == "כ":
        return "k" if info["dagesh"] else "kh"
    if letter == "פ":
        return "p" if info["dagesh"] else "f"
    if letter == "ש":
        return "s" if info["sin_dot"] else "sh"
    if letter == "צ":
        return "ts"
    if letter == "ק":
        return "q"
    if letter == "ח":
        return "h"
    if letter == "ט":
        return "t"
    if letter == "ת":
        return "t"

    if letter == "ו":
        if ownv in ("o", "u"):
            return ""
        return "v"

    if letter == "י":
        return "y"

    table = {
        "ג": "g", "ד": "d", "ז": "z", "ל": "l",
        "מ": "m", "נ": "n", "ס": "s", "ר": "r",
    }
    return table.get(letter, letter)

# =========================
# MAIN TRANSLITERATION
# =========================

def transliterate_word(token: str) -> str:
    base_letters = letters_only(token)

    if base_letters == "יהוה":
        return "adonai"
    if base_letters in {"אלהים", "אלוהים"}:
        return "elohim"

    if base_letters and not token_has_vocalization(token):
        return ""

    units = parse_units(token)
    if not units:
        return ""

    infos = [unit_info(u) for u in units]

    out = []
    prev_vowel = None
    n = len(units)

    for idx, (letter, marks) in enumerate(units):
        info = infos[idx]
        ownv = own_vowel(letter, info)

        next_has_sheva = idx + 1 < n and infos[idx + 1]["sheva"]
        next_letter = infos[idx + 1]["letter"] if idx + 1 < n else None
        next_ownv = own_vowel(next_letter, infos[idx + 1]) if idx + 1 < n else ""

        if letter == "י" and not ownv and not info["sheva"]:
            if idx == 0 or prev_vowel != "i":
                out.append("y")
            continue

        if letter == "י" and ownv:
            seg = "i" if (ownv == "i" and prev_vowel == "i") else "y" + ownv
            out.append(seg)
            prev_vowel = ownv
            continue

        vowel = ""
        if ownv:
            vowel = ownv
        elif info["sheva"]:
            if idx == n - 1:
                vowel = ""
            elif idx == 0:
                vowel = "e"
            elif infos[idx - 1]["sheva"]:
                vowel = "e"
            elif next_letter in GUTTURALS and next_ownv:
                vowel = "e"
            elif next_has_sheva:
                vowel = ""
            elif prev_vowel in ("o", "u"):
                vowel = "e"

        if letter == "ח" and idx == n - 1 and ownv == "a":
            out.append("ah")
            prev_vowel = "a"
            continue

        cons = map_consonant(letter, info, idx, n, ownv)

        seg = ownv if (letter == "ו" and ownv in ("o", "u")) else cons + vowel

        if seg:
            out.append(seg)
            prev_vowel = ownv or vowel

    return "".join(out)

# =========================
# BUILDERS
# =========================

def normalize_torah_text(text: str) -> str:
    text = text.replace(MAQAF, " ")
    text = re.sub(r"\[[^\]]*\]", " ", text)
    text = re.sub(r"\([^)]*\)", " ", text)
    text = re.sub(r"\d+", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def build_torah(text: str) -> str:
    text = normalize_torah_text(text)
    raw_tokens = re.split(r"\s+", text.strip())
    out = []

    for raw in raw_tokens:
        punct = "|" if (SOF_PASUQ in raw or ATNAH in raw or ZAQEF_KATAN in raw) else ""

        phon = transliterate_word(raw)
        if phon:
            out.append(phon)
        if punct:
            out.append("|")

    return " ".join(out)

def build_modern(text: str) -> str:
    text = text.replace(MAQAF, " ")
    text = re.sub(r"(?<=\s)[א-ת]{1,3}\.\s*", " ", text)
    text = re.sub(r"\d+", " ", text)
    text = re.sub(r"[.?!;:,]+", " | ", text)
    text = re.sub(r"[–—\-]+", " ", text)
    text = re.sub(r"[\"'„“”‘’()\[\]{}<>/\\]", " ", text)
    text = text.replace("״", " ").replace("׳", " ")
    text = text.replace("…", " | ")
    text = re.sub(r"\s+", " ", text).strip()

    out = []
    for raw in text.split():
        if raw == "|":
            out.append("|")
        else:
            phon = transliterate_word(raw)
            if phon:
                out.append(phon)

    phon = " ".join(out)
    phon = re.sub(r"\s*\|\s*", " | ", phon)
    phon = re.sub(r"\|\s*\|+", "|", phon)
    return phon.strip("| ").strip()

# =========================
# MAIN
# =========================

def main():
    if len(sys.argv) < 4:
        print("Usage: python phonetic_pipeline.py input.txt output.txt torah|modern [--qamats-o]")
        sys.exit(1)

    inp, outp, mode = sys.argv[1], sys.argv[2], sys.argv[3].lower()

    if qamats_as_o:
        base, ext = os.path.splitext(outp)
        outp = base + "_qo" + ext

    with open(inp, encoding="utf8") as f:
        raw = f.read()

    phon = build_torah(raw) if mode == "torah" else build_modern(raw)

    with open(outp, "w", encoding="utf8") as f:
        f.write(phon)

    meta = {
        "mode": mode,
        "qamats": "o" if qamats_as_o else "a",
        "input_sha256": sha256(inp),
        "output_sha256": sha256(outp),
        "timestamp": datetime.datetime.now().isoformat()
    }

    with open(outp + ".meta.json", "w", encoding="utf8") as f:
        json.dump(meta, f, indent=2)

    words = [w for w in phon.split() if w != "|"]

    print("WORDS:", len(words))
    print("UNIQUE_WORDS:", len(set(words)))
    print("QAMATS:", meta["qamats"])
    print("SHA256:", meta["output_sha256"])


if __name__ == "__main__":
    main()