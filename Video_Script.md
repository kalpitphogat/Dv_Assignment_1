# Video demo script — 5:00 maximum

> **The deck is built:** `slides/DAS732_A1_Video_Demo.pptx` — 18 slides, one per
> beat of this script. Every slide carries its timecode and its lines in the
> **speaker notes**, so run it in PowerPoint's Presenter View while recording and
> read off the second screen.

The brief: *"crisp and at most 5 minutes long, where each member explains their
task, visualization solutions, and inferences. The first minute can be used by the
team leader or the data processing contributor to mention the preprocessing."*

**Budget:** 0:00–1:00 Lakshya (hook + preprocessing) · 1:00–2:15 Lakshya (Task A) ·
2:15–3:30 Arnav (Task B) · 3:30–4:45 Kalpit (Task C) · 4:45–5:00 close.

**How to use this.** It's written to be *said*, not read out. Don't memorise it
word for word — get the numbers right and let the sentences come out however they
come out. The bold bits are the ones that actually have to land. Where you see
`[...]` that's a beat, not a word.

---

## 0:00–0:20 — Hook (Lakshya)

*Slide 1 — title.*

> "Hi, we're Lakshya, Arnav and Kalpit.
>
> So everyone kind of assumes natural disasters are getting worse every year. We
> took EM-DAT — that's a hundred and twenty-three years of disaster records,
> two hundred and twenty-five countries, about **fifteen thousand events** — and
> we asked one question. **Has it actually got worse? And are we getting any
> better at surviving it?**
>
> Short answer, yes to both. But the two halves don't fit together the way you'd
> think."

## 0:20–1:00 — Preprocessing (Lakshya)

*Slides 2–3.*

> "Before we could plot anything, four things had to be fixed.
>
> One: the file is semicolon-separated and uses commas as decimal points. So if
> you just open it normally, every number comes in as text.
>
> Two: it's a snapshot from April 2023, so 2023 is only a part-year. We dropped
> those fifty-one rows — otherwise every trend line falls off a cliff right at
> the end.
>
> Three: some of the hazard labels have a trailing space. So 'Extreme
> temperature' was quietly being counted as two different categories.
>
> And four: we didn't just assume the adjusted damage column was
> inflation-adjusted, we checked it. It's the raw figure times a hundred over
> CPI, and CPI is exactly a hundred in 2022.
>
> One more thing, and this one actually matters. **Where a value was missing, we
> left it missing — we never filled it with zero.** If you treat 'not reported'
> as 'nobody died', every old decade suddenly looks way safer than it was."

## 1:00–2:15 — Task Set A: *When?* (Lakshya)

*Slides 4–8.*

> **[Slide 5 — Fig 4]** "Okay. Events per year. Looks like an explosion after
> 1970, right? That's where we nearly went wrong.
>
> **[Slide 6 — Fig 5]** Because look at this. **Ninety-one percent of the whole
> record sits in forty-three percent of the years.** And damage reporting never
> covers more than about half the records in any decade. So this count is
> measuring how well people wrote things down, as much as it's measuring actual
> disasters. From here on, we use rates — not counts.
>
> **[Slide 7 — Fig 6]** And this is the finding. Top panel is total deaths —
> peaks in the 1920s, five point two million. But look at the bottom panel.
> Deaths *per event*. It goes from about **twenty thousand** down to about **a
> hundred and thirty**. That's a ninety-nine point four percent drop. [...]
> Quick note — two separate panels, not one chart with two y-axes. With a twin
> axis you get to pick where the lines cross, and that's not honest.
>
> **[Slide 8 — Fig 7]** Then we tried to break our own result. Take out just the
> three worst records from each decade — and the decline completely vanishes.
> The 2000s actually sit *above* the 1900s. So that big fall in total deaths is
> mostly the giant disasters disappearing, things like the 1931 China flood.
> It's not that ordinary disasters got safer. **The per-event number is the one
> that holds up.**
>
> Arnav, over to you."

## 2:15–3:30 — Task Set B: *Where?* (Arnav)

*Slides 9–12. **Do the map switch live in Tableau** — this is the bit the rubric
is explicitly looking for.*

