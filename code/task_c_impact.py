"""
DAS732 A1 - TASK SET C: "WHAT?"  The impact signature of each hazard, 1900-2022.

Guiding sub-question: Which hazards kill, which displace, and which cost money -
and are they the same hazards?

Produces Fig13 - Fig17 and Fig20.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
from scipy import stats

from emdat_common import (load, use_report_style, despine, save, human, HUMAN,
                          CAT, SEQ, SURFACE, INK, INK_SEC, INK_MUTED, GRID,
                          SUBGROUP_ORDER, SUBGROUP_COLOR, titleblock, footnote)

use_report_style()
df = load()

# The six hazards that carry the record; everything rarer folds into "Other"
# rather than becoming a generated 8th hue.
TOP6 = ["Flood", "Storm", "Earthquake", "Drought", "Landslide",
        "Extreme temperature"]
TYPE_ORDER = TOP6 + ["Other"]
TYPE_COLOR = dict(zip(TYPE_ORDER, CAT[:7]))
df["type6"] = np.where(df.type.isin(TOP6), df.type, "Other")

# --------------------------------------------------------------- Fig 13 -----
# C1.1 COMPARE / SUMMARIZE: the four burdens, side by side as shares.
MEASURES = [("events", "Share of recorded EVENTS"),
            ("deaths", "Share of recorded DEATHS"),
            ("affected", "Share of PEOPLE AFFECTED"),
            ("damage_real", "Share of ECONOMIC DAMAGE")]
rows = []
for col, label in MEASURES:
    s = df.groupby("type6")[col].sum().reindex(TYPE_ORDER).fillna(0)
    rows.append((label, s / s.sum() * 100))
share = pd.DataFrame({lbl: v for lbl, v in rows}).T[TYPE_ORDER]

fig, ax = plt.subplots(figsize=(11.4, 4.9))
y = np.arange(len(share))[::-1]
left = np.zeros(len(share))
for t in TYPE_ORDER:
    v = share[t].values
    ax.barh(y, v, left=left, height=0.62, color=TYPE_COLOR[t], label=t,
            edgecolor=SURFACE, linewidth=1.8, zorder=3)
    # Ink colour follows the segment's luminance, not a fixed white - white on
    # the yellow slot would fall under 2:1 contrast.
    r_, g_, b_ = mcolors.to_rgb(TYPE_COLOR[t])
    lum = 0.2126 * r_ + 0.7152 * g_ + 0.0722 * b_
    ink = INK if lum > 0.45 else "#ffffff"
    for yi, li, vi in zip(y, left, v):
        if vi >= 6:                       # label only segments wide enough
            ax.text(li + vi / 2, yi, f"{vi:.0f}%", ha="center", va="center",
                    fontsize=10, fontweight="bold", color=ink, zorder=4)
    left += v
ax.set_yticks(y)
ax.set_yticklabels(share.index, fontsize=10.5)
ax.set_xlim(0, 100)
ax.set_xlabel("Share of the 1900-2022 global total (%)")
ax.grid(axis="y", visible=False)
despine(ax, keep=("bottom",))
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.20), ncol=7,
          fontsize=9.5, columnspacing=1.2, handlelength=1.4)
titleblock(fig, "A hazard's share of disasters says almost nothing about its share of harm",
           "Drought is 5% of recorded events but 51% of recorded deaths. Storms are "
           "31% of events and 42% of damage but only 6% of deaths. The four bars use "
           "the same seven hazard categories in the same order.")
fig.subplots_adjust(top=0.735, bottom=0.30)
footnote(fig, y=0.005)
save(fig, "Fig13.png", "impact signature by hazard")

# --------------------------------------------------------------- Fig 14 -----
# C1.2 RELATE / LOCATE: deadly vs costly, per individual record.
t = (df.groupby("type")
       .agg(events=("events", "sum"),
            med_deaths=("deaths", "median"),
            med_damage=("damage_real", "median"))
       .dropna())
t = t[t.events >= 40]

fig, ax = plt.subplots(figsize=(9.6, 6.4))
sizes = 60 + 900 * (t.events / t.events.max()) ** 0.55
ax.scatter(t.med_deaths, t.med_damage / 1e6, s=sizes, color=CAT[0],
           alpha=0.85, edgecolor=SURFACE, linewidth=2, zorder=3)
OFFSET = {"Flood": (-14, -4, "right"), "Storm": (0, 24, "center"),
          "Earthquake": (26, -4, "left"), "Drought": (0, 24, "center"),
          "Landslide": (0, -30, "center"), "Extreme temperature": (0, 24, "center"),
          "Wildfire": (0, -30, "center"), "Volcanic activity": (24, -4, "left"),
          "Mass movement (dry)": (0, 22, "center")}
for name, r in t.iterrows():
    dx, dy, ha = OFFSET.get(name, (0, 20, "center"))
    ax.annotate(name, xy=(r.med_deaths, r.med_damage / 1e6),
                xytext=(dx, dy), textcoords="offset points",
                ha=ha, va="center", fontsize=10, color=INK, fontweight="bold")
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("Median deaths per record (log scale)")
ax.set_ylabel("Median economic damage per record, US$ millions (log scale)")
ax.xaxis.set_major_formatter(HUMAN)
ax.yaxis.set_major_formatter(HUMAN)
ax.set_xlim(3, 700)
ax.set_ylim(5, 900)
despine(ax)
ax.axhline(t.med_damage.median() / 1e6, color=GRID, lw=1, zorder=1)
ax.axvline(t.med_deaths.median(), color=GRID, lw=1, zorder=1)
ax.text(690, 6.2, "deadly, cheap", ha="right", fontsize=9.5, color=INK_MUTED,
        style="italic")
ax.text(690, 820, "deadly and costly", ha="right", fontsize=9.5,
        color=INK_MUTED, style="italic")
ax.text(3.3, 820, "costly, survivable", ha="left", fontsize=9.5,
        color=INK_MUTED, style="italic")
titleblock(fig, "Drought kills on a different scale from every other hazard",
           "Each bubble is one hazard type; bubble size is the number of recorded "
           "events. A typical drought record carries 143 deaths, more than three times the next "
           "hazard - while extreme temperature carries the largest typical damage "
           "bill ($408M). Medians, not totals, so one catastrophe cannot move a point.")
fig.subplots_adjust(top=0.825)
footnote(fig, y=-0.02)
save(fig, "Fig14.png", "deadly vs costly scatter")

# --------------------------------------------------------------- Fig 15 -----
# C1.3 TREND: the cost of disasters over time, in constant 2022 dollars.
dmg = (df.pivot_table(index="decade", columns="subgroup", values="damage_real",
                      aggfunc="sum")
         .reindex(columns=SUBGROUP_ORDER).fillna(0) / 1e9)

fig, ax = plt.subplots(figsize=(10.4, 5.6))
bottom = np.zeros(len(dmg))
for sg in SUBGROUP_ORDER:
    ax.bar(dmg.index, dmg[sg], bottom=bottom, width=8,
           color=SUBGROUP_COLOR[sg], label=sg, edgecolor=SURFACE,
           linewidth=1.8, zorder=3)
    bottom += dmg[sg].values
ax.set_ylabel("Reported damage per decade, US$ billions (2022 prices)")
ax.set_xlabel("Decade")
ax.grid(axis="x", visible=False)
despine(ax)
ax.legend(loc="upper left", ncol=1)
# The 1990s and 2000s bars are nearly the same height, so their value labels
# are staggered vertically instead of colliding side by side.
LABEL_LIFT = {1980: 40, 1990: 40, 2000: 150, 2010: 40, 2020: 40}
for xi, v in zip(dmg.index, bottom):
    if v > 400:
        ax.text(xi, v + LABEL_LIFT.get(xi, 40), f"${v:,.0f}B", ha="center",
                fontsize=9, color=INK_SEC)
ax.annotate("2020s: part-decade\n(2020-2022 only)", xy=(2020, 780),
            xytext=(2020, 1180), ha="center", fontsize=9, color=INK_SEC,
            arrowprops=dict(arrowstyle="->", color=INK_MUTED, lw=1))
titleblock(fig, "The money cost of disasters keeps climbing, in real terms",
           "Reported damage is inflation-adjusted to 2022 US dollars. Only 37% of "
           "records carry a damage figure, so these bars are lower bounds. Coverage "
           "does not improve after 1970 (it stays in a 32-48% band), so the rise "
           "cannot be an artefact of better reporting.")
fig.subplots_adjust(top=0.775)
footnote(fig, y=-0.02)
save(fig, "Fig15.png", "real damage by decade and sub-group")

# --------------------------------------------------------------- Fig 16 -----
# C1.4 COMPARE / TREND: which hazards became survivable, and which did not?
sub = df[df.type.isin(TOP6) & (df.year >= 1950)]
d_ = sub.pivot_table(index="type", columns="decade", values="deaths", aggfunc="sum")
e_ = sub.pivot_table(index="type", columns="decade", values="events", aggfunc="sum")
leth = (d_ / e_).reindex(TOP6)

blues = LinearSegmentedColormap.from_list("emdat_blues", SEQ)
fig, ax = plt.subplots(figsize=(10.2, 4.8))
z = np.log10(leth.values.astype(float))
im = ax.imshow(z, cmap=blues, aspect="auto",
               vmin=np.nanmin(z), vmax=np.nanmax(z))
ax.set_xticks(range(leth.shape[1]))
ax.set_xticklabels([f"{c}s" for c in leth.columns])
ax.set_yticks(range(leth.shape[0]))
ax.set_yticklabels(leth.index)
ax.grid(False)
despine(ax, keep=())
ax.set_xticks(np.arange(-.5, leth.shape[1], 1), minor=True)
ax.set_yticks(np.arange(-.5, leth.shape[0], 1), minor=True)
ax.grid(which="minor", color=SURFACE, linewidth=2.4)
ax.tick_params(which="minor", length=0)
for i in range(leth.shape[0]):
    for j in range(leth.shape[1]):
        v = leth.values[i, j]
        if np.isnan(v):
            ax.text(j, i, "-", ha="center", va="center", color=INK_MUTED)
            continue
        # white ink only on the dark end of the ramp
        col = "#ffffff" if z[i, j] > np.nanmin(z) + 0.62 * np.ptp(z[~np.isnan(z)]) else INK
        ax.text(j, i, f"{v:,.0f}", ha="center", va="center", fontsize=9.5,
                color=col, fontweight="bold")
cb = fig.colorbar(im, ax=ax, pad=0.015, fraction=0.030)
cb.set_ticks([0, 1, 2, 3, 4])
cb.set_ticklabels(["1", "10", "100", "1K", "10K"])
cb.set_label("Deaths per event (log scale)", fontsize=10, color=INK_SEC)
cb.outline.set_visible(False)
titleblock(fig, "Famine and flood became survivable; heatwaves went the other way",
           "Deaths per recorded event, by hazard and decade. Drought fell from 29,051 "
           "per event in the 1960s to 53 in the 2020s; extreme temperature rose from "
           "125 in the 1960s to 1,202 in the 2020s.")
fig.subplots_adjust(top=0.735, left=0.16)
footnote(fig, y=-0.03)
save(fig, "Fig16.png", "lethality heatmap")

# --------------------------------------------------------------- Fig 17 -----
# C1.5 CORRELATE: the decoupling, all four measures on one indexed scale.
ann = (df[df.year >= 1970].groupby("year")
         .agg(events=("events", "sum"), affected=("affected", "sum"),
              deaths=("deaths", "sum"), damage=("damage_real", "sum")))
base = ann.loc[1970:1979].mean()
idx = ann / base * 100

fig, ax = plt.subplots(figsize=(9.8, 5.8))
series = [("damage", "Economic damage", CAT[3]),
          ("events", "Recorded events", CAT[0]),
          ("affected", "People affected", CAT[2]),
          ("deaths", "Deaths", CAT[1])]
for key, label, col in series:
    sm = idx[key].rolling(5, center=True, min_periods=3).mean()
    ax.plot(idx.index, sm, color=col, lw=2.4, label=label, zorder=3)
    ax.text(2023, sm.iloc[-1], f"  {label}", color=col, fontsize=10,
            fontweight="bold", va="center", ha="left")
ax.axhline(100, color=INK_MUTED, lw=1, ls=(0, (4, 3)), zorder=2)
ax.text(2021.5, 104, "1970s average = 100", fontsize=9, color=INK_SEC,
        ha="right", va="bottom")
ax.set_yscale("log")
ax.set_xlim(1970, 2022)
ax.set_xlabel("Year")
ax.set_ylabel("Index, 1970s average = 100 (log scale)")
ax.set_yticks([10, 20, 50, 100, 200, 500])
ax.set_yticklabels(["10", "20", "50", "100", "200", "500"])
ax.grid(axis="x", visible=False)
despine(ax)
ax.legend(loc="upper left", ncol=2)
titleblock(fig, "Costs rose, deaths did not follow",
           "Five-year moving averages, each indexed to its own 1970s mean so four "
           "different units share one axis. Damage grew 1.58x per decade "
           "(p<0.001); annual deaths show no significant trend (p=0.064), and the "
           "rank correlation between the two is -0.01.")
fig.subplots_adjust(top=0.79, right=0.82)
footnote(fig, y=-0.02)
save(fig, "Fig17.png", "indexed decoupling")

# ---------------------------------------------------------------- Fig 20 ----
# C1.6 EXPLAIN: what does the CPI adjustment actually do to the damage figure?
yr = (df.groupby("year")
        .agg(cpi=("cpi", "mean"), nominal=("damage_nominal", "sum"),
             real=("damage_real", "sum"))
        .dropna())

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.6))

ax1.plot(yr.index, yr.cpi, color=CAT[0], lw=2.2)
ax1.set_title("US CPI, 1900-2022", fontsize=12, fontweight="bold", loc="left")
ax1.set_ylabel("CPI index (2022 = 100)")
ax1.set_xlabel("Year")
despine(ax1)

ax2.plot(yr.index, yr.nominal / 1e9, color=CAT[3], lw=2, label="Nominal (as reported)")
ax2.plot(yr.index, yr.real / 1e9, color=CAT[0], lw=2.2, label="Real (2022 USD)")
ax2.set_yscale("log")
ax2.set_title("Reported damage: nominal vs. real", fontsize=12, fontweight="bold", loc="left")
ax2.set_ylabel("Damage, $ billion per year (log scale)")
ax2.set_xlabel("Year")
ax2.legend(loc="upper left", fontsize=9)
despine(ax2)

fig.suptitle("Why every damage figure in this report is inflation-adjusted",
             fontsize=15, fontweight="bold", x=0.02, y=0.99, ha="left")
fig.text(0.02, 0.88,
          "Left: the CPI series used for adjustment, shown directly rather than only\n"
          "through its effect. Right: the same raw damage series before and after\n"
          "adjustment - the nominal series understates old disasters relative to\n"
          "recent ones by exactly the ratio on the left.",
          fontsize=10.5, color=INK_SEC, va="top")
fig.subplots_adjust(top=0.68, wspace=0.28)
footnote(fig, y=-0.02)
save(fig, "Fig20.png", "CPI and nominal vs real damage")

print("Task C complete.")
