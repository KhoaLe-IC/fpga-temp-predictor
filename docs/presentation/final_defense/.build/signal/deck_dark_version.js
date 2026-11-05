// Weather forecasting on FPGA — final defense, "signal & silicon" redesign
const path = require("path");
const fs = require("fs");
const NM = process.env.NM;
const pptxgen = require(path.join(NM, "pptxgenjs"));
const { applyTheme } = require(process.env.SKILL + "/scripts/apply_theme.js");

const B = __dirname;
const OUT = process.argv[2];
const notes = JSON.parse(fs.readFileSync(path.join(B, "notes.json"), "utf8"));
const win = JSON.parse(fs.readFileSync(path.join(B, "window.json"), "utf8"));

// ---------- palette & type ----------
const K = {
  bg: "0B1320", panel: "121D2E", panel2: "1A283D", line: "2A3A52", grid: "16233A",
  text: "EEF2F6", muted: "93A3B8", dim: "56677F",
  teal: "5EEAD4", tealDeep: "134E4A", amber: "FBBF24", amberDeep: "4A3710",
  paper: "FFFFFF", ink: "0B1320", inkMuted: "5B6B80", rule: "DCE3EC", tint: "F3F6F9",
  tealInk: "0F766E", amberInk: "B45309",
};
const H = "Calibri", M = "Consolas";
const THEME = {
  name: "Signal and Silicon", headFontFace: H, bodyFontFace: H,
  colors: {
    dk1: K.ink, lt1: K.paper, dk2: K.panel, lt2: K.text,
    accent1: K.teal, accent2: K.amber, accent3: K.muted, accent4: K.line,
    accent5: K.tealInk, accent6: K.amberInk, hlink: K.tealInk, folHlink: K.inkMuted,
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.title = "Weather forecasting on FPGA — final defense";
pres.subject = "CE436 Discrete-Time Signal Processing";
pres.theme = { headFontFace: H, bodyFontFace: H };

const W = 13.333, X0 = 0.6, CW = W - 2 * X0;

// ---------- layouts ----------
pres.defineSlideMaster({
  title: "COVER", background: { color: K.bg },
});
pres.defineSlideMaster({
  title: "SIGNAL",
  background: { path: path.join(B, "graticule.png") },
  objects: [
    { text: { text: "CE436  ·  WEATHER FORECASTING ON FPGA", options: { x: X0, y: 6.98, w: 6, h: 0.3, fontFace: M, fontSize: 9, color: K.dim, charSpacing: 1, margin: 0 } } },
    { placeholder: { options: { name: "kicker", type: "body", x: X0, y: 0.5, w: 9, h: 0.32, fontFace: M, fontSize: 12, color: K.teal, charSpacing: 2, margin: 0, valign: "middle" }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: X0, y: 0.84, w: CW, h: 0.82, fontFace: H, fontSize: 34, bold: true, color: K.text, margin: 0, valign: "top", align: "left" }, text: "" } },
  ],
  slideNumber: { x: 11.93, y: 6.98, w: 0.8, h: 0.3, fontFace: M, fontSize: 9, color: K.dim, align: "right" },
});
pres.defineSlideMaster({
  title: "BACKUP",
  background: { color: K.paper },
  objects: [
    { text: { text: "BACKUP  ·  FOR QUESTIONS", options: { x: X0, y: 6.98, w: 6, h: 0.3, fontFace: M, fontSize: 9, color: K.inkMuted, charSpacing: 1, margin: 0 } } },
    { placeholder: { options: { name: "kicker", type: "body", x: X0, y: 0.5, w: 9, h: 0.32, fontFace: M, fontSize: 12, color: K.tealInk, charSpacing: 2, margin: 0, valign: "middle" }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: X0, y: 0.84, w: CW, h: 0.95, fontFace: H, fontSize: 28, bold: true, color: K.ink, margin: 0, valign: "top", align: "left" }, text: "" } },
  ],
});

// ---------- helpers ----------
let n = 0;
const fresh = (o) => JSON.parse(JSON.stringify(o));
function slide(master, section, kicker, title, ownNotes) {
  const s = pres.addSlide({ masterName: master, sectionTitle: section });
  if (kicker) s.addText(kicker, { placeholder: "kicker" });
  if (title) s.addText(title, { placeholder: "title" });
  if (ownNotes) { s.addNotes(ownNotes); return s; } // inserted slide: keeps original note numbering intact
  n += 1;
  const nt = notes[String(n)];
  if (nt) s.addNotes(nt.replace(/Source: Source:/g, "Source:"));
  return s;
}
function t(s, text, o) { s.addText(text, Object.assign({ isTextBox: true, margin: 0, fontFace: H, color: K.text, valign: "top" }, o)); }
function rect(s, o) { s.addShape(pres.shapes.RECTANGLE, Object.assign({ line: { type: "none" } }, o)); }
function rrect(s, o) { s.addShape(pres.shapes.ROUNDED_RECTANGLE, Object.assign({ rectRadius: 0.08, line: { type: "none" } }, o)); }
function line(s, x, y, w, h, color, wpt = 1, extra = {}) {
  s.addShape(pres.shapes.LINE, Object.assign({ x, y, w, h, line: { color, width: wpt } }, extra));
}
function dot(s, cx, cy, r, fill, lineColor) {
  s.addShape(pres.shapes.OVAL, { x: cx - r, y: cy - r, w: 2 * r, h: 2 * r, fill: fill ? { color: fill } : { type: "none" }, line: lineColor ? { color: lineColor, width: 1.25 } : { type: "none" } });
}
function chip(s, x, y, w, label, o = {}) {
  rrect(s, { x, y, w, h: 0.42, fill: { color: o.fill || K.panel2 }, line: o.border ? { color: o.border, width: 1 } : { type: "none" }, rectRadius: 0.21 });
  t(s, label, { x, y, w, h: 0.42, align: "center", valign: "middle", fontSize: o.size || 13, color: o.color || K.text, fontFace: o.mono ? M : H, bold: !!o.bold });
}
function arrow(s, x, y, w, color = K.dim) {
  line(s, x, y, w, 0, color, 1.25, { line: { color, width: 1.25, endArrowType: "triangle" } });
}
function shadow() { return { type: "outer", color: "000000", blur: 18, offset: 6, angle: 90, opacity: 0.45 }; }
// Crop a native screenshot without touching its bytes: px coords of the source image
function screenshot(s, file, imgPx, crop, x, y, w) {
  const k = w / crop.w;
  const h = crop.h * k;
  s.addImage({ path: path.join(B, file), x, y, w: imgPx[0] * k, h: imgPx[1] * k,
    sizing: { type: "crop", x: crop.x * k, y: crop.y * k, w, h } });
  return { h, k };
}

// =====================================================================
pres.addSection({ title: "Talk" });

// 1 — Cover -----------------------------------------------------------
{
  const s = slide("COVER", "Talk");
  s.addImage({ path: path.join(B, "trace_cover.png"), x: -0.1, y: 3.55, w: 13.55, h: 3.73 });
  t(s, "CE436  ·  DISCRETE-TIME SIGNAL PROCESSING  ·  FINAL DEFENSE", { x: X0, y: 0.6, w: 10, h: 0.3, fontFace: M, fontSize: 12, color: K.teal, charSpacing: 2 });
  t(s, "Weather forecasting\non FPGA", { x: X0, y: 1.05, w: 9, h: 2.0, fontSize: 60, bold: true, lineSpacingMultiple: 0.9 });
  t(s, "Parallel fixed-point inference and verification on a Cyclone II DE2 board", { x: X0, y: 3.05, w: 8.5, h: 0.45, fontSize: 20, color: K.muted });
  t(s, "Every line below is real data: 43,824 hourly temperature observations, Ho Chi Minh City, 2021–2025 (NASA POWER)", { x: X0, y: 6.95, w: 11, h: 0.3, fontFace: M, fontSize: 9, color: K.dim });
}

