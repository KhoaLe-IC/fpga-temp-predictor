# Claude revision of the final-defense deck

Output: `../output/Weather_Forecasting_FPGA_Claude_Revision_EN.pptx`. It has 17 main slides and 9 hidden backups (B1–B9). Every slide has speaker notes with timing cues that add up to about 14 minutes.

## Template

The deck is built on "Automotive Training Center" by SlidesCarnival, licensed under CC BY 4.0. The original file is in `template/`. The build keeps its master, theme, colours and embedded fonts (League Spartan, Poppins), but removes its sample slides and stock photos. The credit line is on backup B9.

## Rebuild

```bash
python3 src/assets.py <project_root> assets
python3 src/build.py <project_root> . <output.pptx>
src/render.sh <output.pptx> <render_dir>   # OnlyOffice x2t + pdftoppm
```

## Checks performed

- All 25 slides were rendered (`qa/`) and inspected.
- The five accuracy charts match `versions/weather_v2/reports/metrics.csv` (test split: selected_fixed, persistence, diurnal) exactly.
- The architecture and cycle schedule were checked against `weather_ar_channel.v`, `weather_predictor_speed.v`, `weather_system_speed.v` and `wind_direction_cordic.v`.
- Verification counts were checked against `speed_dpi.log`, the ModelSim SDF `simulation.log`, `weather_speed_physical_replay.txt` and `SIGNALTAP_CAPTURE_CHECK.json`.
- Package validation passed.

## Known limits

- The renders substitute Arial for League Spartan and Poppins, because neither font is installed on this machine. PowerPoint uses the fonts embedded in the file. Other apps without those fonts will fall back to Arial.
- The deck has not been opened in Microsoft PowerPoint.
- Slide 14 compares multipliers per value and time per value with published designs; the full table is backup B8.
- Student names are not on the cover; add them before presenting.