> **[Slide 9 — Figs 8 & 9]** "Thanks. So — this is where disasters actually get
> recorded. And it's basically everywhere. All two hundred and twenty-five
> countries.
>
> Now watch what happens when I switch the exact same map over to deaths.
> **[SWITCH]** It collapses onto two countries. **China and India together are
> sixty-eight percent of all twenty-two point nine million deaths.**
>
> **[Slide 10 — Fig 10]** Same idea as four separate rankings — and they barely
> overlap. The US is **number one** for how many disasters it gets, and **number
> one** for money lost. And **twenty-third** for deaths. Bangladesh is the
> mirror image: third for deaths, twenty-third for damage. Basically, if a
> country is rich, disasters cost it money instead of lives.
>
> **[Slide 11 — Fig 11]** This just puts a number on it. **Two countries** get
> you to half of all deaths. It takes **twenty** to get to half of all disasters.
>
> **[Slide 12 — Fig 12]** And this is the one that changed how we read the whole
> dataset. These are the twenty most disaster-hit countries — so they're all
> heavily exposed, roughly comparable. And the death rate still varies by a
> factor of a **thousand**. China's at eleven thousand deaths per event.
> Australia's at eleven.
>
> Two honest caveats — there's no population data in this file, and China's
> number is pulled up by the old famines. But even allowing for both, that gap is
> far too big to be about the hazards. **That's vulnerability.**
>
> Kalpit."

## 3:30–4:45 — Task Set C: *What?* (Kalpit)

*Slides 13–17.*

> **[Slide 13 — Fig 13]** "Thanks. If I could keep one chart from this whole
> project, it'd be this one. Four bars, same seven hazards, same order every
> time. [...] **Drought is five percent of events. And fifty-one percent of
> deaths.** Storms are the exact opposite — thirty-one percent of events,
> forty-two percent of the money, six percent of the deaths. So what a hazard's
> share of disasters tells you about its share of harm is basically nothing.
>
> **[Slide 14 — Fig 14]** Here's each hazard placed by how deadly and how
> expensive a typical one is. Drought's out on its own on the right. Wildfire is
> the opposite corner — expensive, but a typical one kills seven people.
>
> **[Slide 15 — Fig 15]** Money over time, all in 2022 dollars. The 2010s cost
> **two point zero seven trillion** — that's a record. And damage reporting
> doesn't get better after 1970, so that rise isn't just better record-keeping.
>
> **[Slide 16 — Fig 16]** But the improvement isn't even. Drought went from
> twenty-nine thousand deaths per event down to fifty-three. Floods and storms
> dropped too — and those are all things you get warning about. Earthquakes,
> which you don't get warning about, didn't improve at all. **And heatwaves went
> the wrong way** — a hundred and twenty-five in the sixties, twelve hundred in
> the 2020s.
>
> **[Slide 17 — Fig 17]** Last one. Since 1970: disasters, damage, people
> affected — all clearly rising. Deaths? No significant trend at all, p is
> 0.064. And the correlation between deaths and damage is basically zero. **They
> have completely come apart.**"

## 4:45–5:00 — Close (any one of you)

*Slide 18.*

> "So — more exposure, less vulnerability, and a much bigger bill.
>
> We got a lot better at not dying in disasters. Just not everywhere, not at all
> for earthquakes, and with heat it's actually going backwards.
>
> Thanks for watching."

---

## Delivery notes

- **Say the numbers, don't read them.** "About twenty thousand" beats "nineteen
  thousand eight hundred and ninety-seven". The exact figures are in the report.
- **Pause before the punchline.** The two that deserve a beat: *"and fifty-one
  percent of deaths"* and *"Australia's at eleven."*
- **Don't read the slide.** The chart already has its title on it. Say the thing
  the chart *doesn't* say.
- **Hand over by name** — "Arnav, over to you" / "Kalpit". It makes the three-way
  split obvious to whoever is marking it.
- If you fluff a line, stop and retake that slide. Don't try to save it.

## Production checklist

- [x] Names and roll numbers filled in (Lakshya Jain BT2024044, Arnav Jain
      BT2024233, Kalpit BT2024093)
- [ ] Each member's signed AI disclosure attached separately, on the
      instructor's form — the brief requires one per member
- [ ] Tableau workbook published and the URL pasted into `README.md`
- [ ] Each member records their own segment — the brief requires it
- [ ] At least one **live Tableau interaction** on camera (the Fig 8 → Fig 9 map
      switch is the natural one); the rubric names "Tableau demo" explicitly
- [ ] Run it once with a timer before recording — **5:00 is a hard ceiling**
- [ ] Export at 1080p, check the audio before uploading