// 2 — Three hours ahead -------------------------------------------------
{
  const s = slide("SIGNAL", "Talk", "01 · THE TASK", "Forecast the weather three hours ahead");
  t(s, "+3", { x: X0, y: 1.9, w: 3.2, h: 1.9, fontSize: 140, bold: true, color: K.teal, lineSpacingMultiple: 0.85 });
  t(s, "HOURS", { x: X0 + 0.08, y: 3.85, w: 3, h: 0.35, fontFace: M, fontSize: 16, color: K.teal, charSpacing: 4 });
  t(s, "Five quantities from each hourly frame", { x: X0, y: 4.55, w: 3.4, h: 0.3, fontSize: 14, color: K.muted });
  ["Temperature", "Pressure", "Humidity", "Wind speed", "Wind direction"].forEach((q, i) => {
    t(s, q, { x: X0, y: 4.95 + i * 0.32, w: 3.4, h: 0.3, fontSize: 15, color: K.text });
  });

  // real 25-hour history + 3 h target, drawn as a stem plot
  const px = 4.6, pw = 7.85, py = 2.05, ph = 2.75; // plot box
  rrect(s, { x: px - 0.25, y: py - 0.3, w: pw + 0.5, h: ph + 1.15, fill: { color: K.panel } });
  const all = win.history.concat(win.future);
  const lo = Math.min(...all, win.pred) - 0.8, hi = Math.max(...all, win.pred) + 0.8;
  const sx = (i) => px + 0.2 + (i / 27) * (pw - 2.2);
  const sy = (v) => py + ph - ((v - lo) / (hi - lo)) * ph;
  const base = py + ph;
  line(s, px, base, pw, 0, K.line, 1);
  win.history.forEach((v, i) => {
    const c = i === 24 ? K.text : K.muted;
    line(s, sx(i), sy(v), 0, base - sy(v), i === 24 ? K.text : K.dim, 1.25);
    dot(s, sx(i), sy(v), 0.055, c);
  });
  // horizon band
  rect(s, { x: sx(24) + 0.05, y: py - 0.1, w: sx(27) - sx(24) + 0.1, h: ph + 0.1, fill: { color: K.teal, transparency: 90 } });
  win.future.forEach((v, i) => dot(s, sx(25 + i), sy(v), 0.055, null, K.dim));
  line(s, sx(27), sy(win.pred), 0, base - sy(win.pred), K.teal, 1.5);
  dot(s, sx(27), sy(win.pred), 0.11, K.teal);
  t(s, `forecast ${win.pred.toFixed(2)} °C`, { x: sx(27) + 0.25, y: sy(win.pred) - 0.3, w: 1.7, h: 0.28, fontFace: M, fontSize: 12, color: K.teal });
  t(s, `observed ${win.future[2].toFixed(2)} °C`, { x: sx(27) + 0.25, y: sy(win.pred) - 0.02, w: 1.7, h: 0.28, fontFace: M, fontSize: 12, color: K.muted });
  const lab = { fontFace: M, fontSize: 11, color: K.muted, h: 0.26 };
  t(s, "t − 24 h", Object.assign({ x: sx(0) - 0.1, y: base + 0.1, w: 1.2 }, lab));
  t(s, "t · 12:00", Object.assign({ x: sx(24) - 1.0, y: base + 0.1, w: 1.0, align: "right", color: K.text }, lab));
  t(s, "15:00", Object.assign({ x: sx(27) - 0.5, y: base + 0.1, w: 0.75, align: "right", color: K.teal }, lab));
  t(s, `Real 2025 test-set window (${win.day}, local time) · temperature lane of the deployed model`, { x: px, y: base + 0.5, w: pw, h: 0.26, fontFace: M, fontSize: 10, color: K.dim });

  // system path
  const y = 5.95;
  const steps = [["Recorded frames", 1.55], ["Host", 0.8], ["JTAG", 0.8], ["FPGA · fixed coefficients", 2.3], ["Result to host", 1.4]];
  let x = px - 0.25;
  steps.forEach(([lbl, w], i) => {
    chip(s, x, y, w, lbl, i === 3 ? { fill: K.tealDeep, color: K.teal, bold: true, size: 12 } : { size: 12 });
    x += w;
    if (i < steps.length - 1) { arrow(s, x + 0.05, y + 0.21, 0.2); x += 0.3; }
  });
}

// 3 — Extension -----------------------------------------------------------
{
  const s = slide("SIGNAL", "Talk", "02 · THE EXTENSION", "From one temperature output to five weather quantities");
  const cw = 5.3, cy = 2.05, ch = 4.15;
  const cards = [
    { x: X0, big: "1", head: "Temperature prototype", acc: K.muted, fill: K.panel, rows: [["Model", "Three-parameter seasonal OLS"], ["Arithmetic", "One lane · 16-bit Q8"], ["Direction", "No direction path"]] },
    { x: X0 + cw + 1.5, big: "5", head: "Current weather design", acc: K.teal, fill: K.panel2, rows: [["Model", "Seven-lag regression per channel"], ["Arithmetic", "Six lanes · 18-bit Q8"], ["Direction", "Cosine + sine, CORDIC angle"]] },
  ];
  cards.forEach((c, i) => {
    rrect(s, { x: c.x, y: cy, w: cw, h: ch, fill: { color: c.fill }, line: i ? { color: K.teal, width: 1.25 } : { type: "none" } });
    t(s, c.big, { x: c.x + 0.4, y: cy + 0.2, w: 1.3, h: 1.3, fontSize: 88, bold: true, color: c.acc, lineSpacingMultiple: 0.85 });
    t(s, i ? "weather quantities" : "forecast quantity", { x: c.x + 1.65, y: cy + 0.5, w: 3.4, h: 0.3, fontSize: 15, color: K.muted });
    t(s, c.head, { x: c.x + 1.65, y: cy + 0.82, w: 3.5, h: 0.4, fontSize: 20, bold: true });
    c.rows.forEach(([k, v], j) => {
      const ry = cy + 1.85 + j * 0.72;
      line(s, c.x + 0.4, ry - 0.12, cw - 0.8, 0, K.line, 0.75);
      t(s, k.toUpperCase(), { x: c.x + 0.4, y: ry, w: 1.5, h: 0.3, fontFace: M, fontSize: 11, color: K.dim, charSpacing: 1 });
      t(s, v, { x: c.x + 1.9, y: ry - 0.03, w: cw - 2.3, h: 0.36, fontSize: 16, color: i ? K.text : K.muted });
    });
  });
  arrow(s, X0 + cw + 0.35, cy + ch / 2, 0.8, K.teal);
  t(s, "Unchanged: hourly inputs and the three-hour target horizon", { x: X0, y: 6.42, w: CW, h: 0.3, fontSize: 14, color: K.muted });
}

// 4 — Chronological split ---------------------------------------------------
{
  const s = slide("SIGNAL", "Talk", "03 · DATA", "A chronological split: the model never sees the future");
  s.addImage({ path: path.join(B, "trace_split.png"), x: X0, y: 1.85, w: CW, h: CW / (3700 / 640) });
  const by = 4.05;
  const seg = [
    { f: 0.6, c: K.text, fill: K.panel2, yr: "2021–2023", n: "26,253", role: "Training", d: "Fits the coefficients" },
    { f: 0.2, c: K.teal, fill: K.tealDeep, yr: "2024", n: "8,781", role: "Validation", d: "Selects the model" },
    { f: 0.2, c: K.amber, fill: K.amberDeep, yr: "2025", n: "8,757", role: "Test", d: "Held out, frozen model" },
  ];
  let x = X0;
  seg.forEach((g) => {
    const w = CW * g.f - 0.06;
    rect(s, { x, y: by, w, h: 0.12, fill: { color: g.c } });
    t(s, g.yr, { x, y: by + 0.28, w, h: 0.3, fontFace: M, fontSize: 13, color: g.c });
    t(s, g.n, { x, y: by + 0.65, w, h: 0.8, fontSize: 46, bold: true, color: g.c === K.text ? K.text : g.c });
    t(s, g.role, { x, y: by + 1.5, w, h: 0.35, fontSize: 18, bold: true });
    t(s, g.d, { x, y: by + 1.88, w, h: 0.3, fontSize: 14, color: K.muted });
    x += CW * g.f;
  });
  t(s, "Usable examples: each needs a valid 25-hour history and a target three hours later. NASA POWER hourly, Ho Chi Minh City, UTC.", { x: X0, y: 6.42, w: CW, h: 0.3, fontSize: 13, color: K.dim });
}

