# ==============================================================================
# DECK SLIDES 6 TO 11: BENCHMARKS, QUANTIZATION & ARITHMETIC INTEGRITY
# Streamlined "A word to the wise is enough" Edition
# Clean Academic White Theme (IEEE Navy, Slate, Green, Amber)
# ==============================================================================
import re
from deck_header import (
    C_BG, C_BG_PAGE, C_TEXT_MAIN, C_TEXT_SUB, C_TEXT_MUTED,
    C_NAVY, C_BLUE, C_BLUE_LIGHT, C_GREEN, C_GREEN_BG,
    C_AMBER, C_AMBER_BG, C_RED, C_PURPLE,
    C_BORDER, C_BORDER_DARK, C_CARD_WHITE, C_CARD_BG, C_CARD_ALT,
    svg_header, svg_footer, standard_header, standard_footer, write_slide
)

# ==============================================================================
# SLIDE 6: Algorithmic Benchmarks & Pareto Frontier
# ==============================================================================
def gen_slide_06():
    svg = svg_header("content")
    svg += standard_header("hdr_06", "ALGORITHMIC BENCHMARKS &amp; PARETO FRONTIER", 
                           "Model Comparison: Accuracy vs Silicon Footprint", 
                           "Held-out test dataset (17,520 hours) evaluating predictive accuracy against DSP demand")
    
    # Left Panel: Benchmark Table (760 px wide)
    svg += f"""  <g id="tbl_benchmarks" data-pptx-bounds="60 135 760 500">
    <rect x="60" y="135" width="760" height="500" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="60" y="135" width="760" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="80" y="162" fill="{C_NAVY}" font-size="14" font-weight="bold">HELD-OUT TEST SET ACCURACY (17,520 SAMPLES)</text>
    
    <!-- Table Header Row -->
    <rect x="80" y="195" width="720" height="32" rx="4" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="216" fill="{C_NAVY}" font-size="12" font-weight="bold">Architecture</text>
    <text x="270" y="216" fill="{C_NAVY}" font-size="12" font-weight="bold">MAE (°C)</text>
    <text x="380" y="216" fill="{C_NAVY}" font-size="12" font-weight="bold">RMSE (°C)</text>
    <text x="495" y="216" fill="{C_NAVY}" font-size="12" font-weight="bold">DSP Units</text>
    <text x="640" y="216" fill="{C_NAVY}" font-size="12" font-weight="bold">Latency</text>
    
    <!-- Row 1: Linear OLS (Selected) -->
    <rect x="80" y="235" width="720" height="46" rx="4" fill="{C_BLUE_LIGHT}" stroke="{C_BLUE}" stroke-width="1.5"/>
    <text x="95" y="264" fill="{C_NAVY}" font-size="13" font-weight="bold">Linear OLS (Selected)</text>
    <text x="270" y="264" fill="{C_NAVY}" font-size="13" font-weight="bold">0.538 °C</text>
    <text x="380" y="264" fill="{C_NAVY}" font-size="13" font-weight="bold">0.786 °C</text>
    <text x="495" y="264" fill="{C_GREEN}" font-size="13" font-weight="bold">1–2 Mults</text>
    <text x="640" y="264" fill="{C_GREEN}" font-size="13" font-weight="bold">5–9 Clocks</text>
    
    <!-- Row 2: Ridge-6 Regression -->
    <rect x="80" y="289" width="720" height="42" rx="4" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="316" fill="{C_TEXT_MAIN}" font-size="12">Ridge-6 (Multi-var)</text>
    <text x="270" y="316" fill="{C_TEXT_MAIN}" font-size="12">0.509 °C</text>
    <text x="380" y="316" fill="{C_TEXT_MAIN}" font-size="12">0.736 °C</text>
    <text x="495" y="316" fill="{C_TEXT_SUB}" font-size="12">6 Mults</text>
    <text x="640" y="316" fill="{C_TEXT_SUB}" font-size="12">14 Clocks</text>
    
    <!-- Row 3: Multilayer Perceptron -->
    <rect x="80" y="339" width="720" height="42" rx="4" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="366" fill="{C_TEXT_MAIN}" font-size="12">MLP Neural Net (12-16-1)</text>
    <text x="270" y="366" fill="{C_TEXT_MAIN}" font-size="12">0.382 °C</text>
    <text x="380" y="366" fill="{C_TEXT_MAIN}" font-size="12">0.555 °C</text>
    <text x="495" y="366" fill="{C_AMBER}" font-size="12">32 Mults</text>
    <text x="640" y="366" fill="{C_AMBER}" font-size="12">48 Clocks</text>
    
    <!-- Row 4: Diurnal Baseline -->
    <rect x="80" y="389" width="720" height="42" rx="4" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="416" fill="{C_TEXT_MUTED}" font-size="12">Diurnal Base: T(t-21)</text>
    <text x="270" y="416" fill="{C_RED}" font-size="12">0.832 °C</text>
    <text x="380" y="416" fill="{C_RED}" font-size="12">1.187 °C</text>
    <text x="495" y="416" fill="{C_TEXT_MUTED}" font-size="12">0 Mults</text>
    <text x="640" y="416" fill="{C_TEXT_MUTED}" font-size="12">0 Clocks</text>
    
    <!-- Row 5: Persistence Baseline -->
    <rect x="80" y="439" width="720" height="42" rx="4" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="466" fill="{C_TEXT_MUTED}" font-size="12">Persistence: T(t)</text>
    <text x="270" y="466" fill="{C_RED}" font-size="12">2.080 °C</text>
    <text x="380" y="466" fill="{C_RED}" font-size="12">2.733 °C</text>
    <text x="495" y="466" fill="{C_TEXT_MUTED}" font-size="12">0 Mults</text>
    <text x="640" y="466" fill="{C_TEXT_MUTED}" font-size="12">0 Clocks</text>
    
    <!-- 3 Big Stat KPI Callout Badges -->
    <rect x="80" y="495" width="230" height="125" rx="6" fill="{C_BLUE_LIGHT}" stroke="{C_BLUE}" stroke-width="1"/>
    <text x="195" y="528" fill="{C_NAVY}" font-size="24" font-weight="bold" text-anchor="middle">74.1%</text>
    <text x="195" y="552" fill="{C_BLUE}" font-size="11" font-weight="bold" text-anchor="middle">ERROR REDUCTION</text>
    <text x="195" y="574" fill="{C_TEXT_SUB}" font-size="10" text-anchor="middle">vs 2.080°C Persistence</text>
    <text x="195" y="594" fill="{C_NAVY}" font-size="10" font-weight="bold" text-anchor="middle">35.3% over Diurnal Base</text>
    
    <rect x="325" y="495" width="230" height="125" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="440" y="528" fill="{C_NAVY}" font-size="24" font-weight="bold" text-anchor="middle">0.156 °C</text>
    <text x="440" y="552" fill="{C_NAVY}" font-size="11" font-weight="bold" text-anchor="middle">MARGINAL MLP GAP</text>
    <text x="440" y="574" fill="{C_TEXT_SUB}" font-size="10" text-anchor="middle">MLP demands 32 DSPs</text>
    <text x="440" y="594" fill="{C_GREEN}" font-size="10" font-weight="bold" text-anchor="middle">94% DSP Silicon Saved</text>
    
    <rect x="570" y="495" width="230" height="125" rx="6" fill="{C_GREEN_BG}" stroke="{C_GREEN}" stroke-width="1"/>
    <text x="685" y="528" fill="{C_GREEN}" font-size="24" font-weight="bold" text-anchor="middle">11.6×</text>
    <text x="685" y="552" fill="{C_GREEN}" font-size="11" font-weight="bold" text-anchor="middle">SILICON EFFICIENCY</text>
    <text x="685" y="574" fill="{C_TEXT_SUB}" font-size="10" text-anchor="middle">Metric: 1 / (MAE × DSP)</text>
    <text x="685" y="594" fill="{C_GREEN}" font-size="10" font-weight="bold" text-anchor="middle">OLS 0.93 vs MLP 0.08</text>
  </g>
"""

    # Right Panel: Silicon Budget Callout (380 px wide)
    svg += f"""  <g id="pareto_callout" data-pptx-bounds="840 135 380 500">
    <rect x="840" y="135" width="380" height="500" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="840" y="135" width="380" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="860" y="162" fill="{C_NAVY}" font-size="14" font-weight="bold">SILICON DSP ALLOCATION</text>
    
    <!-- Cyclone II Budget Card -->
    <rect x="860" y="195" width="340" height="95" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="875" y="222" fill="{C_NAVY}" font-size="12" font-weight="bold">Cyclone II Multipliers (EP2C35)</text>
    <text x="875" y="246" fill="{C_TEXT_SUB}" font-size="11">• Total Embedded DSP: 35 9×9 Multipliers</text>
    <text x="875" y="268" fill="{C_AMBER}" font-size="11" font-weight="bold">• MLP Demands 32 DSPs (91.4% capacity)</text>
    
    <!-- OLS Allocation Card -->
    <rect x="860" y="305" width="340" height="95" rx="6" fill="{C_BLUE_LIGHT}" stroke="{C_BLUE}" stroke-width="1"/>
    <text x="875" y="332" fill="{C_NAVY}" font-size="12" font-weight="bold">Linear OLS Allocation Profile</text>
    <text x="875" y="356" fill="{C_NAVY}" font-size="11">• Speed Core: 2 DSP units (5.7% budget)</text>
    <text x="875" y="378" fill="{C_GREEN}" font-size="11" font-weight="bold">• Resource Core: 1 Shared DSP (2.8% budget)</text>
    
    <!-- Decision Card -->
    <rect x="860" y="415" width="340" height="205" rx="6" fill="{C_GREEN_BG}" stroke="{C_GREEN}" stroke-width="1.5"/>
    <text x="875" y="445" fill="{C_GREEN}" font-size="13" font-weight="bold">Pareto Optimal Decision:</text>
    <text x="875" y="475" fill="{C_TEXT_MAIN}" font-size="11.5">Linear OLS captures diurnal physics</text>
    <text x="875" y="495" fill="{C_TEXT_MAIN}" font-size="11.5">without exhausting on-chip multipliers.</text>
    <line x1="875" y1="515" x2="1185" y2="515" stroke="{C_GREEN}" stroke-width="1"/>
    <text x="1030" y="555" fill="{C_GREEN}" font-size="28" font-weight="bold" text-anchor="middle">11.6×</text>
    <text x="1030" y="580" fill="{C_NAVY}" font-size="12" font-weight="bold" text-anchor="middle">Higher Accuracy-per-DSP vs MLP</text>
    <text x="1030" y="602" fill="{C_TEXT_SUB}" font-size="10" text-anchor="middle">0 SRAM Blocks (Pure Shift Logic)</text>
  </g>
"""
    svg += standard_footer("ftr_06", "Linear OLS achieves 0.538°C MAE with 94% fewer multipliers than deep learning.")
    svg += svg_footer()
    write_slide("06_ml_benchmarks.svg", svg)

