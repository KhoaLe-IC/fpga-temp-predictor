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
  t(s, "Li et al., EGUsphere preprint 2025, doi:10.5194/egusphere-2025-3638, Table 5", { x: 7.0, y: 6.98, w: 4.8, h: 0.3, fontFace: M, fontSize: 9, color: K.dim, align: "right" });
}