// 5 — Seven lags --------------------------------------------------------------
{
  const s = slide("SIGNAL", "Talk", "04 · MODEL", "Seven lags per channel, one linear sum");
  t(s, [
    { text: "x̂", options: { color: K.teal } },
    { text: "(t + 3)  =  b  +  Σ  w", options: {} },
    { text: "k", options: { subscript: true } },
    { text: " · x(t − ℓ", options: {} },
    { text: "k", options: { subscript: true } },
    { text: ")", options: {} },
  ], { x: X0, y: 1.85, w: 8, h: 0.6, fontFace: H, fontSize: 32, color: K.text });
  t(s, "k = 1 … 7   ·   each channel uses only its own history", { x: X0, y: 2.5, w: 8, h: 0.3, fontFace: M, fontSize: 12, color: K.muted });

  const lags = [0, 1, 3, 6, 12, 21, 24];
  const wts = [1.2228, -0.5698, 0.0989, -0.0125, 0.0009, 0.8489, -0.6337];
  const px = X0 + 0.3, pw = CW - 0.6;
  const sx = (lag) => px + pw - (lag / 24) * pw; // lag 0 on the right (most recent)
  const hist = win.history; // hist[24] = t
  const lo = Math.min(...hist) - 0.5, hi = Math.max(...hist) + 0.5;
  const base = 4.55, ph = 1.45;
  const sy = (v) => base - ((v - lo) / (hi - lo)) * ph;
  line(s, px - 0.1, base, pw + 0.2, 0, K.line, 1);
  for (let lag = 0; lag <= 24; lag++) {
    const v = hist[24 - lag];
    const on = lags.includes(lag);
    line(s, sx(lag), sy(v), 0, base - sy(v), on ? K.teal : K.dim, on ? 2 : 1);
    dot(s, sx(lag), sy(v), on ? 0.085 : 0.045, on ? K.teal : K.dim);
    if (on) t(s, String(lag), { x: sx(lag) - 0.3, y: base + 0.1, w: 0.6, h: 0.32, align: "center", fontFace: M, fontSize: 15, bold: true, color: K.teal });
  }
  t(s, "← older", { x: px - 0.1, y: base + 0.45, w: 1.2, h: 0.28, fontFace: M, fontSize: 10, color: K.dim });
  t(s, "lag ℓ in hours", { x: px + pw / 2 - 1.0, y: base + 0.45, w: 2, h: 0.28, fontFace: M, fontSize: 10, color: K.dim });

  // deployed temperature weights: diverging bars under each tap
  const zy = 5.75, sc = 0.55;
  line(s, px - 0.1, zy, pw + 0.2, 0, K.line, 0.75, { line: { color: K.line, width: 0.75, dashType: "dash" } });
  lags.forEach((lag, i) => {
    const v = wts[i], hgt = Math.max(Math.abs(v) * sc, 0.02);
    rect(s, { x: sx(lag) - 0.14, y: v >= 0 ? zy - hgt : zy, w: 0.28, h: hgt, fill: { color: v >= 0 ? K.teal : K.amber } });
    const ly = v >= 0 ? zy + 0.06 : zy - 0.3;
    t(s, (v >= 0 ? "+" : "−") + Math.abs(v).toFixed(Math.abs(v) < 0.01 ? 4 : 2), { x: sx(lag) - 0.5, y: ly, w: 1.0, h: 0.24, align: "center", fontFace: M, fontSize: 10, color: K.muted });
  });
  t(s, "Deployed temperature weights: the last hours and the same hours yesterday dominate", { x: X0, y: 6.42, w: CW, h: 0.3, fontSize: 13, color: K.muted });
}

// 6 — Wind direction ---------------------------------------------------------
{
  const s = slide("SIGNAL", "Talk", "05 · DIRECTION", "Wind direction wraps around at 0°");
  const cx = X0 + 2.3, cy = 3.95, r = 1.7;
  dot(s, cx, cy, r, K.panel, K.line);
  line(s, cx - r - 0.15, cy, 2 * r + 0.3, 0, K.line, 0.75);
  line(s, cx, cy - r - 0.15, 0, 2 * r + 0.3, K.line, 0.75);
  t(s, "N · 0°", { x: cx - 0.6, y: cy - r - 0.5, w: 1.2, h: 0.28, align: "center", fontFace: M, fontSize: 11, color: K.muted });
  const a = 9 * Math.PI / 180, dx = r * Math.sin(a), dy = r * Math.cos(a);
  line(s, cx, cy - dy, dx, dy, K.teal, 2.5, { flipV: true });
  line(s, cx - dx, cy - dy, dx, dy, K.amber, 2.5);
  t(s, "1°", { x: cx + dx + 0.05, y: cy - dy + 0.05, w: 0.6, h: 0.3, fontFace: M, fontSize: 14, bold: true, color: K.teal });
  t(s, "359°", { x: cx - dx - 0.75, y: cy - dy + 0.05, w: 0.7, h: 0.3, align: "right", fontFace: M, fontSize: 14, bold: true, color: K.amber });
  t(s, "2° apart, not 358°", { x: cx - 1.6, y: cy + r + 0.22, w: 3.2, h: 0.4, align: "center", fontSize: 20, bold: true });

  // encoding pipeline
  const x0 = 6.2, cols = [x0, x0 + 2.05, x0 + 4.2];
  t(s, "ENCODE ON HOST", { x: cols[0], y: 2.25, w: 2, h: 0.3, fontFace: M, fontSize: 11, color: K.dim, charSpacing: 1 });
  t(s, "PREDICT ON FPGA", { x: cols[1], y: 2.25, w: 2, h: 0.3, fontFace: M, fontSize: 11, color: K.dim, charSpacing: 1 });
  t(s, "RECONSTRUCT", { x: cols[2], y: 2.25, w: 2.3, h: 0.3, fontFace: M, fontSize: 11, color: K.dim, charSpacing: 1 });
  chip(s, cols[0], 2.95, 1.6, "cos θ", { mono: true, size: 16 });
  chip(s, cols[0], 3.65, 1.6, "sin θ", { mono: true, size: 16 });
  chip(s, cols[1], 2.95, 1.6, "lane 5", { mono: true, size: 14, color: K.muted });
  chip(s, cols[1], 3.65, 1.6, "lane 6", { mono: true, size: 14, color: K.muted });
  arrow(s, cols[0] + 1.68, 3.16, 0.3); arrow(s, cols[0] + 1.68, 3.86, 0.3);
  arrow(s, cols[1] + 1.68, 3.16, 0.3); arrow(s, cols[1] + 1.68, 3.86, 0.3);
  rrect(s, { x: cols[2], y: 2.95, w: 2.4, h: 1.12, fill: { color: K.amberDeep }, line: { color: K.amber, width: 1.25 } });
  t(s, "CORDIC", { x: cols[2], y: 3.06, w: 2.4, h: 0.45, align: "center", fontSize: 22, bold: true, color: K.amber });
  t(s, "16 iterations → θ̂", { x: cols[2], y: 3.55, w: 2.4, h: 0.3, align: "center", fontFace: M, fontSize: 12, color: K.amber });
  t(s, "Each angle becomes two smooth components, so nearby directions stay numerically close. The FPGA predicts both and turns them back into one angle.", { x: x0, y: 4.65, w: 6.4, h: 0.9, fontSize: 16, color: K.text });
  t(s, "Zero component pair → direction flagged undefined", { x: x0, y: 5.75, w: 6.4, h: 0.3, fontFace: M, fontSize: 12, color: K.muted });
  t(s, "Rays drawn wider apart than 2° for legibility", { x: X0, y: 6.42, w: 5, h: 0.3, fontSize: 12, color: K.dim });
}

// 7 — Fixed point -------------------------------------------------------------
{
  const s = slide("SIGNAL", "Talk", "06 · ARITHMETIC", "Fixed point: keep every bit until the final shift");
  const bp = 7.55, cell = 0.112, rh = 0.36; // binary-point x, bit width, row height
  const rows = [
    ["Sample", "Q8 · 18 bit", 10, 8, K.text],
    ["Weight", "Q14 · 18 bit", 4, 14, K.text],
    ["Product", "Q22 · 36 bit", 14, 22, K.teal],
    ["Accumulator", "Q22 · 48 bit", 26, 22, K.teal],
    ["Output", "Q8 · 18 bit  (>>> 14, limit)", 10, 8, K.amber],
  ];
  const y0 = 2.15, gap = 0.62;
  rows.forEach(([name, fmt, ib, fb, c], i) => {
    const y = y0 + i * gap;
    t(s, name, { x: X0, y: y + 0.02, w: 1.6, h: 0.34, fontSize: 16, bold: true, color: c === K.text ? K.text : c });
    for (let b = 0; b < ib + fb; b++) {
      const x = bp - ib * cell + b * cell;
      rect(s, { x: x + 0.012, y, w: cell - 0.024, h: rh, fill: { color: b < ib ? K.panel2 : c, transparency: b < ib ? 0 : 55 } });
    }
    t(s, fmt, { x: bp + fb * cell + 0.15, y: y + 0.05, w: 3.2, h: 0.28, fontFace: M, fontSize: 12, color: K.muted });
  });
  line(s, bp, y0 - 0.25, 0, rows.length * gap + 0.05, K.amber, 1.5, { line: { color: K.amber, width: 1.5, dashType: "dash" } });
  t(s, "binary point", { x: bp - 0.75, y: y0 - 0.55, w: 1.5, h: 0.26, align: "center", fontFace: M, fontSize: 11, color: K.amber });
  t(s, "integer bits", { x: bp - 1.6, y: y0 + rows.length * gap - 0.15, w: 1.5, h: 0.26, align: "right", fontFace: M, fontSize: 10, color: K.dim });
  t(s, "fraction bits", { x: bp + 0.1, y: y0 + rows.length * gap - 0.15, w: 1.5, h: 0.26, fontFace: M, fontSize: 10, color: K.dim });

  rrect(s, { x: X0, y: 5.6, w: CW, h: 0.95, fill: { color: K.panel } });
  t(s, [{ text: "30 °C", options: { color: K.text } }, { text: "  ×  2⁸  =  ", options: { color: K.muted } }, { text: "7680", options: { color: K.teal, bold: true } }, { text: "  raw", options: { color: K.muted } }],
    { x: X0 + 0.35, y: 5.6, w: 5.2, h: 0.95, valign: "middle", fontFace: M, fontSize: 22 });
  t(s, "Aligned bias, floor scaling, range limits. The C++ reference uses identical rules, so any mismatch is an implementation bug, not forecast error.", { x: X0 + 5.6, y: 5.6, w: CW - 5.95, h: 0.95, valign: "middle", fontSize: 14, color: K.muted });
}

