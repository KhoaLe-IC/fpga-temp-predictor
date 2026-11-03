# ==============================================================================
# DECK SLIDES 18 TO 22: REGRESSION, SYNTHESIS, VALIDATION, ROADMAP & Q&A
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
# SLIDE 18: Verification Coverage & Edge Corner-Case Stress Suite
# ==============================================================================
def gen_slide_18():
    svg = svg_header("content")
    svg += standard_header("hdr_18", "CORNER-CASE VERIFICATION REGRESSION", 
                           "Verification Coverage &amp; Edge Corner-Case Analysis", 
                           "Functional regression testing verifying dynamic range extremes, sat16 clamping, and burst streaming")
    
    cases = [
        ("Test 1: Zero Temperature (0.0 °C)", "16'h0000 across all taps", "Sign integrity & zero floor scaling", "PASSED", C_GREEN),
        ("Test 2: Positive Saturation (&gt; +127.996 °C)", "+130.0 °C step (16'h8200)", "Upper sat16 clamp to 16'sh7FFF", "PASSED", C_GREEN),
        ("Test 3: Freezing Sub-Zero (&lt; -128.000 °C)", "-135.0 °C step (16'h7900)", "Lower sat16 clamp to 16'sh8000", "PASSED", C_GREEN),
        ("Test 4: Extreme Delta Swing (ΔT = 25.0 °C)", "25°C step between t and t-3", "33-bit datapath headroom", "PASSED", C_GREEN),
        ("Test 5: Back-to-Back Streaming (II = 1)", "New sample every clock", "Pipeline hazard & zero bubble stall", "PASSED", C_GREEN),
        ("Test 6: Random Walk & 17.5K Replay", "10,000+ Gaussian vectors + replay", "Coverage & paired DPI-C check", "PASSED", C_GREEN)
    ]
    
    svg += f"""  <g id="tbl_corners" data-pptx-bounds="60 135 1160 500">
    <rect x="60" y="135" width="1160" height="500" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="60" y="135" width="1160" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="80" y="162" fill="{C_NAVY}" font-size="14" font-weight="bold">SYSTEMVERILOG CORNER-CASE REGRESSION SUITE</text>
    
    <!-- Table Header Row -->
    <rect x="80" y="195" width="1120" height="32" rx="4" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="216" fill="{C_NAVY}" font-size="12" font-weight="bold">Corner Case Description</text>
    <text x="440" y="216" fill="{C_NAVY}" font-size="12" font-weight="bold">Stimulus Vector</text>
    <text x="740" y="216" fill="{C_NAVY}" font-size="12" font-weight="bold">Hardware Stress Target</text>
    <text x="1050" y="216" fill="{C_NAVY}" font-size="12" font-weight="bold">Scoreboard Status</text>
"""
    for i, (name, stim, target, stat, col) in enumerate(cases):
        y_row = 235 + i * 50
        svg += f"""    <!-- Row {i+1} -->
    <rect x="80" y="{y_row}" width="1120" height="44" rx="4" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="{y_row+26}" fill="{C_TEXT_MAIN}" font-size="12" font-weight="bold">{name}</text>
    <text x="440" y="{y_row+26}" fill="{C_TEXT_SUB}" font-size="11">{stim}</text>
    <text x="740" y="{y_row+26}" fill="{C_TEXT_SUB}" font-size="11">{target}</text>
    <rect x="1040" y="{y_row+10}" width="90" height="24" rx="4" fill="{C_GREEN_BG}" stroke="{C_GREEN}" stroke-width="1"/>
    <text x="1085" y="{y_row+26}" fill="{C_GREEN}" font-size="11" font-weight="bold" text-anchor="middle">{stat}</text>
"""

    svg += f"""    <!-- Bottom Summary Box -->
    <rect x="80" y="545" width="1120" height="75" rx="6" fill="{C_GREEN_BG}" stroke="{C_GREEN}" stroke-width="1"/>
    <text x="100" y="570" fill="{C_GREEN}" font-size="12" font-weight="bold">Regression Verification Results:</text>
    <text x="100" y="595" fill="{C_TEXT_MAIN}" font-size="11">5 coefficient profiles × 8,825 forecasts + 4,072-point replay: 100% bit-exact (0 mismatches).</text>
  </g>
"""
    svg += standard_footer("ftr_18", "Zero functional mismatches across extreme dynamic range, temperature jumps, and continuous streaming bursts.")
    svg += svg_footer()
    write_slide("18_corner_cases.svg", svg)

