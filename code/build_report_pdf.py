"""
DAS732 A1 - build report/DAS732_A1_Report.pdf from the LaTeX source.

    python build_report_pdf.py

Runs pdflatex three times (once to typeset, twice more to settle the table of
contents, the lists of figures and tables, and every cross-reference), then
inspects the log and fails loudly on anything that would reach a marker:
errors, undefined references, missing figures, and overfull lines wide enough
to be visible on the page.

Use this rather than a bare pdflatex call. A single pass leaves "??" in place of
every cross-reference, and pdflatex exits 0 even when references are undefined.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "report"
TEX = REPORT_DIR / "DAS732_A1_Report.tex"
PDF = REPORT_DIR / "DAS732_A1_Report.pdf"
LOG = REPORT_DIR / "DAS732_A1_Report.log"

PASSES = 3
OVERFULL_LIMIT_PT = 15.0          # anything wider is visible on the page
N_FIGURES = 17
AUX_SUFFIXES = (".aux", ".out", ".toc", ".lof", ".lot", ".fls",
                ".fdb_latexmk", ".synctex.gz")


def find_pdflatex() -> str:
    exe = shutil.which("pdflatex")
    if exe is None:
        sys.exit("pdflatex not found on PATH. Install MiKTeX or TeX Live, or "
                 "upload report/DAS732_A1_Report.tex to Overleaf.")
    return exe


def run_passes(exe: str) -> None:
    for i in range(1, PASSES + 1):
        proc = subprocess.run(
            [exe, "-interaction=nonstopmode", "-halt-on-error", TEX.name],
            cwd=REPORT_DIR, capture_output=True, text=True, timeout=600)
        if proc.returncode != 0:
            print(f"  pdflatex failed on pass {i}:")
            source = (LOG.read_text(errors="replace").splitlines()
                      if LOG.exists() else proc.stdout.splitlines())
            for line in source:
                if line.startswith("! "):
                    print("   ", line)
            sys.exit(1)
        print(f"  pass {i}/{PASSES} ok")


def inspect_log() -> list[str]:
    """Return the problems worth failing the build for."""
    if not LOG.exists():
        return ["no log file produced"]
    log = LOG.read_text(errors="replace")
    problems: list[str] = []

    for line in log.splitlines():
        if line.startswith("! "):
            problems.append(f"LaTeX error: {line}")
        if "Undefined control sequence" in line:
            problems.append(f"undefined control sequence: {line}")

    if "There were undefined references" in log:
        problems.append("undefined references (a \\ref or \\cite points nowhere)")
    for m in re.finditer(r"Citation `([^']+)' on page \d+ undefined", log):
        problems.append(f"undefined citation: {m.group(1)}")
    if "Rerun to get cross-references right" in log:
        problems.append(f"cross-references still unsettled after {PASSES} passes")

    for m in re.finditer(r"Overfull \\hbox \(([0-9.]+)pt too wide\)", log):
        pt = float(m.group(1))
        if pt > OVERFULL_LIMIT_PT:
            problems.append(f"overfull hbox {pt:.1f}pt (text runs into the margin)")

    problems += [f"missing figure file: {f}"
                 for f in re.findall(r"File `([^']+)' not found", log)]
    return problems


def clean_aux() -> None:
    for suf in AUX_SUFFIXES:
        f = REPORT_DIR / (TEX.stem + suf)
        if f.exists():
            f.unlink()


def main() -> int:
    if not TEX.exists():
        sys.exit(f"missing {TEX}")
    missing = [n for n in range(1, N_FIGURES + 1)
               if not (ROOT / "images" / f"Fig{n}.png").exists()]
    if missing:
        sys.exit(f"missing figures {missing}; generate them first "
                 "(python run_all.py)")

    run_passes(find_pdflatex())

    log = LOG.read_text(errors="replace")
    problems = inspect_log()
    if problems:
        print("\n  BUILD PROBLEMS:")
        for p in dict.fromkeys(problems):
            print("   -", p)
        return 1

    pages = re.search(r"Output written on .*? \((\d+) pages", log)
    clean_aux()
    print(f"  wrote {PDF.relative_to(ROOT)}  "
          f"({pages.group(1) if pages else '?'} pages, "
          f"{PDF.stat().st_size / 1024:,.0f} KB)")
    print("  log clean: no errors, no undefined references, "
          "no visible overfull lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