// 8 — Six lanes --------------------------------------------------------------
{
  const s = slide("SIGNAL", "Talk", "07 · ARCHITECTURE", "Six lanes in parallel, one multiplier each");
  const lanes = ["Temperature", "Pressure", "Humidity", "Wind speed", "Cosine", "Sine"];
  const taps = [0, 1, 3, 6, 12, 21, 24];
  const y0 = 2.0, gap = 0.62, rx = 2.45, cell = 0.165;
  t(s, "25-SAMPLE HISTORY  ·  7 TAPS", { x: rx, y: y0 - 0.38, w: 4.2, h: 0.26, fontFace: M, fontSize: 10, color: K.dim, charSpacing: 1 });
  t(s, "MAC", { x: 6.95, y: y0 - 0.38, w: 0.7, h: 0.26, align: "center", fontFace: M, fontSize: 10, color: K.dim, charSpacing: 1 });
  lanes.forEach((ln, i) => {
    const y = y0 + i * gap, cyy = y + 0.2, dir = i >= 4;
    t(s, ln, { x: X0, y: y + 0.03, w: 1.75, h: 0.34, fontSize: 16, bold: !dir, color: dir ? K.amber : K.text });
    for (let k = 0; k < 25; k++) {
      const lag = 24 - k, on = taps.includes(lag);
      rect(s, { x: rx + k * cell, y: y + 0.06, w: cell - 0.035, h: 0.28, fill: { color: on ? (dir ? K.amber : K.teal) : K.panel2 } });
    }
    arrow(s, rx + 25 * cell + 0.05, cyy, 0.33);
    dot(s, 7.3, cyy, 0.25, K.panel2, dir ? K.amber : K.teal);
    t(s, "×+", { x: 7.05, y: cyy - 0.2, w: 0.5, h: 0.4, align: "center", valign: "middle", fontSize: 14, bold: true, color: dir ? K.amber : K.teal });
    if (!dir) {
      arrow(s, 7.62, cyy, 1.0);
      t(s, ln, { x: 8.75, y: y + 0.03, w: 2.5, h: 0.34, fontSize: 15, color: K.muted });
    }
  });
  // cos/sin merge into CORDIC
  const ya = y0 + 4 * gap + 0.2, yb = y0 + 5 * gap + 0.2;
  line(s, 7.55, ya, 0.6, 0, K.amber, 1.25); line(s, 7.55, yb, 0.6, 0, K.amber, 1.25);
  line(s, 8.15, ya, 0, yb - ya, K.amber, 1.25);
  arrow(s, 8.15, (ya + yb) / 2, 0.35, K.amber);
  rrect(s, { x: 8.55, y: (ya + yb) / 2 - 0.27, w: 1.35, h: 0.54, fill: { color: K.amberDeep }, line: { color: K.amber, width: 1 } });
  t(s, "CORDIC", { x: 8.55, y: (ya + yb) / 2 - 0.27, w: 1.35, h: 0.54, align: "center", valign: "middle", fontSize: 14, bold: true, color: K.amber });
  arrow(s, 9.95, (ya + yb) / 2, 0.3, K.amber);
  t(s, "Direction", { x: 10.35, y: (ya + yb) / 2 - 0.17, w: 1.6, h: 0.34, fontSize: 15, color: K.muted });

  // callout
  rrect(s, { x: 10.35, y: 1.95, w: 2.38, h: 2.25, fill: { color: K.panel } });
  t(s, "6", { x: 10.6, y: 2.05, w: 1.0, h: 1.05, fontSize: 64, bold: true, color: K.teal });
  t(s, "multipliers,\nnot 42", { x: 11.45, y: 2.32, w: 1.25, h: 0.7, fontSize: 15, bold: true });
  t(s, "Each multiplier walks its seven taps over time.", { x: 10.6, y: 3.2, w: 1.95, h: 0.8, fontSize: 13, color: K.muted });
  t(s, "History advances only when a frame is accepted. The wrapper aligns scalar results with the reconstructed direction.", { x: X0, y: 6.15, w: CW, h: 0.5, fontSize: 13, color: K.dim });
}

// 9 — Latency vs interval --------------------------------------------------------
{
  const s = slide("SIGNAL", "Talk", "08 · TIMING", "40 cycles of latency, a new frame every 23");
  t(s, "40", { x: X0, y: 1.9, w: 3, h: 1.6, fontSize: 120, bold: true, color: K.teal, lineSpacingMultiple: 0.85 });
  t(s, "CYCLES LATENCY", { x: X0 + 0.06, y: 3.55, w: 3, h: 0.3, fontFace: M, fontSize: 14, color: K.teal, charSpacing: 3 });
  t(s, "0.80 µs at 50 MHz", { x: X0 + 0.06, y: 4.0, w: 3, h: 0.4, fontSize: 20, bold: true });
  t(s, "First forecast follows the 25th accepted frame: 24 frames fill the history.", { x: X0 + 0.06, y: 4.6, w: 3.1, h: 0.9, fontSize: 14, color: K.muted });

  const gx = 4.3, gw = 8.4, span = 46, cx = (c) => gx + (c / span) * gw;
  // cycle ruler
  for (let c = 0; c <= span; c++) {
    const major = [0, 22, 23, 40].includes(c);
    line(s, cx(c), 2.25 - (major ? 0.14 : 0.06), 0, major ? 0.14 : 0.06, major ? K.muted : K.dim, 0.75);
  }
  line(s, gx, 2.25, gw, 0, K.dim, 0.75);
  [[0, "N"], [22, "N+22"], [40, "N+40"]].forEach(([c, l]) => t(s, l, { x: cx(c) - 0.5, y: 1.78, w: 1.0, h: 0.26, align: "center", fontFace: M, fontSize: 11, color: K.muted }));
  // frame A
  const ya = 2.75, hb = 0.62;
  t(s, "Frame A", { x: gx, y: ya - 0.33, w: 2, h: 0.28, fontFace: M, fontSize: 11, color: K.muted });
  rect(s, { x: cx(0), y: ya, w: cx(22) - cx(0) - 0.03, h: hb, fill: { color: K.teal } });
  t(s, "7 × multiply-accumulate", { x: cx(0) + 0.15, y: ya, w: 3.8, h: hb, valign: "middle", fontSize: 15, bold: true, color: K.bg });
  rect(s, { x: cx(22), y: ya, w: cx(40) - cx(22), h: hb, fill: { color: K.amber } });
  t(s, "CORDIC direction", { x: cx(22) + 0.15, y: ya, w: 3.0, h: hb, valign: "middle", fontSize: 15, bold: true, color: K.bg });
  // frame B
  const yb = 3.95;
  t(s, "Frame B", { x: cx(23) + 0.12, y: yb - 0.33, w: 2, h: 0.28, fontFace: M, fontSize: 11, color: K.muted });
  rect(s, { x: cx(23), y: yb, w: cx(span) - cx(23), h: hb, fill: { color: K.teal, transparency: 35 } });
  t(s, "accepted at N+23 …", { x: cx(23) + 0.15, y: yb, w: 3.5, h: hb, valign: "middle", fontSize: 15, bold: true, color: K.bg });
  // markers
  line(s, cx(23), 2.25, 0, 3.0, K.text, 1, { line: { color: K.text, width: 1, dashType: "dash" } });
  line(s, cx(40), 2.25, 0, 3.0, K.teal, 1, { line: { color: K.teal, width: 1, dashType: "dash" } });
  // brackets
  const by = 5.0;
  line(s, cx(0), by, cx(23) - cx(0), 0, K.text, 1.25, { line: { color: K.text, width: 1.25, beginArrowType: "arrow", endArrowType: "arrow" } });
  t(s, "acceptance interval · 23", { x: cx(0), y: by + 0.1, w: cx(23) - cx(0), h: 0.3, align: "center", fontFace: M, fontSize: 12, color: K.text });
  line(s, cx(0), by + 0.65, cx(40) - cx(0), 0, K.teal, 1.25, { line: { color: K.teal, width: 1.25, beginArrowType: "arrow", endArrowType: "arrow" } });
  t(s, "latency · 40  →  forecast_valid", { x: cx(0), y: by + 0.75, w: cx(40) - cx(0), h: 0.3, align: "center", fontFace: M, fontSize: 12, color: K.teal });
  t(s, "An idle clock is not another hour: history shifts only on accepted frames.", { x: X0, y: 6.42, w: CW, h: 0.3, fontSize: 13, color: K.dim });
}

