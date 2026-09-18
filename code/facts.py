"""Verification harness: every quantitative claim in the report is produced here."""
import pandas as pd, numpy as np
from emdat_common import load, load_raw
pd.set_option("display.width", 200)

raw = load_raw(); df = load()
P = print
P("="*78); P("DATASET SHAPE")
P(f"raw rows={len(raw):,}  clean rows={len(df):,}  dropped(2023 partial)={len(raw)-len(df)}")
P("2023 rows in raw:", (raw.Year==2023).sum(), "| CPI null in raw:", raw.CPI.isna().sum(),
  "| all 2023 have null CPI:", raw.loc[raw.Year==2023,'CPI'].isna().all())
P("years:", df.year.min(), "-", df.year.max(), "| countries:", df.country.nunique(),
  "| ISO:", df.iso.nunique(), "| types:", df.type.nunique(), "| subtypes:", df.subtype.nunique(),
  "| subgroups:", df.subgroup.nunique(), "| groups:", df.group.unique().tolist())
P("total events recorded:", f"{df.events.sum():,}")

P("\n"+"="*78); P("MISSINGNESS (clean)")
for c in ["deaths","affected","damage_real","damage_nominal","cpi"]:
    P(f"  {c:16s} missing {df[c].isna().sum():6,} / {len(df):,}  ({df[c].isna().mean()*100:5.1f}%)")

P("\n"+"="*78); P("CPI / ADJUSTMENT SANITY")
s = df.dropna(subset=["damage_real","damage_nominal","cpi"])
ratio = s.damage_real/s.damage_nominal
implied = 100/s.cpi
P("  adjusted>=nominal in", f"{(ratio>=0.999).mean()*100:.1f}% of rows")
P("  max |real/nominal - 100/cpi| =", f"{(ratio-implied).abs().max():.4g}  -> adjusted = nominal * 100/CPI (constant 2022 USD)")
P("  CPI range:", f"{df.cpi.min():.3f} - {df.cpi.max():.3f}; CPI in 2022 =", df.loc[df.year==2022,'cpi'].unique())

P("\n"+"="*78); P("HEADLINE TOTALS (1900-2022)")
P(f"  total deaths      {df.deaths.sum():,.0f}")
P(f"  total affected    {df.affected.sum():,.0f}")
P(f"  damage nominal    ${df.damage_nominal.sum()/1e12:,.2f} T")
P(f"  damage real(2022) ${df.damage_real.sum()/1e12:,.2f} T")

P("\n"+"="*78); P("A) DECADAL TABLE")
dec = df.groupby("decade").agg(events=("events","sum"), deaths=("deaths","sum"),
        affected=("affected","sum"), damage=("damage_real","sum"), rows=("events","size"))
dec["deaths_per_event"] = dec.deaths/dec.events
dec["affected_per_event"] = dec.affected/dec.events
P(dec.to_string(float_format=lambda v: f"{v:,.1f}"))
P("\n  events 1900s:", int(dec.loc[1900,'events']), " 2000s:", int(dec.loc[2000,'events']),
  " 2010s:", int(dec.loc[2010,'events']), " ratio 2000s/1900s:", f"{dec.loc[2000,'events']/dec.loc[1900,'events']:.1f}x")
P("  peak events decade:", dec.events.idxmax(), int(dec.events.max()))
P("  peak deaths decade:", dec.deaths.idxmax(), f"{dec.deaths.max():,.0f}")
P("  deaths/event 1900s:", f"{dec.loc[1900,'deaths_per_event']:,.0f}",
  " 2010s:", f"{dec.loc[2010,'deaths_per_event']:,.0f}",
  " decline:", f"{(1-dec.loc[2010,'deaths_per_event']/dec.loc[1900,'deaths_per_event'])*100:.1f}%")

P("\n  --- deaths per decade excluding the 3 largest single rows per decade (robustness) ---")
def trimmed(g):
    g = g.dropna(subset=["deaths"]).sort_values("deaths", ascending=False)
    return g.iloc[3:].deaths.sum()
tr = df.groupby("decade", group_keys=False).apply(trimmed, include_groups=False)
P((tr/1e3).round(1).to_string())

P("\n"+"="*78); P("A) TOP 10 SINGLE ROWS BY DEATHS")
P(df.nlargest(10,"deaths")[["year","country","type","subtype","events","deaths","affected"]].to_string(index=False))

P("\n"+"="*78); P("A) EVENT COUNT BY SUBGROUP PER ERA")
pv = df.pivot_table(index="era", columns="subgroup", values="events", aggfunc="sum").fillna(0)
P(pv.to_string(float_format=lambda v: f"{v:,.0f}"))
P("\n  share of ALL recorded events occurring 1970-2022:",
  f"{df.loc[df.era=='1970-2022','events'].sum()/df.events.sum()*100:.1f}%")