# ==============================================================================
# SLIDE 7: State-of-the-Art Literature Comparison
# ==============================================================================
def gen_slide_07():
    svg = svg_header("content")
    svg += standard_header("hdr_07", "PRIOR ART &amp; LITERATURE COMPARISON", 
                           "Hardware Benchmarks vs Published FPGA Linear Solvers", 
                           "Silicon area, DSP multiplier count, and streaming throughput comparison")
    
    # Top Panel: Literature Comparison Matrix (Table)
    svg += f"""  <g id="prior_art_matrix" data-pptx-bounds="60 135 1160 255">
    <rect x="60" y="135" width="1160" height="255" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="60" y="135" width="1160" height="38" rx="8" fill="{C_CARD_ALT}"/>
    <text x="80" y="160" fill="{C_NAVY}" font-size="13" font-weight="bold">QUANTITATIVE COMPARISON WITH PUBLISHED FPGA REGRESSION SOLVERS</text>
    
    <!-- Table Column Headers -->
    <rect x="75" y="180" width="1130" height="24" rx="4" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="85" y="196" fill="{C_TEXT_MUTED}" font-size="11" font-weight="bold">Reference / Work</text>
    <text x="270" y="196" fill="{C_TEXT_MUTED}" font-size="11" font-weight="bold">Target Device</text>
    <text x="420" y="196" fill="{C_TEXT_MUTED}" font-size="11" font-weight="bold">Arithmetic Format</text>
    <text x="565" y="196" fill="{C_TEXT_MUTED}" font-size="11" font-weight="bold">Logic Footprint</text>
    <text x="700" y="196" fill="{C_TEXT_MUTED}" font-size="11" font-weight="bold">DSP Multipliers</text>
    <text x="840" y="196" fill="{C_TEXT_MUTED}" font-size="11" font-weight="bold">Timing &amp; Latency</text>
    <text x="1000" y="196" fill="{C_TEXT_MUTED}" font-size="11" font-weight="bold">Partition Strategy</text>
    
    <!-- Row 1: Ferreira et al. (SBCCI 2019) -->
    <rect x="75" y="208" width="1130" height="32" rx="4" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="0.8"/>
    <text x="85" y="229" fill="{C_TEXT_MAIN}" font-size="11">SBCCI '19 (Ferreira)</text>
    <text x="270" y="229" fill="{C_TEXT_SUB}" font-size="11">Cyclone IV EP4CE115</text>
    <text x="420" y="229" fill="{C_TEXT_SUB}" font-size="11">Signed Q16.16 (32b)</text>
    <text x="565" y="229" fill="{C_TEXT_SUB}" font-size="11">9,158 LEs</text>
    <text x="700" y="229" fill="{C_RED}" font-size="11" font-weight="bold">473 Mults (89%)</text>
    <text x="840" y="229" fill="{C_TEXT_SUB}" font-size="11">1 cycle (no Fmax)</text>
    <text x="1000" y="229" fill="{C_TEXT_SUB}" font-size="11">On-chip batch solver</text>
    
    <!-- Row 2: Sensors 2022 (Tactile) -->
    <rect x="75" y="243" width="1130" height="32" rx="4" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="0.8"/>
    <text x="85" y="264" fill="{C_TEXT_MAIN}" font-size="11">Sensors '22 (Tactile)</text>
    <text x="270" y="264" fill="{C_TEXT_SUB}" font-size="11">Virtex-6 (xc6vlx240t)</text>
    <text x="420" y="264" fill="{C_TEXT_SUB}" font-size="11">IEEE Float (32b)</text>
    <text x="565" y="264" fill="{C_TEXT_SUB}" font-size="11">3,440 LUTs, 198 FFs</text>
    <text x="700" y="264" fill="{C_AMBER}" font-size="11" font-weight="bold">9 DSP Slices</text>
    <text x="840" y="264" fill="{C_TEXT_SUB}" font-size="11">40.25 ns (24.8 MSps)</text>
    <text x="1000" y="264" fill="{C_TEXT_SUB}" font-size="11">Rolling OLS covariance</text>
    
    <!-- Row 3: Royer et al. (DCIS 2011) -->
    <rect x="75" y="278" width="1130" height="32" rx="4" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="0.8"/>
    <text x="85" y="299" fill="{C_TEXT_MAIN}" font-size="11">DCIS '11 (Royer)</text>
    <text x="270" y="299" fill="{C_TEXT_SUB}" font-size="11">Virtex-5 (XC5VLX)</text>
    <text x="420" y="299" fill="{C_TEXT_SUB}" font-size="11">Custom Fixed-Point</text>
    <text x="565" y="299" fill="{C_TEXT_SUB}" font-size="11">66–89 Slices</text>
    <text x="700" y="299" fill="{C_TEXT_SUB}" font-size="11">5 DSP Slices</text>
    <text x="840" y="299" fill="{C_TEXT_SUB}" font-size="11">439 MHz Fmax</text>
    <text x="1000" y="299" fill="{C_TEXT_SUB}" font-size="11">Block OLS fitting</text>
    
    <!-- Row 4: This Work: Speed Core -->
    <rect x="75" y="313" width="1130" height="32" rx="4" fill="{C_BLUE_LIGHT}" stroke="{C_BLUE}" stroke-width="1.2"/>
    <text x="85" y="334" fill="{C_NAVY}" font-size="11" font-weight="bold">This Work: Speed Core</text>
    <text x="270" y="334" fill="{C_NAVY}" font-size="11" font-weight="bold">Cyclone II EP2C35</text>
    <text x="420" y="334" fill="{C_NAVY}" font-size="11" font-weight="bold">Signed Q8.8 / Q2.14</text>
    <text x="565" y="334" fill="{C_GREEN}" font-size="11" font-weight="bold">412 LEs (1.2%)</text>
    <text x="700" y="334" fill="{C_GREEN}" font-size="11" font-weight="bold">2 Mults (5.7%)</text>
    <text x="840" y="334" fill="{C_BLUE}" font-size="11" font-weight="bold">5 clk (II=1) | 142 MHz</text>
    <text x="1000" y="334" fill="{C_NAVY}" font-size="11" font-weight="bold">Diurnal Edge Streaming</text>
    
    <!-- Row 5: This Work: Resource Core -->
    <rect x="75" y="348" width="1130" height="32" rx="4" fill="{C_GREEN_BG}" stroke="{C_GREEN}" stroke-width="1.2"/>
    <text x="85" y="369" fill="{C_NAVY}" font-size="11" font-weight="bold">This Work: Resource Core</text>
    <text x="270" y="369" fill="{C_TEXT_SUB}" font-size="11">Cyclone II EP2C35</text>
    <text x="420" y="369" fill="{C_TEXT_SUB}" font-size="11">Signed Q8.8 / Q2.14</text>
    <text x="565" y="369" fill="{C_GREEN}" font-size="11" font-weight="bold">236 LEs (0.7%)</text>
    <text x="700" y="369" fill="{C_GREEN}" font-size="11" font-weight="bold">1 Shared Mult (2.8%)</text>
    <text x="840" y="369" fill="{C_TEXT_MAIN}" font-size="11">9 clk (II=10) | 118 MHz</text>
    <text x="1000" y="369" fill="{C_TEXT_SUB}" font-size="11">Time-Muxed Edge IoT</text>
  </g>
"""
    
    # Bottom Left Panel: Engineering Advantages
    svg += f"""  <g id="card_superiority" data-pptx-bounds="60 405 565 230">
    <rect x="60" y="405" width="565" height="230" rx="8" fill="{C_CARD_WHITE}" stroke="{C_GREEN}" stroke-width="1.5"/>
    <rect x="60" y="405" width="565" height="34" rx="8" fill="{C_GREEN_BG}"/>
    <text x="80" y="427" fill="{C_GREEN}" font-size="12" font-weight="bold">ENGINEERING ADVANTAGES (KEY DIFFERENTIATORS)</text>
    
    <text x="80" y="460" fill="{C_NAVY}" font-size="11" font-weight="bold">• 99.5% DSP Savings: <tspan fill="{C_TEXT_SUB}" font-weight="normal">Uses 1–2 mults vs 473 in SBCCI '19.</tspan></text>
    <text x="80" y="500" fill="{C_NAVY}" font-size="11" font-weight="bold">• II = 1 Streaming: <tspan fill="{C_TEXT_SUB}" font-weight="normal">50 MSps @ 142.3 MHz F_max (0 bubble stalls).</tspan></text>
    <text x="80" y="540" fill="{C_NAVY}" font-size="11" font-weight="bold">• Diurnal Anchor: <tspan fill="{C_TEXT_SUB}" font-weight="normal">&gt;85% variance captured at zero logic cost.</tspan></text>
    <text x="80" y="580" fill="{C_NAVY}" font-size="11" font-weight="bold">• DPI-C Verified: <tspan fill="{C_TEXT_SUB}" font-weight="normal">100% bit-exact across 10,000+ vectors.</tspan></text>
  </g>
"""

    # Bottom Right Panel: Architectural Boundaries
    svg += f"""  <g id="card_inferiority" data-pptx-bounds="655 405 565 230">
    <rect x="655" y="405" width="565" height="230" rx="8" fill="{C_CARD_WHITE}" stroke="{C_AMBER}" stroke-width="1.5"/>
    <rect x="655" y="405" width="565" height="34" rx="8" fill="{C_AMBER_BG}"/>
    <text x="675" y="427" fill="{C_AMBER}" font-size="12" font-weight="bold">ARCHITECTURAL BOUNDARIES &amp; DESIGN DECISIONS</text>
    
    <text x="675" y="460" fill="{C_NAVY}" font-size="11" font-weight="bold">• Offline Partition: <tspan fill="{C_TEXT_SUB}" font-weight="normal">Weights fitted in C++, reloadable via UART.</tspan></text>
    <text x="675" y="500" fill="{C_NAVY}" font-size="11" font-weight="bold">• Bounded Range: <tspan fill="{C_TEXT_SUB}" font-weight="normal">Q8.8 [-128°C, +128°C] tailored for sensors.</tspan></text>
    <text x="675" y="540" fill="{C_NAVY}" font-size="11" font-weight="bold">• 3-Tap Scope: <tspan fill="{C_TEXT_SUB}" font-weight="normal">Local edge predictor vs generic matrix solver.</tspan></text>
    <text x="675" y="580" fill="{C_NAVY}" font-size="11" font-weight="bold">• Target Silicon: <tspan fill="{C_TEXT_SUB}" font-weight="normal">90nm Cyclone II; portable to modern ASIC.</tspan></text>
  </g>
"""
    svg += standard_footer("ftr_07", "Offline weight fitting reduces DSP footprint by 99.5% while sustaining II=1 throughput.")
    svg += svg_footer()
    write_slide("07_hardware_tradeoff.svg", svg)