// 10 — Verification ladder ----------------------------------------------------------
{
  const s = slide("SIGNAL", "Talk", "09 · VERIFICATION", "Three independent checks, each closer to silicon");
  const st = [
    ["STAGE 1", "RTL + DPI-C", "1,124", "forecasts checked", "from 1,200 accepted frames", "C++ golden model, cycle-level scoreboard"],
    ["STAGE 2", "Core SDF", "264", "forecasts checked", "from 288 input frames", "Gate-level netlist, max delays, 20 ns clock"],
    ["STAGE 3", "Physical JTAG", "104", "forecasts checked", "from 128 input frames", "Real responses read from the DE2 board"],
  ];
  const w = 3.65, g = (CW - 3 * w) / 2, y = 1.95, h = 3.6;
  st.forEach((r, i) => {
    const x = X0 + i * (w + g), hot = i === 2;
    rrect(s, { x, y, w, h, fill: { color: hot ? K.panel2 : K.panel }, line: hot ? { color: K.teal, width: 1.25 } : { type: "none" }, shadow: shadow() });
    t(s, r[0], { x: x + 0.35, y: y + 0.3, w: 2, h: 0.28, fontFace: M, fontSize: 11, color: K.dim, charSpacing: 2 });
    t(s, r[1], { x: x + 0.35, y: y + 0.6, w: w - 0.6, h: 0.4, fontSize: 20, bold: true });
    t(s, r[2], { x: x + 0.3, y: y + 1.15, w: w - 0.6, h: 1.0, fontSize: 64, bold: true, color: hot ? K.teal : K.text });
    t(s, r[3], { x: x + 0.35, y: y + 2.15, w: w - 0.6, h: 0.3, fontSize: 15, bold: true, color: hot ? K.teal : K.text });
    t(s, r[4], { x: x + 0.35, y: y + 2.45, w: w - 0.6, h: 0.3, fontSize: 14, color: K.muted });
    t(s, r[5], { x: x + 0.35, y: y + 2.95, w: w - 0.6, h: 0.5, fontSize: 12, color: K.dim });
    if (i < 2) arrow(s, x + w + 0.08, y + h / 2, g - 0.16, K.dim);
  });
  t(s, "CHECKED AT EVERY STAGE", { x: X0, y: 5.95, w: 3, h: 0.42, valign: "middle", fontFace: M, fontSize: 11, color: K.dim, charSpacing: 1 });
  let x = X0 + 2.95;
  [["Values", 1.1], ["Transaction order", 2.0], ["Reset behavior", 1.75], ["Cycle timing", 1.55]].forEach(([l, w2]) => { chip(s, x, 5.95, w2, l, { size: 13 }); x += w2 + 0.2; });
}

// 11 — Accuracy charts ---------------------------------------------------------------
{
  const s = slide("SIGNAL", "Talk", "10 · ACCURACY", "The model beats both baselines on every quantity");
  const data = [
    ["Temperature", "°C", [0.507906, 2.080369, 0.83228], 2],
    ["Pressure", "kPa", [0.0346, 0.135167, 0.085775], 3],
    ["Humidity", "pp", [2.614292, 8.831186, 3.804237], 2],
    ["Wind speed", "m/s", [0.566878, 0.830494, 0.891217], 2],
    ["Direction", "degrees", [18.084598, 21.42381, 35.292273], 1],
  ];
  const cw = 2.3, gap = (CW - 5 * cw) / 4;
  data.forEach(([name, unit, v, dp], i) => {
    const x = X0 + i * (cw + gap);
    const best = Math.min(v[1], v[2]);
    const gain = Math.round((1 - v[0] / best) * 100);
    t(s, name, { x, y: 1.9, w: cw, h: 0.34, fontSize: 18, bold: true });
    t(s, `MAE · ${unit}`, { x, y: 2.25, w: cw, h: 0.26, fontFace: M, fontSize: 11, color: K.dim });
    t(s, `−${gain}%`, { x, y: 2.6, w: cw, h: 0.55, fontSize: 30, bold: true, color: K.teal });
    t(s, "vs best baseline", { x, y: 3.13, w: cw, h: 0.26, fontSize: 12, color: K.muted });
    s.addChart(pres.charts.BAR, [{ name: "MAE", labels: ["Model", "Latest", "Prev. day"], values: v }], {
      x: x - 0.1, y: 3.5, w: cw + 0.2, h: 2.6, barDir: "col", barGapWidthPct: 35,
      chartColors: [K.teal, "5B6B80", "34465F"], showLegend: false, showTitle: false,
      showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: dp === 3 ? "0.000" : dp === 1 ? "0.0" : "0.00",
      dataLabelColor: K.text, dataLabelFontSize: 11, dataLabelFontFace: "+mn-lt",
      catAxisLabelColor: K.muted, catAxisLabelFontSize: 10, catAxisLabelFontFace: "+mn-lt", catAxisLineShow: true, catAxisLineColor: K.line,
      valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
      valAxisMinVal: 0, valAxisMaxVal: Math.max(...v) * 1.22,
      plotArea: { fill: { color: K.bg, transparency: 100 } },
    });
  });
  t(s, "2025 test set · 8,757 scalar targets · direction: 8,593 non-calm targets (≥ 0.5 m/s), ideal decoding of quantized components", { x: X0, y: 6.42, w: CW, h: 0.3, fontSize: 12, color: K.dim });
}

// 11b — Accuracy in context ------------------------------------------------------------
{
  const s = slide("SIGNAL", "Talk", "11 · IN CONTEXT", "Against the same persistence baseline at 3 hours", [
    "Fair yardstick: raw MAE cannot be compared across sites, variables and seasons, so each model is scored against its own paper's persistence forecast at the same 3-hour horizon: reduction = 1 - MAE_model / MAE_persistence.",
    "This work: 2025 test set, 8,757 hourly targets, Ho Chi Minh City 2 m air temperature (NASA POWER). Persistence MAE 2.080 C, deployed fixed-point model 0.508 C, reduction 75.6%.",
    "Li, Zhou, Wu, Ren, Guo, Chen, Lin (2025), 'A Hybrid Method for Winter Road Surface Temperature Prediction Using Improved LSTMs and Stacking-Based Ensemble Learning', EGUsphere preprint egusphere-2025-3638, https://doi.org/10.5194/egusphere-2025-3638 . Table 5, 3-hour horizon: persistence MAE 2.497 C, ILES 1.268 C (the paper itself reports a 49.22% reduction), RF 1.415 C, LSTM 1.453 C. Reductions for RF and LSTM are computed by us from Table 5. Data: road meteorological station M9393, Jiangsu, winters Dec 2020 - Feb 2024. Target is road-surface temperature, not air temperature.",
    "Caveat for questions: this is not a head-to-head contest. Different site, variable, season and climate. It only shows that our gain over the naive baseline is at least in the range reported by a recent deep-learning study using the same baseline definition (value at t+h equals value at t).",
    "Planned speaking time: 50 seconds.",
  ].join("\n"));
  const rows = [
    ["This work", "7-lag linear model on FPGA", 1 - 0.507906 / 2.080369, true],
    ["Li et al. 2025", "ILES stacked LSTM ensemble", 1 - 1.268 / 2.497],
    ["Li et al. 2025", "Random forest", 1 - 1.415 / 2.497],
    ["Li et al. 2025", "LSTM", 1 - 1.453 / 2.497],
  ];
  t(s, "MAE REDUCTION VERSUS PERSISTENCE · 3-HOUR HORIZON", { x: X0, y: 1.95, w: 7.4, h: 0.28, fontFace: M, fontSize: 11, color: K.dim, charSpacing: 1 });
  const bx = X0 + 2.75, bw = 4.15, y0 = 2.45, rh = 0.82;
  rows.forEach(([who, what, v, ours], i) => {
    const y = y0 + i * rh;
    t(s, who, { x: X0, y: y + 0.02, w: 2.6, h: 0.3, fontSize: 15, bold: true, color: ours ? K.teal : K.text });
    t(s, what, { x: X0, y: y + 0.33, w: 2.6, h: 0.28, fontSize: 12, color: K.muted });
    rect(s, { x: bx, y: y + 0.08, w: bw, h: 0.46, fill: { color: K.panel } });
    rect(s, { x: bx, y: y + 0.08, w: bw * v, h: 0.46, fill: { color: ours ? K.teal : "5B6B80" } });
    t(s, `${(v * 100).toFixed(1)}%`, { x: bx + bw * v + 0.12, y: y + 0.08, w: 1.1, h: 0.46, valign: "middle", fontFace: M, fontSize: 16, bold: true, color: ours ? K.teal : K.text });
  });
  t(s, [{ text: "reduction  =  1 − MAE", options: {} }, { text: "model", options: { subscript: true } }, { text: " / MAE", options: {} }, { text: "persistence", options: { subscript: true } }],
    { x: X0, y: y0 + 4 * rh + 0.1, w: 7.4, h: 0.4, fontSize: 16, color: K.muted });

  // side-by-side facts
  const px = 8.75, pw = 3.98;
  rrect(s, { x: px, y: 1.95, w: pw, h: 4.25, fill: { color: K.panel } });
  const facts = [
    ["Target", "2 m air temp.", "Road surface"],
    ["Site", "Ho Chi Minh City", "Jiangsu, China"],
    ["Test data", "2025, all year", "Winters 2020–24"],
    ["Persistence", "2.08 °C", "2.50 °C"],
    ["Best model", "0.51 °C", "1.27 °C"],
    ["Runs on", "FPGA, 18-bit", "Software, float"],
  ];
  t(s, "THIS WORK", { x: px + 1.3, y: 2.2, w: 1.3, h: 0.26, fontFace: M, fontSize: 10, color: K.teal, charSpacing: 1 });
  t(s, "LI ET AL.", { x: px + 2.65, y: 2.2, w: 1.3, h: 0.26, fontFace: M, fontSize: 10, color: K.muted, charSpacing: 1 });
  facts.forEach(([k, a, b], i) => {
    const y = 2.6 + i * 0.58;
    line(s, px + 0.25, y - 0.08, pw - 0.5, 0, K.line, 0.5);
    t(s, k, { x: px + 0.25, y, w: 1.05, h: 0.45, fontSize: 12, color: K.dim });
    t(s, a, { x: px + 1.3, y, w: 1.3, h: 0.45, fontSize: 12, color: K.text });
    t(s, b, { x: px + 2.65, y, w: 1.25, h: 0.45, fontSize: 12, color: K.muted });
  });
  t(s, "Different site, variable and season: each model is scored only against its own persistence baseline.", { x: X0, y: 6.42, w: CW, h: 0.3, fontSize: 13, color: K.dim });
  t(s, "Source: Li et al. 2025, EGUsphere, doi:10.5194/egusphere-2025-3638, Table 5", { x: 5.6, y: 6.98, w: 6.2, h: 0.3, fontFace: M, fontSize: 9, color: K.dim, align: "right" });
}

