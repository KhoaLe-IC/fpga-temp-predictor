"""One-off restyle of deck.js: neon dark -> Swiss editorial light."""
import re

s = open("deck.js").read()


def rep(a, b, cnt=1):
    global s
    n = s.count(a)
    assert n == cnt, (a[:70], n)
    s = s.replace(a, b)


# 1 palette and fonts
rep('''  bg: "0B1320", panel: "121D2E", panel2: "1A283D", line: "2A3A52", grid: "16233A",
  text: "EEF2F6", muted: "93A3B8", dim: "56677F",
  teal: "5EEAD4", tealDeep: "134E4A", amber: "FBBF24", amberDeep: "4A3710",''',
    '''  // Swiss/editorial: white page, ink text, institutional navy, one ochre accent
  bg: "FFFFFF", panel: "F4F6F9", panel2: "E8EDF3", line: "D5DCE5", grid: "F4F6F9",
  text: "0F172A", muted: "475569", dim: "64748B",
  teal: "1E3A5F", tealDeep: "E3EAF3", amber: "A16207", amberDeep: "FBF3E2",''')
rep('const H = "Calibri", M = "Consolas";', 'const H = "Calibri", M = "Consolas", SERIF = "Cambria";')
rep('name: "Signal and Silicon", headFontFace: H,', 'name: "Signal and Silicon", headFontFace: SERIF,')
rep('dk1: K.ink, lt1: K.paper, dk2: K.panel, lt2: K.text,', 'dk1: K.ink, lt1: K.paper, dk2: K.teal, lt2: K.panel,')
rep('accent1: K.teal, accent2: K.amber, accent3: K.muted, accent4: K.line,', 'accent1: K.teal, accent2: K.amber, accent3: K.muted, accent4: "94A3B8",')
rep('pres.theme = { headFontFace: H, bodyFontFace: H };', 'pres.theme = { headFontFace: SERIF, bodyFontFace: H };')

# 2 layouts
rep('background: { path: path.join(B, "graticule.png") },', 'background: { color: K.bg },')
rep('{ text: { text: "CE436  ·  WEATHER FORECASTING ON FPGA", options: { x: X0, y: 6.98, w: 6, h: 0.3, fontFace: M, fontSize: 9, color: K.dim, charSpacing: 1, margin: 0 } } },',
    '{ text: { text: "CE436 · Weather forecasting on FPGA", options: { x: X0, y: 6.98, w: 6, h: 0.3, fontFace: H, fontSize: 10, color: K.dim, margin: 0 } } },')
rep('{ text: { text: "BACKUP  ·  FOR QUESTIONS", options: { x: X0, y: 6.98, w: 6, h: 0.3, fontFace: M, fontSize: 9, color: K.inkMuted, charSpacing: 1, margin: 0 } } },',
    '{ text: { text: "Backup · for questions", options: { x: X0, y: 6.98, w: 6, h: 0.3, fontFace: H, fontSize: 10, color: K.inkMuted, margin: 0 } } },')
rep('fontFace: M, fontSize: 12, color: K.teal, charSpacing: 2, margin: 0, valign: "middle"',
    'fontFace: H, fontSize: 14, bold: true, color: K.amber, margin: 0, valign: "middle"')
rep('fontFace: M, fontSize: 12, color: K.tealInk, charSpacing: 2, margin: 0, valign: "middle"',
    'fontFace: H, fontSize: 14, bold: true, color: K.amberInk, margin: 0, valign: "middle"')
rep('fontFace: H, fontSize: 34, bold: true, color: K.text, margin: 0', 'fontFace: SERIF, fontSize: 32, bold: true, color: K.text, margin: 0')
rep('fontFace: H, fontSize: 28, bold: true, color: K.ink, margin: 0', 'fontFace: SERIF, fontSize: 26, bold: true, color: K.ink, margin: 0')
rep('slideNumber: { x: 11.93, y: 6.98, w: 0.8, h: 0.3, fontFace: M, fontSize: 9,', 'slideNumber: { x: 11.93, y: 6.98, w: 0.8, h: 0.3, fontFace: H, fontSize: 10,')

# 3 helpers
rep('  if (kicker) s.addText(kicker, { placeholder: "kicker" });',
    '''  if (kicker) {
    // "04 · MODEL" -> "04   Model": sentence case, no tracking
    const [a, b] = kicker.split(" · ");
    const label = a === "BACKUP" ? `Backup ${b}` : `${a}   ${b[0]}${b.slice(1).toLowerCase()}`;
    s.addText(label, { placeholder: "kicker" });
  }''')
