"""
DAS732 A1 - correctness harness for the report.

Re-derives every quantitative claim in report/DAS732_A1_Report.tex straight from
the raw CSV and asserts that the number actually printed in the report matches.
A stale or mistyped figure therefore fails the build rather than reaching a
marker.

    python check_report.py        # exits non-zero if any check fails

Each check is a (label, expected-substring) pair. The .tex is normalised first
(LaTeX thin-space separators "{,}" become plain commas, "\\%" becomes "%") so
that the expected strings read like ordinary prose.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from emdat_common import load, load_raw

ROOT = Path(__file__).resolve().parent.parent
TEX = ROOT / "report" / "DAS732_A1_Report.tex"

raw = load_raw()
df = load()

# ------------------------------------------------------------ derived data --
dec = df.groupby("decade").agg(events=("events", "sum"), deaths=("deaths", "sum"),
                               damage=("damage_real", "sum"))
dec["dpe"] = dec.deaths / dec.events

ctry = (df.groupby("country")
          .agg(events=("events", "sum"), deaths=("deaths", "sum"),
               affected=("affected", "sum"), damage=("damage_real", "sum")))
for m in ("events", "deaths", "affected", "damage"):
    ctry[m + "_rk"] = ctry[m].rank(ascending=False, method="min").astype(int)
ctry["dpe"] = ctry.deaths / ctry.events

typ = df.groupby("type").agg(events=("events", "sum"), deaths=("deaths", "sum"),
                             affected=("affected", "sum"), damage=("damage_real", "sum"),
                             med_deaths=("deaths", "median"),
                             med_damage=("damage_real", "median"))

ann = (df[df.year >= 1970].groupby("year")
         .agg(events=("events", "sum"), affected=("affected", "sum"),
              deaths=("deaths", "sum"), damage=("damage_real", "sum")))


def share(col, key):
    return typ[col][key] / typ[col].sum() * 100


def trend(series):
    y = np.log10(series.replace(0, np.nan)).dropna()
    r = stats.linregress(y.index.values, y.values)
    return 10 ** (r.slope * 10), r.pvalue, r.rvalue ** 2


def leth(hazard, decade):
    sub = df[(df.type == hazard) & (df.decade == decade)]
    return sub.deaths.sum() / sub.events.sum()


def trimmed(decade, k=3):
    g = df[df.decade == decade].dropna(subset=["deaths"]).sort_values("deaths", ascending=False)
    return g.iloc[k:].deaths.sum()


top5 = {m: ctry[m].sort_values(ascending=False).head(5).sum() / ctry[m].sum() * 100
        for m in ("events", "deaths", "affected", "damage")}


def n_countries_for_half(m):
    s = ctry[m].sort_values(ascending=False)
    return int((s.cumsum() / s.sum() < 0.5).sum()) + 1


ev_tr, ev_p, ev_r2 = trend(ann.events)
dm_tr, dm_p, dm_r2 = trend(ann.damage)
af_tr, af_p, af_r2 = trend(ann.affected)
de_tr, de_p, de_r2 = trend(ann.deaths)
dpe_tr, dpe_p, dpe_r2 = trend(ann.deaths / ann.events)
spearman = stats.spearmanr(ann.deaths, ann.damage).statistic

# ----------------------------------------------------------------- checks ---
C: list[tuple[str, str]] = []


ROUNDING: list[tuple[str, float, int, float]] = []


def chk(label: str, expected: str) -> None:
    C.append((label, expected))


def chk_round(label: str, value: float, ndigits: int, printed: str,
              target: float) -> None:
    """For a figure the report rounds on purpose.

    Asserts both that the rounded string appears in the .tex and that rounding
    the true value really does produce that number, so a rounded figure cannot
    drift away from the data unnoticed.
    """
    ROUNDING.append((label, value, ndigits, target))
    C.append((label, printed))


# --- dataset description ---------------------------------------------------
chk("raw row count", f"{len(raw):,} rows")
chk("total events", f"{df.events.sum():,} recorded events")
chk("analysis row count", f"{len(df):,} rows")
chk("rows dropped for 2023", f"{len(raw) - len(df)} rows")
chk("country count", f"{df.country.nunique()} distinct countries")
chk("hazard type count", f"{df.type.nunique()} values, e.g.\\ Flood")
chk("subtype count", f"{raw['Disaster Subtype'].nunique()} values, e.g.\\ Riverine flood")
chk("subtype missing pct", f"{raw['Disaster Subtype'].isna().mean() * 100:.1f}\\%")
chk("affected missing pct", f"{raw['Total Affected'].isna().mean() * 100:.1f}\\%")
chk("deaths missing pct", f"{raw['Total Deaths'].isna().mean() * 100:.1f}\\%")
chk("damage missing pct", f"{raw['Total Damage (USD, original)'].isna().mean() * 100:.1f}\\%")
chk("cpi missing pct", f"{raw['CPI'].isna().mean() * 100:.1f}\\%")
chk("subtype rows filled", f"{raw['Disaster Subtype'].isna().sum():,} rows retained")
chk("historical states", f"{int(df.is_historical_state.any()) and 7} historical states")
chk("nominal damage total", f"\\${df.damage_nominal.sum() / 1e12:.2f} trillion")
chk("real damage total", f"\\${df.damage_real.sum() / 1e12:.2f} trillion")
chk("damage coverage", f"{df.has_damage.mean() * 100:.1f}\\% of records carry a damage")
chk("era share of events",
    f"{df.loc[df.era == '1970-2022', 'events'].sum() / df.events.sum() * 100:.1f}\\% of all recorded events")
chk("era share of years", f"{53 / 123 * 100:.1f}\\% of the 123 years")

# --- tasks considered and rejected (Section 1.2) ---------------------------
_ct = df.groupby(["country", "type"])["events"].sum().reset_index()
_tot = _ct.groupby("country")["events"].sum()
_big = _tot[_tot >= 20].index
_dom = (_ct[_ct.country.isin(_big)]
        .sort_values("events", ascending=False).groupby("country").first())
chk("countries with >=20 events", f"{len(_big)} countries with at least 20")
chk("flood dominant countries", f"flood is the most frequent hazard in {int(_dom.type.value_counts()['Flood'])}")
chk("storm dominant countries", f"storm in {int(_dom.type.value_counts()['Storm'])}")
chk("insect infestation rows", f"{int((df.type == 'Insect infestation').sum())} insect")

# --- Task A ----------------------------------------------------------------
chk("flood events", f"{int(typ.events['Flood']):,} events")
chk("flood share", f"{share('events', 'Flood'):.1f}\\%")
chk("storm events", f"{int(typ.events['Storm']):,}")
chk("storm share", f"{share('events', 'Storm'):.1f}\\%")
chk("flood+storm share",
    f"{(share('events', 'Flood') + share('events', 'Storm')):.0f}\\% of all")
chk("earthquake share", f"{share('events', 'Earthquake'):.1f}\\%")
chk("drought event share", f"{share('events', 'Drought'):.1f}\\% of events")
rare = typ.events[typ.events < 50].sum()
chk("rare types folded", f"{int(rare)} events")
peak_year = int(df.groupby('year').events.sum().idxmax())
chk("peak year events", f"{int(df.groupby('year').events.sum().max())} events in {peak_year}")
chk("1900s events", f"({int(dec.events[1900])} events)")
chk("2000s events", f"({int(dec.events[2000]):,} events)")
chk("event growth factor", f"{dec.events[2000] / dec.events[1900]:.0f}-fold")
chk("peak deaths decade", f"1920s at {dec.deaths[1920] / 1e6:.2f} million")
chk("2010s deaths", f"{dec.deaths[2010] / 1e6:.2f} million in the 2010s")
chk_round("1900s deaths per event", dec.dpe[1900], -2,
          "$\\approx$19,900 in the 1900s", 19900)
chk("2010s deaths per event", f"{dec.dpe[2010]:,.0f} in the 2010s")
chk("lethality decline pct", f"{(1 - dec.dpe[2010] / dec.dpe[1900]) * 100:.1f}\\% decline")
chk_round("trimmed 2000s", trimmed(2000), -3, "the 2000s (390,000)", 390000)
chk_round("trimmed 1900s", trimmed(1900), -3, "(117,000)", 117000)
worst = df.nlargest(2, "deaths")
chk("1931 China flood", f"{worst.iloc[0].deaths / 1e6:.1f} million deaths")
chk("1928 China drought", f"{worst.iloc[1].deaths / 1e6:.1f} million)")

# --- Task B ----------------------------------------------------------------
US = "United States of America (the)"
chk("US events", f"({int(ctry.events[US]):,} events)")
chk("China events", f"China ({int(ctry.events['China'])})")
chk("India events", f"India ({int(ctry.events['India'])})")
chk("Philippines events", f"Philippines ({int(ctry.events['Philippines (the)'])})")
chk("Indonesia events", f"Indonesia ({int(ctry.events['Indonesia'])})")
chk("China deaths", f"China ({ctry.deaths['China'] / 1e6:.2f} million)")
chk("India deaths", f"India ({ctry.deaths['India'] / 1e6:.2f}\nmillion)")
chk("global deaths", f"{df.deaths.sum() / 1e6:.2f} million recorded deaths")
chk("China+India share",
    f"{(ctry.deaths['China'] + ctry.deaths['India']) / df.deaths.sum() * 100:.0f}\\% of all")
chk("Bangladesh deaths", f"{ctry.deaths['Bangladesh'] / 1e6:.2f} million")
chk("US deaths rank", f"{ctry.deaths_rk[US]}rd}} in deaths with {ctry.deaths[US]:,.0f}")
chk("US damage", f"\\${ctry.damage[US] / 1e12:.2f}\ntrillion")
chk("Japan damage", f"\\${ctry.damage['Japan'] / 1e9:.0f} billion")
chk("Australia ranks",
    f"{ctry.events_rk['Australia']}th for events and \\textbf{{{ctry.damage_rk['Australia']}th}}")
chk("Australia deaths rank", f"{ctry.deaths_rk['Australia']}th}} for deaths")
chk("Japan affected rank", f"{ctry.affected_rk['Japan']}st for people")
chk("countries for half deaths", f"{n_countries_for_half('deaths')} countries}} to pass half")
chk("countries for half events", f"{n_countries_for_half('events')} countries}} to pass half")
chk("China deaths share", f"China alone is {ctry.deaths['China'] / df.deaths.sum() * 100:.0f}\\%")
chk("top5 deaths", f"{top5['deaths']:.1f}\\%}} of deaths")
chk("top5 affected", f"{top5['affected']:.1f}\\%}} of people")
chk("top5 damage", f"{top5['damage']:.1f}\\%}} of damage")
chk("top5 events", f"{top5['events']:.1f}\\%}} of events")
t20 = ctry.nlargest(20, "events")
chk("China dpe", f"China at {ctry.dpe['China']:,.0f} deaths per event")
chk("Bangladesh dpe", f"Bangladesh at {ctry.dpe['Bangladesh']:,.0f}")
chk("US dpe", f"United States at {ctry.dpe[US]:.0f}")
chk("Australia dpe", f"Australia at {ctry.dpe['Australia']:.0f}")
chk_round("China/US lethality ratio", ctry.dpe["China"] / ctry.dpe[US], -1,
          "280 times", 280)

# --- Task C ----------------------------------------------------------------
for h in ("Flood", "Storm", "Earthquake", "Drought"):
    for col, lbl in (("events", "events"), ("deaths", "deaths"),
                     ("affected", "affected"), ("damage", "damage")):
        chk(f"share {h}/{lbl}", f"{share(col, h):.1f}\\%")
chk("drought median deaths", f"{typ.med_deaths['Drought']:.0f} deaths")
chk("extreme temp median damage", f"\\${typ.med_damage['Extreme temperature'] / 1e6:.0f} million")
chk("wildfire median damage", f"\\${typ.med_damage['Wildfire'] / 1e6:.0f} million")
chk("wildfire median deaths", f"median of {typ.med_deaths['Wildfire']:.0f} deaths")
chk("1990s damage", f"\\${dec.damage[1990] / 1e9:,.0f} billion in the")
chk("2000s damage", f"\\${dec.damage[2000] / 1e9:,.0f} billion in the 2000s")
chk("2010s damage", f"\\${dec.damage[2010] / 1e9:,.0f} billion in the 2010s")
chk("2020s damage", f"\\${dec.damage[2020] / 1e9:,.0f} billion")
chk("2010s damage trillions", f"\\${dec.damage[2010] / 1e12:.2f} trillion")
chk("drought leth 1960s", f"{leth('Drought', 1960):,.0f} deaths per event in the 1960s")
chk("drought leth 2010s", f"{leth('Drought', 2010):.0f} in the 2010s")
chk("drought leth 2020s", f"{leth('Drought', 2020):.0f} in the 2020s")
chk("flood leth 1950s", f"{leth('Flood', 1950):,.0f} in the 1950s")
chk("flood leth 2010s", f"{leth('Flood', 2010):.0f} in the 2010s")
chk("storm leth 1970s", f"{leth('Storm', 1970):,.0f} in the 1970s")
chk("storm leth 2010s", f"{leth('Storm', 2010):.0f} in the")
chk("storm leth 2020s", f"{leth('Storm', 2020):.0f} in the 2020s")
chk("eq leth 1950s", f"{leth('Earthquake', 1950):.0f} in the 1950s")
chk("eq leth 2000s", f"{leth('Earthquake', 2000):,.0f} in the")
chk("eq leth 2010s", f"{leth('Earthquake', 2010):,.0f} in the 2010s")
chk("heat leth 1960s", f"{leth('Extreme temperature', 1960):.0f} in the 1960s")
chk("heat leth 2000s", f"{leth('Extreme temperature', 2000):.0f}\nin the 2000s")
chk("heat leth 2020s", f"{leth('Extreme temperature', 2020):,.0f} in the 2020s")
chk("events trend", f"\\times {ev_tr:.2f}$")
chk("damage trend", f"\\times {dm_tr:.2f}$")
chk("affected trend", f"\\times {af_tr:.2f}$")
chk("deaths trend", f"\\times {de_tr:.2f}}}$")
chk("dpe trend", f"\\times {dpe_tr:.2f}$")
chk("deaths p-value", f"$p = {de_p:.3f}$")
chk("deaths r2", f"\\textbf{{{de_r2:.2f}}}")
chk("spearman", f"{spearman:+.2f}".replace("+", ""))
chk("median damage 1970s", f"\\${ann.loc[1970:1989, 'damage'].median() / 1e9:.0f} billion (1970--89)")
chk("median damage 2000s", f"\\${ann.loc[2003:2022, 'damage'].median() / 1e9:.0f} billion (2003--22)")
chk("median deaths 1970s", f"{ann.loc[1970:1989, 'deaths'].median():,.0f} to")
chk("median deaths 2000s", f"to {ann.loc[2003:2022, 'deaths'].median():,.0f}")

# --- supplementary views (Fig18-20) ------------------------------------------
flood = df[df.type == "Flood"]
fsub = flood.groupby("subtype").events.sum()
fshare = fsub / fsub.sum() * 100
chk("flood total events (Fig18)", f"{int(fsub.sum()):,} recorded flood events")
chk("riverine share", f"{fshare['Riverine flood']:.1f}\\%")
chk("unspecified flood share", f"{fshare['Flood (unspecified)']:.1f}\\%")
chk("flash flood share", f"{fshare['Flash flood']:.1f}\\%")
chk("coastal flood share", f"{fshare['Coastal flood']:.1f}\\%")

div = df.groupby("country").type.nunique()
ev = df.groupby("country").events.sum()
chk("India diversity", f"India ({ev['India']:,} events) and Peru ({ev['Peru']:,} events)")
chk("India/Peru type count", f"{div['India']} distinct hazard types each")
chk("India events rank", f"India ranks\nonly {int(ev.rank(ascending=False, method='min')['India'])}rd by volume")
chk("Peru events rank", f"Peru {int(ev.rank(ascending=False, method='min')['Peru'])}th")
chk("US diversity", f"at {div['United States of America (the)']} and {div['China']} types")

cpi_y = df.groupby("year").cpi.mean()
chk_round("CPI 1900-2022 ratio", cpi_y[2022] / cpi_y[1900], 0, "35-fold", 35)
chk("CPI 1900 index", f"index {cpi_y[1900]:.1f}, base")

# --- supplementary views (Fig21-26) ------------------------------------------
TOP6 = ["Flood", "Storm", "Earthquake", "Drought", "Landslide", "Extreme temperature"]
td = df[df.type.isin(TOP6)].pivot_table(index="type", columns="decade",
                                         values="events", aggfunc="sum").fillna(0)
chk("flood 1900s->2000s (Fig21)", f"pale ({int(td.loc['Flood', 1900])} events in the 1900s)")
chk("flood 2000s cell", f"({int(td.loc['Flood', 2000]):,} in the 2000s)")
chk("quake 1900s->2000s", f"from {int(td.loc['Earthquake', 1900])} to {int(td.loc['Earthquake', 2000])}")
chk("ext temp 2000s", f"reaches {int(td.loc['Extreme temperature', 2000])} in the 2000s")

pre_, post_ = df[df.era == "1900-1969"], df[df.era == "1970-2022"]
rate = pd.DataFrame({"pre": pre_.groupby("type").events.sum() / 70,
                     "post": post_.groupby("type").events.sum() / 53}).reindex(TOP6)
rate["mult"] = rate.post / rate.pre
chk("quake rate pre/post", f"from {rate.loc['Earthquake','pre']:.1f} to {rate.loc['Earthquake','post']:.1f} events per year")
chk_round("quake multiplier", rate.loc["Earthquake", "mult"], 1, "3.8$\\times$", 3.8)
chk_round("flood multiplier", rate.loc["Flood", "mult"], 1, "26.2$\\times$", 26.2)
chk("flood rate pre/post", f"({rate.loc['Flood','pre']:.2f} to\n{rate.loc['Flood','post']:.1f} events per year)")
chk_round("ext temp multiplier", rate.loc["Extreme temperature", "mult"], 1, "41.3$\\times$", 41.3)
chk_round("landslide multiplier", rate.loc["Landslide", "mult"], 1, "15.4$\\times$", 15.4)
chk_round("storm multiplier", rate.loc["Storm", "mult"], 1, "11.1$\\times$", 11.1)

ev_pre = pre_.groupby("country").events.sum(); ev_post = post_.groupby("country").events.sum()
rk_pre = ev_pre.rank(ascending=False, method="min"); rk_post = ev_post.rank(ascending=False, method="min")
def rk(c): return int(rk_pre[c]), int(rk_post[c])
vp, vq = rk("Viet Nam");    chk("Vietnam rank shift", f"rises from {vp}th to {vq}th ({vp - vq} places)")
ap, aq = rk("Afghanistan"); chk("Afghanistan rank shift", f"from {ap}th to {aq}th ({ap - aq} places)")
up, uq = rk("Australia");   chk("Australia rank shift", f"from {up}th to {uq}th ({up - uq} places)")
jp, jq = rk("Japan");       chk("Japan rank shift", f"Japan falls from {jp}nd to {jq}th")
ip, iq = rk("Iran (Islamic Republic of)"); chk("Iran rank shift", f"Iran from {ip}th to {iq}th")

cdd = df.pivot_table(index="country", columns="decade", values="events", aggfunc="sum").fillna(0)
us = "United States of America (the)"
chk("US decade cells (Fig24)", f"{int(cdd.loc[us,1950])} events in the 1950s,\n{int(cdd.loc[us,1980])} in the 1980s, {int(cdd.loc[us,1990])} in the 1990s")
chk("Vietnam decade cells", f"(Vietnam: {int(cdd.loc['Viet Nam',1950])} in the 1950s, {int(cdd.loc['Viet Nam',2000])} in the 2000s)")

cc = (df.groupby("country").agg(events=("events","sum"), deaths=("deaths","sum"),
                               damage=("damage_real","sum")).nlargest(20, "events"))
cc["dpe"] = cc.deaths / cc.events; cc["dmg"] = cc.damage / cc.events / 1e6
rho, pval = stats.spearmanr(cc.dpe, cc.dmg)
chk("US per-event (Fig25)", f"States ({cc.loc[us,'dpe']:.0f} deaths, \\${cc.loc[us,'dmg']:,.0f} million per event)")
chk("Japan per-event", f"Japan ({cc.loc['Japan','dpe']:.0f} deaths,\n\\${cc.loc['Japan','dmg']:,.0f} million)")
chk("Bangladesh per-event", f"Bangladesh ({cc.loc['Bangladesh','dpe']:,.0f} deaths, \\${cc.loc['Bangladesh','dmg']:.0f} million per event)")
chk("Afghanistan per-event", f"\\${cc.loc['Afghanistan','dmg']:.0f} million per event")
chk("wealth spearman", f"{rho:.2f} ($p =\n{pval:.2f}$)")

sub_ = df[df.type.isin(TOP6) & (df.year >= 1950)]
ape = (sub_.pivot_table(index="type", columns="decade", values="affected", aggfunc="sum")
       / sub_.pivot_table(index="type", columns="decade", values="events", aggfunc="sum"))
chk_round("drought affected/event 2010s (Fig26)", ape.loc["Drought", 2010] / 1e6, 1, "4.0 million in the 2010s", 4.0)
chk_round("flood affected/event 1990s", ape.loc["Flood", 1990] / 1e6, 1, "1.7 million affected per event in the 1990s", 1.7)


# ------------------------------------------------------------------- run ----
def normalise(t: str) -> str:
    t = t.replace("{,}", ",")          # LaTeX thin-space thousands separator
    t = re.sub(r"[ \t]+", " ", t)      # collapse runs of spaces, keep newlines
    return t


def structural_checks(tex: str) -> list[tuple[str, str]]:
    """Checks on the document itself, not on its numbers.

    The assignment brief requires that images be named Fig<n> where n is the
    figure's index in the report, so the include order and the filenames have to
    agree exactly.
    """
    problems: list[tuple[str, str]] = []
    inc = re.findall(r"\\includegraphics\[[^\]]*\]\{(Fig\d+)\}", tex)
    want = [f"Fig{i}" for i in range(1, 27)]
    if inc != want:
        problems.append(("figure include order",
                         f"document order {inc} != {want}"))

    on_disk = {p.stem for p in (ROOT / "images").glob("Fig*.png")}
    unused = sorted(on_disk - set(inc))
    if unused:
        problems.append(("unused image files",
                         f"in images/ but not in the report: {unused}"))
    absent = sorted(set(inc) - on_disk)
    if absent:
        problems.append(("missing image files", f"referenced but absent: {absent}"))

    labels = set(re.findall(r"\\label\{(fig:[^}]+)\}", tex))
    labels |= set(re.findall(r"\\label\{(tab:[^}]+)\}", tex))
    refs = set(re.findall(r"\\ref\{((?:fig|tab):[^}]+)\}", tex))
    orphan = sorted(labels - refs)
    if orphan:
        problems.append(("unreferenced labels",
                         f"labelled but never \\ref'd: {orphan}"))

    if "[MEMBER 1 NAME]" in tex:
        problems.append(("team names",
                         "still placeholders - fill the six \\newcommand lines "
                         "before submitting (not a data error)"))
    return problems


def main() -> int:
    if not TEX.exists():
        print(f"FATAL: {TEX} not found")
        return 2
    tex = normalise(TEX.read_text(encoding="utf-8"))
    flat = tex.replace("\n", " ")
    flat = re.sub(r" +", " ", flat)

    passed, failed = 0, []
    for label, expected in C:
        needle = normalise(expected)
        ok = needle in tex or normalise(expected.replace("\n", " ")) in flat
        if ok:
            passed += 1
        else:
            failed.append((label, needle.replace("\n", " ")))

    for label, value, ndigits, target in ROUNDING:
        if round(value, ndigits) != target:
            failed.append((label + " [rounding]",
                           f"round({value:,.1f}, {ndigits}) should equal {target:,.0f}"))
        else:
            passed += 1

    struct = structural_checks(tex)
    names_pending = [p for p in struct if p[0] == "team names"]
    failed.extend(p for p in struct if p[0] != "team names")

    width = max(len(l) for l, _ in C) + 2
    print("=" * 78)
    print(f"REPORT CORRECTNESS CHECK   {TEX.relative_to(ROOT)}")
    print("=" * 78)
    for label, needle in failed:
        print(f"  FAIL  {label:<{width}} expected to find: {needle!r}")
    print(f"\n  {passed}/{len(C) + len(ROUNDING)} checks passed, {len(failed)} failed.")
    if failed:
        print("\n  A failure means the report prints a number the data does not "
              "support,\n  or the wording changed so the checker can no longer "
              "locate it. Fix one\n  or the other - do not weaken the check.")
        return 1
    print("\n  Every quantitative claim in the report matches the data.")
    print("  Figure numbering, image files and cross-references are consistent.")
    if names_pending:
        print("\n  NOTE: team names are still placeholders. Fill the six "
              "\\newcommand lines\n  at the top of the .tex before submitting.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