// 12 — Quartus fit -------------------------------------------------------------------
{
  const s = slide("SIGNAL", "Talk", "12 · IMPLEMENTATION", "The design fits in a fifth of the Cyclone II");
  const stats = [
    ["6,253", "logic elements", "19% of EP2C35F672C6", K.teal],
    ["6", "18 × 18 multipliers", "12 of 70 nine-bit elements", K.text],
    ["50 MHz", "physical test clock", "+7.459 ns setup slack", K.text],
    ["79.74 MHz", "fitted Fmax estimate", "not a measured clock sweep", K.muted],
  ];
  stats.forEach(([big, lbl, sub, c], i) => {
    const x = X0 + (i % 2) * 2.55, y = 1.95 + Math.floor(i / 2) * 2.05;
    t(s, big, { x, y, w: 2.5, h: 0.75, fontSize: i < 2 ? 44 : 32, bold: true, color: c, valign: "bottom" });
    t(s, lbl, { x, y: y + 0.8, w: 2.4, h: 0.3, fontSize: 15, bold: true });
    t(s, sub, { x, y: y + 1.1, w: 2.4, h: 0.5, fontSize: 12, color: K.muted });
  });
  // native Quartus Flow Summary, cropped (bytes untouched)
  const fx = 6.05, fy = 1.95, fw = 6.68;
  const crop = { x: 515, y: 110, w: 885, h: 452 };
  const fh = crop.h * (fw / crop.w);
  rect(s, { x: fx - 0.08, y: fy - 0.08, w: fw + 0.16, h: fh + 0.16, fill: { color: K.panel2 }, shadow: shadow() });
  const { k } = screenshot(s, "image.png", [2448, 1378], crop, fx, fy, fw);
  // highlight rows: logic elements (y≈335) and multipliers (y≈518)
  [[322, K.teal], [505, K.teal]].forEach(([py, c]) => {
    s.addShape(pres.shapes.RECTANGLE, { x: fx + (515 - crop.x) * k, y: fy + (py - crop.y) * k, w: 662 * k, h: 26 * k, fill: { type: "none" }, line: { color: c, width: 1.75 } });
  });
  t(s, "Native Quartus II 13.0 Flow Summary · uninstrumented JTAG build · no values altered", { x: fx, y: fy + fh + 0.2, w: fw, h: 0.26, fontFace: M, fontSize: 9, color: K.dim });
  t(s, "Fit includes the board JTAG wrapper and excludes SignalTap. Timing panels in backup B5.", { x: X0, y: 6.42, w: CW, h: 0.3, fontSize: 13, color: K.dim });
}

// 12b — Hardware in context ------------------------------------------------------------
{
  const s = slide("SIGNAL", "Talk", "13 · IN CONTEXT", "Published FPGA predictors: different devices, same idea", [
    "No ranking is implied: LEs (Intel/Altera), LUTs and slices (Xilinx) are different units, and timing evidence ranges from board measurement to synthesis estimates. The table states what each paper reports and how.",
    "Vasquez, Perez, Travieso, Alonso, 'Meteorological Prediction Implemented on Field-Programmable Gate Array', Cognitive Computation 5 (2013) 551-557, doi:10.1007/s12559-012-9158-z. MLP temperature predictor in fixed point, Xilinx System Generator, fully parallel, maximum delay 74 ns. Taken from the abstract; full text and resource table not inspected.",
    "Ferreira, Grout, da Silva, 'FPGA hardware linear regression implementation using fixed-point arithmetic', SBCCI 2019, doi:10.1145/3338852.3339853. Cyclone IV EP4CE115 (DE2-115): 8% of 114,480 LEs, 89% of 532 embedded multipliers; signed 32-bit, 16 fraction bits; authors report one clock cycle per regression/prediction, no Fmax given. PDF p. 4, Table 1.",
    "Silva, da Silva, Dias, Fernandes, 'Prediction Techniques on FPGA for Latency Reduction on Tactile Internet', Sensors 22(9) 3556 (2022), doi:10.3390/s22093556. Virtex-6 xc6vlx240t, one LR instance: 198 registers, 3,440 LUTs, 9 multipliers, 32-bit float, processing time 40.25 ns. Table 2.",
    "Royer et al., 'Area-Efficient Linear Regression Architecture for Real-Time Signal Processing on FPGAs', DCIS 2011. 256-sample version: 66 slices, 5 DSP48E, estimated maximum frequency 458 MHz. Section V, Table II. Estimated timing only.",
    "This work: Quartus II 13.0 fit of the uninstrumented JTAG build, 6,253 LEs, 12 nine-bit multiplier elements, fitted Fmax 79.74 MHz; 40-cycle documented RTL latency = 0.80 us at the 50 MHz physical test clock; 104 physical forecasts checked bit-exact against the C++ reference.",
    "Details of all four papers: docs/specs/ols_fpga_literature_review.md.",
    "Planned speaking time: 50 seconds.",
  ].join("\n"));
  const cols = [["Design", 2.35], ["Task", 2.5], ["Device · arithmetic", 2.35], ["Resources", 2.25], ["Timing", 2.68]];
  const head = cols.map(([h]) => ({ text: h.toUpperCase(), options: { fontFace: M, fontSize: 10, color: K.dim, charSpacing: 1, fill: { color: K.bg, transparency: 100 }, border: [{ type: "none" }, { type: "none" }, { pt: 1, color: K.line }, { type: "none" }] } }));
  const data = [
    [["This work", "CE436 · 2026"], ["5 weather quantities, 6 lanes × 7 taps", ""], ["Cyclone II EP2C35", "18-bit fixed point"], ["6,253 LEs", "12 × 9-bit multipliers"], ["0.80 µs · 40 cycles", "RTL latency, 50 MHz board clock"]],
    [["Vásquez et al.", "Cogn. Comput. 2013"], ["Temperature, MLP network", ""], ["Xilinx", "fixed point"], ["not reported in abstract", ""], ["74 ns max. delay", "abstract-reported"]],
    [["Ferreira et al.", "SBCCI 2019"], ["Linear regression fit + 8 predictions", ""], ["Cyclone IV EP4CE115", "32-bit fixed point"], ["8% of 114,480 LEs", "89% of 532 multipliers"], ["“one clock cycle”", "no Fmax reported"]],
    [["Silva et al.", "Sensors 2022"], ["Rolling linear-regression predictor", ""], ["Virtex-6", "32-bit float"], ["3,440 LUTs", "9 multipliers"], ["40.25 ns processing", "synthesis result"]],
    [["Royer et al.", "DCIS 2011"], ["Block linear-regression fit", ""], ["Xilinx DSP48E", "fixed point"], ["66 slices", "5 DSP48E"], ["458 MHz Fmax", "estimate"]],
  ];
  const body = data.map((r, i) => r.map(([a, b], j) => ({
    text: [
      { text: a, options: { fontSize: 13, bold: j === 0 || i === 0, color: i === 0 ? (j === 0 ? K.teal : K.text) : K.text, breakLine: !!b } },
      ...(b ? [{ text: b, options: { fontSize: 11, color: i === 0 && j === 4 ? K.teal : K.muted } }] : []),
    ],
    options: { fill: { color: i === 0 ? K.panel2 : K.bg, transparency: i === 0 ? 0 : 100 }, border: [{ type: "none" }, { type: "none" }, { pt: 0.5, color: K.line }, { type: "none" }], valign: "middle", margin: [0.07, 0.12, 0.07, 0.12] },
  })));
  s.addTable([head, ...body], { x: X0, y: 1.9, w: CW, colW: cols.map((c) => c[1]), rowH: [0.38, 0.72, 0.72, 0.72, 0.72, 0.72], fontFace: H, color: K.text });
  t(s, "LEs, LUTs and slices are different units, and timing evidence ranges from board tests to estimates: context, not a ranking.", { x: X0, y: 6.42, w: CW, h: 0.3, fontSize: 13, color: K.dim });
}

