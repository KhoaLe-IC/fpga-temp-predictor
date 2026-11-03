# ==============================================================================
# DECK SLIDES 1 TO 5: OVERVIEW, PROBLEM & DIURNAL DSP FORMULATION
# Streamlined "A word to the wise is enough" Edition
# Clean Academic White Theme (IEEE Navy, Slate, Green, Amber)
# ==============================================================================
from deck_header import (
    C_BG, C_BG_PAGE, C_TEXT_MAIN, C_TEXT_SUB, C_TEXT_MUTED,
    C_NAVY, C_BLUE, C_BLUE_LIGHT, C_GREEN, C_GREEN_BG,
    C_AMBER, C_AMBER_BG, C_RED, C_PURPLE,
    C_BORDER, C_BORDER_DARK, C_CARD_WHITE, C_CARD_BG, C_CARD_ALT,
    svg_header, svg_footer, standard_header, standard_footer, write_slide
)

# ==============================================================================
# SLIDE 1: Formal Title & Welcome
# ==============================================================================
def gen_slide_01():
    svg = svg_header("cover")
    svg += f"""  <g id="hero_header" data-pptx-bounds="60 40 1160 250">
    <rect x="60" y="40" width="1160" height="250" rx="10" fill="{C_CARD_BG}" stroke="{C_BORDER_DARK}" stroke-width="1.5"/>
    <rect x="60" y="40" width="10" height="250" rx="4" fill="{C_NAVY}"/>
    
    <rect x="90" y="65" width="460" height="26" rx="4" fill="{C_BLUE_LIGHT}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="100" y="83" fill="{C_NAVY}" font-size="12" font-weight="bold" letter-spacing="1">CE436: DISCRETE-TIME SIGNAL PROCESSING &amp; APPLICATIONS</text>
    
    <text x="90" y="140" fill="{C_TEXT_MAIN}" font-size="34" font-weight="bold">FPGA Edge Temperature Predictor</text>
    <text x="90" y="178" fill="{C_NAVY}" font-size="20" font-weight="bold">Dual-Core RTL Design &amp; Bit-Exact DPI-C Verification</text>
    <text x="90" y="210" fill="{C_TEXT_SUB}" font-size="14">Altera Cyclone II (DE2) | Signed Q8.8 / Q2.14 | 50 MHz Real-Time Inference</text>
    
    <rect x="90" y="235" width="310" height="26" rx="4" fill="{C_GREEN_BG}" stroke="{C_GREEN}" stroke-width="1"/>
    <text x="100" y="253" fill="{C_GREEN}" font-size="12" font-weight="bold">100% BIT-EXACT MATCH (10,000+ VECTORS)</text>
  </g>
  <g id="card_platform" data-pptx-bounds="60 315 365 315">
    <rect x="60" y="315" width="365" height="315" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="60" y="315" width="365" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="80" y="342" fill="{C_NAVY}" font-size="13" font-weight="bold">TARGET PLATFORM</text>
    
    <text x="80" y="385" fill="{C_NAVY}" font-size="12" font-weight="bold">FPGA Device:</text>
    <text x="95" y="405" fill="{C_TEXT_SUB}" font-size="12">Cyclone II EP2C35F672C6 (90nm)</text>
    
    <text x="80" y="435" fill="{C_NAVY}" font-size="12" font-weight="bold">Development Board:</text>
    <text x="95" y="455" fill="{C_TEXT_SUB}" font-size="12">Terasic DE2 @ 50 MHz Oscillator</text>
    
    <text x="80" y="485" fill="{C_NAVY}" font-size="12" font-weight="bold">Serial Interface:</text>
    <text x="95" y="505" fill="{C_TEXT_SUB}" font-size="12">RS-232 UART @ 115,200 Baud</text>
    
    <rect x="80" y="545" width="325" height="55" rx="6" fill="{C_BLUE_LIGHT}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="570" fill="{C_NAVY}" font-size="12" font-weight="bold">DSP Multiplier Budget: 35 Units</text>
    <text x="95" y="588" fill="{C_BLUE}" font-size="11">Predictor uses &lt;6% chip DSP capacity</text>
  </g>
  <g id="card_scope" data-pptx-bounds="455 315 365 315">
    <rect x="455" y="315" width="365" height="315" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="455" y="315" width="365" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="475" y="342" fill="{C_NAVY}" font-size="13" font-weight="bold">RTL DESIGN SCOPE</text>
    
    <text x="475" y="385" fill="{C_NAVY}" font-size="12" font-weight="bold">Signal Algorithm:</text>
    <text x="490" y="405" fill="{C_TEXT_SUB}" font-size="12">3-Tap Diurnal Residual OLS</text>
    
    <text x="475" y="435" fill="{C_NAVY}" font-size="12" font-weight="bold">Speed Core:</text>
    <text x="490" y="455" fill="{C_TEXT_SUB}" font-size="12">6 Stages | II = 1 (50 MSps) | 412 LEs</text>
    
    <text x="475" y="485" fill="{C_NAVY}" font-size="12" font-weight="bold">Resource Core:</text>
    <text x="490" y="505" fill="{C_TEXT_SUB}" font-size="12">10 States | 1 Shared Mult | 236 LEs</text>
    
    <rect x="475" y="545" width="325" height="55" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="490" y="570" fill="{C_NAVY}" font-size="12" font-weight="bold">Signed Fixed-Point: Q8.8 / Q2.14</text>
    <text x="490" y="588" fill="{C_TEXT_SUB}" font-size="11">LSB = 0.0039°C with sat16 clamp</text>
  </g>
  <g id="card_defense" data-pptx-bounds="850 315 370 315">
    <rect x="850" y="315" width="370" height="315" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="850" y="315" width="370" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="870" y="342" fill="{C_NAVY}" font-size="13" font-weight="bold">DEFENSE METADATA</text>
    
    <text x="870" y="385" fill="{C_NAVY}" font-size="12" font-weight="bold">Student Engineers:</text>
    <text x="885" y="405" fill="{C_TEXT_MAIN}" font-size="11.5">Le Dang Khoa (24520816) — Lead / RTL</text>
    <text x="885" y="425" fill="{C_TEXT_MAIN}" font-size="11.5">Nguyen Nghia Khoa (24520832) — Model</text>
    <text x="885" y="445" fill="{C_TEXT_MAIN}" font-size="11.5">Nguyen Minh Khoa (24520831) — DV / TB</text>
    
    <text x="870" y="475" fill="{C_NAVY}" font-size="12" font-weight="bold">Academic Advisor:</text>
    <text x="885" y="495" fill="{C_TEXT_SUB}" font-size="12">Dr. Tran Xuan Phuoc (CE-UIT)</text>
    
    <rect x="870" y="545" width="330" height="55" rx="6" fill="{C_GREEN_BG}" stroke="{C_GREEN}" stroke-width="1"/>
    <text x="885" y="570" fill="{C_GREEN}" font-size="12" font-weight="bold">Status: 100% Bit-Exact Match</text>
    <text x="885" y="588" fill="{C_TEXT_SUB}" font-size="11">0 Mismatches across 10,000+ vectors</text>
  </g>
"""
    svg += svg_footer()
    write_slide("01_title_welcome.svg", svg)

