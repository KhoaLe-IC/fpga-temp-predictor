# Weather forecasting FPGA final defense

Open `output/Weather_Forecasting_FPGA_Final_Defense_EN.pptx`. This is the redesigned current deck. The separately named `Weather_Forecasting_FPGA_Final_Defense_Redesigned_EN.pptx` contains identical validated bytes. The previous visual version is retained in `archive/Weather_Forecasting_FPGA_Final_Defense_Before_Redesign_EN.pptx`.

The deck contains 15 main slides and eight hidden technical backups, B1–B8. Its rehearsal plan lasts 14 minutes 15 seconds, with 45 seconds reserved for pauses and speaker changes. These are speaker-note cues, not automatic slide advancement. Use PowerPoint's slide navigator to access hidden backups during questions.

Text, diagrams, five comparison charts, and five tables remain editable. Native Quartus and SignalTap screenshot files retain their original bytes. Cropped views enlarge the relevant application panes. The atmospheric cover artwork is an illustration and has no role in implementation evidence.

## Design references

See [Design references](DESIGN_REFERENCES.md) for the professional portfolio sources and visual decisions. This version uses Roboto and Roboto Condensed, a warm light canvas, dark hardware slides, and teal and amber emphasis. The earlier assertion–evidence template remains in `reference/` as historical design context.

## Content and evidence

The parent `FINAL_DEFENSE_15_MIN_BASELINE_EN.md` supplies the narrative and speaking plan. Its earlier uniform visual-direction instructions are superseded by this redesign. The deck focuses on the parallel weather-speed implementation. The temperature-only model supplies development history.

Source records include `versions/weather_v2/models/model.json`, `versions/weather_v2/reports/metrics.csv`, `docs/reports/JTAG_IMPLEMENTATION_REPORT.md`, the predictor-core SDF manifest, and the physical records under `docs/reports/defense_session/`.

Forecast error and hardware-reference agreement describe different comparisons. The deck identifies the uninstrumented fit, the separately instrumented capture, the 50 MHz physical test clock, the fitted Fmax estimate, and the SignalTap versus RTL observation conventions.

## Build and review

Current authoring source: `.build/redesign.mjs`. Finalization: `.build/finalize_redesign.mjs`. Both use the bundled Artifact Tool runtime. Private finalization receipt: `.build/redesign/final.validation.json`. Review renders: `.build/redesign/final_renders/`.

All 23 slides were rendered and individually reviewed. The final export was rendered again. Its renders matched the reviewed authoring renders on 21 slides; slides 7 and 9 had minor rendering differences and were separately inspected. Package validation passed. All 15 chart values match the test metrics CSV within six-decimal rounding. The five native screenshot files were verified byte for byte in the PPTX. This review does not claim a native Microsoft PowerPoint execution test.