# ==============================================================================
# SLIDE 19: Physical Silicon Synthesis & Altera Cyclone II Results
# ==============================================================================
def gen_slide_19():
    svg = svg_header("content")
    svg += standard_header("hdr_19", "HARDWARE SYNTHESIS &amp; RESOURCE UTILIZATION", 
                           "Altera Cyclone II (EP2C35F672C6) Physical Synthesis Results", 
                           "Quartus II 13.0sp1 place-and-route resource utilization, multiplier footprint, and timing closure")
    
    svg += f"""  <g id="tbl_synthesis" data-pptx-bounds="60 135 1160 500">
    <rect x="60" y="135" width="1160" height="500" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="60" y="135" width="1160" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="80" y="162" fill="{C_NAVY}" font-size="14" font-weight="bold">QUARTUS II SYNTHESIS &amp; TIMING COMPARISON MATRIX</text>
    
    <!-- Table Header Row -->
    <rect x="80" y="195" width="1120" height="32" rx="4" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="216" fill="{C_NAVY}" font-size="12" font-weight="bold">Hardware Metric</text>
    <text x="360" y="216" fill="{C_NAVY}" font-size="12" font-weight="bold">Speed Core (Pipelined)</text>
    <text x="620" y="216" fill="{C_NAVY}" font-size="12" font-weight="bold">Resource Core (FSM)</text>
    <text x="880" y="216" fill="{C_NAVY}" font-size="12" font-weight="bold">Silicon Difference / Savings</text>
    
    <!-- Row 1: Logic Elements -->
    <rect x="80" y="235" width="1120" height="45" rx="4" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="263" fill="{C_TEXT_MAIN}" font-size="12" font-weight="bold">Total Logic Elements (LEs)</text>
    <text x="360" y="263" fill="{C_NAVY}" font-size="12">412 LEs (1.2% of EP2C35)</text>
    <text x="620" y="263" fill="{C_GREEN}" font-size="12" font-weight="bold">236 LEs (0.7% of EP2C35)</text>
    <text x="880" y="263" fill="{C_GREEN}" font-size="12" font-weight="bold">-176 LEs (-42.7% Area Saved!)</text>
    
    <!-- Row 2: Embedded Multipliers -->
    <rect x="80" y="285" width="1120" height="45" rx="4" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="313" fill="{C_TEXT_MAIN}" font-size="12" font-weight="bold">Embedded Multipliers (9-bit)</text>
    <text x="360" y="313" fill="{C_NAVY}" font-size="12">4 Blocks (2 17×16 Multipliers)</text>
    <text x="620" y="313" fill="{C_GREEN}" font-size="12" font-weight="bold">2 Blocks (1 17×16 Multiplier)</text>
    <text x="880" y="313" fill="{C_GREEN}" font-size="12" font-weight="bold">-2 Blocks (-50% DSP Saved!)</text>
    
    <!-- Row 3: Max Clock Freq -->
    <rect x="80" y="335" width="1120" height="45" rx="4" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="363" fill="{C_TEXT_MAIN}" font-size="12" font-weight="bold">Max Clock Frequency (F_max)</text>
    <text x="360" y="363" fill="{C_BLUE}" font-size="12" font-weight="bold">142.3 MHz (Speed Grade C6)</text>
    <text x="620" y="363" fill="{C_TEXT_MAIN}" font-size="12">118.5 MHz (Speed Grade C6)</text>
    <text x="880" y="363" fill="{C_BLUE}" font-size="12">+23.8 MHz (+20.1% for Speed)</text>
    
    <!-- Row 4: Initiation Interval -->
    <rect x="80" y="385" width="1120" height="45" rx="4" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="413" fill="{C_TEXT_MAIN}" font-size="12" font-weight="bold">Initiation Interval (II)</text>
    <text x="360" y="413" fill="{C_BLUE}" font-size="12" font-weight="bold">II = 1 Clock Cycle</text>
    <text x="620" y="413" fill="{C_TEXT_MAIN}" font-size="12">II = 10 Clock Cycles</text>
    <text x="880" y="413" fill="{C_BLUE}" font-size="12">10x Higher Throughput (Speed)</text>
    
    <!-- Row 5: Inference Latency -->
    <rect x="80" y="435" width="1120" height="45" rx="4" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="463" fill="{C_TEXT_MAIN}" font-size="12" font-weight="bold">Latency @ 50 MHz System Clock</text>
    <text x="360" y="463" fill="{C_TEXT_MAIN}" font-size="12">5 Cycles (100 nanoseconds)</text>
    <text x="620" y="463" fill="{C_TEXT_MAIN}" font-size="12">9 Cycles (180 nanoseconds)</text>
    <text x="880" y="463" fill="{C_TEXT_MUTED}" font-size="12">Both &lt; 0.20 microseconds</text>
    
    <!-- Synthesis Analysis Box -->
    <rect x="80" y="495" width="1120" height="120" rx="6" fill="{C_BLUE_LIGHT}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="100" y="522" fill="{C_NAVY}" font-size="12" font-weight="bold">Synthesis Findings &amp; Engineering Rationale:</text>
    <text x="100" y="546" fill="{C_TEXT_SUB}" font-size="11">• Area Footprint: Both cores occupy &lt;1.5% of Cyclone II capacity</text>
    <text x="100" y="569" fill="{C_TEXT_SUB}" font-size="11">• Resource Core: -42.7% LEs, -50% DSPs via multiplier time-muxing</text>
    <text x="100" y="594" fill="{C_GREEN}" font-size="11" font-weight="bold">• Speed Core: 142.3 MHz F_max provides 2.8x timing slack over 50 MHz</text>
  </g>
"""
    svg += standard_footer("ftr_19", "Quartus II synthesis confirms 42.7% area reduction for Resource Core and 142.3 MHz F_max for Speed Core.")
    svg += svg_footer()
    write_slide("19_synthesis_results.svg", svg)

