"""
DAS732 A1 - TASK SET B: "WHERE?"  The geography of exposure, 1900-2022.

Guiding sub-question: Where does the disaster burden fall, and does the place
that records the most disasters also suffer the most harm?

Produces Fig8 - Fig12.  Fig8/Fig9 are Plotly choropleths exported through
kaleido; the rest are matplotlib.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from emdat_common import (load, use_report_style, despine, save, human, HUMAN,
                          CAT, SEQ, SURFACE, INK, INK_SEC, INK_MUTED,
                          IMAGES, rounded_barh, titleblock, footnote,
                          SOURCE_NOTE)

use_report_style()
df = load()

# Country-level roll-up, the shared base for every figure in this task set.
c = (df.groupby(["country", "iso"])
       .agg(events=("events", "sum"), deaths=("deaths", "sum"),
            affected=("affected", "sum"), damage=("damage_real", "sum"))
       .reset_index())
c["deaths_per_event"] = c.deaths / c.events

SHORT = {
    "United States of America (the)": "United States",
    "Iran (Islamic Republic of)": "Iran",
    "Philippines (the)": "Philippines",
    "Russian Federation (the)": "Russia",
    "Venezuela (Bolivarian Republic of)": "Venezuela",
    "Korea (the Republic of)": "South Korea",
    "Taiwan (Province of China)": "Taiwan",
    "Netherlands (the)": "Netherlands",
    "Niger (the)": "Niger",
    "Sudan (the)": "Sudan",
    "Viet Nam": "Vietnam",
    "Tanzania, United Republic of": "Tanzania",
    "Bolivia (Plurinational State of)": "Bolivia",
    "Dominican Republic (the)": "Dominican Rep.",
    "Congo (the Democratic Republic of the)": "DR Congo",
    "Moldova (the Republic of)": "Moldova",
    "Korea (the Democratic People's Republic of)": "North Korea",
}
c["label"] = c.country.replace(SHORT)


# ------------------------------------------------------- choropleth helper ---
def choropleth(values_iso, values, title, subtitle, cbar_title, fname,
               tickvals, ticktext):
    """Sequential-blue world choropleth on a log10 scale.

    A single hue, light -> dark, is the correct encoding for magnitude; the
    log scale is required because the country totals span five orders of
    magnitude and a linear ramp would collapse every country but two.
    """
    fig = go.Figure(go.Choropleth(
        locations=values_iso, z=np.log10(values), locationmode="ISO-3",
        colorscale=[[i / (len(SEQ) - 1), col] for i, col in enumerate(SEQ)],
        marker_line_color=SURFACE, marker_line_width=0.6,
        colorbar=dict(title=dict(text=cbar_title, side="top",
                                 font=dict(size=16, color=INK_SEC)),
                      orientation="h", x=0.012, xanchor="left",
                      y=0.005, yanchor="bottom",
                      tickvals=tickvals, ticktext=ticktext,
                      len=0.32, thickness=14, outlinewidth=0,
                      tickfont=dict(size=15, color=INK_SEC)),
        zmin=float(np.log10(values).min()), zmax=float(np.log10(values).max()),
    ))
    fig.update_geos(showframe=False, showcoastlines=False,
                    projection_type="robinson",
                    lataxis_range=[-58, 84], lonaxis_range=[-170, 180],
                    landcolor="#eceae4", bgcolor=SURFACE, lakecolor=SURFACE,
                    showland=True, showocean=False, showcountries=False)
    fig.update_layout(
        title=dict(text=f"<b>{title}</b><br>"
                        f"<span style='font-size:19px;color:{INK_SEC}'>{subtitle}</span>",
                   x=0.012, xanchor="left", y=0.97, yanchor="top",
                   font=dict(size=30, color=INK)),
        margin=dict(l=6, r=6, t=152, b=104), paper_bgcolor=SURFACE,
        geo_bgcolor=SURFACE,
        annotations=[dict(x=0.012, y=-0.145, xref="paper", yref="paper",
                          showarrow=False, xanchor="left", align="left",
                          text=SOURCE_NOTE + "  Grey = no recorded event. "
                               "Colour scale is logarithmic.",
                          font=dict(size=14, color=INK_MUTED))],
        font=dict(family="Arial, Helvetica, sans-serif"))
    out = IMAGES / fname
    # Narrower canvas with larger type: the map is placed at ~16.6cm in the
    # LaTeX report, so anything set small here becomes unreadable in print.
    fig.write_image(str(out), width=1150, height=690, scale=2.2)
    print(f"  saved {fname}")


# ---------------------------------------------------------------- Fig 8 -----
# B1.1 LOCATE / OVERVIEW: where are disasters recorded?
m = c[c.events > 0]
choropleth(m.iso, m.events,
           "Almost every country on Earth appears in the disaster record",
           "Total recorded disaster events per country, 1900-2022.<br>"
           "225 countries appear; the United States (1,119) and China (984) lead.",
           "Recorded events per country", "Fig8.png",
           tickvals=[0, 1, 2, 3], ticktext=["1", "10", "100", "1,000"])

# ---------------------------------------------------------------- Fig 9 -----
# B1.2 LOCATE / COMPARE: where do people actually die?
m = c[c.deaths > 0]
choropleth(m.iso, m.deaths,
           "But death is concentrated in a handful of countries",
           "Total recorded disaster deaths per country, 1900-2022.<br>China and India "
           "alone account for more than half of all 22.9 million recorded deaths.",
           "Recorded deaths per country", "Fig9.png",
           tickvals=[0, 2, 4, 6], ticktext=["1", "100", "10K", "1M"])

# ---------------------------------------------------------------- Fig 10 -----
# B1.3 RANK / COMPARE: four measures, four different leaderboards.
N = 12
panels = [("events", "Recorded events", CAT[0], lambda v: f"{v:,.0f}"),
          ("deaths", "Recorded deaths", CAT[1], lambda v: human(v)),
          ("affected", "People affected", CAT[2], lambda v: human(v)),
          ("damage", "Economic damage (2022 US$)", CAT[3], lambda v: "$" + human(v))]

fig, axes = plt.subplots(2, 2, figsize=(12.4, 8.4))
for ax, (metric, label, col, fmt) in zip(axes.ravel(), panels):
    top = c.nlargest(N, metric).sort_values(metric)
    y = np.arange(N)
    rounded_barh(ax, y, top[metric].values, col, height=0.66,
                 labels=[fmt(v) for v in top[metric].values])
    ax.set_yticks(y)
    ax.set_yticklabels(top.label, fontsize=9.5)
    ax.set_xticks([])
    ax.grid(False)
    despine(ax, keep=())
    ax.set_title(label, fontsize=12, loc="left", pad=8, color=INK)
titleblock(fig, "Most disasters, most deaths, most people affected and most money lost "
                "are four different maps",
           "Top 12 countries on each measure, 1900-2022. The United States tops events "
           "and damage but ranks 23rd for deaths; Bangladesh is 3rd for deaths and "
           "23rd for damage.")
fig.subplots_adjust(top=0.855, hspace=0.34, wspace=0.42)
footnote(fig, y=-0.005)
save(fig, "Fig10.png", "four leaderboards")

# ---------------------------------------------------------------- Fig 11 -----
# B1.4 DERIVE / COMPARE: how concentrated is each burden?
fig, ax = plt.subplots(figsize=(9.6, 5.6))
curves = [("events", "Recorded events", CAT[0]),
          ("damage", "Economic damage", CAT[3]),
          ("affected", "People affected", CAT[2]),
          ("deaths", "Deaths", CAT[1])]
# Direct labels are placed where each curve is isolated, not at a common x -
# the four curves converge above 95% and would collide there.
LABEL_AT = {"events": (30, 50, "top"), "deaths": (3.2, 88, "bottom")}
cum_by_metric = {}
for metric, label, col in curves:
    s_ = np.sort(c[metric].dropna().values)[::-1]
    cum = np.cumsum(s_) / s_.sum() * 100
    x = np.arange(1, len(cum) + 1)
    cum_by_metric[metric] = (x, cum)
    ax.plot(x, cum, color=col, lw=2.2, label=label, zorder=3)
    if metric in LABEL_AT:
        lx, ly, va = LABEL_AT[metric]
        ax.text(lx, ly, label, color=col, fontsize=10.5, fontweight="bold",
                va=va, ha="left", zorder=5)
ax.axhline(50, color=INK_MUTED, lw=1, ls=(0, (4, 3)), zorder=2)
ax.text(5.5, 52.5, "half of the global total", fontsize=9, color=INK_SEC)
ax.set_xscale("log")
ax.set_xlim(1, 225)
ax.set_ylim(0, 101)
ax.set_xticks([1, 2, 5, 10, 20, 50, 100, 225])
ax.set_xticklabels(["1", "2", "5", "10", "20", "50", "100", "225"])
ax.set_xlabel("Number of countries, ranked from worst-affected (log scale)")
ax.set_ylabel("Cumulative share of the global total (%)")
ax.grid(axis="x", visible=False)
despine(ax)
ax.legend(loc="lower right")
xd, cd = cum_by_metric["deaths"]
for k in (1, 2):
    ax.plot([k], [cd[k - 1]], marker="o", ms=8, color=CAT[1],
            markeredgecolor=SURFACE, markeredgewidth=2, zorder=6)
ax.text(1.06, 44, "China alone: 48%\nof all recorded deaths", fontsize=9.5,
        color=INK_SEC, va="top", ha="left")
ax.text(2.15, 70, "+ India: 68%", fontsize=9.5, color=INK_SEC,
        va="bottom", ha="left")
titleblock(fig, "Half of all deaths fall on 2 countries; half of all disasters are spread over 20",
           "Cumulative share of each global total, countries ranked worst-first. Deaths and people affected are the most concentrated burdens; the raw count of events is by far the most evenly spread.")
fig.subplots_adjust(top=0.825)
footnote(fig, y=-0.02)
save(fig, "Fig11.png", "concentration curves")

# ---------------------------------------------------------------- Fig 10 ----
# B1.5 DERIVE / RANK: lethality, once exposure is held roughly constant.
top20 = c.nlargest(20, "events").sort_values("deaths_per_event")
fig, ax = plt.subplots(figsize=(9.8, 6.6))
y = np.arange(len(top20))
rounded_barh(ax, y, top20.deaths_per_event.values, CAT[1], height=0.66,
             labels=[f"{v:,.0f}" for v in top20.deaths_per_event.values])
ax.set_yticks(y)
ax.set_yticklabels(top20.label)
ax.set_xlabel("Recorded deaths per recorded disaster event, 1900-2022")
ax.xaxis.set_major_formatter(HUMAN)
ax.grid(axis="y", visible=False)
despine(ax, keep=("bottom",))
ax.annotate("about 280 times the\nUnited States figure of 40",
            xy=(10900, 19), xytext=(6100, 15.2), fontsize=9.5, color=INK_SEC,
            arrowprops=dict(arrowstyle="->", color=INK_MUTED, lw=1))
titleblock(fig, "Among equally disaster-prone countries, lethality differs by a factor of 1,000",
           "The 20 countries with the most recorded events, ranked by deaths per event. "
           "Exposure is similar; the outcome is not - which points at vulnerability and "
           "response capacity, not at the hazards themselves.")
fig.subplots_adjust(top=0.80)
footnote(fig, y=-0.02)
save(fig, "Fig12.png", "lethality among the most-exposed countries")

print("Task B complete.")
