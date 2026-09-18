"""
DAS732 A1 - verification harness, part 2.

Second pass of the fact checks: sub-group composition, the costliest
single records, reporting completeness by decade, per-event trends,
the lethality grid behind Figure 16, and the country rank table.
Run by run_all.py, which saves its output to facts2_output.txt.
"""
import pandas as pd, numpy as np
from scipy import stats
from emdat_common import load
pd.set_option("display.width",200)
df=load(); P=print
P("== Biological subgroup composition =="); P(df[df.subgroup=="Biological"].type.value_counts().to_string())
P("\n== any epidemic/COVID rows? ==", df[df.type.str.contains("Epidem|Pandem|Disease",case=False,na=False)].shape[0])
P("\n== subgroup share of events ==")
sg=df.groupby("subgroup").events.sum().sort_values(ascending=False); P((sg/sg.sum()*100).round(1).to_string()); P(sg.to_string())
P("\n== top 10 costliest single rows (real 2022 USD) ==")
P(df.nlargest(10,"damage_real")[["year","country","type","subtype","events","deaths","damage_real"]]
    .assign(damage_B=lambda d:(d.damage_real/1e9).round(1)).drop(columns="damage_real").to_string(index=False))
P("\n== damage per event by era (real) ==")
for e,g in df.groupby("era"):
    P(f"  {e}: ${g.damage_real.sum()/g.events.sum()/1e6:,.1f}M/event  (reported-damage rows only: ${g.damage_real.sum()/g.loc[g.has_damage,'events'].sum()/1e6:,.1f}M)")
P("\n== reporting completeness by decade (% rows with a deaths / damage figure) ==")
rc=df.groupby("decade").agg(pct_deaths=("has_deaths","mean"),pct_damage=("has_damage","mean"),rows=("events","size"))
P((rc.assign(pct_deaths=lambda d:(d.pct_deaths*100).round(1),pct_damage=lambda d:(d.pct_damage*100).round(1))).to_string())
P("\n== deaths by decade x subgroup (thousands) ==")
P((df.pivot_table(index="decade",columns="subgroup",values="deaths",aggfunc="sum").fillna(0)/1e3).round(1).to_string())
P("\n== affected per event, trend 1970-2022 ==")
ann=df[df.year>=1970].groupby("year").agg(a=("affected","sum"),e=("events","sum"),d=("deaths","sum"),dm=("damage_real","sum"))
for lbl,ser in [("affected/event",ann.a/ann.e),("deaths/event",ann.d/ann.e),("damage/event",ann.dm/ann.e)]:
    y=np.log10(ser.replace(0,np.nan)).dropna(); r=stats.linregress(y.index.values,y.values)
    P(f"  log10({lbl:14s}) slope/decade {r.slope*10:+.3f} dex (x{10**(r.slope*10):.2f})  p={r.pvalue:.2g} R2={r.rvalue**2:.2f}")
P("\n== lethality heatmap: deaths per event, type x decade (top 6 types, 1950+) ==")
top6=df.groupby("type").events.sum().nlargest(6).index.tolist(); P(top6)
h=df[df.type.isin(top6)&(df.year>=1950)].pivot_table(index="type",columns="decade",values="deaths",aggfunc="sum")
e=df[df.type.isin(top6)&(df.year>=1950)].pivot_table(index="type",columns="decade",values="events",aggfunc="sum")
P((h/e).round(0).to_string())
P("\n== top 15 countries: rank differences ==")
c=df.groupby("country").agg(events=("events","sum"),deaths=("deaths","sum"),affected=("affected","sum"),damage=("damage_real","sum"))
for m in ["events","deaths","affected","damage"]: c[m+"_rk"]=c[m].rank(ascending=False,method="min")
P(c.nlargest(15,"events")[["events_rk","deaths_rk","affected_rk","damage_rk"]].astype(int).to_string())
P("\n  USA: deaths rank",int(c.loc['United States of America (the)','deaths_rk']),"deaths",f"{c.loc['United States of America (the)','deaths']:,.0f}",
  "| damage rank",int(c.loc['United States of America (the)','damage_rk']))
P("  Haiti: events",int(c.loc['Haiti','events']),"deaths",f"{c.loc['Haiti','deaths']:,.0f}","deaths/event",f"{c.loc['Haiti','deaths']/c.loc['Haiti','events']:,.0f}")
P("\n== deaths per event, top-20-by-events countries ==")
t20=c.nlargest(20,"events").assign(dpe=lambda d:(d.deaths/d.events)).sort_values("dpe",ascending=False)
P(t20[["events","deaths","dpe"]].round(0).to_string())
P("\n== ISO sanity for choropleth ==", df.iso.str.len().value_counts().to_dict())