# ==============================================================================
# SLIDE 20: Real-World In-Silico Validation on 2024–2025 Test Telemetry
# ==============================================================================
def gen_slide_20():
    svg = svg_header("content")
    svg += standard_header("hdr_20", "REAL-WORLD TELEMETRY VALIDATION", 
                           "In-Silico Validation on 2-Year Continuous Test Data", 
                           "Streaming 17,520 hours of continuous satellite telemetry through synthesized FPGA hardware")
    
    # Left Box: Summary Metrics (565 px wide)
    svg += f"""  <g id="box_val_summary" data-pptx-bounds="60 135 565 500">
    <rect x="60" y="135" width="565" height="500" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="60" y="135" width="565" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="80" y="162" fill="{C_NAVY}" font-size="14" font-weight="bold">HELD-OUT TEST DATASET METRICS (2024–2025)</text>
    
    <text x="80" y="205" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Dataset Volume &amp; Protocol:</text>
    <text x="80" y="228" fill="{C_TEXT_SUB}" font-size="12">• Jan 2024 – Dec 2025: 17,520 continuous hourly records</text>
    <text x="80" y="250" fill="{C_TEXT_SUB}" font-size="12">• Strict causal protocol: zero future data leakage</text>
    
    <text x="80" y="295" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Hardware Prediction Accuracy:</text>
    
    <rect x="80" y="315" width="525" height="50" rx="6" fill="{C_BLUE_LIGHT}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="338" fill="{C_NAVY}" font-size="12" font-weight="bold">Mean Absolute Error (MAE):  0.5381 °C</text>
    <text x="95" y="354" fill="{C_TEXT_SUB}" font-size="11">Average deviation across 17,520 hours of real weather.</text>
    
    <rect x="80" y="375" width="525" height="50" rx="6" fill="{C_BLUE_LIGHT}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="398" fill="{C_NAVY}" font-size="12" font-weight="bold">Root Mean Squared Error (RMSE):  0.7862 °C</text>
    <text x="95" y="414" fill="{C_TEXT_SUB}" font-size="11">Penalizes large transient forecast errors.</text>
    
    <rect x="80" y="440" width="525" height="175" rx="6" fill="{C_GREEN_BG}" stroke="{C_GREEN}" stroke-width="1"/>
    <text x="95" y="468" fill="{C_GREEN}" font-size="12" font-weight="bold">Baseline Outperformance Proof:</text>
    <text x="95" y="495" fill="{C_TEXT_MAIN}" font-size="11.5">• 74.1% Gain vs Persistence (2.080°C MAE)</text>
    <text x="95" y="520" fill="{C_TEXT_MAIN}" font-size="11.5">• 35.3% Gain vs Diurnal (0.832°C MAE)</text>
    <text x="95" y="545" fill="{C_TEXT_MAIN}" font-size="11.5">• 100% Bit-Exact to C++ reference (0 drift)</text>
    <line x1="95" y1="565" x2="585" y2="565" stroke="{C_GREEN}" stroke-width="0.8"/>
    <text x="95" y="592" fill="{C_GREEN}" font-size="11" font-weight="bold">Zero numerical drift over 2 years of continuous inference!</text>
  </g>
"""

    # Right Box: Distribution & Drift (565 px wide)
    svg += f"""  <g id="box_val_distrib" data-pptx-bounds="655 135 565 500">
    <rect x="655" y="135" width="565" height="500" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="655" y="135" width="565" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="675" y="162" fill="{C_NAVY}" font-size="14" font-weight="bold">ERROR DISTRIBUTION &amp; NUMERICAL STABILITY</text>
    
    <text x="675" y="205" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Residual Error Distribution:</text>
    
    <rect x="675" y="225" width="525" height="45" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="690" y="252" fill="{C_NAVY}" font-size="12" font-weight="bold">|Error| &lt;= 0.5 °C:  68.4% of all test hours</text>
    
    <rect x="675" y="278" width="525" height="45" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="690" y="305" fill="{C_NAVY}" font-size="12" font-weight="bold">|Error| &lt;= 1.0 °C:  91.8% of all test hours</text>
    
    <rect x="675" y="331" width="525" height="45" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="690" y="358" fill="{C_NAVY}" font-size="12" font-weight="bold">|Error| &lt;= 1.5 °C:  98.2% of all test hours</text>
    
    <text x="675" y="400" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Residual Statistical Properties:</text>
    <text x="675" y="425" fill="{C_TEXT_SUB}" font-size="12">• Mean: μ = -0.0018 °C (Zero-centered)</text>
    <text x="675" y="447" fill="{C_TEXT_SUB}" font-size="12">• StdDev: σ = 0.786 °C</text>
    <text x="675" y="469" fill="{C_TEXT_SUB}" font-size="12">• Zero cumulative drift across entire test run</text>
    
    <rect x="675" y="495" width="525" height="120" rx="6" fill="{C_CARD_ALT}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="690" y="522" fill="{C_NAVY}" font-size="12" font-weight="bold">Silicon Verification Audit:</text>
    <text x="690" y="546" fill="{C_TEXT_SUB}" font-size="11">• 17,520 hours simulated in under 2 minutes of hardware sim.</text>
    <text x="690" y="568" fill="{C_GREEN}" font-size="11" font-weight="bold">• Exactly 0 mismatches between RTL simulation and C++ reference.</text>
    <text x="690" y="592" fill="{C_GREEN}" font-size="11" font-weight="bold">• Confirms numerical stability and precision contract in silicon.</text>
  </g>
"""
    svg += standard_footer("ftr_20", "Over 17,520 hours of real telemetry, hardware prediction achieves 0.538°C MAE with zero numerical drift.")
    svg += svg_footer()
    write_slide("20_real_world_validation.svg", svg)

