"""
DAS732 A1 - TASK SET A: "WHEN?"  The temporal record, 1900-2022.

Guiding sub-question: How has the recorded disaster burden changed over time,
and how much of that change is real rather than an artefact of record-keeping?

Produces Fig3 - Fig7 and Fig18 - Fig20.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from emdat_common import (load, use_report_style, despine, save, HUMAN,
                          CAT, GRID, SURFACE, INK_SEC, INK_MUTED,
                          SUBGROUP_ORDER, SUBGROUP_COLOR, rounded_barh,
                          titleblock, footnote)

use_report_style()
df = load()

# ---------------------------------------------------------------- Fig 3 -----
# A1.1 OVERVIEW / SUMMARIZE: what is actually in the record?
t = df.groupby("type")["events"].sum().sort_values(ascending=False)
small = t[t < 50]
t = pd.concat([t[t >= 50], pd.Series({"Other (4 rare types)": small.sum()})])
t = t.sort_values()
share = t / df["events"].sum() * 100

fig, ax = plt.subplots(figsize=(9.2, 5.4))
y = np.arange(len(t))
rounded_barh(ax, y, t.values, CAT[0], height=0.62,
             labels=[f"{v:,}   ({s:.1f}%)" for v, s in zip(t.values, share.values)])
ax.set_yticks(y)
ax.set_yticklabels(t.index)
ax.set_xlabel("Recorded disaster events, 1900-2022")
ax.xaxis.set_major_formatter(HUMAN)
ax.grid(axis="y", visible=False)
despine(ax, keep=("bottom",))
titleblock(fig, "Two hazards account for seven of every ten recorded disasters",
           "Floods and storms dominate the EM-DAT record: 15,015 events across "
           "225 countries and 13 hazard types.")
fig.subplots_adjust(top=0.84)
footnote(fig, y=-0.02)
save(fig, "Fig3.png", "events by disaster type")

# ---------------------------------------------------------------- Fig 4 -----
# A1.2 TREND: when were these events recorded?
piv = (df.pivot_table(index="year", columns="subgroup", values="events",
                      aggfunc="sum")
         .reindex(columns=SUBGROUP_ORDER).fillna(0)
         .reindex(range(1900, 2023)).fillna(0))

fig, ax = plt.subplots(figsize=(9.6, 5.2))
ax.stackplot(piv.index, [piv[c].values for c in SUBGROUP_ORDER],
             colors=[SUBGROUP_COLOR[c] for c in SUBGROUP_ORDER],
             labels=SUBGROUP_ORDER, linewidth=0.8, edgecolor=SURFACE, zorder=3)
ax.set_xlim(1900, 2022)
ax.set_ylim(0, None)
ax.set_ylabel("Events recorded per year")
ax.set_xlabel("Year")
ax.grid(axis="x", visible=False)
despine(ax)
ax.axvline(1970, color=INK_MUTED, lw=1.2, ls=(0, (4, 3)), zorder=4)
ax.annotate("1970: EM-DAT's modern\nreporting era begins", xy=(1970, 215),
            xytext=(1913, 215), fontsize=9.5, color=INK_SEC, va="center",
            arrowprops=dict(arrowstyle="->", color=INK_MUTED, lw=1))
ax.text(2018, 45, "Hydrological", fontsize=9.5, color="#0d366b",
        fontweight="bold", ha="right")
ax.text(2018, 185, "Meteorological", fontsize=9.5, color="#7a2f11",
        fontweight="bold", ha="right")
ax.legend(loc="upper left", bbox_to_anchor=(0.005, 0.99))
titleblock(fig, "The record explodes after 1970 - mostly floods and storms",
           "91% of all events in the file are dated 1970-2022, a period covering "
           "only 43% of the 123 years.")
fig.subplots_adjust(top=0.85)
footnote(fig, y=-0.02)
save(fig, "Fig4.png", "annual events by sub-group")

# ---------------------------------------------------------------- Fig 5 -----
# A1.3 IDENTIFY / VALIDATE: is the rise real, or is it record-keeping?
dec = df.groupby("decade").agg(events=("events", "sum"),
                               pct_deaths=("has_deaths", "mean"),
                               pct_damage=("has_damage", "mean"))

fig, axes = plt.subplots(1, 2, figsize=(10.8, 5.0))
ax = axes[0]
ax.bar(dec.index, dec.events, width=8, color=CAT[0], edgecolor=SURFACE,
       linewidth=1.6, zorder=3)
ax.set_ylabel("Events recorded per decade")
ax.set_xlabel("Decade")
ax.set_title("a. Volume of the record", fontsize=12, loc="left", pad=8)
ax.grid(axis="x", visible=False)
despine(ax)
ax.annotate("2020s is a part-decade\n(2020-2022 only)", xy=(2017, 1300),
            xytext=(1901, 2750), fontsize=9, color=INK_SEC,
            arrowprops=dict(arrowstyle="->", color=INK_MUTED, lw=1))

ax = axes[1]
ax.plot(dec.index, dec.pct_deaths * 100, color=CAT[0], lw=2, marker="o", ms=5.5,
        zorder=3, label="Has a death toll")
ax.plot(dec.index, dec.pct_damage * 100, color=CAT[1], lw=2, marker="s", ms=5.5,
        zorder=3, label="Has an economic-damage figure")
ax.set_ylim(0, 100)
ax.set_ylabel("% of records carrying the field")
ax.set_xlabel("Decade")
ax.set_title("b. Completeness of the record", fontsize=12, loc="left", pad=8)
ax.grid(axis="x", visible=False)
despine(ax)
ax.text(2018, 64, "Death toll", ha="right", va="top", color="#0d366b",
        fontsize=9.5, fontweight="bold")
ax.text(2018, 26, "Damage figure", ha="right", va="top", color="#7a2f11",
        fontsize=9.5, fontweight="bold")
ax.legend(loc="upper right", fontsize=9)
titleblock(fig, "The count of disasters is partly a count of reporting",
           "Volume grew 52x from the 1900s to the 2000s, but the share of records "
           "carrying an economic-damage figure peaks at just 50% - so every damage "
           "total in this report is a lower bound.")
fig.subplots_adjust(top=0.735, wspace=0.26)
footnote(fig, y=-0.03)
save(fig, "Fig5.png", "reporting-bias diagnostic")

# ---------------------------------------------------------------- Fig 6 -----
# A1.4 COMPARE / DERIVE: the central divergence of the whole story.
d = df.groupby("decade").agg(deaths=("deaths", "sum"), events=("events", "sum"))
d["dpe"] = d.deaths / d.events

fig, axes = plt.subplots(2, 1, figsize=(9.8, 7.2), sharex=True,
                         gridspec_kw=dict(hspace=0.30))
ax = axes[0]
ax.bar(d.index, d.deaths / 1e6, width=8, color=CAT[0], edgecolor=SURFACE,
       linewidth=1.6, zorder=3)
ax.set_ylabel("Deaths per decade (millions)", fontsize=10)
ax.set_title("a. Total recorded deaths", fontsize=12, loc="left", pad=6)
ax.grid(axis="x", visible=False)
despine(ax)
for xi, v in zip(d.index, d.deaths / 1e6):
    if v > 1:
        ax.text(xi, v + 0.12, f"{v:.1f}M", ha="center", fontsize=9, color=INK_SEC)
ax.annotate("2020s: part-decade\n(2020-2022 only)", xy=(2020, 0.06),
            xytext=(1994, 1.9), fontsize=9, color=INK_SEC,
            arrowprops=dict(arrowstyle="->", color=INK_MUTED, lw=1))

ax = axes[1]
ax.plot(d.index, d.dpe, color=CAT[1], lw=2.2, marker="o", ms=6,
        markeredgecolor=SURFACE, markeredgewidth=1.5, zorder=3)
ax.set_yscale("log")
ax.set_ylabel("Deaths per event (log scale)", fontsize=10)
ax.set_xlabel("Decade")
ax.set_title("b. Deaths per recorded event", fontsize=12, loc="left", pad=6)
ax.grid(axis="x", visible=False)
despine(ax)
ax.yaxis.set_major_formatter(HUMAN)
for xi in (1900, 2010):
    ax.annotate(f"{d.loc[xi, 'dpe']:,.0f}", xy=(xi, d.loc[xi, "dpe"]),
                xytext=(0, 13), textcoords="offset points", ha="center",
                fontsize=10.5, fontweight="bold", color="#7a2f11")
titleblock(fig, "Disasters became far more survivable even as they became far more numerous",
           "Deaths per recorded event fell 99.4%, from ~19,900 in the 1900s to ~129 "
           "in the 2010s. The two measures use different scales, so they are drawn "
           "as two panels rather than on a twin axis.")
fig.subplots_adjust(top=0.80)
footnote(fig, y=-0.015)
save(fig, "Fig6.png", "deaths vs deaths-per-event")


# ---------------------------------------------------------------- Fig 7 -----
# A1.5 VALIDATE: is the death decline broad, or is it the loss of mega-events?
def trimmed_sum(g, k=3):
    g = g.dropna(subset=["deaths"]).sort_values("deaths", ascending=False)
    return g.iloc[k:]["deaths"].sum()


tr = df.groupby("decade", group_keys=False).apply(trimmed_sum, include_groups=False)
label_b = "Excluding each decade's 3 deadliest records"

# A dot plot rather than bars. Bar LENGTH encodes value, and on a logarithmic
# axis length is no longer proportional to the value, so any ratio a reader
# takes off the bars is wrong. Dots encode by POSITION, which survives the log
# transform, and the connector makes the gap between the two series - which is
# what this chart is actually about - the most visible thing on it.
fig, ax = plt.subplots(figsize=(9.8, 5.4))
for x in d.index:
    ax.plot([x, x], [d.deaths[x], tr[x]], color=GRID, lw=2.6, zorder=2,
            solid_capstyle="round")
ax.plot(d.index, d.deaths, marker="o", ms=9, color=CAT[0], linestyle="none",
        markeredgecolor=SURFACE, markeredgewidth=1.6, label="All records",
        zorder=4)
ax.plot(tr.index, tr.values, marker="o", ms=9, color=CAT[1], linestyle="none",
        markeredgecolor=SURFACE, markeredgewidth=1.6, label=label_b, zorder=4)

ax.set_yscale("log")
ax.set_ylim(2e4, 2.6e7)
ax.set_xlim(1893, 2027)
ax.yaxis.set_major_formatter(HUMAN)
ax.set_ylabel("Recorded deaths per decade (log scale)")
ax.set_xlabel("Decade")
ax.set_xticks(list(d.index))
ax.set_xticklabels([f"{x}s" for x in d.index], fontsize=9)
ax.grid(axis="x", visible=False)
despine(ax)
ax.legend(loc="upper right")
ax.annotate("1931 China flood alone:\n3.7M deaths", xy=(1930, d.deaths[1930]),
            xytext=(1900, 1.15e7), fontsize=9, color=INK_SEC, ha="left",
            arrowprops=dict(arrowstyle="->", color=INK_MUTED, lw=1))
ax.annotate("the gap is the\nmega-catastrophes", xy=(1950, 4.3e5),
            xytext=(1957, 2.6e6), fontsize=9, color=INK_SEC, ha="left",
            arrowprops=dict(arrowstyle="->", color=INK_MUTED, lw=1))
for x in (1900, 2000):
    ax.annotate(f"{tr[x]:,.0f}", xy=(x, tr[x]), xytext=(0, -24),
                textcoords="offset points", ha="center", fontsize=9.5,
                fontweight="bold", color="#7a2f11")
titleblock(fig, "The fall in deaths is the disappearance of mega-catastrophes, not a broad decline",
           "Strip each decade's three deadliest records and the residual death toll "
           "shows no downward trend at all - the 2000s sit above the 1900s. A dot "
           "plot is used rather than bars because bar length is not proportional to "
           "value on a logarithmic axis.")
fig.subplots_adjust(top=0.80)
footnote(fig, y=-0.02)
save(fig, "Fig7.png", "trimmed-deaths robustness check")

# ---------------------------------------------------------------- Fig 18 ----
# A1.6 DRILL DOWN: floods drive the post-1970 rise (Fig4) - which floods?
flood = df[df["type"] == "Flood"]
SUBTYPE_ORDER = ["Riverine flood", "Flash flood", "Coastal flood", "Flood (unspecified)"]
piv2 = (flood.pivot_table(index="year", columns="subtype", values="events",
                          aggfunc="sum")
             .reindex(columns=SUBTYPE_ORDER).fillna(0))
piv2_s = piv2.rolling(5, min_periods=1, center=True).mean()

fig, ax = plt.subplots(figsize=(9.6, 5.0))
ax.stackplot(piv2_s.index, piv2_s.T.values, labels=piv2_s.columns,
             colors=CAT[:4], alpha=0.92)
ax.set_xlim(1900, 2022)
ax.set_ylabel("Flood events per year (5-yr moving average)")
ax.set_xlabel("Year")
despine(ax)
ax.legend(loc="upper left", ncol=2, fontsize=9)
titleblock(fig, "Riverine flooding, not flash or coastal flooding, drives the flood trend",
           "Flood events split by subtype. A stacked area chart is used because the "
           "question is which subtype grows fastest inside an already-growing total, "
           "not any single subtype's absolute level.")
fig.subplots_adjust(top=0.84)
footnote(fig, y=-0.02)
save(fig, "Fig18.png", "flood events by subtype")

# ---------------------------------------------------------------- Fig 19 ----
# A1.7 COMPARE across type x decade: which hazards grew, and when?
from emdat_common import heatmap_log, INK
TOP6 = ["Flood", "Storm", "Earthquake", "Drought", "Landslide", "Extreme temperature"]
ev_td = (df[df.type.isin(TOP6)]
           .pivot_table(index="type", columns="decade", values="events", aggfunc="sum")
           .reindex(TOP6).fillna(0))

fig, ax = plt.subplots(figsize=(10.6, 4.9))
heatmap_log(ax, ev_td, "Events per decade (log scale)")
titleblock(fig, "Every hazard's record thickens after 1970, but not at the same rate",
           "Recorded events by hazard type and decade. Floods rise from 6 in the 1900s "
           "to 1,720 in the 2000s; earthquakes - the hardest hazard to miss - only from "
           "38 to 289. The 2020s column covers 2020-2022 only.")
fig.subplots_adjust(top=0.735, left=0.17)
footnote(fig, y=-0.03)
save(fig, "Fig19.png", "events by type and decade")

# ---------------------------------------------------------------- Fig 20 ----
# A1.8 VALIDATE with a control: annualised rate before and after 1970, per type.
pre = df[df.era == "1900-1969"]
post = df[df.era == "1970-2022"]
n_pre, n_post = 70, 53
rate = pd.DataFrame({
    "pre":  pre.groupby("type").events.sum().reindex(TOP6) / n_pre,
    "post": post.groupby("type").events.sum().reindex(TOP6) / n_post,
})
rate["mult"] = rate.post / rate.pre
rate = rate.sort_values("mult")

fig, ax = plt.subplots(figsize=(9.6, 5.2))
y = np.arange(len(rate))
for yi, (name, r) in zip(y, rate.iterrows()):
    ax.plot([r.pre, r.post], [yi, yi], color=GRID, lw=3, zorder=2,
            solid_capstyle="round")
ax.scatter(rate.pre, y, s=110, color=CAT[3], edgecolor=SURFACE, linewidth=1.5,
           zorder=3, label="1900-1969 (per year)")
ax.scatter(rate.post, y, s=110, color=CAT[0], edgecolor=SURFACE, linewidth=1.5,
           zorder=3, label="1970-2022 (per year)")
for yi, (name, r) in zip(y, rate.iterrows()):
    ax.text(r.post * 1.12, yi, f"x{r.mult:.1f}", va="center", fontsize=10,
            fontweight="bold", color="#7a2f11" if name != "Earthquake" else INK)
ax.set_xscale("log")
ax.set_yticks(y)
ax.set_yticklabels(rate.index)
ax.set_xlabel("Recorded events per year (log scale)")
ax.grid(axis="y", visible=False)
despine(ax, keep=("bottom",))
ax.legend(loc="upper left", fontsize=9.5)
ax.axhspan(list(rate.index).index("Earthquake") - 0.45,
           list(rate.index).index("Earthquake") + 0.45,
           color=GRID, alpha=0.5, zorder=1)
ax.text(rate.pre.min() * 0.9, list(rate.index).index("Earthquake") + 0.32,
        "control hazard: hard to under-report", fontsize=8.5, color=INK_SEC,
        style="italic", ha="left", va="bottom")
titleblock(fig, "Earthquakes set the reporting baseline; floods and heatwaves exceed it by far",
           "Annualised event rate before and after 1970. Earthquakes - physically hard to "
           "miss even in 1950 - rose 3.8x, an estimate of pure reporting improvement. "
           "Floods rose 26x and extreme temperature 41x: the excess over 3.8x is not "
           "bookkeeping.")
fig.subplots_adjust(top=0.79)
footnote(fig, y=-0.02)
save(fig, "Fig20.png", "pre/post-1970 rate per type with earthquake control")

print("Task A complete.")