// 13 — SignalTap ----------------------------------------------------------------------
{
  const s = slide("SIGNAL", "Talk", "14 · ON THE BOARD", "A forecast captured on the physical board");
  const crop = { x: 10, y: 60, w: 2430, h: 385 };
  const fx = X0, fy = 2.3, fw = CW;
  const fh = crop.h * (fw / crop.w);
  rect(s, { x: fx - 0.06, y: fy - 0.06, w: fw + 0.12, h: fh + 0.12, fill: { color: K.panel2 }, shadow: shadow() });
  const { k } = screenshot(s, "image2.png", [2448, 530], crop, fx, fy, fw);
  // annotate acceptance (x≈985) and forecast_valid (x≈1543) in source px
  [[985, "frame accepted", K.text], [1543, "forecast_valid", K.teal]].forEach(([px, lbl, c]) => {
    const ax = fx + (px - crop.x) * k;
    line(s, ax, fy - 0.3, 0, 0.3, c, 1.5);
    t(s, lbl, { x: ax - 1.0, y: fy - 0.6, w: 2.0, h: 0.28, align: "center", fontFace: M, fontSize: 12, bold: true, color: c });
  });
  const y = 5.05;
  t(s, "104", { x: X0, y, w: 2.2, h: 1.0, fontSize: 64, bold: true, color: K.teal });
  t(s, "forecasts checked\nfrom 128 input frames", { x: X0 + 2.15, y: y + 0.2, w: 2.4, h: 0.7, fontSize: 15, color: K.text });
  line(s, 5.0, y + 0.1, 0, 1.0, K.line, 0.75);
  t(s, "temperature_out_q8", { x: 5.35, y: y + 0.05, w: 3.5, h: 0.28, fontFace: M, fontSize: 11, color: K.dim });
  t(s, [{ text: "01A72h", options: { color: K.text } }, { text: "  →  6770 / 256  →  ", options: { color: K.muted } }, { text: "26.4453 °C", options: { color: K.teal, bold: true } }], { x: 5.35, y: y + 0.4, w: 5.5, h: 0.45, fontFace: M, fontSize: 19 });
  t(s, "41 acquisition intervals ≈ documented 40-cycle RTL latency (sampling convention)", { x: 5.35, y: y + 0.95, w: 7.3, h: 0.3, fontSize: 13, color: K.muted });
  t(s, "Native SignalTap capture, separately instrumented build · STP and decoded CSV retained", { x: X0, y: fy + fh + 0.15, w: CW, h: 0.26, fontFace: M, fontSize: 9, color: K.dim });
}

// 14 — Scope ---------------------------------------------------------------------------
{
  const s = slide("SIGNAL", "Talk", "15 · SCOPE", "What we demonstrated, and what we did not claim");
  const w = (CW - 0.4) / 2, y = 1.95, h = 4.1;
  const cols = [
    { x: X0, head: "Demonstrated", c: K.teal, fill: K.panel2, mark: "✓", items: ["Five quantities forecast on the FPGA", "Recorded observations replayed over JTAG", "Fixed, pre-trained coefficients", "Physical replay at 50 MHz"] },
    { x: X0 + w + 0.4, head: "Further work", c: K.muted, fill: K.panel, mark: "○", items: ["Live sensor acquisition", "Other sites and years", "Rainfall probability", "Power measurement and clock sweep"] },
  ];
  cols.forEach((c) => {
    rrect(s, { x: c.x, y, w, h, fill: { color: c.fill } });
    t(s, c.head, { x: c.x + 0.45, y: y + 0.35, w: w - 0.9, h: 0.45, fontSize: 24, bold: true, color: c.c === K.teal ? K.teal : K.text });
    c.items.forEach((it, i) => {
      const iy = y + 1.2 + i * 0.75;
      t(s, c.mark, { x: c.x + 0.45, y: iy, w: 0.4, h: 0.4, fontSize: 20, bold: true, color: c.c });
      t(s, it, { x: c.x + 0.95, y: iy + 0.02, w: w - 1.4, h: 0.4, fontSize: 18, color: c.c === K.teal ? K.text : K.muted });
    });
  });
  t(s, "Hourly forecasting does not need sub-microsecond speed: the contribution is a verified hardware implementation and its schedule.", { x: X0, y: 6.42, w: CW, h: 0.3, fontSize: 13, color: K.dim });
}

// 15 — Closing -------------------------------------------------------------------------
{
  const s = slide("COVER", "Talk");
  s.addImage({ path: path.join(B, "trace_cover.png"), x: -0.1, y: 3.95, w: 13.55, h: 3.73, transparency: 55 });
  t(s, "CE436  ·  FINAL DEFENSE", { x: X0, y: 0.6, w: 8, h: 0.3, fontFace: M, fontSize: 12, color: K.teal, charSpacing: 2 });
  t(s, "Weather inference,\nverified on FPGA", { x: X0, y: 1.05, w: 9, h: 1.8, fontSize: 52, bold: true, lineSpacingMultiple: 0.9 });
  const st = [["5", "forecast quantities"], ["0.80 µs", "RTL latency at 50 MHz"], ["104", "physical forecasts checked"]];
  st.forEach(([b, l], i) => {
    const x = X0 + i * 3.3;
    t(s, b, { x, y: 3.25, w: 3.1, h: 0.85, fontSize: 48, bold: true, color: K.teal });
    t(s, l, { x, y: 4.1, w: 3.1, h: 0.3, fontSize: 15, color: K.muted });
  });
  t(s, "THANK YOU  ·  QUESTIONS?", { x: 7.5, y: 0.6, w: 5.23, h: 0.3, fontFace: M, fontSize: 12, color: K.text, charSpacing: 2, align: "right" });
}

// =====================================================================
pres.addSection({ title: "Backup" });
const tbl = (rows, colW, o = {}) => rows.map((r, i) => r.map((c) => ({
  text: String(c),
  options: Object.assign({
    fontFace: o.mono && i > 0 ? M : H, fontSize: i === 0 ? 12 : 14, bold: i === 0, color: i === 0 ? K.inkMuted : K.ink,
    fill: { color: i === 0 ? K.tint : K.paper }, border: [{ type: "none" }, { type: "none" }, { pt: 0.75, color: K.rule }, { type: "none" }],
    margin: [0.06, 0.12, 0.06, 0.12], valign: "middle",
  }, typeof c === "object" ? {} : {}),
})));
function backup(code, title) {
  const s = slide("BACKUP", "Backup", `BACKUP · ${code}`, title);
  s.hidden = true;
  return s;
}
const bt = (s, text, o) => t(s, text, Object.assign({ color: K.ink }, o));