# ==============================================================================
# SLIDE 8: Fixed-Point Precision Contract & Register Bitfields
# ==============================================================================
def gen_slide_08():
    svg = svg_header("content")
    svg += standard_header("hdr_08", "FIXED-POINT QUANTIZATION ARCHITECTURE", 
                           "Precision Contract: Signed Q8.8 &amp; Q2.14 Bitfields", 
                           "Eliminating floating-point silicon overhead via two's complement integer arithmetic")
    
    # Left Panel: Register Bitfield Diagrams (760 px wide)
    svg += f"""  <g id="bitfield_visual" data-pptx-bounds="60 135 760 500">
    <rect x="60" y="135" width="760" height="500" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="60" y="135" width="760" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="80" y="162" fill="{C_NAVY}" font-size="14" font-weight="bold">REGISTER BITFIELD STRUCTURE</text>
    
    <!-- Register 1: Temperature Q8.8 Format -->
    <text x="80" y="205" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">1. Temperature Telemetry: Signed Q8.8 (16 Bits)</text>
    
    <text x="95" y="228" fill="{C_TEXT_MUTED}" font-size="10">Bit 15</text>
    <text x="140" y="228" fill="{C_TEXT_MUTED}" font-size="10">14</text>
    <text x="375" y="228" fill="{C_TEXT_MUTED}" font-size="10">8</text>
    <text x="440" y="228" fill="{C_TEXT_MUTED}" font-size="10">7</text>
    <text x="735" y="228" fill="{C_TEXT_MUTED}" font-size="10">0</text>
    
    <!-- Bitfield Bar Q8.8 -->
    <rect x="80" y="238" width="45" height="42" fill="{C_AMBER_BG}" stroke="{C_AMBER}" stroke-width="1.5"/>
    <text x="102" y="264" fill="{C_AMBER}" font-size="12" font-weight="bold" text-anchor="middle">S</text>
    
    <rect x="125" y="238" width="285" height="42" fill="{C_BLUE_LIGHT}" stroke="{C_NAVY}" stroke-width="1.5"/>
    <text x="267" y="264" fill="{C_NAVY}" font-size="12" font-weight="bold" text-anchor="middle">Integer: 7 Bits [14:8]</text>
    
    <line x1="410" y1="233" x2="410" y2="285" stroke="{C_RED}" stroke-width="2.5" stroke-dasharray="3 2"/>
    <text x="410" y="300" fill="{C_RED}" font-size="10" font-weight="bold" text-anchor="middle">Radix Point</text>
    
    <rect x="410" y="238" width="350" height="42" fill="{C_CARD_BG}" stroke="{C_BLUE}" stroke-width="1.5"/>
    <text x="585" y="264" fill="{C_BLUE}" font-size="12" font-weight="bold" text-anchor="middle">Fractional: 8 Bits [7:0]</text>
    
    <text x="80" y="328" fill="{C_TEXT_SUB}" font-size="11">• Range: [-128.000 °C, +127.996 °C] | LSB = 2^-8 = 0.0039 °C (25.6x below sensor noise)</text>
    
    <!-- Register 2: Coefficients Q2.14 Format -->
    <text x="80" y="375" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">2. Model Weights: Signed Q2.14 (16 Bits)</text>
    
    <text x="95" y="398" fill="{C_TEXT_MUTED}" font-size="10">Bit 15</text>
    <text x="140" y="398" fill="{C_TEXT_MUTED}" font-size="10">14</text>
    <text x="180" y="398" fill="{C_TEXT_MUTED}" font-size="10">13</text>
    <text x="735" y="398" fill="{C_TEXT_MUTED}" font-size="10">0</text>
    
    <!-- Bitfield Bar Q2.14 -->
    <rect x="80" y="408" width="45" height="42" fill="{C_AMBER_BG}" stroke="{C_AMBER}" stroke-width="1.5"/>
    <text x="102" y="434" fill="{C_AMBER}" font-size="12" font-weight="bold" text-anchor="middle">S</text>
    
    <rect x="125" y="408" width="45" height="42" fill="{C_BLUE_LIGHT}" stroke="{C_NAVY}" stroke-width="1.5"/>
    <text x="147" y="434" fill="{C_NAVY}" font-size="11" font-weight="bold" text-anchor="middle">I0</text>
    
    <line x1="170" y1="403" x2="170" y2="455" stroke="{C_RED}" stroke-width="2.5" stroke-dasharray="3 2"/>
    <text x="170" y="470" fill="{C_RED}" font-size="10" font-weight="bold" text-anchor="middle">Radix Point</text>
    
    <rect x="170" y="408" width="590" height="42" fill="{C_CARD_BG}" stroke="{C_PURPLE}" stroke-width="1.5"/>
    <text x="465" y="434" fill="{C_PURPLE}" font-size="12" font-weight="bold" text-anchor="middle">Fractional: 14 Bits [13:0]</text>
    
    <text x="80" y="498" fill="{C_TEXT_SUB}" font-size="11">• Range: [-2.0000, +1.9999] | Resolution LSB = 2^-14 = 0.000061</text>
    
    <!-- Verilog Parameter Box -->
    <rect x="80" y="525" width="680" height="85" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="550" fill="{C_NAVY}" font-size="11" font-weight="bold">Hardware Quantized Weight Constants (Verilog / DPI-C):</text>
    <text x="95" y="572" fill="{C_TEXT_MAIN}" font-size="11">COEF_A = 16'sh2FB6; // a = 0.7455 × 16384 = 12214 (Q2.14)</text>
    <text x="95" y="594" fill="{C_TEXT_MAIN}" font-size="11">COEF_B = 16'sh0096; // b = 0.0091 × 16384 = 150 (Q2.14)  |  COEF_C = 16'sh0000; (Q8.8)</text>
  </g>
"""

    # Right Panel: Precision Specs (380 px wide)
    svg += f"""  <g id="quant_table" data-pptx-bounds="840 135 380 500">
    <rect x="840" y="135" width="380" height="500" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="840" y="135" width="380" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="860" y="162" fill="{C_NAVY}" font-size="14" font-weight="bold">FORMAT SPECIFICATION</text>
    
    <text x="860" y="205" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Signal Mapping:</text>
    
    <rect x="860" y="220" width="340" height="44" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="875" y="239" fill="{C_NAVY}" font-size="11" font-weight="bold">T(t), T(t-24), T(t-21), T(t-3):</text>
    <text x="875" y="255" fill="{C_TEXT_SUB}" font-size="10.5">Signed Q8.8 (16b) | Radix at bit 8</text>
    
    <rect x="860" y="270" width="340" height="44" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="875" y="289" fill="{C_NAVY}" font-size="11" font-weight="bold">Coefficients a, b:</text>
    <text x="875" y="305" fill="{C_TEXT_SUB}" font-size="10.5">Signed Q2.14 (16b) | Radix at bit 14</text>
    
    <rect x="860" y="320" width="340" height="44" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="875" y="339" fill="{C_NAVY}" font-size="11" font-weight="bold">Multipliers P1, P2:</text>
    <text x="875" y="355" fill="{C_TEXT_SUB}" font-size="10.5">Signed Q11.22 (33b) | Radix at bit 22</text>
    
    <rect x="860" y="370" width="340" height="44" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="875" y="389" fill="{C_NAVY}" font-size="11" font-weight="bold">Accumulator Bus:</text>
    <text x="875" y="405" fill="{C_TEXT_SUB}" font-size="10.5">Signed Q13.22 (35b) | Shifted to Q13.8</text>
    
    <rect x="860" y="425" width="340" height="190" rx="6" fill="{C_GREEN_BG}" stroke="{C_GREEN}" stroke-width="1"/>
    <text x="875" y="452" fill="{C_GREEN}" font-size="12" font-weight="bold">Quantization Loss Audit:</text>
    <text x="875" y="478" fill="{C_TEXT_MAIN}" font-size="11.5">• Floating-Point MAE:  0.5378 °C</text>
    <text x="875" y="502" fill="{C_TEXT_MAIN}" font-size="11.5">• Fixed-Point Q8.8 MAE:  0.5381 °C</text>
    <text x="875" y="526" fill="{C_TEXT_MAIN}" font-size="11.5">• Precision Loss:  0.0003 °C (0.05% relative)</text>
    <line x1="875" y1="544" x2="1185" y2="544" stroke="{C_GREEN}" stroke-width="0.8"/>
    <text x="875" y="570" fill="{C_GREEN}" font-size="11" font-weight="bold">Negligible Precision Loss</text>
    <text x="875" y="592" fill="{C_TEXT_SUB}" font-size="10">Masked by physical sensor noise floor.</text>
  </g>
"""
    svg += standard_footer("ftr_08", "Strict Q8.8 and Q2.14 precision contracts eliminate floating-point logic while incurring only 0.0003°C error.")
    svg += svg_footer()
    write_slide("08_fixed_point_contract.svg", svg)

