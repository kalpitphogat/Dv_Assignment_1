# Video demo script — 5:00 maximum

The brief: *"crisp and at most 5 minutes long, where each member explains their
task, visualization solutions, and inferences. The first minute can be used by the
team leader or the data processing contributor to mention the preprocessing."*

Budget: **0:00–1:00 preprocessing · 1:00–2:15 Member 1 · 2:15–3:30 Member 2 ·
3:30–4:45 Member 3 · 4:45–5:00 close.** Rehearse with a timer — going over is a
straightforward mark loss.

---

## 0:00–0:20 — Hook and question (Member 1)

> "Everyone believes natural disasters are getting worse. We took EM-DAT — 123
> years, 225 countries, 15,015 recorded events — and asked one question:
> **has the burden actually grown, and are we getting better at surviving it?**
> The answer turned out to be yes to both, and the two halves don't fit together
> the way you'd expect."

*On screen: title slide with the guiding question.*

## 0:20–1:00 — Preprocessing (Member 1)

*On screen: the raw CSV in a text editor, then the cleaned extract.*

> "Four things had to be fixed before any chart. One — the file is
> semicolon-separated with commas as decimal points, so read naively every number
> arrives as text. Two — it's a snapshot from April 2023, so 2023 is a part-year;
> we dropped those 51 rows or every trend would fake a collapse at the end.
> Three — some hazard type labels carry a trailing space, which silently splits
> 'Extreme temperature' into two categories. Four — we verified rather than
> assumed that the adjusted damage column is constant 2022 dollars: it's the
> nominal figure times 100 over CPI, and CPI is exactly 100 in 2022.
> Critically, we left missing impact values as missing, never zero — treating
> 'not reported' as 'nobody died' would have flattered every historical decade."

## 1:00–2:15 — Task Set A: *When?* (Member 1)

*On screen: Fig 4 → Fig 5 → Fig 6 → Fig 7.*

> "**Figure 4.** Events per year. It looks like an explosion after 1970 — and
> that's where we nearly went wrong. **Figure 5** is the check: 91% of the whole
> record sits in 43% of the years, and damage reporting covers at most
> half the records. So the count measures reporting as much as hazard. Everything
> after this uses rates, not counts.
>
> **Figure 6** is the finding. Total deaths peaked in the 1920s at 5.2 million.
> But look at panel b — deaths *per recorded event* fell from about nineteen
> nine hundred to a hundred and twenty-nine. A 99.4% fall. Note we used two
> panels, not a twin axis, because a twin axis lets you pick the crossing point.
>
> **Figure 7** is us trying to break our own result. Strip each decade's three
> deadliest records and the decline disappears entirely — the 2000s sit *above*
> the 1900s. So the century-scale fall in total deaths is mostly the
> disappearance of mega-catastrophes like the 1931 China flood, not a broad
> improvement. The per-event improvement is the robust claim."

## 2:15–3:30 — Task Set B: *Where?* (Member 2)

*On screen: Fig 8 → Fig 9 → Fig 10 → Fig 11 → Fig 12. **Do the map switch live in
Tableau** — it is the strongest moment in the demo.*

> "**Figure 8**, where disasters are recorded — all 225 countries appear, fairly
> evenly shaded. Now watch what happens when I switch the same map to deaths.
> **[switch]** **Figure 9.** It collapses onto two countries. China and India
> alone are 68% of all 22.9 million recorded deaths.
>
> **Figure 10** ranks countries on four measures and the leaderboards barely
> overlap. The United States is first for events *and* first for damage — and
> 23rd for deaths. Bangladesh is 3rd for deaths and 23rd for damage.
>
> **Figure 11** quantifies it: two countries reach half of all deaths, but it takes
> twenty to reach half of all *events*.
>
> **Figure 12** is the one that changed how we read the dataset. Take the twenty
> most disaster-prone countries — so exposure is roughly held constant — and
> lethality still spans a factor of a thousand. China at 11,139 deaths per event,
> Australia at 11. That gap isn't hazard. It's vulnerability."

## 3:30–4:45 — Task Set C: *What?* (Member 3)

*On screen: Fig 13 → Fig 14 → Fig 15 → Fig 16 → Fig 17.*

> "**Figure 13** is the chart I'd keep if I could keep one. Four bars, same seven
> hazards, same order. Drought is five percent of events — and fifty-one percent
> of deaths. Storms are the mirror image: 31% of events, 42% of the money, six
> percent of the deaths. A hazard's share of disasters tells you almost nothing
> about its share of harm.
>
> **Figure 14** places each hazard in a deadliness–cost plane. Drought sits alone
> on the right. Wildfire is the opposite corner: expensive, but a median of seven
> deaths.
>
> **Figure 15** — real damage, inflation-adjusted. The 2010s cost $2.07 trillion,
> a record. And damage reporting doesn't improve after 1970, so that rise isn't a
> reporting artefact.
>
> **Figure 16** shows the improvement is uneven. Drought fell from 29,000 deaths
> per event to 53. Floods and storms collapsed too. Earthquakes — which give no
> warning — didn't improve at all. And extreme temperature went the *wrong* way:
> 125 in the 1960s, 1,202 in the 2020s.
>
> **Figure 17** closes it. Since 1970, events, damage and people affected all rise
> significantly. Annual deaths show no significant trend at all — p is 0.064 — and
> the rank correlation between deaths and damage is minus 0.01. Costs and
> mortality have decoupled completely."

## 4:45–5:00 — Close (any member)

> "So: exposure up, vulnerability down, and the bill rising. The world got
> dramatically better at not dying in disasters — unevenly, not at all for
> earthquakes, and going backwards for heat. Thank you."

---

## Production checklist

- [x] Names and roll numbers are already filled in (Lakshya Jain BT2024044,
      Arnav Jain BT2024233, Kalpit BT2024093)
- [ ] Each member's signed AI declaration attached separately, on the
      instructor's form — the brief requires one per member
- [ ] Tableau workbook published and the URL pasted into `README.md`
- [ ] Each member records their own segment — the brief requires it
- [ ] At least one **live Tableau interaction** on camera (the Fig 8 → Fig 9 map
      switch is the natural one); the rubric names "Tableau demo" explicitly
- [ ] Slides used for the question, the preprocessing summary and the close;
      Tableau/figures for everything else
- [ ] Run to time — **5:00 is a hard ceiling**
- [ ] Export at 1080p, check the audio before uploading