{ // B1
  const s = backup("B1", "The original temperature model: a seasonal anchor and two corrections");
  rrect(s, { x: X0, y: 2.05, w: CW, h: 0.95, fill: { color: K.tint } });
  bt(s, "T̂(t + 3)  =  T(t − 21)  +  a·Δdaily  +  b·Δrecent  +  c", { x: X0 + 0.4, y: 2.05, w: CW - 0.8, h: 0.95, valign: "middle", fontFace: H, fontSize: 26, color: K.tealInk });
  bt(s, "Δdaily  = T(t) − T(t − 24)\nΔrecent = T(t) − T(t − 3)", { x: X0, y: 3.4, w: 5.5, h: 1.0, fontFace: M, fontSize: 16 });
  s.addTable(tbl([["Parameter", "Fitted value"], ["a", "0.7454870439"], ["b", "0.0091494450"], ["c", "0.0011295817 °C"]], null, { mono: true }), { x: 7.2, y: 3.35, w: 5.53, colW: [1.8, 3.73] });
  bt(s, [{ text: "Temperature test MAE   ", options: { color: K.inkMuted } }, { text: "0.538017 °C", options: { bold: true } }, { text: " prototype   →   ", options: { color: K.inkMuted } }, { text: "0.507906 °C", options: { bold: true, color: K.tealInk } }, { text: " current model", options: { color: K.inkMuted } }], { x: X0, y: 5.9, w: CW, h: 0.4, fontSize: 16 });
}
{ // B2
  const s = backup("B2", "The temperature lane: seven deployed weights and a Q8 bias");
  const rows = [["Lag (h)", "Input Q8", "Weight Q14", "Product"], ["0", "7680", "20035", "153868800"], ["1", "7552", "−9335", "−70497920"], ["3", "7168", "1621", "11619328"], ["6", "6912", "−205", "−1416960"], ["12", "6656", "15", "99840"], ["21", "7936", "13908", "110373888"], ["24", "7424", "−10382", "−77075968"]];
  s.addTable(tbl(rows, null, { mono: true }), { x: X0, y: 1.95, w: 7.6, colW: [1.3, 1.8, 1.9, 2.6], rowH: 0.42 });
  rrect(s, { x: 8.75, y: 1.95, w: 3.98, h: 3.36, fill: { color: K.tint } });
  bt(s, "SUM INCLUDING ALIGNED BIAS", { x: 9.1, y: 2.25, w: 3.4, h: 0.28, fontFace: M, fontSize: 11, color: K.inkMuted });
  bt(s, "S = 132050048", { x: 9.1, y: 2.6, w: 3.4, h: 0.45, fontFace: M, fontSize: 20, bold: true });
  bt(s, "SCALE BACK TO Q8", { x: 9.1, y: 3.4, w: 3.4, h: 0.28, fontFace: M, fontSize: 11, color: K.inkMuted });
  bt(s, "⌊S / 16384⌋ = 8059", { x: 9.1, y: 3.75, w: 3.4, h: 0.45, fontFace: M, fontSize: 20, bold: true, color: K.tealInk });
  bt(s, "8059 / 256 = 31.48 °C", { x: 9.1, y: 4.35, w: 3.4, h: 0.4, fontFace: M, fontSize: 15, color: K.inkMuted });
}
{ // B3
  const s = backup("B3", "Test errors keep the physical unit of each quantity");
  const rows = [["Target", "MAE", "RMSE"], ["Temperature (°C)", "0.507906", "0.730939"], ["Pressure (kPa)", "0.034600", "0.044638"], ["Humidity (percentage points)", "2.614292", "3.685767"], ["Wind speed (m/s)", "0.566878", "0.750218"], ["Direction (degrees)", "18.084598", "30.201056"]];
  const tr = tbl(rows);
  tr.forEach((r, i) => { if (i) { r[1].options.fontFace = M; r[2].options.fontFace = M; } });
  s.addTable(tr, { x: X0, y: 1.95, w: CW, colW: [6.13, 3, 3], rowH: 0.48 });
  bt(s, "8,757 scalar targets. Direction: 8,593 targets with wind speed ≥ 0.5 m/s, ideal atan2 of quantized components. CORDIC maximum conversion error: 0.005635°.", { x: X0, y: 5.25, w: CW, h: 0.6, fontSize: 14, color: K.inkMuted });
}
{ // B4
  const s = backup("B4", "Each lane repeats operand, product and accumulate for seven terms");
  const rows = [["Edge", "Operation"], ["N", "Accept frame, shift history, initialize bias"], ["N + 1", "Capture lag-0 operand"], ["N + 2", "Capture product"], ["N + 3", "Add product to accumulator"], ["N + 4 … N + 21", "Repeat for the remaining six terms"], ["N + 22", "Scale, limit and publish lane result"], ["N + 23", "Earliest next eligible acceptance"]];
  const tr = tbl(rows);
  tr.forEach((r, i) => { if (i) r[0].options.fontFace = M; });
  s.addTable(tr, { x: X0, y: 1.95, w: CW, colW: [2.6, CW - 2.6], rowH: 0.44 });
  bt(s, "Synchronous active-low reset cancels pending work and restarts history eligibility.", { x: X0, y: 5.75, w: CW, h: 0.35, fontSize: 14, color: K.inkMuted });
}
{ // B5
  const s = backup("B5", "Native TimeQuest panels record the fitted timing margins");
  const w1 = 7.4;
  const c1 = { x: 516, y: 110, w: 976, h: 220 };
  const h1 = c1.h * w1 / c1.w;
  rect(s, { x: X0 - 0.04, y: 2.0 - 0.04, w: w1 + 0.08, h: h1 + 0.08, fill: { color: K.rule } });
  screenshot(s, "image3.png", [2448, 1378], c1, X0, 2.0, w1);
  const c2 = { x: 516, y: 110, w: 600, h: 90 };
  const w2 = 4.6, h2 = c2.h * w2 / c2.w;
  const y2 = 2.0 + h1 + 0.5;
  rect(s, { x: X0 - 0.04, y: y2 - 0.04, w: w2 + 0.08, h: h2 + 0.08, fill: { color: K.rule } });
  screenshot(s, "image4.png", [2448, 1378], c2, X0, y2, w2);
  bt(s, "PHYSICAL TEST CLOCK", { x: 8.75, y: 2.1, w: 3.9, h: 0.28, fontFace: M, fontSize: 11, color: K.inkMuted });
  bt(s, "50 MHz", { x: 8.75, y: 2.4, w: 3.9, h: 0.7, fontSize: 40, bold: true, color: K.tealInk });
  bt(s, "FITTED ESTIMATE", { x: 8.75, y: 3.4, w: 3.9, h: 0.28, fontFace: M, fontSize: 11, color: K.inkMuted });
  bt(s, "79.74 MHz", { x: 8.75, y: 3.7, w: 3.9, h: 0.7, fontSize: 40, bold: true });
  bt(s, "Setup slack 7.459 ns · hold 0.215 ns", { x: 8.75, y: 4.5, w: 3.9, h: 0.3, fontSize: 14, color: K.inkMuted });
}
{ // B6
  const s = backup("B6", "The original SignalTap acquisition with decoded buses and trigger");
  const c = { x: 0, y: 40, w: 2448, h: 1338 };
  const h = 4.85, w = c.w * h / c.h;
  const x = (W - w) / 2;
  rect(s, { x: x - 0.04, y: 1.9 - 0.04, w: w + 0.08, h: h + 0.08, fill: { color: K.rule } });
  screenshot(s, "image5.png", [2448, 1378], c, x, 1.9, w);
}
{ // B7
  const s = backup("B7", "The JTAG mailbox holds each request and keeps the completed forecast");
  const steps = ["Stage payload", "Toggle request", "Wait for acknowledgement", "Read stable result"];
  const w = 2.6, g = (CW - 4 * w) / 3, y = 2.4;
  steps.forEach((st, i) => {
    const x = X0 + i * (w + g);
    rrect(s, { x, y, w, h: 1.4, fill: { color: K.tint } });
    bt(s, String(i + 1).padStart(2, "0"), { x: x + 0.3, y: y + 0.25, w: 1, h: 0.35, fontFace: M, fontSize: 14, bold: true, color: K.tealInk });
    bt(s, st, { x: x + 0.3, y: y + 0.65, w: w - 0.5, h: 0.6, fontSize: 18, bold: true });
    if (i < 3) s.addShape(pres.shapes.LINE, { x: x + w + 0.06, y: y + 0.7, w: g - 0.12, h: 0, line: { color: K.inkMuted, width: 1.25, endArrowType: "triangle" } });
  });
  [["128-bit", "source word (host → FPGA)"], ["256-bit", "probe word (FPGA → host)"], ["1", "outstanding request at a time"]].forEach(([b, l], i) => {
    const x = X0 + i * 4.1;
    bt(s, b, { x, y: 4.45, w: 3.8, h: 0.7, fontSize: 36, bold: true, color: i < 2 ? K.tealInk : K.ink });
    bt(s, l, { x, y: 5.15, w: 3.8, h: 0.3, fontSize: 15, color: K.inkMuted });
  });
  bt(s, "Warm-up replies acknowledge without a forecast.", { x: X0, y: 5.95, w: CW, h: 0.3, fontSize: 14, color: K.inkMuted });
}
{ // B8
  const s = backup("B8", "Source records behind the model, implementation and physical results");
  const groups = [
    ["Model and evaluation", ["versions/weather_v2/models/model.json", "versions/weather_v2/reports/metrics.csv", "versions/weather_v2/data/weather.csv"]],
    ["Implementation", ["docs/reports/JTAG_IMPLEMENTATION_REPORT.md", "docs/reports/weather_speed_modelsim_timing.json"]],
    ["Physical session", ["docs/reports/defense_session/", "Native screenshots, replay logs, STP and decoded CSV"]],
    ["Related work", ["Li et al. 2025       doi:10.5194/egusphere-2025-3638", "Vásquez et al. 2013  doi:10.1007/s12559-012-9158-z", "Ferreira et al. 2019 doi:10.1145/3338852.3339853", "Silva et al. 2022    doi:10.3390/s22093556", "Royer et al. 2011    DCIS · docs/specs/ols_fpga_literature_review.md"]],
  ];
  groups.forEach(([h, items], i) => {
    const y = 1.95 + i * 1.18;
    line(s, X0, y - 0.15, CW, 0, K.rule, 0.75);
    bt(s, h, { x: X0, y, w: 3.5, h: 0.4, fontSize: 18, bold: true, color: K.tealInk });
    bt(s, items.join("\n"), { x: 4.4, y: y + 0.02, w: 8.3, h: 1.1, fontFace: M, fontSize: i === 3 ? 12 : 13 });
  });
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT, n, "slides");
})();