# ==============================================================================
# SLIDE 21: Project Conclusion & Future Roadmap
# ==============================================================================
def gen_slide_21():
    svg = svg_header("content")
    svg += standard_header("hdr_21", "PROJECT CONCLUSION &amp; FUTURE ROADMAP", 
                           "Engineering Summary, Contributions &amp; Extension Roadmap", 
                           "Core achievements across signal processing, RTL micro-architecture, and verification")
    
    # Left Panel: Core Achievements (565 px wide)
    svg += f"""  <g id="box_achieve" data-pptx-bounds="60 135 565 500">
    <rect x="60" y="135" width="565" height="500" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="60" y="135" width="565" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="80" y="162" fill="{C_NAVY}" font-size="14" font-weight="bold">CORE ENGINEERING ACHIEVEMENTS</text>
    
    <text x="80" y="205" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">1. Model-to-Silicon Workflow</text>
    <text x="80" y="228" fill="{C_TEXT_SUB}" font-size="11">• 43,800h NASA data: 0.538°C MAE (74.1% gain vs persistence)</text>
    
    <text x="80" y="265" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">2. Dual Synthesizable RTL Cores</text>
    <text x="80" y="288" fill="{C_TEXT_SUB}" font-size="11">• Speed Core: 6-stage pipeline, II=1, 142.3 MHz F_max, 412 LEs</text>
    <text x="80" y="308" fill="{C_TEXT_SUB}" font-size="11">• Resource Core: 10-state FSM, 1 shared mult, 236 LEs (-42.7%)</text>
    
    <text x="80" y="345" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">3. 100% Bit-Exact Verification via DPI-C</text>
    <text x="80" y="368" fill="{C_TEXT_SUB}" font-size="11">• SystemVerilog testbench paired with live C++ golden oracle</text>
    <text x="80" y="388" fill="{C_GREEN}" font-size="11" font-weight="bold">• 0 mismatches across 10,000+ synthetic and 17,520h test vectors</text>
    
    <text x="80" y="425" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">4. Standalone Cyclone II DE2 System</text>
    <text x="80" y="448" fill="{C_TEXT_SUB}" font-size="11">• RS-232 UART receiver and BCD 7-segment display logic</text>
    
    <rect x="80" y="485" width="525" height="125" rx="6" fill="{C_GREEN_BG}" stroke="{C_GREEN}" stroke-width="1"/>
    <text x="95" y="512" fill="{C_GREEN}" font-size="12" font-weight="bold">Academic Milestone:</text>
    <text x="95" y="538" fill="{C_TEXT_MAIN}" font-size="11">Completed full IC Design &amp; DV capstone flow:</text>
    <text x="95" y="562" fill="{C_NAVY}" font-size="12" font-weight="bold">Signal Theory → RTL Cores → DPI-C Verification → Silicon Proof</text>
  </g>
"""

    # Right Panel: Roadmap (565 px wide)
    svg += f"""  <g id="box_roadmap" data-pptx-bounds="655 135 565 500">
    <rect x="655" y="135" width="565" height="500" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="655" y="135" width="565" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="675" y="162" fill="{C_NAVY}" font-size="14" font-weight="bold">FUTURE TECHNICAL EXTENSIONS</text>
    
    <text x="675" y="205" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Extension 1: Multi-Variable Ridge Model</text>
    <text x="675" y="228" fill="{C_TEXT_SUB}" font-size="11">• Integrates Relative Humidity (RH2M) and Surface Pressure (PS)</text>
    <text x="675" y="248" fill="{C_TEXT_SUB}" font-size="11">• Ridge-6 benchmarked: MAE = 0.509°C (-5.4% error reduction)</text>
    
    <text x="675" y="285" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Extension 2: On-Chip Online LMS Adaptation</text>
    <text x="675" y="308" fill="{C_TEXT_SUB}" font-size="11">• On-chip Least Mean Squares weight updates for seasonal shifts</text>
    <text x="675" y="328" fill="{C_TEXT_SUB}" font-size="11">• Hardware footprint: +1 error subtractor and +3 scaling shifters</text>
    
    <text x="675" y="365" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Extension 3: ASIC Tape-Out Flow</text>
    <text x="675" y="388" fill="{C_TEXT_SUB}" font-size="11">• Synthesize targeting SkyWater 130nm PDK (OpenLane)</text>
    <text x="675" y="408" fill="{C_TEXT_SUB}" font-size="11">• Estimated die area: &lt;0.05 mm² with sub-milliwatt power</text>
    
    <rect x="675" y="485" width="525" height="125" rx="6" fill="{C_BLUE_LIGHT}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="690" y="512" fill="{C_NAVY}" font-size="12" font-weight="bold">Immediate Next Steps:</text>
    <text x="690" y="538" fill="{C_TEXT_MAIN}" font-size="11">1. Hardware demo video on physical Altera DE2 FPGA board</text>
    <text x="690" y="562" fill="{C_TEXT_MAIN}" font-size="11">2. Final technical report submission with Quartus II timing reports</text>
  </g>
"""
    svg += standard_footer("ftr_21", "Project fulfills all CE436 requirements with extensive DV and multi-architecture extensions.")
    svg += svg_footer()
    write_slide("21_conclusion_roadmap.svg", svg)

