"""
DAS732 A1 - regenerate the whole submission from the raw CSV.

    python run_all.py

Runs, in order: preprocessing (writes the Tableau extract), the fact-verification
harness (writes facts_output.txt / facts2_output.txt), the method diagrams and the
three task-set figure scripts (Fig1-Fig17), and the LaTeX report build, and the report correctness check.
"""
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

STEPS = [
    ("Preprocess + write Tableau extract", "emdat_common.py"),
    ("Verify facts (part 1)", "facts.py"),
    ("Verify facts (part 2)", "facts2.py"),
    ("Method diagrams (Fig1-2)", "task_0_diagrams.py"),
    ("Task Set A - temporal (Fig3-7)", "task_a_temporal.py"),
    ("Task Set B - geography (Fig8-12)", "task_b_geography.py"),
    ("Task Set C - impact (Fig13-17)", "task_c_impact.py"),
    ("Build report PDF from LaTeX", "build_report_pdf.py"),
    ("Check every number in the report against the data", "check_report.py"),
]

CAPTURE = {"facts.py": "facts_output.txt", "facts2.py": "facts2_output.txt"}


def main():
    t0 = time.time()
    for i, (label, script) in enumerate(STEPS, 1):
        print(f"\n[{i}/{len(STEPS)}] {label}")
        r = subprocess.run([sys.executable, script], cwd=HERE,
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stdout)
            print(r.stderr, file=sys.stderr)
            sys.exit(f"FAILED at {script}")
        if script in CAPTURE:
            (HERE / CAPTURE[script]).write_text(r.stdout, encoding="utf-8")
            print(f"  wrote {CAPTURE[script]}  "
                  f"({len(r.stdout.splitlines())} lines of verified figures)")
        else:
            print(r.stdout.rstrip() or "  done")

    figs = sorted((ROOT / "images").glob("Fig*.png"))
    print(f"\nDone in {time.time() - t0:.1f}s.  {len(figs)} figures in images/, "
          f"report at report/DAS732_A1_Report.pdf")
    missing = [f"Fig{n}.png" for n in range(1, 18)
               if not (ROOT / "images" / f"Fig{n}.png").exists()]
    if missing:
        sys.exit(f"MISSING FIGURES: {missing}")


if __name__ == "__main__":
    main()
