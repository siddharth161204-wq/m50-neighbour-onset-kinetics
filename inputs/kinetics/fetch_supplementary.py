#!/usr/bin/env python3
"""Download the supplementary material of Koenig, Zhao and Deng (2025) and check it against the recorded hashes.

Usage: python3 fetch_supplementary.py [--dest supplementary]

The zip is not redistributed here. It holds An_Ele.csv, NCM811.csv, Separator.csv (every SVGD particle of the three
B-CRNN submodels) and CSV_model_key.docx (their layout). The SHA-256 values are those of the file used in this study.
"""
import argparse, hashlib, io, json, os, urllib.request, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REC = json.load(open(os.path.join(HERE, "bcrnn_mean_model.json")))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dest", default=os.path.join(HERE, "supplementary")); a = ap.parse_args()
    url = REC["supplementary_url"]
    data = urllib.request.urlopen(url, timeout=60).read()
    h = hashlib.sha256(data).hexdigest()
    want = REC["supplementary_sha256"]["mmc1.zip"]
    print("downloaded", len(data), "bytes, sha256", h, "(matches)" if h == want else "(DOES NOT MATCH " + want + ")")
    os.makedirs(a.dest, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for name in z.namelist():
            b = z.read(name)
            hh = hashlib.sha256(b).hexdigest()
            ok = hh == REC["supplementary_sha256"].get(name)
            open(os.path.join(a.dest, name), "wb").write(b)
            print(f"  {name}: {len(b)} bytes, sha256 {'matches' if ok else 'DIFFERS'}")


if __name__ == "__main__":
    main()
