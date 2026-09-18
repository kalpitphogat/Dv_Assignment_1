# Rebuilding the key views in Tableau

For the video demo. Every view below is built from one file —
`data/emdat_clean_tableau.csv` (10,380 rows, 18 columns) — which is already
cleaned, so **no data preparation is needed inside Tableau**.

## 0. Connect

1. Tableau Public → **Connect → Text file** → select `data/emdat_clean_tableau.csv`.
2. Check the data pane. Tableau should infer:
   - **Dimensions:** `country`, `iso`, `group`, `subgroup`, `type`, `subtype`, `era`,
     `has deaths`, `has damage`, `is historical state`
   - **Measures:** `year`, `decade`, `events`, `deaths`, `affected`,
     `damage nominal`, `damage real`, `cpi`
3. Fix two things Tableau usually gets wrong:
   - Drag **`year`** and **`decade`** from Measures to **Dimensions**.
   - Set **`iso`** → right-click → *Geographic Role* → **Country/Region**.
4. Create these calculated fields (used repeatedly below):

   | Name | Formula |
   |---|---|
   | `Deaths per event` | `SUM([Deaths]) / SUM([Events])` |
   | `Damage per event ($M)` | `SUM([Damage Real]) / SUM([Events]) / 1000000` |
   | `Damage ($B, 2022)` | `SUM([Damage Real]) / 1000000000` |

> `damage real` is already inflation-adjusted to constant 2022 US dollars. Use it
> for anything involving money across years. `damage nominal` is there only for
> comparison and should not be trended.

---

## View 1 — "The record explodes after 1970" (Figure 4)

*Task A1.2 — trend.*

1. **Columns:** `year` (continuous, exact date → keep as continuous dimension).
2. **Rows:** `SUM(Events)`.
3. **Marks:** Area.
4. **Colour:** `subgroup`.
5. Sort the colour legend manually to Hydrological → Meteorological → Geophysical
   → Climatological → Biological so it matches the report.
6. Add a **reference line** at `year = 1970`, labelled "modern reporting era".

**Talking point:** the curve looks like a hazard explosion, but 91% of the record
sits after 1970.

---

## View 2 — "Deaths per event collapsed" (Figure 6)

*Task A1.4 — compare/derive.* Two sheets, then a dashboard — **not** a dual axis.

1. Sheet `Deaths by decade`: Columns `decade`, Rows `SUM(Deaths)`, Marks Bar.
2. Sheet `Lethality`: Columns `decade`, Rows `Deaths per event`, Marks Line.
   Right-click the axis → **Logarithmic**.
3. New dashboard, stack the two sheets vertically so they share the decade axis.

**Talking point:** total deaths fell *and* events rose — it is the ratio that
carries the finding. Two panels, never a twin axis.

---

## View 3 — Events map vs deaths map (Figures 8 and 9)

*Tasks B1.1, B1.2 — locate.*

1. Double-click **`iso`** → Tableau draws the map.
2. **Marks → Colour:** `SUM(Events)`. Edit Colours → **Blue** sequential →
   tick **Use Logarithmic scale** (essential — without it only the US and China
   are visible).
3. Duplicate the sheet, swap Colour to `SUM(Deaths)`, keep the log scale.
4. Put both on one dashboard, side by side.

**Talking point:** the two maps have completely different shapes. Disasters happen
everywhere; deaths do not.

---

## View 4 — Four leaderboards (Figure 10)

*Task B1.3 — rank/compare.*

1. Sheet 1: **Rows** `country`, **Columns** `SUM(Events)`, Marks Bar, sort
   descending, **Filter → Top 12 by SUM(Events)**.
2. Repeat for `SUM(Deaths)`, `SUM(Affected)`, `Damage ($B, 2022)` — each in its
   own sheet with its own Top-12 filter *on that measure*.
3. Combine all four into a 2 × 2 dashboard.

**Talking point:** the United States is 1st for events and damage, 23rd for
deaths. Wealth converts exposure into property loss instead of death.

---

## View 5 — The impact signature (Figure 13) — *the money shot for the demo*

*Task C1.1 — compare.*

1. **Columns:** `Measure Names`; **Rows:** nothing yet.
2. Drag `SUM(Events)`, `SUM(Deaths)`, `SUM(Affected)`, `SUM(Damage Real)` into
   **Measure Values**.
3. **Marks:** Bar; **Colour:** `type`.
4. Right-click `SUM(Events)` on Measure Values → **Quick Table Calculation →
   Percent of Total**, and set **Compute Using → type**. Repeat for the other
   three measures.
5. Swap rows/columns so the four bars are horizontal.
6. Group the rarer hazard types into "Other" (select them in the legend →
   right-click → **Group**) so the colour count stays at seven.

**Talking point:** drought is 5% of events and 51% of deaths. A hazard's share of
disasters tells you almost nothing about its share of harm.

---

## View 6 (optional) — Lethality heatmap (Figure 16)

*Task C1.4 — compare/trend.*

1. **Columns:** `decade`; **Rows:** `type`.
2. **Marks:** Square; **Colour:** `Deaths per event` (blue sequential, log scale);
   **Label:** `Deaths per event`.
3. Filter `type` to the six main hazards and `decade` to ≥ 1950.

**Talking point:** drought and flood became survivable; earthquakes did not
improve; extreme temperature got *worse*.

---

## Publishing for assessment

Tableau Public workbooks are public by default, which satisfies the brief's
"appropriate access shall be managed for assessment". After publishing:

1. Copy the workbook URL.
2. Paste it into `README.md` under **Tableau workbook**.
3. Do not edit the workbook after the submission deadline — the brief records the
   latest timestamp on any submitted file as the submission time.
