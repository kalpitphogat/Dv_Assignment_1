/**
 * DAS732 A1 - build the video-demo deck.
 *
 *     node make_slides.js
 *
 * Writes ../slides/DAS732_A1_Video_Demo.pptx: 18 slides timed to the 5-minute
 * script in Video_Script.md, with the exact spoken line and its timecode in each
 * slide's speaker notes.
 *
 * Palette and typography deliberately match the LaTeX report, so the deck, the
 * figures and the report read as one piece of work.
 */
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const ROOT = path.resolve(__dirname, "..");
const IMG = path.join(ROOT, "images");
const OUT_DIR = path.join(ROOT, "slides");
const OUT = path.join(OUT_DIR, "DAS732_A1_Video_Demo.pptx");
fs.mkdirSync(OUT_DIR, { recursive: true });

// ----------------------------------------------------------------- palette --
const NAVY = "10243E";   // dark slides: title + closing
const INK = "0B0B0B";
const INK2 = "52514E";
const MUTED = "8A8985";
const SURF = "FCFCFB";   // light slide background, same as the figures
const PANEL = "F4F3EF";
const RULE = "E3E2DE";
const BLUE = "2A78D6";   // report series 1
const ORANGE = "EB6834"; // report series 2
const GOLD = "EDA100";   // report series 4
const WHITE = "FFFFFF";

const H_FONT = "Calibri";
const B_FONT = "Calibri";

// Speaker chip colours - the deck's one repeated motif.
const WHO = {
  L: { name: "Lakshya Jain", color: BLUE },
  A: { name: "Arnav Jain", color: ORANGE },
  K: { name: "Kalpit", color: GOLD },
  ALL: { name: "All three", color: INK2 },
};

// ------------------------------------------------------- image dimensions --
/** Read width/height straight out of the PNG IHDR chunk - no dependency. */
function pngSize(file) {
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}
const ASPECT = {};
for (let n = 1; n <= 17; n++) {
  const f = path.join(IMG, `Fig${n}.png`);
  const { w, h } = pngSize(f);
  ASPECT[n] = w / h;
}

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";         // 10" x 5.625" - set BEFORE adding slides
pres.author = "Lakshya Jain, Arnav Jain, Kalpit";
pres.title = "DAS732 A1 - A Century of Natural Disasters";

const W = 10, H = 5.625, M = 0.5;

// --------------------------------------------------------------- helpers ---
function chip(slide, who) {
  // Dark pill + a colour dot for identity. White on the orange or gold series
  // colour is only ~3:1, which is below the threshold for 11pt text, so the
  // fill stays dark and the member's colour is carried by the dot instead.
  const p = WHO[who];
  const x = W - M - 2.05, y = H - 0.72;
  slide.addShape(pres.ShapeType.roundRect, {
    x, y, w: 2.05, h: 0.34,
    fill: { color: NAVY }, line: { color: NAVY }, rectRadius: 0.17,
  });
  slide.addShape(pres.ShapeType.ellipse, {
    x: x + 0.17, y: y + 0.11, w: 0.13, h: 0.13,
    fill: { color: p.color }, line: { color: p.color },
  });
  slide.addText(p.name, {
    x: x + 0.36, y, w: 1.55, h: 0.34, isTextBox: true,
    align: "left", valign: "middle", margin: 0,
    fontFace: B_FONT, fontSize: 11, bold: true, color: WHITE,
  });
}

function title(slide, text, sub) {
  slide.addText(text, {
    x: M, y: 0.26, w: W - 2 * M, h: 0.64, isTextBox: true,
    margin: 0, valign: "middle",
    fontFace: H_FONT, fontSize: 25, bold: true, color: INK,
  });
  if (sub) {
    slide.addText(sub, {
      x: M, y: 0.90, w: W - 2 * M, h: 0.34, isTextBox: true,
      margin: 0, valign: "middle",
      fontFace: B_FONT, fontSize: 13, color: INK2,
    });
  }
}

/** Place Fig<n> centred inside a box, preserving its aspect ratio. */
function figure(slide, n, box) {
  const a = ASPECT[n];
  let w = box.w, h = w / a;
  if (h > box.h) { h = box.h; w = h * a; }
  slide.addImage({
    path: path.join(IMG, `Fig${n}.png`),
    x: box.x + (box.w - w) / 2, y: box.y + (box.h - h) / 2, w, h,
  });
}

