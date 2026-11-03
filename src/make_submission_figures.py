#!/usr/bin/env python3
"""The figure files for the Journal of The Electrochemical Society (Brief 21, M4), from the manuscript's figures.

Each main figure, manuscript/figures/figN.pdf (drawn by make_manuscript_figures.py from the results files), is written to
manuscript/submission/figures/ as figureN.pdf (vector, scaled to the full two-column width, 17.1 cm) and figureN.tif
(300 dpi at that width, LZW-compressed, one composite file per figure, as the journal asks). Every figure has panels side
by side or a table, so none is set to the one-column width (8.2 cm). The scale from the manuscript's 13.76 cm is 1.243,
so the smallest lettering, 7 pt, becomes 8.7 pt, about 2.2 mm in capital height, above the journal's 1.6 mm. A report of
the sizes is written beside them (sizes.json).

Usage: python3 make_submission_figures.py
"""
import json, os, subprocess, tempfile
from PIL import Image
from pypdf import PdfReader, PdfWriter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "manuscript", "figures")
OUT = os.path.join(HERE, "..", "manuscript", "submission", "figures")
FULL_CM = 17.1
DPI = 300
SMALLEST_PT = 7.0                       # the smallest lettering in make_manuscript_figures.py (FS_SMALL)
CAP_HEIGHT = 0.73                       # DejaVu Sans' capital height, as a fraction of the font size


def main():
    os.makedirs(OUT, exist_ok=True)
    report = {}
    for n in range(1, 9):
        src = os.path.join(SRC, f"fig{n}.pdf")
        page = PdfReader(src).pages[0]
        w_pt, h_pt = float(page.mediabox.width), float(page.mediabox.height)
        scale = (FULL_CM / 2.54 * 72.0) / w_pt
        wr = PdfWriter()
        page.scale_by(scale)
        wr.add_page(page)
        pdf_out = os.path.join(OUT, f"figure{n}.pdf")
        with open(pdf_out, "wb") as fh:
            wr.write(fh)
        w_px = round(FULL_CM / 2.54 * DPI)
        with tempfile.TemporaryDirectory() as td:
            base = os.path.join(td, "p")
            subprocess.run(["pdftoppm", "-png", "-r", str(DPI), "-singlefile", pdf_out, base], check=True)
            im = Image.open(base + ".png").convert("RGB")
        if abs(im.size[0] - w_px) > 2:
            im = im.resize((w_px, round(im.size[1] * w_px / im.size[0])), Image.LANCZOS)
        tif_out = os.path.join(OUT, f"figure{n}.tif")
        im.save(tif_out, dpi=(DPI, DPI), compression="tiff_lzw")
        cap_mm = SMALLEST_PT * scale * CAP_HEIGHT * 25.4 / 72.0
        report[f"figure{n}"] = {"width_cm": FULL_CM, "height_cm": round(h_pt * scale / 72.0 * 2.54, 2),
                                "tif_px": list(im.size), "dpi": DPI, "scale_from_manuscript": round(scale, 4),
                                "smallest_lettering_pt": round(SMALLEST_PT * scale, 2),
                                "smallest_capital_height_mm": round(cap_mm, 2)}
        print(f"figure{n}: {report[f'figure{n}']}")
    json.dump(report, open(os.path.join(OUT, "sizes.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
