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

/** A figure slide: finding as the title, chart big, one takeaway line. */
function figSlide({ n, who, head, sub, take, notes }) {
  const s = pres.addSlide();
  s.background = { color: SURF };
  title(s, head, sub);
  chip(s, who);
  figure(s, n, { x: M, y: sub ? 1.32 : 1.08, w: W - 2 * M,
                 h: (H - 0.78) - (sub ? 1.32 : 1.08) });
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
    "0:00-0:10  TITLE. Hold while Lakshya opens.\n\n" +
    "\"Everyone believes natural disasters are getting worse. We took EM-DAT - " +
    "123 years, 225 countries, 15,015 recorded events - and asked one question.\"");
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
    "0:10-0:20  THE QUESTION.\n\n" +
    "\"Has the burden actually grown, and are we getting better at surviving it? " +
    "The answer turned out to be yes to both - and the two halves don't fit " +
    "together the way you'd expect.\"");
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
    "0:20-1:00  PREPROCESSING (Lakshya - the brief allows the first minute for this).\n\n" +
    "\"Four things had to be fixed before any chart. The file is semicolon-separated " +
    "with comma decimals. It's an April 2023 snapshot, so 2023 is a part-year - we " +
    "dropped those 51 rows or every trend would fake a collapse at the end. Some " +
    "hazard labels carry a trailing space, which silently splits 'Extreme " +
    "temperature' into two categories. And we verified rather than assumed that the " +
    "adjusted damage column is constant 2022 dollars - nominal times 100 over CPI, " +
    "and CPI is exactly 100 in 2022.\n\n" +
    "Critically, we left missing impact values missing, never zero - treating 'not " +
    "reported' as 'nobody died' would have flattered every historical decade.\"");
}

// =========================================================== 4. task map ===
{
  const s = pres.addSlide();
  s.background = { color: SURF };
  title(s, "One question, three owned task sets, fifteen charts");
  chip(s, "ALL");
  figure(s, 1, { x: M, y: 1.02, w: W - 2 * M, h: 3.85 });
  s.addNotes(
    "1:00  HANDOVER.\n\n" +
    "\"We split it three ways - when, where and what. Each of us owns a " +
    "sub-question end to end: its tasks, its charts and its inferences.\"");
}

// ======================================================= 5-8. Task Set A ===
figSlide({
  n: 4, who: "L",
  head: "The record explodes after 1970",
  take: "That shape is also exactly what a step-change in data collection looks like.",
  notes:
    "1:00-1:15  A1.2 TREND.\n\n" +
    "\"Events per year. It looks like an explosion after 1970 - and this is where " +
    "we nearly went wrong.\"",
});

figSlide({
  n: 5, who: "L",
  head: "...but it is partly a count of reporting",
  take: "91% of the record sits in 43% of the years. So we use rates, not counts, from here on.",
  notes:
    "1:15-1:35  A1.3 IDENTIFY - the diagnostic figure.\n\n" +
    "\"Volume grew 52-fold, which no physical change in hazard could produce on its " +
    "own. And damage reporting covers at most half the records in any decade. So " +
    "the count measures reporting as much as it measures hazard. Everything after " +
    "this uses rates.\"",
});

figSlide({
  n: 6, who: "L",
  head: "Deaths per recorded event fell 99.4%",
  take: "Two panels, never a twin axis - a twin axis lets the author pick the crossing point.",
  notes:
    "1:35-1:55  A1.4 COMPARE - the headline finding.\n\n" +
    "\"Total deaths peaked in the 1920s at 5.2 million. But look at panel b - deaths " +
    "per recorded event fell from about nineteen nine hundred to a hundred and " +
    "twenty-nine. An individual recorded disaster today kills roughly one 150th of " +
    "what one did a century ago.\"",
});

figSlide({
  n: 7, who: "L",
  head: "Then we tried to break our own finding",
  take: "Strip each decade's three deadliest records and the decline vanishes entirely.",
  notes:
    "1:55-2:15  A1.5 VALIDATE - the honest caveat. Do not skip this slide.\n\n" +
    "\"The 2000s sit above the 1900s once the mega-catastrophes are removed. So the " +
    "century-scale fall in TOTAL deaths is mostly the disappearance of events like " +
    "the 1931 China flood, not a broad improvement. The per-event improvement is the " +
    "claim that survives.\"\n\n" +
    "Handover to Arnav.",
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
    "2:15-2:35  B1.1 / B1.2 LOCATE. *** DO THE MAP SWITCH LIVE IN TABLEAU ***\n" +
    "The rubric names \"Tableau demo\" explicitly - this is the moment to earn it.\n\n" +
    "\"Here is where disasters are recorded - all 225 countries, fairly evenly " +
    "shaded. Now watch what happens when I switch the same map to deaths. " +
    "[SWITCH] It collapses onto two countries. China and India alone are 68% of " +
    "all 22.9 million recorded deaths.\"");
}