function takeaway(slide, text) {
  slide.addText(text, {
    x: M, y: H - 0.72, w: W - 2 * M - 2.25, h: 0.36, isTextBox: true,
    margin: 0,
    valign: "middle", fontFace: B_FONT, fontSize: 13, italic: true,
    color: INK2,
  });
}

/**
 * A figure slide. No big slide title: every chart already carries its own
 * headline and subtitle, so repeating them here wasted the space the chart
 * needs to stay readable on video. Instead a compact task label ties the slide
 * back to the report's task numbering, and the chart gets the rest.
 */
function figSlide({ n, task, who, head, take, notes }) {
  const s = pres.addSlide();
  s.background = { color: SURF };
  s.addText([
    { text: task, options: { bold: true, color: INK } },
    { text: "   " + head, options: { color: INK2 } },
  ], {
    x: M, y: 0.22, w: W - 2 * M, h: 0.34, isTextBox: true, margin: 0,
    valign: "middle", fontFace: B_FONT, fontSize: 13,
  });
  chip(s, who);
  figure(s, n, { x: 0.34, y: 0.66, w: W - 0.68, h: (H - 0.80) - 0.66 });
  if (take) takeaway(s, take);
  s.addNotes(notes);
  return s;
}

// ============================================================== 1. title ===
{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addText("A Century of Natural Disasters", {
    x: M, y: 1.25, w: W - 2 * M, h: 0.75, isTextBox: true, margin: 0,
    fontFace: H_FONT, fontSize: 40, bold: true, color: WHITE,
  });
  s.addText("More events, fewer deaths, bigger bills", {
    x: M, y: 2.02, w: W - 2 * M, h: 0.5, isTextBox: true, margin: 0,
    fontFace: H_FONT, fontSize: 22, color: "CADCFC",
  });
  s.addText("Visual exploration of the EM-DAT Emergency Events Database, 1900-2022",
    { x: M, y: 2.62, w: W - 2 * M, h: 0.34, isTextBox: true, margin: 0,
      fontFace: B_FONT, fontSize: 13, color: "9FB3CC" });

  const team = [
    ["Lakshya Jain", "BT2024044", "When?  The temporal record", BLUE],
    ["Arnav Jain", "BT2024233", "Where?  The geography of exposure", ORANGE],
    ["Kalpit", "BT2024093", "What?  The impact signature of hazards", GOLD],
  ];
  team.forEach(([nm, roll, task, col], i) => {
    const y = 3.35 + i * 0.44;
    s.addShape(pres.ShapeType.ellipse, {
      x: M, y: y + 0.07, w: 0.18, h: 0.18,
      fill: { color: col }, line: { color: col },
    });
    s.addText(`${nm}  (${roll})`, {
      x: M + 0.32, y, w: 2.9, h: 0.32, isTextBox: true, margin: 0,
      valign: "middle", fontFace: B_FONT, fontSize: 13, bold: true,
      color: WHITE,
    });
    s.addText(task, {
      x: M + 3.25, y, w: 5.6, h: 0.32, isTextBox: true, margin: 0,
      valign: "middle", fontFace: B_FONT, fontSize: 13, color: "9FB3CC",
    });
  });
  s.addText("DAS732 Data Visualization  ·  Programming Assignment 1  ·  IIIT Bangalore",
    { x: M, y: H - 0.62, w: W - 2 * M, h: 0.32, isTextBox: true, margin: 0,
      fontFace: B_FONT, fontSize: 11, color: "7C93AD" });
  s.addNotes(
    "0:00-0:20  HOOK  |  Lakshya\n\n\"Hi, we're Lakshya, Arnav and Kalpit.\n\nSo everyone kind of assumes natural disasters are getting worse every year. We took EM-DAT - that's a hundred and twenty-three years of disaster records, two hundred and twenty-five countries, about fifteen thousand events - and we asked one question. Has it actually got worse? And are we getting any better at surviving it?\n\nShort answer, yes to both. But the two halves don't fit together the way you'd think.\"");
}

