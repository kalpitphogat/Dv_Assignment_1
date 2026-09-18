# DAS732 A1 — Visual Exploration of the EM-DAT Natural Disasters Database

**A Century of Natural Disasters: More Events, Fewer Deaths, Bigger Bills**

International Institute of Information Technology Bangalore · Data Visualization,
Term 1 (2026–27) · Programming Assignment 1 · 3-member team

| Member | Roll number | Task set |
|---|---|---|
| Lakshya Jain | BT2024044 | Task Set A — *When?* Temporal record (Figs 3–7) + preprocessing |
| Arnav Jain | BT2024233 | Task Set B — *Where?* Geography of exposure (Figs 8–12) |
| Kalpit | BT2024093 | Task Set C — *What?* Impact signature of hazards (Figs 13–17) |

**Tableau workbook:** _[paste your Tableau Public URL here before submitting]_
**Video demo:** _[paste the video link here before submitting]_

---

## Guiding question

> Over 1900–2022, has the burden of natural disasters actually grown, and has the
> world become better or worse at surviving it?

**Short answer.** Exposure rose, vulnerability fell, and the bill kept growing.
Deaths per recorded disaster fell **99.4%** across the century, while real economic
damage rose to a record **$2.07 trillion** in the 2010s and annual deaths show no
significant post-1970 trend at all. The improvement is unevenly shared — two
countries carry half of all recorded deaths — absent for earthquakes, and
*reversing* for extreme heat.

---

## What is in this folder

```
DAS732_A1_Submission/
├── README.md                     <- you are here
├── Tableau_Guide.md              <- step-by-step rebuild of 6 views in Tableau
├── Video_Script.md               <- timed 5-minute demo script + checklist
│
├── report/
│   ├── DAS732_A1_Report.pdf      <- THE REPORT (submit this) — 32 pages
│   └── DAS732_A1_Report.tex      <- LaTeX source; the PDF is built from it
│
├── images/                       <- Fig1.png .. Fig26.png, all featured in the report
│
├── data/
│   ├── emdat_country_profiles_raw.csv   <- raw Kaggle download, unmodified
│   └── emdat_clean_tableau.csv          <- cleaned extract; open this in Tableau
│
└── code/
    ├── emdat_common.py           <- shared loading, cleaning, palette, plot helpers
    ├── facts.py, facts2.py       <- derive every number the report quotes
    ├── facts_output.txt, facts2_output.txt   <- their saved output
    ├── task_0_diagrams.py        <- Fig1–Fig2   (method diagrams)
    ├── task_a_temporal.py        <- Fig3–Fig7, Fig18–20 (Task Set A)
    ├── task_b_geography.py       <- Fig8–Fig12, Fig21–23 (Task Set B)
    ├── task_c_impact.py          <- Fig13–Fig17, Fig24–26 (Task Set C)
    ├── build_report_pdf.py       <- runs pdflatex 3x and fails on any log problem
    ├── check_report.py           <- asserts all 172 numbers in the .tex against the data
    └── run_all.py                <- regenerates everything above from the raw CSV
```

**Every image in `images/` appears in the report**, numbered `Fig<n>.png` where
`n` is exactly that figure's number in the report. There are no extra images, so
no supplementary image README is required.

## Figure index

| File | Task | Figure title |
|---|---|---|
| `Fig1.png` | — | Task decomposition: one question, three task sets *(diagram)* |
| `Fig2.png` | — | Data pipeline from raw CSV to figures *(diagram)* |
| `Fig3.png` | A1.1 | Two hazards account for seven of every ten recorded disasters |
| `Fig4.png` | A1.2 | The record explodes after 1970 — mostly floods and storms |
| `Fig5.png` | A1.3 | The count of disasters is partly a count of reporting |
| `Fig6.png` | A1.4 | Disasters became far more survivable even as they became far more numerous |
| `Fig7.png` | A1.5 | The fall in deaths is the disappearance of mega-catastrophes, not a broad decline |
| `Fig8.png` | B1.1 | Almost every country on Earth appears in the disaster record |
| `Fig9.png` | B1.2 | But death is concentrated in a handful of countries |
| `Fig10.png` | B1.3 | Most disasters, most deaths, most people affected and most money lost are four different maps |
| `Fig11.png` | B1.4 | Half of all deaths fall on 2 countries; half of all disasters are spread over 20 |
| `Fig12.png` | B1.5 | Among equally disaster-prone countries, lethality differs by a factor of 1,000 |
| `Fig13.png` | C1.1 | A hazard's share of disasters says almost nothing about its share of harm |
| `Fig14.png` | C1.2 | Drought kills on a different scale from every other hazard |
| `Fig15.png` | C1.3 | The money cost of disasters keeps climbing, in real terms |
| `Fig16.png` | C1.4 | Famine and flood became survivable; heatwaves went the other way |
| `Fig17.png` | C1.5 | Costs rose, deaths did not follow |
| `Fig18.png` | A1.6 | Riverine flooding, not flash or coastal flooding, drives the flood trend |
| `Fig19.png` | A1.7 | Every hazard's record thickens after 1970, but not at the same rate |
| `Fig20.png` | A1.8 | Earthquakes set the reporting baseline; floods and heatwaves exceed it by far |
| `Fig21.png` | B1.6 | High event volume and broad hazard diversity are different things |
| `Fig22.png` | B1.7 | The map of exposure has moved: Vietnam climbed 40 places, Japan fell 5 |
| `Fig23.png` | B1.8 | Two kinds of hotspot: early-and-steady versus late-and-sudden |
| `Fig24.png` | C1.6 | Why every damage figure in this report is inflation-adjusted |
| `Fig25.png` | C1.7 | Wealth turns deaths into bills: lethality and cost per event are unrelated |
| `Fig26.png` | C1.8 | Drought stopped killing but never stopped displacing |