# ==============================================================================
# SLIDE 2: Project Overview & Engineering Pillars
# ==============================================================================
def gen_slide_02():
    svg = svg_header("content")
    svg += standard_header("hdr_02", "FULL-STACK IC DESIGN", 
                           "Project Overview: Three Engineering Pillars", 
                           "Signal theory, synthesizable RTL micro-architecture, and closed-loop DV")
    
    pillars = [
        ("pillar_dsp", "PILLAR 1: SIGNAL PROCESSING", C_NAVY, [
            ("43,800 h", "NASA 5-Yr Telemetry"),
            ("3-Tap OLS", "Diurnal Residual Model"),
            ("74.1%", "Gain vs Persistence")
        ], [
            "• Anchor captures &gt;85% variance",
            "• 0.538°C MAE on held-out test data",
            "• Zero on-chip matrix inversion"
        ]),
        ("pillar_rtl", "PILLAR 2: RTL DESIGN", C_BLUE, [
            ("Speed Core", "6 Stages | II = 1 (50 MSps)"),
            ("Resource", "10 States | -42.7% LE Area"),
            ("142.3 MHz", "F_max on Cyclone II")
        ], [
            "• Synthesizable Verilog (EP2C35)",
            "• 1 Shared Mult in Resource Core",
            "• Signed Q8.8 / Q2.14 sat16 datapath"
        ]),
        ("pillar_dv", "PILLAR 3: DESIGN VERIFICATION", C_GREEN, [
            ("DPI-C Co-Sim", "Live C++ Golden Oracle"),
            ("10,000+", "Test Vectors Replayed"),
            ("0 Errors", "100% Bit-Exact Match")
        ], [
            "• Lockstep cycle-exact assertions",
            "• 6-corner stress regression suite",
            "• 17,520h continuous telemetry pass"
        ])
    ]
    
    for i, (pid, title, col, stats, bullets) in enumerate(pillars):
        x = 60 + i * 395
        y = 135
        svg += f"""  <g id="{pid}" data-pptx-bounds="{x} {y} 370 500">
    <rect x="{x}" y="{y}" width="370" height="500" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="{x}" y="{y}" width="370" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="{x+20}" y="{y+26}" fill="{col}" font-size="13" font-weight="bold">{title}</text>
    
    <rect x="{x+15}" y="{y+55}" width="340" height="60" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="{x+30}" y="{y+82}" fill="{col}" font-size="18" font-weight="bold">{stats[0][0]}</text>
    <text x="{x+30}" y="{y+102}" fill="{C_TEXT_SUB}" font-size="11">{stats[0][1]}</text>
    
    <rect x="{x+15}" y="{y+125}" width="340" height="60" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="{x+30}" y="{y+152}" fill="{col}" font-size="18" font-weight="bold">{stats[1][0]}</text>
    <text x="{x+30}" y="{y+172}" fill="{C_TEXT_SUB}" font-size="11">{stats[1][1]}</text>
    
    <rect x="{x+15}" y="{y+195}" width="340" height="60" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="{x+30}" y="{y+222}" fill="{col}" font-size="18" font-weight="bold">{stats[2][0]}</text>
    <text x="{x+30}" y="{y+242}" fill="{C_TEXT_SUB}" font-size="11">{stats[2][1]}</text>
    
    <rect x="{x+15}" y="{y+270}" width="340" height="210" rx="6" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="{x+25}" y="{y+298}" fill="{C_NAVY}" font-size="12" font-weight="bold">Core Highlights:</text>
    <text x="{x+25}" y="{y+330}" fill="{C_TEXT_MAIN}" font-size="11">{bullets[0]}</text>
    <text x="{x+25}" y="{y+370}" fill="{C_TEXT_MAIN}" font-size="11">{bullets[1]}</text>
    <text x="{x+25}" y="{y+410}" fill="{C_TEXT_MAIN}" font-size="11">{bullets[2]}</text>
    <line x1="{x+25}" y1="{y+435}" x2="{x+335}" y2="{y+435}" stroke="{C_BORDER}" stroke-width="0.8"/>
    <text x="{x+25}" y="{y+460}" fill="{col}" font-size="11" font-weight="bold">Silicon &amp; DPI-C Verified</text>
  </g>
"""
    svg += standard_footer("ftr_02", "End-to-end flow: diurnal signal model, dual RTL cores, and bit-exact DPI-C verification.")
    svg += svg_footer()
    write_slide("02_team_overview.svg", svg)