// ============================================================ 2. question ===
{
  const s = pres.addSlide();
  s.background = { color: SURF };
  title(s, "One question");
  chip(s, "L");
  s.addShape(pres.ShapeType.roundRect, {
    x: M, y: 1.05, w: W - 2 * M, h: 1.05,
    fill: { color: PANEL }, line: { color: PANEL }, rectRadius: 0.06,
  });
  s.addText("Over 1900-2022, has the burden of natural disasters actually grown -\nand has the world become better or worse at surviving it?",
    { x: M + 0.35, y: 1.05, w: W - 2 * M - 0.7, h: 1.05, isTextBox: true,
      margin: 0, valign: "middle", fontFace: H_FONT, fontSize: 18, bold: true,
      color: INK, lineSpacingMultiple: 1.15 });

  s.addText("A disaster has no single cost - and the four costs do not move together.",
    { x: M, y: 2.35, w: W - 2 * M, h: 0.32, isTextBox: true, margin: 0,
      fontFace: B_FONT, fontSize: 14, color: INK2 });

  const cards = [
    ["Counted", "15,015 events", BLUE],
    ["Killed", "22.9M deaths", ORANGE],
    ["Displaced", "8.5B affected", "1BAF7A"],
    ["Cost", "$6.7T damage", GOLD],
  ];
  const cw = 2.14, gap = 0.29;
  cards.forEach(([lab, val, col], i) => {
    const x = M + i * (cw + gap);
    s.addShape(pres.ShapeType.roundRect, {
      x, y: 2.82, w: cw, h: 1.36,
      fill: { color: WHITE }, line: { color: RULE, width: 1 }, rectRadius: 0.06,
    });
    s.addShape(pres.ShapeType.ellipse, {
      x: x + 0.22, y: 3.02, w: 0.26, h: 0.26,
      fill: { color: col }, line: { color: col },
    });
    s.addText(lab, {
      x: x + 0.58, y: 2.98, w: cw - 0.75, h: 0.34, isTextBox: true, margin: 0,
      valign: "middle", fontFace: H_FONT, fontSize: 15, bold: true, color: INK,
    });
    s.addText(val, {
      x: x + 0.22, y: 3.44, w: cw - 0.44, h: 0.52, isTextBox: true, margin: 0,
      valign: "middle", fontFace: H_FONT, fontSize: 17, bold: true, color: INK,
    });
  });
  takeaway(s, "Three sub-questions, one per member - so no task is split across the team.");
  s.addNotes(
    "0:20  THE QUESTION  |  Lakshya\n\nUse this slide while you finish the hook. The four cards are the four costs - counted, killed, displaced, cost. Point at them, don't read them.");
}

// ======================================================= 3. preprocessing ===
{
  const s = pres.addSlide();
  s.background = { color: SURF };
  title(s, "Four things to fix before any chart");
  chip(s, "L");

  const items = [
    ["Semicolon-separated, comma decimals", "read naively, every number arrives as text"],
    ["2023 is a part-year", "51 rows dropped, or every trend fakes a collapse"],
    ["Trailing spaces in hazard labels", "\"Extreme temperature \" split one category in two"],
    ["Missing impacts kept as missing", "zero-filling would flatter every historical decade"],
  ];
  items.forEach(([hd, bd], i) => {
    const y = 1.22 + i * 0.86;
    s.addShape(pres.ShapeType.ellipse, {
      x: M, y: y + 0.04, w: 0.34, h: 0.34,
      fill: { color: BLUE }, line: { color: BLUE },
    });
    s.addText(String(i + 1), {
      x: M, y: y + 0.04, w: 0.34, h: 0.34, isTextBox: true, margin: 0,
      align: "center", valign: "middle", fontFace: H_FONT, fontSize: 13,
      bold: true, color: WHITE,
    });
    s.addText(hd, {
      x: M + 0.48, y, w: 4.25, h: 0.32, isTextBox: true, margin: 0,
      valign: "middle", fontFace: H_FONT, fontSize: 14, bold: true, color: INK,
    });
    s.addText(bd, {
      x: M + 0.48, y: y + 0.31, w: 4.25, h: 0.44, isTextBox: true, margin: 0,
      fontFace: B_FONT, fontSize: 11.5, color: INK2,
    });
  });

  figure(s, 2, { x: 5.42, y: 1.15, w: 4.08, h: 3.05 });
  s.addText("10,431 rows  ->  10,380 rows  ·  15,015 events  ·  225 countries",
    { x: 5.42, y: 4.28, w: 4.08, h: 0.3, isTextBox: true, margin: 0,
      align: "center", fontFace: B_FONT, fontSize: 11, bold: true, color: INK2 });
  takeaway(s, "One cleaning module feeds all 15 charts, so no two figures can disagree.");
  s.addNotes(
    "0:20-1:00  PREPROCESSING  |  Lakshya  (the brief allows the first minute for this)\n\n\"Before we could plot anything, four things had to be fixed.\n\nOne: the file is semicolon-separated and uses commas as decimal points. So if you just open it normally, every number comes in as text.\n\nTwo: it's a snapshot from April 2023, so 2023 is only a part-year. We dropped those fifty-one rows - otherwise every trend line falls off a cliff right at the end.\n\nThree: some of the hazard labels have a trailing space. So 'Extreme temperature' was quietly being counted as two different categories.\n\nAnd four: we didn't just assume the adjusted damage column was inflation-adjusted, we checked it. It's the raw figure times a hundred over CPI, and CPI is exactly a hundred in 2022.\n\nOne more thing, and this one actually matters. Where a value was missing, we left it missing - we never filled it with zero. If you treat 'not reported' as 'nobody died', every old decade suddenly looks way safer than it was.\"");
}