# ==============================================================================
# SLIDE 22: Capstone Defense Q&A & Technical Discussion
# ==============================================================================
def gen_slide_22():
    svg = svg_header("cover")
    svg += f"""  <g id="qa_header" data-pptx-bounds="60 40 1160 250">
    <rect x="60" y="40" width="1160" height="250" rx="10" fill="{C_CARD_BG}" stroke="{C_BORDER_DARK}" stroke-width="1.5"/>
    <rect x="60" y="40" width="10" height="250" rx="4" fill="{C_NAVY}"/>
    
    <rect x="90" y="65" width="400" height="26" rx="4" fill="{C_BLUE_LIGHT}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="100" y="83" fill="{C_NAVY}" font-size="12" font-weight="bold" letter-spacing="1">CE436 PROJECT DEFENSE &amp; EVALUATION</text>
    
    <text x="90" y="140" fill="{C_TEXT_MAIN}" font-size="34" font-weight="bold">Questions &amp; Technical Discussion</text>
    <text x="90" y="178" fill="{C_NAVY}" font-size="20" font-weight="bold">Thank You for Your Attention and Evaluation</text>
    <text x="90" y="212" fill="{C_TEXT_SUB}" font-size="15">FPGA Edge Temperature Predictor: Dual-Core RTL &amp; Bit-Exact DPI-C Verification</text>
    
    <rect x="90" y="235" width="350" height="26" rx="4" fill="{C_GREEN_BG}" stroke="{C_GREEN}" stroke-width="1"/>
    <text x="100" y="253" fill="{C_GREEN}" font-size="12" font-weight="bold">FACULTY OF COMPUTER ENGINEERING — CE-UIT</text>
  </g>
  <g id="card_advisor" data-pptx-bounds="60 315 365 315">
    <rect x="60" y="315" width="365" height="315" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="60" y="315" width="365" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="80" y="342" fill="{C_NAVY}" font-size="14" font-weight="bold">ACADEMIC SUPERVISION</text>
    
    <text x="80" y="385" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Course Instructor / Advisor:</text>
    <text x="80" y="407" fill="{C_NAVY}" font-size="15" font-weight="bold">Dr. Tran Xuan Phuoc</text>
    
    <text x="80" y="440" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Institution:</text>
    <text x="80" y="462" fill="{C_TEXT_SUB}" font-size="12">University of Information Technology</text>
    <text x="80" y="482" fill="{C_TEXT_SUB}" font-size="12">VNU-HCM</text>
    
    <text x="80" y="515" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Department:</text>
    <text x="80" y="537" fill="{C_TEXT_SUB}" font-size="12">Faculty of Computer Engineering (CE-UIT)</text>
    
    <rect x="80" y="565" width="325" height="40" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="590" fill="{C_NAVY}" font-size="12" font-weight="bold">Course Code: CE436.R11.VMTN</text>
  </g>
  <g id="card_team_contact" data-pptx-bounds="455 315 365 315">
    <rect x="455" y="315" width="365" height="315" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="455" y="315" width="365" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="475" y="342" fill="{C_NAVY}" font-size="14" font-weight="bold">STUDENT ENGINEERING TEAM</text>
    
    <text x="475" y="385" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Project Members:</text>
    <text x="475" y="410" fill="{C_TEXT_SUB}" font-size="12">• Le Dang Khoa (24520816) — Lead / RTL</text>
    <text x="475" y="432" fill="{C_TEXT_SUB}" font-size="12">• Nguyen Nghia Khoa (24520832) — Model</text>
    <text x="475" y="454" fill="{C_TEXT_SUB}" font-size="12">• Nguyen Minh Khoa (24520831) — DV / TB</text>
    
    <text x="475" y="488" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Open Source Repository:</text>
    <text x="475" y="512" fill="{C_BLUE}" font-size="12">github.com/KhoaLe-IC/fpga-temp-predictor</text>
    
    <rect x="475" y="565" width="325" height="40" rx="6" fill="{C_GREEN_BG}" stroke="{C_GREEN}" stroke-width="1"/>
    <text x="490" y="590" fill="{C_GREEN}" font-size="12" font-weight="bold">Full RTL, Testbench &amp; C++ Code Available</text>
  </g>
  <g id="card_backup_index" data-pptx-bounds="850 315 370 315">
    <rect x="850" y="315" width="370" height="315" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="850" y="315" width="370" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="870" y="342" fill="{C_NAVY}" font-size="14" font-weight="bold">BACKUP SLIDE DIRECTORY</text>
    
    <text x="870" y="385" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Quick Topic Navigation:</text>
    <text x="870" y="410" fill="{C_TEXT_SUB}" font-size="11">• Slides 4–5: Diurnal Math &amp; Tap Formulation</text>
    <text x="870" y="430" fill="{C_TEXT_SUB}" font-size="11">• Slide 6: Model Benchmarks (OLS vs Ridge vs MLP)</text>
    <text x="870" y="450" fill="{C_TEXT_SUB}" font-size="11">• Slide 7: Literature Comparison Matrix</text>
    <text x="870" y="470" fill="{C_TEXT_SUB}" font-size="11">• Slides 8–11: Q8.8/Q2.14, Bit Growth &amp; Sat16</text>
    <text x="870" y="490" fill="{C_TEXT_SUB}" font-size="11">• Slides 13–15: Pipelined Datapath &amp; FSM Mux</text>
    <text x="870" y="510" fill="{C_TEXT_SUB}" font-size="11">• Slides 17–18: DPI-C Architecture &amp; Regressions</text>
    <text x="870" y="530" fill="{C_TEXT_SUB}" font-size="11">• Slide 19: Quartus II Synthesis &amp; Timing Closure</text>
    
    <rect x="870" y="565" width="330" height="40" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="885" y="590" fill="{C_NAVY}" font-size="12" font-weight="bold">Ready for Committee Technical Q&amp;A</text>
  </g>
"""
    svg += svg_footer()
    write_slide("22_qa_defense.svg", svg)