# ==============================================================================
# SLIDE 3: Agenda & Defense Roadmap
# ==============================================================================
def gen_slide_03():
    svg = svg_header("content")
    svg += standard_header("hdr_03", "DEFENSE OUTLINE", 
                           "Capstone Defense Agenda", 
                           "Structured overview of signal modeling, fixed-point math, dual architectures, and silicon verification")
    
    modules = [
        ("01", "Signal Formulation & Prior Art", "NASA 5-yr data, diurnal equation, and benchmarks"),
        ("02", "Fixed-Point Precision Contract", "Signed Q8.8/Q2.14, bit growth, and sat16 clamping"),
        ("03", "Dual RTL Micro-Architectures", "Speed Core (II=1) vs Resource Core (1 shared mult)"),
        ("04", "Top-Level Integration & IO", "Cyclone II DE2 mapping, RS-232 UART, and 7-segment LEDs"),
        ("05", "Bit-Exact DPI-C Verification", "SystemVerilog testbench, C++ oracle, and regressions"),
        ("06", "Silicon Synthesis & Validation", "Quartus II EP2C35 results and 17,520h test replay")
    ]
    
    for i, (num, title, desc) in enumerate(modules):
        col = i % 2
        row = i // 2
        x = 60 + col * 595
        y = 135 + row * 165
        svg += f"""  <g id="mod_{num}" data-pptx-bounds="{x} {y} 570 148">
    <rect x="{x}" y="{y}" width="570" height="148" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="{x}" y="{y}" width="570" height="38" rx="8" fill="{C_CARD_ALT}"/>
    <rect x="{x+15}" y="{y+8}" width="32" height="22" rx="4" fill="{C_NAVY}"/>
    <text x="{x+31}" y="{y+23}" fill="#FFFFFF" font-size="11" font-weight="bold" text-anchor="middle">{num}</text>
    <text x="{x+60}" y="{y+25}" fill="{C_NAVY}" font-size="13" font-weight="bold">{title}</text>
    
    <text x="{x+20}" y="{y+75}" fill="{C_TEXT_MAIN}" font-size="11.5">{desc}</text>
  </g>
"""
    svg += standard_footer("ftr_03", "Six sections covering theory, arithmetic, micro-architecture, and silicon proof.")
    svg += svg_footer()
    write_slide("03_agenda.svg", svg)