// =========================================================== 4. task map ===
{
  const s = pres.addSlide();
  s.background = { color: SURF };
  title(s, "One question, three owned task sets, fifteen charts");
  chip(s, "ALL");
  figure(s, 1, { x: M, y: 1.02, w: W - 2 * M, h: 3.85 });
  s.addNotes(
    "1:00  THE SPLIT  |  Lakshya\n\n\"We split it three ways - when, where and what. We each own one question the whole way through: our own charts, our own conclusions.\"");
}

// ======================================================= 5-8. Task Set A ===
figSlide({
  n: 4, task: "A1.2  Trend", who: "L",
  head: "The record explodes after 1970",
  take: "That shape is also exactly what a step-change in data collection looks like.",
  notes:
    "1:00-1:15  TASK A1.2  |  Lakshya\n\n\"Okay. Events per year. Looks like an explosion after 1970, right? That's where we nearly went wrong.\"",
});

figSlide({
  n: 5, task: "A1.3  Identify", who: "L",
  head: "...but it is partly a count of reporting",
  take: "91% of the record sits in 43% of the years. So we use rates, not counts, from here on.",
  notes:
    "1:15-1:35  TASK A1.3  |  Lakshya\n\n\"Because look at this. Ninety-one percent of the whole record sits in forty-three percent of the years. And damage reporting never covers more than about half the records in any decade.\n\nSo this count is measuring how well people wrote things down, as much as it's measuring actual disasters. From here on, we use rates - not counts.\"",
});

figSlide({
  n: 6, task: "A1.4  Compare", who: "L",
  head: "Deaths per recorded event fell 99.4%",
  take: "Two panels, never a twin axis - a twin axis lets the author pick the crossing point.",
  notes:
    "1:35-1:55  TASK A1.4  |  Lakshya  --  the headline finding\n\n\"And this is the finding. Top panel is total deaths - peaks in the 1920s, five point two million. But look at the bottom panel. Deaths per event. It goes from about twenty thousand down to about a hundred and thirty. That's a ninety-nine point four percent drop.\n\n[beat]\n\nQuick note - two separate panels, not one chart with two y-axes. With a twin axis you get to pick where the lines cross, and that's not honest.\"",
});

figSlide({
  n: 7, task: "A1.5  Validate", who: "L",
  head: "Then we tried to break our own finding",
  take: "Strip each decade's three deadliest records and the decline vanishes entirely.",
  notes:
    "1:55-2:15  TASK A1.5  |  Lakshya  --  do NOT skip this one\n\n\"Then we tried to break our own result. Take out just the three worst records from each decade - and the decline completely vanishes. The 2000s actually sit above the 1900s.\n\nSo that big fall in total deaths is mostly the giant disasters disappearing, things like the 1931 China flood. It's not that ordinary disasters got safer. The per-event number is the one that holds up.\n\nArnav, over to you.\"",
});