rep('function t(s, text, o) { s.addText(text, Object.assign({ isTextBox: true, margin: 0, fontFace: H, color: K.text, valign: "top" }, o)); }',
    '''function t(s, text, o) {
  const big = o.fontSize >= 36 && !o.fontFace; // display numerals and headlines in the serif
  s.addText(text, Object.assign({ isTextBox: true, margin: 0, fontFace: big ? SERIF : H, color: K.text, valign: "top" }, o));
}''')
rep('function rrect(s, o) { s.addShape(pres.shapes.ROUNDED_RECTANGLE, Object.assign({ rectRadius: 0.08, line: { type: "none" } }, o)); }',
    'function rrect(s, o) { s.addShape(pres.shapes.ROUNDED_RECTANGLE, Object.assign({ line: { type: "none" } }, o, { rectRadius: 0.03 })); }')
rep('rrect(s, { x, y, w, h: 0.42, fill: { color: o.fill || K.panel2 }, line: o.border ? { color: o.border, width: 1 } : { type: "none" }, rectRadius: 0.21 });',
    'rrect(s, { x, y, w, h: 0.42, fill: { color: o.fill || K.bg }, line: { color: o.border || o.fill || K.line, width: 0.75 } });')
rep('function shadow() { return { type: "outer", color: "000000", blur: 18, offset: 6, angle: 90, opacity: 0.45 }; }',
    'function shadow() { return undefined; } // no drop shadows: hairlines and whitespace instead')

# 4 tracked uppercase labels -> sentence case
U = {'"CE436  ·  DISCRETE-TIME SIGNAL PROCESSING  ·  FINAL DEFENSE"': '"CE436 · Discrete-time signal processing · Final defense"',
     '"HOURS"': '"hours ahead"', 'k.toUpperCase()': 'k', '"ENCODE ON HOST"': '"Encode on host"', '"PREDICT ON FPGA"': '"Predict on FPGA"',
     '"RECONSTRUCT"': '"Reconstruct"', '"25-SAMPLE HISTORY  ·  7 TAPS"': '"25-sample history, 7 taps"', '"CYCLES LATENCY"': '"cycles of latency"',
     '"STAGE 1"': '"Stage 1"', '"STAGE 2"': '"Stage 2"', '"STAGE 3"': '"Stage 3"', '"CHECKED AT EVERY STAGE"': '"Checked at every stage"',
     '"MAE REDUCTION VERSUS PERSISTENCE · 3-HOUR HORIZON"': '"MAE reduction versus persistence, 3-hour horizon"', '"THIS WORK"': '"This work"', '"LI ET AL."': '"Li et al."',
     'h.toUpperCase()': 'h', '"CE436  ·  FINAL DEFENSE"': '"CE436 · Final defense"', '"THANK YOU  ·  QUESTIONS?"': '"Thank you. Questions?"',
     '"SUM INCLUDING ALIGNED BIAS"': '"Sum including aligned bias"', '"SCALE BACK TO Q8"': '"Scale back to Q8"', '"PHYSICAL TEST CLOCK"': '"Physical test clock"', '"FITTED ESTIMATE"': '"Fitted estimate"'}
for a, b in U.items():
    rep(a, b)
lines = s.split("\n")
for i, l in enumerate(lines):
    if "charSpacing" in l:
        l = l.replace("fontFace: M", "fontFace: H")
        lines[i] = re.sub(r",\s*charSpacing: \d+", "", l)

# 5 prose labels in mono -> body font; mono stays only for code-like values
frags = ['"Every line below is real data', '`Real 2025 test-set window', '"k = 1 … 7', '"← older"', '"lag ℓ in hours"', '"N · 0°"',
         '"16 iterations → θ̂"', '"Zero component pair', '"binary point"', '"integer bits"', '"fraction bits"', '"Frame A"', '"Frame B"',
         '"acceptance interval · 23"', '`MAE · ${unit}`', '"Source: Li et al. 2025', '"Native Quartus II 13.0', '"Native SignalTap capture',
         '`forecast ${', '`observed ${', 't(s, g.yr,', '`${(v * 100).toFixed(1)}%`', 'String(i + 1).padStart(2, "0")', '"1°"', '"359°"',
         'if (on) t(s, String(lag)']
for frag in frags:
    idx = [i for i, l in enumerate(lines) if frag in l]
    assert len(idx) == 1, (frag, idx)
    assert "fontFace: M" in lines[idx[0]], frag
    lines[idx[0]] = lines[idx[0]].replace("fontFace: M", "fontFace: H", 1)
s = "\n".join(lines)
rep('const lab = { fontFace: M, fontSize: 11, color: K.muted, h: 0.26 };', 'const lab = { fontFace: H, fontSize: 12, color: K.muted, h: 0.26 };')

# 6 data-mark colours
rep('chartColors: [K.teal, "5B6B80", "34465F"]', 'chartColors: [K.teal, "94A3B8", "CBD5E1"]')
rep('fill: { color: ours ? K.teal : "5B6B80" }', 'fill: { color: ours ? K.teal : "94A3B8" }')
rep('fill: { color: K.teal, transparency: 35 } });', 'fill: { color: "4A6587" } });')
rep('fill: { color: K.teal, transparency: 90 } });', 'fill: { color: K.tealDeep } });')

open("deck.js", "w").write(s)
print("restyled")