# ==============================================================================
# SLIDE 4: Meteorological Signal & Diurnal Formulation
# ==============================================================================
def gen_slide_04():
    svg = svg_header("content")
    svg += standard_header("hdr_04", "SIGNAL CHARACTERISTICS &amp; PROBLEM FORMULATION", 
                           "Meteorological Signal &amp; Diurnal Temperature Waveform", 
                           "Exploiting 24-hour solar cyclicity from NASA POWER satellite observations in Ho Chi Minh City")
    
    # Left Panel: Data Specs & Constraints (450 px wide)
    svg += f"""  <g id="data_context" data-pptx-bounds="60 135 450 500">
    <rect x="60" y="135" width="450" height="500" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="60" y="135" width="450" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="80" y="162" fill="{C_NAVY}" font-size="13" font-weight="bold">DATASET &amp; PROBLEM CONSTRAINTS</text>
    
    <rect x="80" y="195" width="410" height="52" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="217" fill="{C_NAVY}" font-size="12" font-weight="bold">NASA POWER Telemetry (HCMC):</text>
    <text x="95" y="235" fill="{C_TEXT_SUB}" font-size="11">43,800 records (2021–2025) | 5 continuous years</text>
    
    <rect x="80" y="257" width="410" height="52" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="279" fill="{C_NAVY}" font-size="12" font-weight="bold">Causal Data Partition:</text>
    <text x="95" y="297" fill="{C_TEXT_SUB}" font-size="11">Train: 26,280 h | Test: 17,520 h (No leakage)</text>
    
    <rect x="80" y="319" width="410" height="52" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="341" fill="{C_NAVY}" font-size="12" font-weight="bold">Forecast Horizon &amp; Buffer:</text>
    <text x="95" y="359" fill="{C_TEXT_SUB}" font-size="11">t+3 Forecast via 25-tap shift buffer</text>
    
    <rect x="80" y="385" width="410" height="225" rx="6" fill="{C_BLUE_LIGHT}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="415" fill="{C_NAVY}" font-size="13" font-weight="bold">Core Signal Processing Insight:</text>
    <text x="95" y="442" fill="{C_TEXT_MAIN}" font-size="11.5">• Solar cyclicity: &gt;85% of total signal energy</text>
    <text x="95" y="468" fill="{C_TEXT_MAIN}" font-size="11.5">• Anchor T(t-21): primary 24h harmonic baseline</text>
    <text x="95" y="494" fill="{C_TEXT_MAIN}" font-size="11.5">• Linear OLS: learns only the residual delta</text>
    <line x1="95" y1="515" x2="475" y2="515" stroke="{C_BORDER_DARK}" stroke-width="0.8"/>
    <text x="95" y="545" fill="{C_BLUE}" font-size="12" font-weight="bold">Bypasses complex multi-layer neural nets</text>
    <text x="95" y="570" fill="{C_GREEN}" font-size="12" font-weight="bold">Requires only 3 arithmetic taps in silicon!</text>
  </g>
"""

    # Right Panel: 48-Hour Waveform & Physical Tap Map (690 px wide)
    svg += f"""  <g id="waveform_chart" data-pptx-bounds="530 135 690 500">
    <rect x="530" y="135" width="690" height="500" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="530" y="135" width="690" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="550" y="162" fill="{C_NAVY}" font-size="13" font-weight="bold">DIURNAL WAVEFORM &amp; PHYSICAL TAPS (48-HOUR CYCLE)</text>
    
    <!-- Chart Background -->
    <rect x="560" y="195" width="630" height="260" fill="{C_CARD_BG}" rx="6" stroke="{C_BORDER}" stroke-width="1"/>
    
    <!-- Grid Reference Lines -->
    <line x1="600" y1="225" x2="1160" y2="225" stroke="{C_BORDER}" stroke-width="1" stroke-dasharray="3 3"/>
    <text x="575" y="229" fill="{C_TEXT_MUTED}" font-size="10">34°C</text>
    
    <line x1="600" y1="275" x2="1160" y2="275" stroke="{C_BORDER}" stroke-width="1" stroke-dasharray="3 3"/>
    <text x="575" y="279" fill="{C_TEXT_MUTED}" font-size="10">29°C</text>
    
    <line x1="600" y1="325" x2="1160" y2="325" stroke="{C_BORDER}" stroke-width="1" stroke-dasharray="3 3"/>
    <text x="575" y="329" fill="{C_TEXT_MUTED}" font-size="10">24°C</text>
    
    <line x1="600" y1="375" x2="1160" y2="375" stroke="{C_BORDER}" stroke-width="1" stroke-dasharray="3 3"/>
    <text x="575" y="379" fill="{C_TEXT_MUTED}" font-size="10">20°C</text>
    
    <!-- X-Axis Line -->
    <line x1="600" y1="400" x2="1160" y2="400" stroke="{C_BORDER_DARK}" stroke-width="1.5"/>
    <text x="630" y="420" fill="{C_TEXT_MUTED}" font-size="10">Day 1 (00:00)</text>
    <text x="760" y="420" fill="{C_TEXT_MUTED}" font-size="10">Day 1 (12:00)</text>
    <text x="890" y="420" fill="{C_TEXT_MUTED}" font-size="10">Day 2 (00:00)</text>
    <text x="1030" y="420" fill="{C_TEXT_MUTED}" font-size="10">Day 2 (12:00)</text>
    <text x="1130" y="420" fill="{C_RED}" font-size="10" font-weight="bold">t+3</text>
    
    <!-- Waveform Polyline -->
    <path d="M 610,360 C 640,380 680,370 710,310 C 740,240 770,225 800,230 C 830,245 860,325 890,365 C 920,385 950,375 980,315 C 1010,245 1040,228 1070,232 C 1100,250 1130,320 1155,350" 
          fill="none" stroke="{C_BLUE}" stroke-width="2.5"/>
          
    <!-- Tap Marker Points -->
    <circle cx="770" cy="228" r="5" fill="{C_PURPLE}"/>
    <text x="740" y="215" fill="{C_PURPLE}" font-size="10" font-weight="bold">T(t-24)</text>
    
    <circle cx="805" cy="232" r="6" fill="{C_GREEN}"/>
    <text x="785" y="260" fill="{C_GREEN}" font-size="10" font-weight="bold">T(t-21) [Anchor]</text>
    
    <circle cx="1010" cy="248" r="5" fill="{C_AMBER}"/>
    <text x="980" y="275" fill="{C_AMBER}" font-size="10" font-weight="bold">T(t-3)</text>
    
    <circle cx="1045" cy="230" r="6" fill="{C_NAVY}"/>
    <text x="1030" y="215" fill="{C_NAVY}" font-size="10" font-weight="bold">T(t) [Now]</text>
    
    <circle cx="1080" cy="235" r="6" fill="{C_RED}" stroke="{C_RED}" stroke-width="2"/>
    <text x="1085" y="200" fill="{C_RED}" font-size="10" font-weight="bold">T_hat(t+3)</text>
    
    <!-- Tap Meaning Card -->
    <rect x="560" y="470" width="630" height="145" rx="6" fill="{C_CARD_ALT}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="575" y="495" fill="{C_NAVY}" font-size="12" font-weight="bold">HARDWARE TAP MAPPING &amp; PHYSICAL MEANING:</text>
    
    <text x="575" y="525" fill="{C_GREEN}" font-size="11" font-weight="bold">• T(t-21) [Diurnal Anchor]:</text>
    <text x="745" y="525" fill="{C_TEXT_MAIN}" font-size="11">24h baseline cycle at target hour ((t+3)-24)</text>
    
    <text x="575" y="555" fill="{C_PURPLE}" font-size="11" font-weight="bold">• T(t) - T(t-24) [Inter-Day]:</text>
    <text x="745" y="555" fill="{C_TEXT_MAIN}" font-size="11">24h weather front delta (today vs yesterday)</text>
    
    <text x="575" y="585" fill="{C_AMBER}" font-size="11" font-weight="bold">• T(t) - T(t-3) [Gradient]:</text>
    <text x="745" y="585" fill="{C_TEXT_MAIN}" font-size="11">Short-term 3h heating / cooling rate</text>
  </g>
"""
    svg += standard_footer("ftr_04", "Diurnal anchor T(t-21) captures 24h baseline; 2 delta taps fit residual dynamics with only 2 multipliers.")
    svg += svg_footer()
    write_slide("04_problem_formulation.svg", svg)