// ====================================================== 9-12. Task Set B ===
{
  const s = pres.addSlide();
  s.background = { color: SURF };
  title(s, "Disasters are global. Death is not.");
  chip(s, "A");
  figure(s, 8, { x: 0.22, y: 1.02, w: 4.74, h: 3.00 });
  figure(s, 9, { x: 5.04, y: 1.02, w: 4.74, h: 3.00 });
  s.addText("All 225 countries appear", {
    x: 0.22, y: 4.08, w: 4.74, h: 0.3, isTextBox: true, margin: 0,
    align: "center", fontFace: H_FONT, fontSize: 13.5, bold: true, color: INK });
  s.addText("China + India = 68% of all deaths", {
    x: 5.04, y: 4.08, w: 4.74, h: 0.3, isTextBox: true, margin: 0,
    align: "center", fontFace: H_FONT, fontSize: 13.5, bold: true, color: INK });
  s.addShape(pres.ShapeType.roundRect, {
    x: 2.55, y: 4.52, w: 3.9, h: 0.38,
    fill: { color: NAVY }, line: { color: NAVY }, rectRadius: 0.19 });
  s.addText("LIVE IN TABLEAU: switch the map here", {
    x: 2.55, y: 4.52, w: 3.9, h: 0.38, isTextBox: true, margin: 0,
    align: "center", valign: "middle", fontFace: B_FONT, fontSize: 12,
    bold: true, color: WHITE });
  s.addNotes(
    "2:15-2:35  TASKS B1.1 / B1.2  |  Arnav\n*** DO THE MAP SWITCH LIVE IN TABLEAU - the rubric names \"Tableau demo\" explicitly ***\n\n\"Thanks. So - this is where disasters actually get recorded. And it's basically everywhere. All two hundred and twenty-five countries.\n\nNow watch what happens when I switch the exact same map over to deaths. [SWITCH] It collapses onto two countries. China and India together are sixty-eight percent of all twenty-two point nine million deaths.\"");
}

figSlide({
  n: 10, task: "B1.3  Rank", who: "A",
  head: "Four measures, four different leaderboards",
  take: "The US is 1st for events and 1st for damage - and 23rd for deaths.",
  notes:
    "2:35-2:55  TASK B1.3  |  Arnav\n\n\"Same idea as four separate rankings - and they barely overlap. The US is number one for how many disasters it gets, and number one for money lost. And twenty-third for deaths. Bangladesh is the mirror image: third for deaths, twenty-third for damage.\n\nBasically, if a country is rich, disasters cost it money instead of lives.\"",
});

figSlide({
  n: 11, task: "B1.4  Derive", who: "A",
  head: "Two countries hold half of all deaths",
  take: "But it takes twenty countries to reach half of all recorded events.",
  notes:
    "2:55-3:10  TASK B1.4  |  Arnav\n\n\"This just puts a number on it. Two countries get you to half of all deaths. It takes twenty to get to half of all disasters.\"",
});

figSlide({
  n: 12, task: "B1.5  Derive", who: "A",
  head: "Same exposure, 1,000x the lethality",
  take: "China 11,139 deaths per event; Australia 11. That gap is not hazard - it is vulnerability.",
  notes:
    "3:10-3:30  TASK B1.5  |  Arnav  --  the slide that changed how we read the data\n\n\"And this is the one that changed how we read the whole dataset. These are the twenty most disaster-hit countries - so they're all heavily exposed, roughly comparable. And the death rate still varies by a factor of a thousand. China's at eleven thousand deaths per event. Australia's at eleven.\n\n[beat]\n\nTwo honest caveats - there's no population data in this file, and China's number is pulled up by the old famines. But even allowing for both, that gap is far too big to be about the hazards. That's vulnerability.\n\nKalpit.\"",
});

// ===================================================== 13-17. Task Set C ===
figSlide({
  n: 13, task: "C1.1  Compare", who: "K",
  head: "5% of events. 51% of deaths.",
  take: "Drought kills, storms cost, floods displace - they are different hazards.",
  notes:
    "3:30-3:55  TASK C1.1  |  Kalpit  --  the key chart of Task Set C\n\n\"Thanks. If I could keep one chart from this whole project, it'd be this one. Four bars, same seven hazards, same order every time.\n\n[beat]\n\nDrought is five percent of events. And fifty-one percent of deaths. Storms are the exact opposite - thirty-one percent of events, forty-two percent of the money, six percent of the deaths. So what a hazard's share of disasters tells you about its share of harm is basically nothing.\"",
});

figSlide({
  n: 14, task: "C1.2  Relate", who: "K",
  head: "Deadly and costly are different hazards",
  take: "Drought: 143 deaths per record. Wildfire: $250M and a median of 7 deaths.",
  notes:
    "3:55-4:05  TASK C1.2  |  Kalpit\n\n\"Here's each hazard placed by how deadly and how expensive a typical one is. Drought's out on its own on the right. Wildfire is the opposite corner - expensive, but a typical one kills seven people.\"",
});