P("  share of years 1970-2022 out of window:", f"{53/123*100:.1f}%")

P("\n"+"="*78); P("B) COUNTRY LEADERBOARDS")
c = df.groupby(["country","iso"]).agg(events=("events","sum"), deaths=("deaths","sum"),
        affected=("affected","sum"), damage=("damage_real","sum")).reset_index()
for m in ["events","deaths","affected","damage"]:
    P(f"\n  top 10 by {m}:")
    P(c.nlargest(10,m)[["country",m]].to_string(index=False,
        float_format=lambda v: f"{v:,.0f}"))
P("\n  concentration (share of global total held by top-N countries):")
for m in ["events","deaths","affected","damage"]:
    s = c[m].sort_values(ascending=False); tot = s.sum()
    P(f"    {m:9s} top5 {s.head(5).sum()/tot*100:5.1f}%  top10 {s.head(10).sum()/tot*100:5.1f}%  "
      f"top20 {s.head(20).sum()/tot*100:5.1f}%  (n countries with any = {(s>0).sum()})")
P("\n  countries needed to reach 50% of global:", end=" ")
for m in ["events","deaths","affected","damage"]:
    s = c[m].sort_values(ascending=False); k = int((s.cumsum()/s.sum()<0.5).sum())+1
    P(f"{m}={k}", end="  ")
P()
P("\n  historical states present:", df.loc[df.is_historical_state,'country'].unique().tolist())

P("\n"+"="*78); P("B) DOMINANT DISASTER TYPE PER COUNTRY (countries with >=20 events)")
ct = df.groupby(["country","type"])["events"].sum().reset_index()
tot = ct.groupby("country")["events"].sum()
big = tot[tot>=20].index
dom = ct[ct.country.isin(big)].sort_values("events",ascending=False).groupby("country").first()
P(dom.type.value_counts().to_string())
P("  n countries with >=20 events:", len(big))

P("\n"+"="*78); P("C) IMPACT PROFILE BY DISASTER TYPE")
t = df.groupby("type").agg(events=("events","sum"), rows=("events","size"),
        deaths=("deaths","sum"), affected=("affected","sum"), damage=("damage_real","sum"),
        med_deaths=("deaths","median"), med_damage=("damage_real","median")).sort_values("events",ascending=False)
t["deaths_per_event"] = t.deaths/t.events
t["affected_per_event"] = t.affected/t.events
t["damage_per_event_M"] = t.damage/t.events/1e6
t["pct_of_events"] = t.events/t.events.sum()*100
t["pct_of_deaths"] = t.deaths/t.deaths.sum()*100
t["pct_of_affected"] = t.affected/t.affected.sum()*100
t["pct_of_damage"] = t.damage/t.damage.sum()*100
P(t.to_string(float_format=lambda v: f"{v:,.1f}"))

P("\n"+"="*78); P("C) DAMAGE OVER TIME (real, 2022 USD, by decade & subgroup, $B)")
dsg = df.pivot_table(index="decade", columns="subgroup", values="damage_real", aggfunc="sum").fillna(0)/1e9
P(dsg.to_string(float_format=lambda v: f"{v:,.1f}"))

P("\n"+"="*78); P("C) DECOUPLING CHECK 1970-2022 (annual series)")
ann = df[df.year>=1970].groupby("year").agg(deaths=("deaths","sum"), damage=("damage_real","sum"),
        events=("events","sum"), affected=("affected","sum"))
from scipy import stats
for m in ["deaths","damage","events","affected"]:
    y = np.log10(ann[m].replace(0,np.nan)).dropna()
    r = stats.linregress(y.index.values, y.values)
    P(f"  log10({m:9s}) ~ year: slope/decade = {r.slope*10:+.3f} dex  (x{10**(r.slope*10):.2f}/decade)  p={r.pvalue:.2g}  R2={r.rvalue**2:.2f}")
P("\n  Spearman deaths vs damage (1970-2022 annual):",
  f"{stats.spearmanr(ann.deaths, ann.damage).statistic:+.3f}")
P("  median annual deaths 1970-1989:", f"{ann.loc[1970:1989,'deaths'].median():,.0f}",
  "| 2003-2022:", f"{ann.loc[2003:2022,'deaths'].median():,.0f}")
P("  median annual damage  1970-1989: $", f"{ann.loc[1970:1989,'damage'].median()/1e9:,.1f}B",
  "| 2003-2022: $", f"{ann.loc[2003:2022,'damage'].median()/1e9:,.1f}B")