# ==============================================================================
# SLIDE 5: Mathematical Formulation & Diurnal Residual Equation
# ==============================================================================
def gen_slide_05():
    svg = svg_header("content")
    svg += standard_header("hdr_05", "MATHEMATICAL RESIDUAL FORMULATION", 
                           "Diurnal Residual Ordinary Least Squares Model", 
                           "Decomposing temperature dynamics into diurnal baseline, inter-day trend, and rate-of-change")
    
    # Hero Equation Card (1160 px wide)
    svg += f"""  <g id="eq_hero" data-pptx-bounds="60 135 1160 110">
    <rect x="60" y="135" width="1160" height="110" rx="8" fill="{C_BLUE_LIGHT}" stroke="{C_BORDER_DARK}" stroke-width="1.5"/>
    <text x="80" y="162" fill="{C_NAVY}" font-size="12" font-weight="bold" letter-spacing="1">PREDICTION EQUATION (OLS FIT IN C++ / PYTHON):</text>
    <text x="80" y="202" fill="{C_TEXT_MAIN}" font-size="22" font-weight="bold">T_hat(t+3) = T(t-21) + a · [T(t) - T(t-24)] + b · [T(t) - T(t-3)] + c</text>
    <text x="80" y="228" fill="{C_BLUE}" font-size="12" font-weight="bold">Coefficients:  a = 0.7455 (16'sh2FB6)  |  b = 0.0091 (16'sh0096)  |  c = 0.0011 °C (16'sh0000)</text>
  </g>
"""

    # 4 Component Cards (280 px wide each)
    components = [
        ("term_anchor", "DIURNAL ANCHOR", "T(t-21)", C_GREEN, [
            "24-hr solar baseline",
            "Target: (t+3) - 24",
            "Energy: &gt;85% variance",
            "0 Mults (wire tap)"
        ]),
        ("term_trend", "INTER-DAY TREND", "a · [T(t) - T(t-24)]", C_NAVY, [
            "24-hr weather front delta",
            "Shift from yesterday",
            "Weight: a = 0.7455",
            "1 Sub + 1 Mult"
        ]),
        ("term_gradient", "SHORT-TERM GRADIENT", "b · [T(t) - T(t-3)]", C_BLUE, [
            "3-hr micro-climate rate",
            "Heating / cooling rate",
            "Weight: b = 0.0091",
            "1 Sub + 1 Mult"
        ]),
        ("term_bias", "SYSTEMATIC BIAS", "c", C_AMBER, [
            "Micro-climate offset",
            "Seasonal baseline bias",
            "Offset: c = 0.0011 °C",
            "Adder constant"
        ])
    ]
    
    for i, (cid, title, expr, col, bullets) in enumerate(components):
        x = 60 + i * 295
        y = 265
        svg += f"""  <g id="{cid}" data-pptx-bounds="{x} {y} 280 370">
    <rect x="{x}" y="{y}" width="280" height="370" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="{x}" y="{y}" width="280" height="36" rx="8" fill="{C_CARD_ALT}"/>
    <text x="{x+15}" y="{y+23}" fill="{col}" font-size="11" font-weight="bold">{title}</text>
    
    <rect x="{x+15}" y="{y+50}" width="250" height="42" rx="4" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="{x+140}" y="{y+76}" fill="{col}" font-size="13" font-weight="bold" text-anchor="middle">{expr}</text>
    
    <text x="{x+15}" y="{y+120}" fill="{C_NAVY}" font-size="12" font-weight="bold">Physical Function:</text>
    <text x="{x+15}" y="{y+145}" fill="{C_TEXT_MAIN}" font-size="11">• {bullets[0]}</text>
    <text x="{x+15}" y="{y+170}" fill="{C_TEXT_SUB}" font-size="11">• {bullets[1]}</text>
    <text x="{x+15}" y="{y+195}" fill="{C_TEXT_SUB}" font-size="11">• {bullets[2]}</text>
    
    <rect x="{x+15}" y="{y+240}" width="250" height="110" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="{x+25}" y="{y+268}" fill="{C_NAVY}" font-size="11" font-weight="bold">Hardware Budget:</text>
    <text x="{x+25}" y="{y+295}" fill="{col}" font-size="12" font-weight="bold">{bullets[3]}</text>
    <text x="{x+25}" y="{y+322}" fill="{C_GREEN}" font-size="10" font-weight="bold">Zero on-chip matrix solve</text>
  </g>
"""
    svg += standard_footer("ftr_05", "OLS formulation isolates 3 simple operations: 2 subtractions, 2 multiplications, and a base addition.")
    svg += svg_footer()
    write_slide("05_math_formulation.svg", svg)