# ==============================================================================
# SLIDE 9: Binary Alignment & Arithmetic Bit Growth Dynamics
# ==============================================================================
def gen_slide_09():
    svg = svg_header("content")
    svg += standard_header("hdr_09", "DATAPATH WORDLENGTH EVOLUTION", 
                           "Binary Radix Alignment &amp; Arithmetic Bit Growth", 
                           "Tracking wordlength expansion through subtraction, multiplication, accumulation, and saturation")
    
    stages = [
        ("Step 1: Input Capture", "T(t), T(t-24), T(t-3), T(t-21)", "Signed Q8.8", "16 Bits", C_NAVY, "Raw 16-bit signed telemetry samples latched into input stage."),
        ("Step 2: Subtraction", "D1 = T(t)-T(t-24),  D2 = T(t)-T(t-3)", "Signed Q9.8", "17 Bits", C_BLUE, "+1 sign bit headroom prevents subtractor wrap on large swings."),
        ("Step 3: Multiplication", "P1 = a · D1,  P2 = b · D2", "Signed Q11.22", "33 Bits", C_PURPLE, "16b coeff × 17b diff generates 33-bit signed product terms."),
        ("Step 4: Adder Tree & Base", "P = P1 + P2;  base = (T21 + c) &lt;&lt; 14", "Signed Q13.22", "35 Bits", C_AMBER, "Aligns diurnal anchor to radix 22; expands to 35-bit bus."),
        ("Step 5: Full Accumulation", "S = P + base;  S_sh = S &gt;&gt;&gt; 14", "Signed Q13.8", "35 Bits", C_NAVY, "Summation followed by arithmetic right shift 14 (floor scaling)."),
        ("Step 6: Sat16 Saturation", "out = sat16(S_sh, -32768, +32767)", "Signed Q8.8", "16 Bits", C_GREEN, "Clamps to [-128°C, +127.996°C]; prevents sign wrap.")
    ]
    
    for i, (title, math_expr, fmt, width, col, desc) in enumerate(stages):
        col_idx = i % 2
        row_idx = i // 2
        x = 60 + col_idx * 595
        y = 135 + row_idx * 165
        svg += f"""  <g id="growth_s{i}" data-pptx-bounds="{x} {y} 570 148">
    <rect x="{x}" y="{y}" width="570" height="148" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="{x}" y="{y}" width="570" height="38" rx="8" fill="{C_CARD_ALT}"/>
    <text x="{x+20}" y="{y+25}" fill="{col}" font-size="13" font-weight="bold">{title}</text>
    
    <rect x="{x+410}" y="{y+8}" width="145" height="22" rx="4" fill="{col}"/>
    <text x="{x+482}" y="{y+23}" fill="#FFFFFF" font-size="11" font-weight="bold" text-anchor="middle">{fmt} ({width})</text>
    
    <rect x="{x+20}" y="{y+50}" width="530" height="34" rx="4" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="{x+35}" y="{y+72}" fill="{C_TEXT_MAIN}" font-size="12" font-weight="bold">{math_expr}</text>
    
    <text x="{x+20}" y="{y+110}" fill="{C_TEXT_SUB}" font-size="11">{desc}</text>
  </g>
"""
    svg += standard_footer("ftr_09", "Explicit bit-growth tracking guarantees zero unhandled arithmetic overflow before final saturation clamping.")
    svg += svg_footer()
    write_slide("09_binary_alignment.svg", svg)