figSlide({
  n: 15, task: "C1.3  Trend", who: "K",
  head: "$2.07 trillion - the costliest decade yet",
  take: "Damage coverage does not improve after 1970, so this rise is not a reporting artefact.",
  notes:
    "4:05-4:20  TASK C1.3  |  Kalpit\n\n\"Money over time, all in 2022 dollars. The 2010s cost two point zero seven trillion - that's a record. And damage reporting doesn't get better after 1970, so that rise isn't just better record-keeping.\"",
});

figSlide({
  n: 16, task: "C1.4  Compare", who: "K",
  head: "Which hazards became survivable?",
  take: "Drought 29,051 -> 53. Earthquakes never improved. Extreme heat went the wrong way.",
  notes:
    "4:20-4:35  TASK C1.4  |  Kalpit\n\n\"But the improvement isn't even. Drought went from twenty-nine thousand deaths per event down to fifty-three. Floods and storms dropped too - and those are all things you get warning about. Earthquakes, which you don't get warning about, didn't improve at all.\n\nAnd heatwaves went the wrong way. A hundred and twenty-five in the sixties, twelve hundred in the 2020s.\"",
});

figSlide({
  n: 17, task: "C1.5  Correlate", who: "K",
  head: "Costs rose. Deaths did not follow.",
  take: "Rank correlation between annual deaths and annual damage: -0.01.",
  notes:
    "4:35-4:45  TASK C1.5  |  Kalpit\n\n\"Last one. Since 1970: disasters, damage, people affected - all clearly rising. Deaths? No significant trend at all, p is 0.064. And the correlation between deaths and damage is basically zero.\n\nThey have completely come apart.\"",
});

// ============================================================= 18. close ===
{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addText("Exposure up. Vulnerability down. The bill still rising.", {
    x: M, y: 0.72, w: W - 2 * M, h: 0.62, isTextBox: true, margin: 0,
    fontFace: H_FONT, fontSize: 28, bold: true, color: WHITE,
  });

  const pts = [
    ["Exposure rose", "more assets, more people - and much better reporting", BLUE],
    ["Vulnerability fell", "deaths per recorded event down 99.4% in a century", "1BAF7A"],
    ["But unevenly", "2 countries carry half of all deaths; heat is getting worse", ORANGE],
  ];
  pts.forEach(([hd, bd, col], i) => {
    const y = 1.72 + i * 0.80;
    s.addShape(pres.ShapeType.ellipse, {
      x: M, y: y + 0.06, w: 0.30, h: 0.30,
      fill: { color: col }, line: { color: col },
    });
    s.addText(hd, {
      x: M + 0.48, y, w: 2.65, h: 0.4, isTextBox: true, margin: 0,
      valign: "middle", fontFace: H_FONT, fontSize: 17, bold: true, color: WHITE,
    });
    s.addText(bd, {
      x: M + 3.20, y, w: 5.9, h: 0.4, isTextBox: true, margin: 0,
      valign: "middle", fontFace: B_FONT, fontSize: 13.5, color: "9FB3CC",
    });
  });

  s.addText("And one caveat on our own headline: most of the fall in total deaths is the loss of mega-catastrophes, not a broad decline.",
    { x: M, y: 4.28, w: W - 2 * M, h: 0.44, isTextBox: true, margin: 0,
      fontFace: B_FONT, fontSize: 12.5, italic: true, color: "7C93AD" });
  s.addText("Thank you.", {
    x: M, y: H - 0.82, w: W - 2 * M, h: 0.4, isTextBox: true, margin: 0,
    fontFace: H_FONT, fontSize: 17, bold: true, color: WHITE });
  s.addNotes(
    "4:45-5:00  CLOSE  |  any one of you\n\n\"So - more exposure, less vulnerability, and a much bigger bill.\n\nWe got a lot better at not dying in disasters. Just not everywhere, not at all for earthquakes, and with heat it's actually going backwards.\n\nThanks for watching.\"\n\nHARD STOP at 5:00.");
}

pres.writeFile({ fileName: OUT }).then(() => {
  const kb = fs.statSync(OUT).size / 1024;
  console.log(`  wrote slides/${path.basename(OUT)}  ` +
              `(${pres.slides ? pres.slides.length : 18} slides, ${kb.toFixed(0)} KB)`);
});
