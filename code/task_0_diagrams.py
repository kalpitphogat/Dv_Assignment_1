"""
DAS732 A1 - Method diagrams.

These are drawn rather than plotted. Fig2.png is the data pipeline from the
raw Kaggle CSV to the fifteen charts; Fig1.png is the decomposition of the
guiding question into three task sets. They are numbered in the order they
appear in the report, which is why the task map is Fig1 and the pipeline Fig2. They use the same palette and typography as the
data figures so the report reads as one document.
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

from emdat_common import (use_report_style, save, CAT, SURFACE, INK, INK_SEC,
                          INK_MUTED, GRID, titleblock, footnote)

use_report_style()

PANEL = "#f4f3ef"


def box(ax, x, y, w, h, title, body=None, edge=CAT[0], fill="#ffffff",
        title_size=10.5, body_size=8.8, lw=1.6, title_color=None,
        body_gap=0.125):
    """Rounded box with a bold title and an optional lighter body block.

    `body_gap` is the drop from the top of the box to the body's first
    baseline; short banner boxes need a smaller gap or the body escapes the
    box entirely.
    """
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.010,rounding_size=0.020",
        linewidth=lw, edgecolor=edge, facecolor=fill, zorder=3))
    if body:
        ax.text(x + w / 2, y + h - 0.050, title, ha="center", va="top",
                fontsize=title_size, fontweight="bold",
                color=title_color or INK, zorder=4)
        ax.text(x + w / 2, y + h - body_gap, body, ha="center", va="top",
                fontsize=body_size, color=INK_SEC, linespacing=1.55, zorder=4)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center",
                fontsize=title_size, fontweight="bold",
                color=title_color or INK, zorder=4)


def arrow(ax, x1, y1, x2, y2, color=None, lw=1.6, rad=0.0, zorder=2):
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=13,
        linewidth=lw, color=color or INK_MUTED, zorder=zorder,
        connectionstyle=f"arc3,rad={rad}", shrinkA=2, shrinkB=2))


def blank_axes(figsize):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_facecolor(SURFACE)
    return fig, ax


# ---------------------------------------------------------------- Fig 1 -----
# The processing pipeline: what happens to the file before any chart exists.
fig, ax = blank_axes((11.0, 5.5))

box(ax, 0.015, 0.44, 0.215, 0.40, "Raw Kaggle CSV",
    "EM-DAT country profiles\nsnapshot 2023-04-06\n"
    "10,431 rows | 13 columns\nsemicolon-delimited,\ncomma decimal mark",
    edge=INK_MUTED)

box(ax, 0.265, 0.34, 0.245, 0.62, "emdat_common.py",
    "1  sep=';', decimal=','\n"
    "2  drop 51 partial-2023 rows\n"
    "3  strip trailing whitespace\n"
    "4  fill missing subtype\n"
    "5  keep impacts NaN, not 0\n"
    "6  derive decade / era\n"
    "7  flag 7 historical states\n"
    "8  verify damage = nominal\n     x 100 / CPI",
    edge=CAT[0], fill=PANEL, body_size=8.6)

box(ax, 0.560, 0.62, 0.20, 0.26, "Analysis frame",
    "10,380 rows\n18 tidy columns\n15,015 events", edge=CAT[0])
box(ax, 0.560, 0.315, 0.20, 0.215, "Tableau extract",
    "emdat_clean_tableau.csv", edge=CAT[2], body_size=8.2)

box(ax, 0.810, 0.725, 0.175, 0.155, "task_a_temporal.py",
    "Figures 3-7", edge=CAT[0], title_size=9.2, body_size=8.4, body_gap=0.098)
box(ax, 0.810, 0.545, 0.175, 0.155, "task_b_geography.py",
    "Figures 8-12", edge=CAT[1], title_size=9.2, body_size=8.4, body_gap=0.098)
box(ax, 0.810, 0.365, 0.175, 0.155, "task_c_impact.py",
    "Figures 13-17", edge=CAT[3], title_size=9.2, body_size=8.4, body_gap=0.098)
box(ax, 0.810, 0.135, 0.175, 0.175, "facts.py / facts2.py",
    "re-derives every\nnumber in this report",
    edge=INK_MUTED, title_size=9.2, body_size=8.4, body_gap=0.098)

arrow(ax, 0.232, 0.64, 0.262, 0.64)
arrow(ax, 0.513, 0.75, 0.557, 0.75)
arrow(ax, 0.513, 0.42, 0.557, 0.42)
for y in (0.802, 0.622, 0.442):
    arrow(ax, 0.763, 0.75, 0.807, y, rad=-0.12)
arrow(ax, 0.660, 0.617, 0.660, 0.534, color=GRID, lw=1.4)
arrow(ax, 0.763, 0.655, 0.807, 0.222, rad=-0.32)

ax.text(0.668, 0.578, "same rules", ha="left", fontsize=7.8,
        color=INK_MUTED, style="italic")

titleblock(fig, "One cleaning module feeds every chart in this report",
           "The three task sets never clean the data themselves, so all fifteen "
           "charts are guaranteed to describe an identical frame. The "
           "verification harness reads that same frame and re-derives every "
           "number quoted in this report.")
fig.subplots_adjust(top=0.80, left=0.01, right=0.99, bottom=0.02)
footnote(fig, "Boxes are files in code/. The row counts shown are printed by "
              "the module itself on every run.", y=0.005)
save(fig, "Fig2.png", "data pipeline diagram")


# ---------------------------------------------------------------- Fig 2 -----
# The decomposition of one question into three independently owned task sets.
fig, ax = blank_axes((11.0, 6.2))

box(ax, 0.145, 0.845, 0.71, 0.135,
    "Over 1900-2022, has the burden of natural disasters actually grown,",
    "and has the world become better or worse at surviving it?",
    edge=INK, fill=PANEL, title_size=11.5, body_size=11.0, body_gap=0.088)

COL_Y, COL_H, COL_W = 0.300, 0.440, 0.290
cols = [
    (0.020, CAT[0], "A.  WHEN?", "Member 1  |  Figures 3-7",
     "The temporal record",
     "A1.1  Overview   composition of the record\n"
     "A1.2  Trend   events through time\n"
     "A1.3  Identify   is the rise real?\n"
     "A1.4  Compare   deaths vs deaths per event\n"
     "A1.5  Validate   is the decline broad?"),
    (0.355, CAT[1], "B.  WHERE?", "Member 2  |  Figures 8-12",
     "The geography of exposure",
     "B1.1  Locate   where disasters occur\n"
     "B1.2  Locate   where people die\n"
     "B1.3  Rank   four leaderboards\n"
     "B1.4  Derive   how concentrated is each?\n"
     "B1.5  Derive   lethality at equal exposure"),
    (0.690, CAT[3], "C.  WHAT?", "Member 3  |  Figures 13-17",
     "The impact signature of hazards",
     "C1.1  Compare   share of four burdens\n"
     "C1.2  Relate   deadly versus costly\n"
     "C1.3  Trend   real damage over time\n"
     "C1.4  Compare   lethality by hazard\n"
     "C1.5  Correlate   the decoupling"),
]

for x, col, head, owner, sub, tasks in cols:
    top = COL_Y + COL_H
    ax.add_patch(FancyBboxPatch(
        (x, COL_Y), COL_W, COL_H,
        boxstyle="round,pad=0.010,rounding_size=0.020",
        linewidth=1.8, edgecolor=col, facecolor="#ffffff", zorder=3))
    ax.add_patch(FancyBboxPatch(
        (x, top - 0.098), COL_W, 0.098,
        boxstyle="round,pad=0.010,rounding_size=0.020",
        linewidth=0, facecolor=col, zorder=4))
    ax.text(x + COL_W / 2, top - 0.033, head, ha="center", va="center",
            fontsize=11.5, fontweight="bold", color="#ffffff", zorder=5)
    ax.text(x + COL_W / 2, top - 0.072, owner, ha="center", va="center",
            fontsize=8.6, color="#ffffff", zorder=5)
    ax.text(x + COL_W / 2, top - 0.135, sub, ha="center", va="center",
            fontsize=10, fontweight="bold", color=INK, zorder=5)
    ax.text(x + 0.020, top - 0.180, tasks, ha="left", va="top", fontsize=8.7,
            color=INK_SEC, linespacing=2.0, zorder=5)
    # zorder above the boxes so the arrowheads are not clipped by them
    arrow(ax, 0.50, 0.843, x + COL_W / 2, top + 0.014, color=col, zorder=6)
    arrow(ax, x + COL_W / 2, COL_Y - 0.004, 0.50, 0.170, color=col, zorder=6)

box(ax, 0.145, 0.035, 0.71, 0.125, "One data story (Section 7)",
    "Exposure up  ->  vulnerability down  ->  the bill still rising",
    edge=INK, fill=PANEL, title_size=11, body_size=10, body_gap=0.080)

titleblock(fig, "One question, three independently owned task sets, fifteen charts",
           "Each member owns a sub-question end to end - its tasks, its figures, "
           "its inferences and its section of the report and of the video - so no "
           "task is split across the team. Task verbs follow the design space of "
           "Schulz et al.")
fig.subplots_adjust(top=0.83, left=0.01, right=0.99, bottom=0.01)
footnote(fig, y=-0.005)
save(fig, "Fig1.png", "task decomposition diagram")

print("Diagrams complete.")