## Dataset

- **Source:** EM-DAT, Centre for Research on the Epidemiology of Disasters (CRED),
  UCLouvain — country-profiles export.
- **Mirror used:** https://www.kaggle.com/datasets/mexwell/natural-disasters-emergency-events-database
- **File:** `_EmergencyEventsDatabase-CountryProfiles_emdat-country-profiles_2023_04_06.csv`
  (snapshot of 6 April 2023), included unmodified as
  `data/emdat_country_profiles_raw.csv`.
- **Shape:** 10,431 rows → 10,380 after preprocessing; 15,015 recorded events;
  225 countries; 13 hazard types; 1900–2022.
- **Gotchas:** semicolon-delimited, comma decimal mark, trailing whitespace on some
  `Disaster Type` values, and a partial 2023. All handled in `emdat_common.py`;
  see Section 2.3 of the report.

## Building the report

The report is LaTeX. Requires a TeX distribution (MiKTeX or TeX Live) plus
Python 3.12 with `pandas`, `numpy`, `scipy`, `matplotlib`, `plotly`, `kaleido`.

```
pip install pandas numpy scipy matplotlib plotly kaleido
cd code
python run_all.py
```

`run_all.py` rewrites the cleaned extract, re-derives every quoted number into
`facts_output.txt` / `facts2_output.txt`, regenerates all 26 figures, runs
`pdflatex` three times, and then asserts every number in the report against the
data. It exits non-zero if anything fails.

To rebuild only the PDF after editing the `.tex`:

```
python code/build_report_pdf.py
```

**No LaTeX installed?** Upload `report/DAS732_A1_Report.tex` and the `images/`
folder to Overleaf and compile there — the document uses only standard packages
(`graphicx`, `booktabs`, `tabularx`, `caption`, `hyperref`, `titlesec`,
`fancyhdr`, `float`, `enumitem`, `microtype`).

## How correctness is enforced

- **`check_report.py`** re-derives **172 quantitative claims** straight from the
  raw CSV and asserts each one appears in `DAS732_A1_Report.tex`. Figures the
  report deliberately rounds (e.g. "≈19,900") are checked by verifying the
  rounding, not by demanding the exact value. It exits non-zero on any mismatch,
  so a stale number cannot survive a rebuild.
- **`build_report_pdf.py`** runs three `pdflatex` passes and then fails the build
  on LaTeX errors, undefined references or citations, missing figure files, or
  any overfull line wide enough to be visible in the margin.
- Nothing in the report is quoted from memory: every number traces to a line in
  `facts_output.txt` or `facts2_output.txt`.

## Method notes

- **Rates over counts.** Because the event count partly measures reporting effort
  (Fig 5), the analysis prefers deaths per event, shares of totals, and damage per
  event wherever a raw count would mislead.
- **Constant prices.** All money is in 2022 US dollars
  (`Total Damage (USD, adjusted)`), verified as `nominal × 100 / CPI`.
- **No dual axes.** Measures on different scales are shown as separate panels
  (Fig 6) or indexed to a common base (Fig 17).
- **Colour.** One fixed categorical slot order across all figures; single-hue
  sequential blue for magnitude; the categorical palette was checked for
  colour-vision separation before use, and every value on a light fill carries a
  visible text label.

## Before you submit — checklist

- [x] Team names and roll numbers filled in (they live in six `\newcommand`
      lines at the top of `report/DAS732_A1_Report.tex` and propagate everywhere)
- [ ] Attach each member's **signed AI declaration** on the form circulated by the
      instructor. These are deliberately **not** in the report — the brief asks
      for one per member, so all three must be submitted alongside it
- [ ] Rebuild if you edit anything: `python code/build_report_pdf.py`
- [ ] Publish the Tableau workbook and paste its URL above
- [ ] Record and upload the video (≤ 5:00), paste the link above
- [ ] Share the folder with the TAs and instructor, and **do not edit any file
      afterwards** — the brief records the latest file timestamp as the
      submission time

## References

1. Schulz, H. J., Nocke, T., Heitzler, M., & Schumann, H. (2013). A design space of
   visualization tasks. *IEEE TVCG*, 19(12), 2366–2375.
2. CRED / UCLouvain. *EM-DAT: The International Disaster Database.* https://www.emdat.be
