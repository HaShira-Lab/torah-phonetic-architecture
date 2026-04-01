import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests


BASE_URL = (
    "https://www.sefaria.org/api/texts/{}"
    "?lang=he&vhe=Tanach_with_Ta%27amei_Hamikra"
    "&context=0&pad=0&commentary=0"
)

DEFAULT_BOOKS = [
    "Genesis",
    "Exodus",
    "Leviticus",
    "Numbers",
    "Deuteronomy",
]


def flatten_text(node):
    if isinstance(node, list):
        out = []
        for item in node:
            out.extend(flatten_text(item))
        return out
    if isinstance(node, str):
        return [node]
    return []


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def safe_filename(book: str) -> str:
    return f"{book.lower().replace(' ', '_')}_raw.txt"


def download_book(session: requests.Session, book: str) -> tuple[str, list[str], str]:
    url = BASE_URL.format(book.replace(" ", "%20"))
    response = session.get(url, timeout=60)
    response.raise_for_status()

    data = response.json()
    if "he" not in data:
        raise ValueError("Missing 'he' field in Sefaria response")

    verses = flatten_text(data["he"])
    if not verses:
        raise ValueError("No Hebrew text segments found")

    full_text = "\n".join(v.strip() for v in verses if isinstance(v, str)).strip()
    if not full_text:
        raise ValueError("Downloaded text is empty")

    return url, verses, full_text


def write_summary_csv(path: Path, rows: list[dict]) -> None:
    fieldnames = [
        "book",
        "status",
        "file",
        "segments",
        "chars",
        "sha256",
        "source_url",
        "error",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download Torah books from Sefaria into explicit output directory."
    )
    parser.add_argument(
        "--books",
        nargs="+",
        required=True,
        help="Books to download, e.g. Genesis Exodus Leviticus Numbers Deuteronomy",
    )
    parser.add_argument(
        "--outdir",
        required=True,
        help="Output directory for downloaded raw text and manifests",
    )
    parser.add_argument(
        "--version-name",
        default="Tanach_with_Ta'amei_Hamikra",
        help="Human-readable source version name for manifest",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    started_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    manifest = {
        "script": "download_torah.py",
        "source": "Sefaria API",
        "version_name": args.version_name,
        "started_utc": started_utc,
        "outdir": str(outdir),
        "books_requested": args.books,
        "results": [],
    }

    summary_rows = []
    ok_count = 0

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "HSR-Project-Downloader/1.0"
        }
    )

    print("=== DOWNLOAD TORAH ===")
    print(f"OUTDIR: {outdir}")
    print(f"BOOKS : {', '.join(args.books)}")
    print()

    for book in args.books:
        print(f"[DOWNLOAD] {book}")
        try:
            source_url, verses, full_text = download_book(session, book)
            filename = safe_filename(book)
            filepath = outdir / filename
            filepath.write_text(full_text, encoding="utf-8")

            sha = sha256_text(full_text)
            row = {
                "book": book,
                "status": "ok",
                "file": filename,
                "segments": len(verses),
                "chars": len(full_text),
                "sha256": sha,
                "source_url": source_url,
                "error": "",
            }
            summary_rows.append(row)
            manifest["results"].append(row)
            ok_count += 1

            print(f"  OK   file={filename}")
            print(f"  segs={len(verses)}  chars={len(full_text)}")
            print(f"  sha256={sha}")
        except Exception as e:
            row = {
                "book": book,
                "status": "error",
                "file": "",
                "segments": "",
                "chars": "",
                "sha256": "",
                "source_url": "",
                "error": str(e),
            }
            summary_rows.append(row)
            manifest["results"].append(row)

            print(f"  ERROR: {e}")

        print()

    finished_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    manifest["finished_utc"] = finished_utc
    manifest["ok_count"] = ok_count
    manifest["error_count"] = len(args.books) - ok_count

    summary_csv = outdir / "download_summary.csv"
    manifest_json = outdir / "download_manifest.json"

    write_summary_csv(summary_csv, summary_rows)
    manifest_json.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("=== DONE ===")
    print(f"OK     : {ok_count}/{len(args.books)}")
    print(f"CSV    : {summary_csv}")
    print(f"MANIFEST: {manifest_json}")

    if ok_count != len(args.books):
        sys.exit(1)


if __name__ == "__main__":
    main()