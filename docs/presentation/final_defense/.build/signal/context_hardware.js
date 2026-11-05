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
    [["This work", "CE436 · 2026"], ["5 weather quantities, 6 lanes × 7 taps", ""], ["Cyclone II EP2C35", "18-bit fixed point"], ["6,253 LEs", "12 × 9-bit multipliers"], ["0.80 µs · 40 cycles", "measured on board at 50 MHz"]],
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
  t(s, "LEs, LUTs and slices are different units, and timing evidence ranges from board measurement to estimates: read across, not down.", { x: X0, y: 6.42, w: CW, h: 0.3, fontSize: 13, color: K.dim });
}