# ==============================================================================
# SLIDE 10: Truncation Noise vs Floor Scaling
# ==============================================================================
def gen_slide_10():
    svg = svg_header("content")
    svg += standard_header("hdr_10", "ROUNDING ARCHITECTURE &amp; NOISE BOUND", 
                           "Truncation Analysis: Floor Scaling vs Silicon Cost", 
                           "Bounded truncation error and silicon cost vs rounding alternatives")
    
    # Left Panel: Mathematical Error Bound Proof
    svg += f"""  <g id="box_trunc_proof" data-pptx-bounds="60 135 565 500">
    <rect x="60" y="135" width="565" height="500" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="60" y="135" width="565" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="80" y="162" fill="{C_NAVY}" font-size="14" font-weight="bold">ARITHMETIC RIGHT SHIFT (FLOOR SCALING)</text>
    
    <text x="80" y="205" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Hardware Implementation (0 Logic Elements):</text>
    <rect x="80" y="220" width="525" height="42" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="246" fill="{C_NAVY}" font-size="12" font-weight="bold">wire signed [34:0] s4_sh = s4_s &gt;&gt;&gt; 14;  // Pure wire routing</text>
    
    <text x="80" y="290" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Mathematical Error Bound Proof:</text>
    <text x="80" y="315" fill="{C_TEXT_SUB}" font-size="12">• Truncation Inequality:</text>
    <text x="100" y="342" fill="{C_BLUE}" font-size="13" font-weight="bold">(x / 2^14) - 1  &lt;  floor(x / 2^14)  &lt;=  (x / 2^14)</text>
    <text x="80" y="375" fill="{C_TEXT_SUB}" font-size="12">• Max Truncation Error in Temperature Domain:</text>
    <text x="100" y="402" fill="{C_GREEN}" font-size="14" font-weight="bold">|ε_trunc| &lt; 2^-8 °C = 0.003906 °C</text>
    
    <rect x="80" y="435" width="525" height="175" rx="6" fill="{C_BLUE_LIGHT}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="465" fill="{C_NAVY}" font-size="13" font-weight="bold">Sensor Noise Floor Comparison:</text>
    <text x="95" y="495" fill="{C_TEXT_MAIN}" font-size="12">• Hardware Thermistor Noise:  ±0.1000 °C</text>
    <text x="95" y="522" fill="{C_TEXT_MAIN}" font-size="12">• Max Truncation Error:  &lt; 0.0039 °C (25.6x smaller)</text>
    <line x1="95" y1="542" x2="585" y2="542" stroke="{C_BORDER_DARK}" stroke-width="0.8"/>
    <text x="95" y="570" fill="{C_NAVY}" font-size="12" font-weight="bold">Noise Floor Masks Truncation Completely</text>
    <text x="95" y="592" fill="{C_GREEN}" font-size="11" font-weight="bold">Rounding adders add silicon cost with zero observable gain.</text>
  </g>
"""

    # Right Panel: Silicon Cost of Rounding Modes
    svg += f"""  <g id="box_rounding_tradeoff" data-pptx-bounds="655 135 565 500">
    <rect x="655" y="135" width="565" height="500" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="655" y="135" width="565" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="675" y="162" fill="{C_NAVY}" font-size="14" font-weight="bold">HARDWARE COST OF ROUNDING MODES</text>
    
    <text x="675" y="205" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Synthesis Comparison (Cyclone II EP2C35):</text>
    
    <!-- Mode 1: Truncation -->
    <rect x="675" y="222" width="525" height="52" rx="6" fill="{C_GREEN_BG}" stroke="{C_GREEN}" stroke-width="1"/>
    <text x="690" y="244" fill="{C_GREEN}" font-size="12" font-weight="bold">1. Floor Truncation (Selected in RTL)</text>
    <text x="690" y="262" fill="{C_TEXT_SUB}" font-size="11">0 LEs | 0 Latency | Bias: -0.002°C (masked by sensor)</text>
    
    <!-- Mode 2: Round-to-Nearest -->
    <rect x="675" y="282" width="525" height="52" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="690" y="304" fill="{C_TEXT_MAIN}" font-size="12" font-weight="bold">2. Round-to-Nearest (+0.5 LSB Adder)</text>
    <text x="690" y="322" fill="{C_TEXT_SUB}" font-size="11">+35 LEs (35-bit adder) | +1 Cycle | Bias: ~0.000°C</text>
    
    <!-- Mode 3: Convergent Rounding -->
    <rect x="675" y="342" width="525" height="52" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="690" y="364" fill="{C_TEXT_MAIN}" font-size="12" font-weight="bold">3. Convergent Round-to-Even</text>
    <text x="690" y="382" fill="{C_TEXT_SUB}" font-size="11">+48 LEs (adder + tie logic) | +1 Cycle | Bias: 0.000°C</text>
    
    <!-- Rationale Box -->
    <rect x="675" y="410" width="525" height="200" rx="6" fill="{C_CARD_ALT}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="690" y="438" fill="{C_NAVY}" font-size="12" font-weight="bold">Silicon Optimization Impact:</text>
    <text x="690" y="465" fill="{C_TEXT_MAIN}" font-size="11">• Silicon: Saves 14.8% of Resource Core logic (no adder)</text>
    <text x="690" y="490" fill="{C_TEXT_MAIN}" font-size="11">• Timing: Saves 2.2 ns critical path (+15% slack)</text>
    <text x="690" y="515" fill="{C_NAVY}" font-size="11" font-weight="bold">• DPI-C C++ Oracle Formula (ols_reference.hpp):</text>
    <rect x="690" y="530" width="495" height="32" rx="4" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="705" y="551" fill="{C_NAVY}" font-size="11" font-weight="bold">s / 16384 - ((s &lt; 0 &amp;&amp; s % 16384 != 0) ? 1 : 0);</text>
    <text x="690" y="590" fill="{C_GREEN}" font-size="11" font-weight="bold">Bit-exact match verified across 10,000+ test vectors.</text>
  </g>
"""
    svg += standard_footer("ftr_10", "Floor truncation costs 0 LEs with error bounded under 0.0039°C, saving 14.8% silicon area without forecast penalty.")
    svg += svg_footer()
    write_slide("10_floor_scaling.svg", svg)

