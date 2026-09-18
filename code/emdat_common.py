"""
DAS732 A1 - Shared preprocessing and plot styling for the EM-DAT
Natural Disasters Emergency Events Database (country profiles, 1900-2022).

Every downstream script imports from here so that the cleaning rules are
applied identically across all three task sets.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

ROOT   = Path(__file__).resolve().parent.parent
RAW    = ROOT / "data" / "emdat_country_profiles_raw.csv"
CLEAN  = ROOT / "data" / "emdat_clean_tableau.csv"
IMAGES = ROOT / "images"
IMAGES.mkdir(exist_ok=True)

# Analysis window: the file is a 2023-04-06 snapshot, so 2023 is a partial year
# and is excluded from every trend figure.
YEAR_MIN, YEAR_MAX = 1900, 2022

# ---------------------------------------------------------------- palette ---
# Validated categorical palette (dataviz reference instance, light surface).
# Fixed slot order - never cycled.
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4",
       "#008300", "#4a3aa7", "#e34948"]
SEQ = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7",
       "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"]
SURFACE    = "#fcfcfb"
INK        = "#0b0b0b"
INK_SEC    = "#52514e"
INK_MUTED  = "#8a8985"
GRID       = "#e3e2de"

# Disaster sub-groups get fixed slots so colour follows the entity, not its rank.
SUBGROUP_ORDER = ["Hydrological", "Meteorological", "Geophysical",
                  "Climatological", "Biological"]
SUBGROUP_COLOR = dict(zip(SUBGROUP_ORDER, CAT[:5]))


def use_report_style():
    mpl.rcParams.update({
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.titlecolor": INK,
        "axes.labelsize": 11,
        "axes.labelcolor": INK_SEC,
        "axes.edgecolor": GRID,
        "axes.linewidth": 0.8,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.7,
        "xtick.color": INK_SEC,
        "ytick.color": INK_SEC,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.frameon": False,
        "legend.fontsize": 10,
        "figure.dpi": 130,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
    })


def despine(ax, keep=("left", "bottom")):
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(s in keep)


def human(x, pos=None):
    """1_234_567 -> '1.2M'."""
    x = float(x)
    for div, suf in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")):
        if abs(x) >= div:
            v = x / div
            return f"{v:,.0f}{suf}" if abs(v) >= 10 else f"{v:,.1f}{suf}"
    return f"{x:,.0f}"


HUMAN = FuncFormatter(human)


def save(fig, name, caption=""):
    out = IMAGES / name
    fig.savefig(out)
    plt.close(fig)
    print(f"  saved {name}  {caption}")
    return out


# ------------------------------------------------------------- data load ---
def load_raw():
    """Raw read: semicolon-separated, comma as the decimal mark."""
    return pd.read_csv(RAW, sep=";", decimal=",")


def load(write_clean=False):
    """Cleaned analysis frame. See README for the full rule list."""
    df = load_raw()

    # 1. Column names -> snake_case, stable across scripts.
    df = df.rename(columns={
        "Disaster Subroup": "subgroup",          # sic: typo is in the source file
        "Disaster Group": "group",
        "Disaster Type": "type",
        "Disaster Subtype": "subtype",
        "Total Events": "events",
        "Total Affected": "affected",
        "Total Deaths": "deaths",
        "Total Damage (USD, original)": "damage_nominal",
        "Total Damage (USD, adjusted)": "damage_real",
        "Year": "year", "Country": "country", "ISO": "iso", "CPI": "cpi",
    })

    # 2. Restrict to complete years (drop the partial 2023 snapshot tail).
    df = df[(df.year >= YEAR_MIN) & (df.year <= YEAR_MAX)].copy()

    # 4. Tidy label columns - the source file carries trailing spaces on some
    #    Disaster Type values (e.g. "Extreme temperature "), which would
    #    otherwise split one category in two; flag historical states too.
    for c in ["country", "iso", "group", "subgroup", "type", "subtype"]:
        df[c] = df[c].astype("string").str.strip()

    # 5. Subtype is missing when EM-DAT recorded only the coarse type.
    df["subtype"] = df["subtype"].fillna(df["type"] + " (unspecified)")
    HISTORICAL = {"Soviet Union", "Czechoslovakia", "Yugoslavia",
                  "Germany Dem Rep", "Serbia Montenegro", "Yemen Arab Rep",
                  "Yemen P Dem Rep"}
    df["is_historical_state"] = df["country"].isin(HISTORICAL)

    # 6. Derived time buckets.
    df["decade"] = (df.year // 10) * 10
    df["era"] = np.where(df.year < 1970, "1900-1969", "1970-2022")

    # 7. Impact columns stay NaN ("not reported"), never silently zero -
    #    zero-filling would understate per-event severity. Totals use a
    #    separate explicitly zero-filled copy.
    for c in ["affected", "deaths", "damage_nominal", "damage_real"]:
        df[c + "_z"] = df[c].fillna(0.0)

    # 8. Reporting completeness flags, used to caveat the trend figures.
    df["has_deaths"] = df["deaths"].notna()
    df["has_damage"] = df["damage_real"].notna()

    df = df.sort_values(["year", "country", "type", "subtype"]).reset_index(drop=True)

    if write_clean:
        cols = ["year", "decade", "era", "country", "iso", "group", "subgroup",
                "type", "subtype", "events", "deaths", "affected",
                "damage_nominal", "damage_real", "cpi",
                "has_deaths", "has_damage", "is_historical_state"]
        df[cols].to_csv(CLEAN, index=False)
        print(f"  wrote {CLEAN.name}  ({len(df):,} rows)")
    return df


if __name__ == "__main__":
    d = load(write_clean=True)
    print(d.shape)


# ------------------------------------------------------------ mark helpers ---
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch


def _rounded_right_path(x0, y0, w, h, rx, ry):
    """Rectangle with the two right-hand corners rounded, square at x0."""
    rx = min(rx, w)
    ry = min(ry, h / 2)
    x1, y1 = x0 + w, y0 + h
    verts = [(x0, y0), (x1 - rx, y0), (x1, y0), (x1, y0 + ry),
             (x1, y1 - ry), (x1, y1), (x1 - rx, y1), (x0, y1), (x0, y0)]
    codes = [MplPath.MOVETO, MplPath.LINETO, MplPath.CURVE3, MplPath.CURVE3,
             MplPath.LINETO, MplPath.CURVE3, MplPath.CURVE3, MplPath.LINETO,
             MplPath.CLOSEPOLY]
    return MplPath(verts, codes)


def rounded_barh(ax, y, widths, color, height=0.62, radius_px=4, labels=None,
                 label_fmt=None, label_pad=0.012, xmax=None, zorder=3):
    """Horizontal bars with a 4px rounded data-end, square against the baseline.

    The corner radius is converted from pixels into x- and y-data units using
    the axes' rendered size, so the rounding stays isotropic on screen instead
    of being stretched by the (very different) x and y scales.
    """
    widths = np.asarray(widths, dtype=float)
    if xmax is None:
        xmax = float(np.nanmax(widths)) if len(widths) else 1.0
    ax.set_xlim(0, xmax * 1.16)
    ax.set_ylim(min(y) - 0.7, max(y) + 0.7)
    ax.figure.canvas.draw()                      # realise the axes geometry
    bb = ax.get_window_extent()
    xr = ax.get_xlim()[1] - ax.get_xlim()[0]
    yr = ax.get_ylim()[1] - ax.get_ylim()[0]
    rx = radius_px * xr / bb.width
    ry = radius_px * yr / bb.height
    for yi, w in zip(y, widths):
        if not np.isfinite(w) or w <= 0:
            continue
        ax.add_patch(PathPatch(
            _rounded_right_path(0.0, yi - height / 2, w, height, rx, ry),
            facecolor=color, linewidth=0, zorder=zorder))
    if labels is not None:
        fmt = label_fmt or human
        for yi, w, lab in zip(y, widths, labels):
            txt = lab if isinstance(lab, str) else fmt(w)
            ax.text(float(w) + xmax * label_pad, yi, txt, va="center",
                    ha="left", fontsize=9.5, color=INK_SEC, zorder=4)
    return ax


def stacked_bar(ax, x, series, colors, labels, width=0.78, horizontal=False):
    """Stacked bars with a 2px surface gap between segments (spacer rule)."""
    bottom = np.zeros(len(x), dtype=float)
    handles = []
    for vals, col, lab in zip(series, colors, labels):
        vals = np.asarray(vals, dtype=float)
        if horizontal:
            h = ax.barh(x, vals, left=bottom, height=width, color=col,
                        label=lab, edgecolor=SURFACE, linewidth=1.6, zorder=3)
        else:
            h = ax.bar(x, vals, bottom=bottom, width=width, color=col,
                       label=lab, edgecolor=SURFACE, linewidth=1.6, zorder=3)
        handles.append(h)
        bottom += np.nan_to_num(vals)
    return handles


def titleblock(fig, title, subtitle=None, pad_in=0.10, gap_in=0.09):
    """Left-aligned title + deck, spaced in inches so they never collide.

    suptitle anchors va='top'; the deck is placed the same way a fixed number
    of inches below it, which keeps the gap constant across figure sizes.
    """
    h = fig.get_size_inches()[1]
    y_title = 1 - pad_in / h
    fig.suptitle(title, x=0.012, ha="left", va="top", y=y_title,
                 fontsize=15.5, fontweight="bold", color=INK)
    if subtitle:
        title_in = 15.5 / 72 * 1.25
        y_sub = y_title - (title_in + gap_in) / h
        fig.text(0.012, y_sub, subtitle, ha="left", va="top", fontsize=10.5,
                 color=INK_SEC, wrap=True)


SOURCE_NOTE = ("Source: EM-DAT Emergency Events Database country profiles "
               "(CRED / UCLouvain), 1900-2022 snapshot of 2023-04-06.")


def footnote(fig, text=SOURCE_NOTE, y=-0.005):
    fig.text(0.012, y, text, ha="left", fontsize=8.5, color=INK_MUTED)


def heatmap_log(ax, table, cbar_label, fmt=lambda v: f"{v:,.0f}",
                cbar_ticks=(0, 1, 2, 3, 4), cbar_labels=("1", "10", "100", "1K", "10K")):
    """Sequential-blue heatmap of a categorical x ordinal table on a log10 colour scale.

    Every cell prints its value so the reader never estimates a number from
    colour; ink flips to white only on the dark end of the ramp. Cells with no
    data are drawn as a dash. Returns the colorbar so callers can adjust it.
    """
    from matplotlib.colors import LinearSegmentedColormap
    blues = LinearSegmentedColormap.from_list("emdat_blues", SEQ)
    vals = table.values.astype(float)
    with np.errstate(divide="ignore"):
        z = np.where(vals > 0, np.log10(np.where(vals > 0, vals, 1)), np.nan)
    im = ax.imshow(z, cmap=blues, aspect="auto", vmin=np.nanmin(z), vmax=np.nanmax(z))
    ax.set_xticks(range(table.shape[1]))
    ax.set_xticklabels([f"{c}s" if isinstance(c, (int, np.integer)) else str(c)
                        for c in table.columns])
    ax.set_yticks(range(table.shape[0]))
    ax.set_yticklabels(table.index)
    ax.grid(False)
    despine(ax, keep=())
    ax.set_xticks(np.arange(-.5, table.shape[1], 1), minor=True)
    ax.set_yticks(np.arange(-.5, table.shape[0], 1), minor=True)
    ax.grid(which="minor", color=SURFACE, linewidth=2.4)
    ax.tick_params(which="minor", length=0)
    thresh = np.nanmin(z) + 0.62 * np.ptp(z[~np.isnan(z)])
    for i in range(table.shape[0]):
        for j in range(table.shape[1]):
            v = vals[i, j]
            if np.isnan(v) or v <= 0:
                ax.text(j, i, "-", ha="center", va="center", color=INK_MUTED)
                continue
            col = "#ffffff" if z[i, j] > thresh else INK
            ax.text(j, i, fmt(v), ha="center", va="center", fontsize=9,
                    color=col, fontweight="bold")
    cb = ax.figure.colorbar(im, ax=ax, pad=0.015, fraction=0.030)
    cb.set_ticks(list(cbar_ticks))
    cb.set_ticklabels(list(cbar_labels))
    cb.set_label(cbar_label, fontsize=10, color=INK_SEC)
    cb.outline.set_visible(False)
    return cb