figSlide({
  n: 10, who: "A",
  head: "Four measures, four different leaderboards",
  take: "The US is 1st for events and 1st for damage - and 23rd for deaths.",
  notes:
    "2:35-2:55  B1.3 RANK.\n\n" +
    "\"The four leaderboards barely overlap. The United States is first for events " +
    "and first for damage, and twenty-third for deaths. Bangladesh is third for " +
    "deaths and twenty-third for damage. Wealth converts disaster exposure into " +
    "property loss instead of death.\"",
});

figSlide({
  n: 11, who: "A",
  head: "Two countries hold half of all deaths",
  take: "But it takes twenty countries to reach half of all recorded events.",
  notes:
    "2:55-3:10  B1.4 DERIVE.\n\n" +
    "\"Deaths are far more concentrated than disasters. The top five countries hold " +
    "87% of deaths but only 27% of events. Disasters happen nearly everywhere; " +
    "dying from them does not.\"",
});

figSlide({
  n: 12, who: "A",
  head: "Same exposure, 1,000x the lethality",
  take: "China 11,139 deaths per event; Australia 11. That gap is not hazard - it is vulnerability.",
  notes:
    "3:10-3:30  B1.5 DERIVE - the slide that changed how we read the data.\n\n" +
    "\"Take the twenty most disaster-prone countries, so exposure is roughly held " +
    "constant, and lethality still spans a factor of a thousand. Two honest caveats: " +
    "there is no population denominator, and China's figure is loaded by the " +
    "pre-1960 famines. Even so, the spread is far too wide to be hazard.\"\n\n" +
    "Handover to Kalpit.",
});

// ===================================================== 13-17. Task Set C ===
figSlide({
  n: 13, who: "K",
  head: "5% of events. 51% of deaths.",
  sub: "Four bars, the same seven hazards, the same colour order.",
  take: "Drought kills, storms cost, floods displace - they are different hazards.",
  notes:
    "3:30-3:55  C1.1 COMPARE - the key chart of Task Set C.\n\n" +
    "\"Drought is five percent of recorded events and fifty-one percent of recorded " +
    "deaths. Storms are the mirror image: 31% of events, 42% of the money, six " +
    "percent of the deaths. Earthquakes are the concentrated destroyer - a tenth of " +
    "events, a quarter of the damage, but only 2.4% of people affected.\"",
});

figSlide({
  n: 14, who: "K",
  head: "Deadly and costly are different hazards",
  take: "Drought: 143 deaths per record. Wildfire: $250M and a median of 7 deaths.",
  notes:
    "3:55-4:05  C1.2 RELATE.\n\n" +
    "\"Each hazard sits somewhere in a deadliness-cost plane. Drought is alone on " +
    "the right. Wildfire is the opposite corner - expensive, but almost harmless to " +
    "life. There is no single severity axis.\"",
});

figSlide({
  n: 15, who: "K",
  head: "$2.07 trillion - the costliest decade yet",
  take: "Damage coverage does not improve after 1970, so this rise is not a reporting artefact.",
  notes:
    "4:05-4:20  C1.3 TREND.\n\n" +
    "\"Real damage, inflation-adjusted to 2022 dollars. The 2010s cost 2.07 trillion " +
    "- a record - and the 2020s are already at 699 billion with only three years " +
    "counted.\"",
});

figSlide({
  n: 16, who: "K",
  head: "Which hazards became survivable?",
  take: "Drought 29,051 -> 53. Earthquakes never improved. Extreme heat went the wrong way.",
  notes:
    "4:20-4:35  C1.4 COMPARE.\n\n" +
    "\"Drought fell from twenty-nine thousand deaths per event to fifty-three. " +
    "Floods and storms collapsed too - all hazards that give warning. Earthquakes, " +
    "which give none, did not improve at all. And extreme temperature went the " +
    "wrong way: 125 in the 1960s, 1,202 in the 2020s.\"",
});

figSlide({
  n: 17, who: "K",
  head: "Costs rose. Deaths did not follow.",
  take: "Rank correlation between annual deaths and annual damage: -0.01.",
  notes:
    "4:35-4:45  C1.5 CORRELATE.\n\n" +
    "\"Since 1970, events, damage and people affected all rise significantly. " +
    "Annual deaths show no significant trend at all - p is 0.064. Costs and " +
    "mortality have decoupled.\"",
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
    "4:45-5:00  CLOSE (any member).\n\n" +
    "\"So: exposure up, vulnerability down, and the bill rising. The world got " +
    "dramatically better at not dying in disasters - unevenly, not at all for " +
    "earthquakes, and going backwards for heat. Thank you.\"\n\n" +
    "HARD STOP at 5:00.");
}

pres.writeFile({ fileName: OUT }).then(() => {
  const kb = fs.statSync(OUT).size / 1024;
  console.log(`  wrote slides/${path.basename(OUT)}  ` +
              `(${pres.slides ? pres.slides.length : 18} slides, ${kb.toFixed(0)} KB)`);
});