# ==============================================================================
# SLIDE 11: Saturation Arithmetic & Clamping Transfer Function
# ==============================================================================
def gen_slide_11():
    svg = svg_header("content")
    svg += standard_header("hdr_11", "DYNAMIC RANGE INTEGRITY", 
                           "Saturation Arithmetic: Sat16 Transfer Function", 
                           "Preventing destructive two's complement sign-inversion wrap-around via signed 16-bit hardware clamping")
    
    # Left Panel: Saturation Transfer Function Graph (600 px wide)
    svg += f"""  <g id="sat_curve_graph" data-pptx-bounds="60 135 600 500">
    <rect x="60" y="135" width="600" height="500" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="60" y="135" width="600" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="80" y="162" fill="{C_NAVY}" font-size="14" font-weight="bold">SAT16 TRANSFER FUNCTION: RESULT_OUT VS SHIFTED_ACCUM</text>
    
    <!-- Graph Canvas Box -->
    <rect x="80" y="195" width="560" height="295" fill="{C_CARD_BG}" rx="6" stroke="{C_BORDER}" stroke-width="1"/>
    
    <!-- Axes: X-Axis at y=345, Y-Axis at x=360 -->
    <line x1="110" y1="345" x2="610" y2="345" stroke="{C_BORDER_DARK}" stroke-width="1.5"/>
    <text x="575" y="362" fill="{C_TEXT_MUTED}" font-size="10">Shifted Accum</text>
    
    <line x1="360" y1="210" x2="360" y2="475" stroke="{C_BORDER_DARK}" stroke-width="1.5"/>
    <text x="365" y="222" fill="{C_TEXT_MUTED}" font-size="10">Output Q8.8</text>
    
    <!-- Grid Reference Lines -->
    <line x1="110" y1="250" x2="610" y2="250" stroke="{C_BORDER}" stroke-width="1" stroke-dasharray="3 3"/>
    <text x="260" y="246" fill="{C_AMBER}" font-size="10" font-weight="bold">+127.996°C (16'sh7FFF)</text>
    
    <line x1="110" y1="440" x2="610" y2="440" stroke="{C_BORDER}" stroke-width="1" stroke-dasharray="3 3"/>
    <text x="260" y="455" fill="{C_AMBER}" font-size="10" font-weight="bold">-128.000°C (16'sh8000)</text>
    
    <!-- Vertical Knee lines: x=210 (-32768), x=510 (+32767) -->
    <line x1="210" y1="210" x2="210" y2="475" stroke="{C_BORDER}" stroke-width="1" stroke-dasharray="3 3"/>
    <text x="175" y="488" fill="{C_TEXT_MUTED}" font-size="9">-32768</text>
    
    <line x1="510" y1="210" x2="510" y2="475" stroke="{C_BORDER}" stroke-width="1" stroke-dasharray="3 3"/>
    <text x="495" y="488" fill="{C_TEXT_MUTED}" font-size="9">+32767</text>
    
    <!-- The Transfer Function Polyline -->
    <line x1="110" y1="440" x2="210" y2="440" stroke="{C_AMBER}" stroke-width="3"/>
    <line x1="210" y1="440" x2="510" y2="250" stroke="{C_BLUE}" stroke-width="3"/>
    <line x1="510" y1="250" x2="610" y2="250" stroke="{C_AMBER}" stroke-width="3"/>
    
    <!-- Knee Points -->
    <circle cx="210" cy="440" r="5" fill="{C_AMBER}"/>
    <circle cx="510" cy="250" r="5" fill="{C_AMBER}"/>
    <circle cx="360" cy="345" r="4" fill="{C_NAVY}"/>
    <text x="370" y="340" fill="{C_NAVY}" font-size="9" font-weight="bold">(0, 0)</text>
    
    <!-- Region Annotations -->
    <rect x="120" y="390" width="85" height="34" rx="4" fill="{C_AMBER_BG}" stroke="{C_AMBER}" stroke-width="1"/>
    <text x="162" y="405" fill="{C_AMBER}" font-size="9" font-weight="bold" text-anchor="middle">MIN CLAMP</text>
    <text x="162" y="418" fill="{C_AMBER}" font-size="9" text-anchor="middle">16'sh8000</text>
    
    <rect x="315" y="275" width="95" height="34" rx="4" fill="{C_BLUE_LIGHT}" stroke="{C_BLUE}" stroke-width="1"/>
    <text x="362" y="290" fill="{C_NAVY}" font-size="9" font-weight="bold" text-anchor="middle">LINEAR PASS</text>
    <text x="362" y="303" fill="{C_BLUE}" font-size="9" text-anchor="middle">y = accum[15:0]</text>
    
    <rect x="515" y="270" width="85" height="34" rx="4" fill="{C_AMBER_BG}" stroke="{C_AMBER}" stroke-width="1"/>
    <text x="557" y="285" fill="{C_AMBER}" font-size="9" font-weight="bold" text-anchor="middle">MAX CLAMP</text>
    <text x="557" y="298" fill="{C_AMBER}" font-size="9" text-anchor="middle">16'sh7FFF</text>
    
    <!-- Bottom Explanation -->
    <rect x="80" y="505" width="560" height="110" rx="6" fill="{C_CARD_ALT}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="528" fill="{C_NAVY}" font-size="11" font-weight="bold">Why Saturation is Mandatory in Two's Complement:</text>
    <text x="95" y="550" fill="{C_TEXT_SUB}" font-size="11">• Unclamped wrap: +128.01°C flips to -127.99°C sign overflow</text>
    <text x="95" y="572" fill="{C_TEXT_SUB}" font-size="11">• Actuator risk: Sign flip triggers false heating alarms</text>
    <text x="95" y="595" fill="{C_GREEN}" font-size="11" font-weight="bold">• Sat16 clamp: Bounds extreme spikes to max signed rails</text>
  </g>
"""

    # Right Panel: Synthesizable Verilog Snippet (540 px wide)
    svg += f"""  <g id="sat_rtl_code" data-pptx-bounds="680 135 540 500">
    <rect x="680" y="135" width="540" height="500" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="680" y="135" width="540" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="700" y="162" fill="{C_NAVY}" font-size="14" font-weight="bold">SYNTHESIZABLE VERILOG SATURATION LOGIC</text>
    
    <text x="700" y="205" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Production RTL Implementation (Speed &amp; Resource):</text>
    
    <rect x="700" y="222" width="500" height="230" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="715" y="244" fill="{C_TEXT_MUTED}" font-size="11">// Arithmetic shift by 14 fractional bits</text>
    <text x="715" y="264" fill="{C_NAVY}" font-size="11" font-weight="bold">wire signed [34:0] s4_sh = s4_s &gt;&gt;&gt; 14;</text>
    <text x="715" y="290" fill="{C_TEXT_MUTED}" font-size="11">// Sat16 signed 16-bit saturation</text>
    <text x="715" y="310" fill="{C_TEXT_MAIN}" font-size="11">always @(posedge clk) begin</text>
    <text x="735" y="330" fill="{C_AMBER}" font-size="11" font-weight="bold">    if (s4_sh &gt; 35'sd32767)</text>
    <text x="755" y="348" fill="{C_TEXT_MAIN}" font-size="11">        s5_out &lt;= 16'sh7FFF;  // +127.996 °C clamp</text>
    <text x="735" y="368" fill="{C_AMBER}" font-size="11" font-weight="bold">    else if (s4_sh &lt; -35'sd32768)</text>
    <text x="755" y="386" fill="{C_TEXT_MAIN}" font-size="11">        s5_out &lt;= 16'sh8000;  // -128.000 °C clamp</text>
    <text x="735" y="406" fill="{C_BLUE}" font-size="11" font-weight="bold">    else</text>
    <text x="755" y="424" fill="{C_TEXT_MAIN}" font-size="11">        s5_out &lt;= s4_sh[15:0]; // Normal pass</text>
    <text x="715" y="442" fill="{C_TEXT_MAIN}" font-size="11">end</text>
    
    <rect x="700" y="468" width="500" height="147" rx="6" fill="{C_GREEN_BG}" stroke="{C_GREEN}" stroke-width="1"/>
    <text x="715" y="495" fill="{C_GREEN}" font-size="12" font-weight="bold">DPI-C Golden Model Verification Contract:</text>
    <text x="715" y="520" fill="{C_TEXT_MAIN}" font-size="11">• C++ oracle executes identical signed check (ols_reference.hpp):</text>
    <text x="730" y="542" fill="{C_NAVY}" font-size="11" font-weight="bold">q &gt; 32767 ? 32767 : q &lt; -32768 ? -32768 : int(q);</text>
    <text x="715" y="568" fill="{C_TEXT_MAIN}" font-size="11">• Stress tests inject extreme inputs (-50°C and +120°C swings).</text>
    <text x="715" y="595" fill="{C_GREEN}" font-size="11" font-weight="bold">Zero mismatches: 100% bit-exact across all saturation corners!</text>
  </g>
"""
    svg += standard_footer("ftr_11", "Hardware sat16 saturation eliminates destructive sign-inversion wrap-around across extreme inputs.")
    svg += svg_footer()
    write_slide("11_saturation_arithmetic.svg", svg)
