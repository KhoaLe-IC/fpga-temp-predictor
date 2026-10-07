#!/usr/bin/env python3
"""
Generate all 22 technical presentation slides as canonical SVGs for ppt-master.
Project: FPGA-Based Edge Temperature Predictor
Course: CE436 - Discrete-Time Signal Processing & Applications
Platform: Altera Cyclone II (EP2C35) on DE2 Board
"""

import sys
from pathlib import Path

PROJECT_DIR = Path("/home/khoale/Documents/University/Semester_5/CE436_Discrete-Time_Signal_Processing/fpga-temp-predictor/presentation/fpga_temp_predictor_20261007")
OUTPUT_DIR = PROJECT_DIR / "svg_output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Theme Palette: Deep Tech Semiconductor
C_BG = "#0B132B"          # Dark Navy/Slate Canvas
C_CARD_BG = "#162238"     # Container fill
C_CARD_ALT = "#1E2D4A"    # Slightly lighter container fill
C_BORDER = "#2A3D66"      # Subtle container border
C_TEXT_WHITE = "#FFFFFF"  # Primary typography
C_TEXT_MUTED = "#8D99AE"  # Secondary typography
C_CYAN = "#48CAE4"        # Primary accent / datapath / signals
C_AMBER = "#F77F00"       # Warning / saturation / critical metrics
C_GREEN = "#10B981"       # Success / pass status
C_RED = "#EF4444"         # Error / persistence baseline
C_BLUE = "#3B82F6"        # Structural blue

def svg_header(role="content"):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720"
     data-pptx-page-role="{role}" lang="en" font-family="Arial, Segoe UI, sans-serif">
  <rect id="bg" data-pptx-role="background" x="0" y="0" width="1280" height="720" fill="{C_BG}"/>
"""

def svg_footer():
    return "</svg>\n"

def standard_header(gid, eyebrow, title, subtitle):
    return f"""  <g id="{gid}" data-pptx-bounds="60 30 1160 85">
    <text x="60" y="52" fill="{C_CYAN}" font-size="13" font-weight="bold" letter-spacing="1">{eyebrow}</text>
    <text x="60" y="86" fill="{C_TEXT_WHITE}" font-size="26" font-weight="bold">{title}</text>
    <text x="60" y="108" fill="{C_TEXT_MUTED}" font-size="14">{subtitle}</text>
    <line x1="60" y1="114" x2="1220" y2="114" stroke="{C_BORDER}" stroke-width="1"/>
  </g>
"""

def standard_footer(gid, takeaway, badge="CE436 CAPSTONE"):
    return f"""  <g id="{gid}" data-pptx-bounds="60 655 1160 40">
    <rect x="60" y="655" width="1160" height="38" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="72" y="663" width="130" height="22" rx="4" fill="{C_CYAN}" fill-opacity="0.2"/>
    <text x="137" y="678" fill="{C_CYAN}" font-size="11" font-weight="bold" text-anchor="middle">{badge}</text>
    <text x="220" y="679" fill="{C_TEXT_WHITE}" font-size="13">{takeaway}</text>
  </g>
"""

def write_slide(filename, content):
    filepath = OUTPUT_DIR / filename
    filepath.write_text(content, encoding="utf-8")
    print(f"Generated: {filename}")

# ==========================================
# SLIDE 01: TITLE & WELCOME
# ==========================================
def gen_slide_01():
    s = svg_header("cover")
    s += f"""  <g id="hero_header" data-pptx-bounds="60 40 1160 250">
    <rect x="60" y="40" width="1160" height="240" rx="12" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="60" y="40" width="8" height="240" rx="4" fill="{C_CYAN}"/>
    <rect x="90" y="65" width="460" height="26" rx="4" fill="{C_CYAN}" fill-opacity="0.15"/>
    <text x="100" y="83" fill="{C_CYAN}" font-size="12" font-weight="bold" letter-spacing="1">CE436: DISCRETE-TIME SIGNAL PROCESSING &amp; APPLICATIONS</text>
    <text x="90" y="140" fill="{C_TEXT_WHITE}" font-size="36" font-weight="bold">FPGA-Based Edge Temperature Predictor</text>
    <text x="90" y="180" fill="{C_CYAN}" font-size="20" font-weight="bold">Dual-Architecture RTL Design &amp; Bit-Exact DPI-C Verification</text>
    <text x="90" y="215" fill="{C_TEXT_MUTED}" font-size="15">Fixed-Point Diurnal Residual Modeling on Altera Cyclone II (DE2) | 50 MHz Real-Time Inference</text>
    <rect x="90" y="235" width="310" height="24" rx="4" fill="{C_GREEN}" fill-opacity="0.2"/>
    <text x="100" y="252" fill="{C_GREEN}" font-size="12" font-weight="bold">HARDWARE VERIFIED: 100% BIT-EXACT MATCH</text>
  </g>
"""
    s += f"""  <g id="card_platform" data-pptx-bounds="60 310 365 305">
    <rect x="60" y="310" width="365" height="305" rx="10" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="60" y="310" width="365" height="40" rx="10" fill="{C_CARD_ALT}"/>
    <text x="80" y="336" fill="{C_CYAN}" font-size="14" font-weight="bold">TARGET PLATFORM &amp; IO</text>
    
    <text x="80" y="380" fill="{C_TEXT_WHITE}" font-size="14" font-weight="bold">Target Silicon:</text>
    <text x="80" y="402" fill="{C_TEXT_MUTED}" font-size="13">Altera Cyclone II EP2C35F672C6</text>
    
    <text x="80" y="435" fill="{C_TEXT_WHITE}" font-size="14" font-weight="bold">Development Board:</text>
    <text x="80" y="457" fill="{C_TEXT_MUTED}" font-size="13">Altera DE2 Development Board</text>
    
    <text x="80" y="490" fill="{C_TEXT_WHITE}" font-size="14" font-weight="bold">Clocking &amp; Serial Telemetry:</text>
    <text x="80" y="512" fill="{C_TEXT_MUTED}" font-size="13">50.000 MHz Oscillator | RS-232 UART</text>
    <text x="80" y="534" fill="{C_TEXT_MUTED}" font-size="13">115,200 Baud (16x Oversampling RX)</text>
    
    <rect x="80" y="560" width="325" height="36" rx="6" fill="{C_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="583" fill="{C_CYAN}" font-size="12" font-weight="bold">Resource Budget: 35 Embedded Multipliers</text>
  </g>
"""
    s += f"""  <g id="card_pipeline" data-pptx-bounds="455 310 365 305">
    <rect x="455" y="310" width="365" height="305" rx="10" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="455" y="310" width="365" height="40" rx="10" fill="{C_CARD_ALT}"/>
    <text x="475" y="336" fill="{C_CYAN}" font-size="14" font-weight="bold">ENGINEERING SCOPE</text>
    
    <text x="475" y="380" fill="{C_TEXT_WHITE}" font-size="14" font-weight="bold">Algorithmic Model:</text>
    <text x="475" y="402" fill="{C_TEXT_MUTED}" font-size="13">Diurnal Residual OLS Regression (3 Terms)</text>
    
    <text x="475" y="435" fill="{C_TEXT_WHITE}" font-size="14" font-weight="bold">Dual RTL Micro-Architectures:</text>
    <text x="475" y="457" fill="{C_TEXT_MUTED}" font-size="13">• Speed Core: Pipelined, II=1, 50 MSps</text>
    <text x="475" y="479" fill="{C_TEXT_MUTED}" font-size="13">• Resource Core: 10-State FSM, Shared Mult</text>
    
    <text x="475" y="512" fill="{C_TEXT_WHITE}" font-size="14" font-weight="bold">Verification Infrastructure:</text>
    <text x="475" y="534" fill="{C_TEXT_MUTED}" font-size="13">SystemVerilog Driver + DPI-C C++ Oracle</text>
    
    <rect x="475" y="560" width="325" height="36" rx="6" fill="{C_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="490" y="583" fill="{C_GREEN}" font-size="12" font-weight="bold">Quantization: Signed Q8.8 &amp; Q2.14 Formats</text>
  </g>
"""
    s += f"""  <g id="card_status" data-pptx-bounds="850 310 370 305">
    <rect x="850" y="310" width="370" height="305" rx="10" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="850" y="310" width="370" height="40" rx="10" fill="{C_CARD_ALT}"/>
    <text x="870" y="336" fill="{C_CYAN}" font-size="14" font-weight="bold">PROJECT DEFENSE METADATA</text>
    
    <text x="870" y="380" fill="{C_TEXT_WHITE}" font-size="14" font-weight="bold">Student / Presenter:</text>
    <text x="870" y="402" fill="{C_TEXT_MUTED}" font-size="13">Khoa Le &amp; Project Engineering Team</text>
    
    <text x="870" y="435" fill="{C_TEXT_WHITE}" font-size="14" font-weight="bold">Specialization Track:</text>
    <text x="870" y="457" fill="{C_TEXT_MUTED}" font-size="13">Undergraduate IC Design &amp; Verification (DV)</text>
    
    <text x="870" y="490" fill="{C_TEXT_WHITE}" font-size="14" font-weight="bold">Academic Context:</text>
    <text x="870" y="512" fill="{C_TEXT_MUTED}" font-size="13">Semester 5 Capstone Defense | CE436</text>
    
    <rect x="870" y="555" width="330" height="44" rx="6" fill="{C_AMBER}" fill-opacity="0.15" stroke="{C_AMBER}" stroke-width="1"/>
    <text x="885" y="575" fill="{C_AMBER}" font-size="11" font-weight="bold">EVALUATION FOCUS:</text>
    <text x="885" y="591" fill="{C_TEXT_WHITE}" font-size="12">Mathematical Rigor, RTL Sizing &amp; Bit-Exact DV</text>
  </g>
"""
    s += f"""  <g id="footer_hero" data-pptx-bounds="60 635 1160 55">
    <rect x="60" y="635" width="1160" height="50" rx="8" fill="{C_CARD_ALT}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="85" y="665" fill="{C_TEXT_WHITE}" font-size="13" font-weight="bold">FACULTY OF COMPUTER ENGINEERING — INTEGRATED CIRCUIT DESIGN LAB</text>
    <text x="1195" y="665" fill="{C_TEXT_MUTED}" font-size="13" text-anchor="end">Slide 1 / 22</text>
  </g>
"""
    s += svg_footer()
    write_slide("01_title_welcome.svg", s)

# ==========================================
# SLIDE 02: TEAM & OVERVIEW
# ==========================================
def gen_slide_02():
    s = svg_header("section")
    s += standard_header("hdr_02", "PROJECT STRUCTURE &amp; WORKFLOW", "Full-Stack IC Design Flow: From Math to Silicon", "Division of engineering responsibilities across algorithm, micro-architecture, and verification pillars")
    s += f"""  <g id="pillar_algo" data-pptx-bounds="60 135 365 500">
    <rect x="60" y="135" width="365" height="500" rx="10" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="60" y="135" width="365" height="42" rx="10" fill="{C_CARD_ALT}"/>
    <text x="80" y="162" fill="{C_CYAN}" font-size="14" font-weight="bold">PILLAR 1: DSP &amp; ALGORITHMS</text>
    
    <text x="80" y="210" fill="{C_TEXT_WHITE}" font-size="15" font-weight="bold">Meteorological Time-Series</text>
    <text x="80" y="235" fill="{C_TEXT_MUTED}" font-size="13">• NASA POWER satellite API integration</text>
    <text x="80" y="255" fill="{C_TEXT_MUTED}" font-size="13">• 5-year HCMC hourly dataset (43,800 pts)</text>
    <text x="80" y="275" fill="{C_TEXT_MUTED}" font-size="13">• Diurnal residual formulation: T(t-21)</text>
    
    <text x="80" y="315" fill="{C_TEXT_WHITE}" font-size="15" font-weight="bold">Model Benchmark Suite</text>
    <text x="80" y="340" fill="{C_TEXT_MUTED}" font-size="13">• Evaluated OLS, Ridge, MLP, GBDT</text>
    <text x="80" y="360" fill="{C_TEXT_MUTED}" font-size="13">• Offline OLS parameter extraction in C++</text>
    <text x="80" y="380" fill="{C_TEXT_MUTED}" font-size="13">• Target MAE: 0.538°C on test data</text>
    
    <text x="80" y="420" fill="{C_TEXT_WHITE}" font-size="15" font-weight="bold">Numerical Specifications</text>
    <text x="80" y="445" fill="{C_TEXT_MUTED}" font-size="13">• Signed Q8.8 inputs &amp; outputs (LSB=1/256)</text>
    <text x="80" y="465" fill="{C_TEXT_MUTED}" font-size="13">• Signed Q2.14 multiplier coefficients</text>
    <text x="80" y="485" fill="{C_TEXT_MUTED}" font-size="13">• Symmetric rounding &amp; floor scaling</text>
    
    <rect x="80" y="530" width="325" height="85" rx="6" fill="{C_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="555" fill="{C_CYAN}" font-size="12" font-weight="bold">Deliverable Artifacts:</text>
    <text x="95" y="575" fill="{C_TEXT_MUTED}" font-size="12">• data/hcmc_t2m_2021_2025.csv</text>
    <text x="95" y="595" fill="{C_TEXT_MUTED}" font-size="12">• software/train_models.py, benchmark.py</text>
  </g>
"""
    s += f"""  <g id="pillar_rtl" data-pptx-bounds="455 135 365 500">
    <rect x="455" y="135" width="365" height="500" rx="10" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="455" y="135" width="365" height="42" rx="10" fill="{C_CARD_ALT}"/>
    <text x="475" y="162" fill="{C_CYAN}" font-size="14" font-weight="bold">PILLAR 2: MICRO-ARCHITECTURE &amp; RTL</text>
    
    <text x="475" y="210" fill="{C_TEXT_WHITE}" font-size="15" font-weight="bold">Speed Core (temp_predictor_speed)</text>
    <text x="475" y="235" fill="{C_TEXT_MUTED}" font-size="13">• Fully pipelined 6-stage feed-forward</text>
    <text x="475" y="255" fill="{C_TEXT_MUTED}" font-size="13">• Initiation Interval II = 1 clock cycle</text>
    <text x="475" y="275" fill="{C_TEXT_MUTED}" font-size="13">• Throughput: 50 MSamples/sec @ 50 MHz</text>
    
    <text x="475" y="315" fill="{C_TEXT_WHITE}" font-size="15" font-weight="bold">Resource Core (temp_predictor_resource)</text>
    <text x="475" y="340" fill="{C_TEXT_MUTED}" font-size="13">• Time-multiplexed 10-state FSM datapath</text>
    <text x="475" y="360" fill="{C_TEXT_MUTED}" font-size="13">• Shares 1 DSP mult &amp; 1 subtractor ALU</text>
    <text x="475" y="380" fill="{C_TEXT_MUTED}" font-size="13">• Backpressure handshake: sample_ready</text>
    
    <text x="475" y="420" fill="{C_TEXT_WHITE}" font-size="15" font-weight="bold">Top-Level SoC Integration</text>
    <text x="475" y="445" fill="{C_TEXT_MUTED}" font-size="13">• 115,200 Baud UART RX/TX telemetry</text>
    <text x="475" y="465" fill="{C_TEXT_MUTED}" font-size="13">• Packet parser, formatter, and FIFO</text>
    <text x="475" y="485" fill="{C_TEXT_MUTED}" font-size="13">• Metastability reset_sync synchronizer</text>
    
    <rect x="475" y="530" width="325" height="85" rx="6" fill="{C_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="490" y="555" fill="{C_CYAN}" font-size="12" font-weight="bold">Deliverable Artifacts:</text>
    <text x="490" y="575" fill="{C_TEXT_MUTED}" font-size="12">• hardware/speed_optimized/ (Verilog)</text>
    <text x="490" y="595" fill="{C_TEXT_MUTED}" font-size="12">• hardware/resource_optimized/ (Verilog)</text>
  </g>
"""
    s += f"""  <g id="pillar_dv" data-pptx-bounds="850 135 370 500">
    <rect x="850" y="135" width="370" height="500" rx="10" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="850" y="135" width="370" height="42" rx="10" fill="{C_CARD_ALT}"/>
    <text x="870" y="162" fill="{C_CYAN}" font-size="14" font-weight="bold">PILLAR 3: VERIFICATION &amp; FPGA</text>
    
    <text x="870" y="210" fill="{C_TEXT_WHITE}" font-size="15" font-weight="bold">SystemVerilog DPI-C Co-Sim</text>
    <text x="870" y="235" fill="{C_TEXT_MUTED}" font-size="13">• Live C++ reference oracle (ols_reference.hpp)</text>
    <text x="870" y="255" fill="{C_TEXT_MUTED}" font-size="13">• Cycle-accurate scoreboard checking</text>
    <text x="870" y="275" fill="{C_TEXT_MUTED}" font-size="13">• Zero-tolerance: 0 LSB mismatch allowed</text>
    
    <text x="870" y="315" fill="{C_TEXT_WHITE}" font-size="15" font-weight="bold">7-Phase Corner-Case Suite</text>
    <text x="870" y="340" fill="{C_TEXT_MUTED}" font-size="13">• 24-sample warm-up lockout verification</text>
    <text x="870" y="360" fill="{C_TEXT_MUTED}" font-size="13">• Extreme thermal saturation sweeps (sat16)</text>
    <text x="870" y="380" fill="{C_TEXT_MUTED}" font-size="13">• 4,096-sample bursts &amp; random stalls</text>
    
    <text x="870" y="420" fill="{C_TEXT_WHITE}" font-size="15" font-weight="bold">Cyclone II Physical Synthesis</text>
    <text x="870" y="445" fill="{C_TEXT_MUTED}" font-size="13">• Fmax > 125 MHz (2.5x timing margin)</text>
    <text x="870" y="465" fill="{C_TEXT_MUTED}" font-size="13">• Resource usage: &lt;1% Logic Elements</text>
    <text x="870" y="485" fill="{C_TEXT_MUTED}" font-size="13">• Ultra-low power: ~11.8 mW dynamic</text>
    
    <rect x="870" y="530" width="330" height="85" rx="6" fill="{C_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="885" y="555" fill="{C_CYAN}" font-size="12" font-weight="bold">Deliverable Artifacts:</text>
    <text x="885" y="575" fill="{C_TEXT_MUTED}" font-size="12">• hardware/tb/ols_tb_driver.sv, dpi/</text>
    <text x="885" y="595" fill="{C_TEXT_MUTED}" font-size="12">• 100% test pass rate on 10,000+ vectors</text>
  </g>
"""
    s += standard_footer("ftr_02", "Pillar Metrics: 43,800 Dataset Samples | 2 Synthesizable RTL Cores | 100% Bit-Exact DPI-C Coverage")
    s += svg_footer()
    write_slide("02_team_overview.svg", s)

# ==========================================
# SLIDE 03: AGENDA
# ==========================================
def gen_slide_03():
    s = svg_header("toc")
    s += standard_header("hdr_03", "PRESENTATION ROADMAP", "Technical Agenda: 4 Sequential Phases of Defense", "Structured walkthrough of theoretical derivation, fixed-point sizing, RTL micro-architecture, and verification")
    
    phases = [
        ("PHASE I: MATHEMATICAL FOUNDATIONS", "Slides 4 – 7", [
            ("Slide 4", "Problem Formulation &amp; Edge Context"),
            ("Slide 5", "Diurnal Residual Math Equation"),
            ("Slide 6", "ML Benchmark Suite (OLS vs MLP)"),
            ("Slide 7", "Hardware vs Accuracy Trade-off")
        ], C_BLUE),
        ("PHASE II: FIXED-POINT ARITHMETIC", "Slides 8 – 11", [
            ("Slide 8", "Q8.8 &amp; Q2.14 Quantization Contract"),
            ("Slide 9", "Binary Alignment &amp; 35-bit Acc"),
            ("Slide 10", "Hardware Floor-Scaling Pitfall"),
            ("Slide 11", "Output Saturation Unit (sat16)")
        ], C_CYAN),
        ("PHASE III: DUAL RTL ARCHITECTURES", "Slides 12 – 16", [
            ("Slide 12", "Speed vs Resource Paradigms"),
            ("Slide 13", "6-Stage Pipelined Speed Core"),
            ("Slide 14", "Shared Datapath Resource Core"),
            ("Slide 15", "10-State FSM Controller"),
            ("Slide 16", "Top-Level SoC &amp; UART Telemetry")
        ], C_AMBER),
        ("PHASE IV: VERIFICATION &amp; DEFENSE", "Slides 17 – 22", [
            ("Slide 17", "SystemVerilog DPI-C Architecture"),
            ("Slide 18", "7-Phase Corner-Case Stress Suite"),
            ("Slide 19", "Cyclone II Synthesis &amp; Timing"),
            ("Slide 20", "HCMC 2-Year In-Silico Inference"),
            ("Slide 21", "Conclusion &amp; Hardware Demo"),
            ("Slide 22", "Technical Defense &amp; Q&amp;A")
        ], C_GREEN)
    ]
    
    xs = [60, 355, 650, 945]
    ws = [270, 270, 270, 275]
    
    for i, (p_title, p_slides, items, accent) in enumerate(phases):
        x, w = xs[i], ws[i]
        s += f"""  <g id="agenda_col_{i+1}" data-pptx-bounds="{x} 135 {w} 500">
    <rect x="{x}" y="135" width="{w}" height="500" rx="10" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="{x}" y="135" width="{w}" height="50" rx="10" fill="{C_CARD_ALT}"/>
    <rect x="{x}" y="135" width="4" height="50" rx="2" fill="{accent}"/>
    <text x="{x+15}" y="157" fill="{accent}" font-size="11" font-weight="bold">{p_title}</text>
    <text x="{x+15}" y="174" fill="{C_TEXT_MUTED}" font-size="12">{p_slides}</text>
    
    <g id="agenda_items_{i+1}">
"""
        y_curr = 205
        for s_idx, (s_num, s_desc) in enumerate(items):
            s += f"""      <rect x="{x+12}" y="{y_curr}" width="{w-24}" height="42" rx="6" fill="{C_BG}" stroke="{C_BORDER}" stroke-width="1"/>
      <text x="{x+22}" y="{y_curr+18}" fill="{C_CYAN}" font-size="11" font-weight="bold">{s_num}</text>
      <text x="{x+22}" y="{y_curr+32}" fill="{C_TEXT_WHITE}" font-size="11">{s_desc}</text>
"""
            y_curr += 48
            
        s += f"""    </g>
  </g>
"""
    
    s += standard_footer("ftr_03", "22 Dense Technical Slides | 100% Aligned with CE436 Syllabus &amp; DE2 Hardware Implementation")
    s += svg_footer()
    write_slide("03_agenda.svg", s)

# ==========================================
# SLIDE 04: PROBLEM FORMULATION & DATASET
# ==========================================
def gen_slide_04():
    s = svg_header("content")
    s += standard_header("hdr_04", "METEOROLOGICAL EDGE COMPUTING", "Edge Meteorological Forecasting: Constraints &amp; Dataset", "Real-time 3-hour ahead surface temperature prediction for resource-constrained IoT weather stations")
    
    # Col 1: Edge Computing Context (60 135 565 500)
    s += f"""  <g id="col_edge_context" data-pptx-bounds="60 135 565 500">
    <rect x="60" y="135" width="565" height="500" rx="10" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="60" y="135" width="565" height="42" rx="10" fill="{C_CARD_ALT}"/>
    <text x="80" y="162" fill="{C_CYAN}" font-size="14" font-weight="bold">EDGE COMPUTING MOTIVATION &amp; TRADEOFFS</text>
    
    <text x="80" y="210" fill="{C_TEXT_WHITE}" font-size="15" font-weight="bold">The Telemetry Energy Bottleneck</text>
    <text x="80" y="235" fill="{C_TEXT_MUTED}" font-size="13">• Remote edge weather stations operate on solar / battery budgets.</text>
    <text x="80" y="255" fill="{C_TEXT_MUTED}" font-size="13">• Wireless RF transmission (Cellular / LoRa) burns 10x–100x more energy</text>
    <text x="80" y="275" fill="{C_TEXT_MUTED}" font-size="13">  per bit than local on-chip digital arithmetic.</text>
    <text x="80" y="295" fill="{C_TEXT_MUTED}" font-size="13">• Cloud dependency introduces network latency, jitter, and outage risks.</text>
    
    <text x="80" y="335" fill="{C_TEXT_WHITE}" font-size="15" font-weight="bold">On-Chip FPGA Inference Advantage</text>
    <text x="80" y="360" fill="{C_TEXT_MUTED}" font-size="13">• Performs local predictive filtering at sub-milliwatt dynamic power.</text>
    <text x="80" y="380" fill="{C_TEXT_MUTED}" font-size="13">• Deterministic cycle-level latency: results ready within microseconds.</text>
    <text x="80" y="400" fill="{C_TEXT_MUTED}" font-size="13">• Transmit over RF only on severe micro-climate divergence / alerts.</text>
    
    <rect x="80" y="440" width="525" height="175" rx="8" fill="{C_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="100" y="468" fill="{C_AMBER}" font-size="13" font-weight="bold">TARGET FORECAST HORIZON SPECIFICATION</text>
    <text x="100" y="495" fill="{C_TEXT_WHITE}" font-size="13">Target: Predict temperature 3 hours in advance: </text>
    <text x="420" y="495" fill="{C_CYAN}" font-size="14" font-weight="bold">T_hat(t+3)</text>
    <text x="100" y="522" fill="{C_TEXT_MUTED}" font-size="12">• Horizon allows agricultural shade deployment and HVAC pre-cooling.</text>
    <text x="100" y="544" fill="{C_TEXT_MUTED}" font-size="12">• System clock: 50.0 MHz | Processing latency: 5 clock cycles (100 ns!).</text>
    <text x="100" y="566" fill="{C_TEXT_MUTED}" font-size="12">• Zero external DRAM requirement; internal logic registers store history.</text>
    <text x="100" y="588" fill="{C_GREEN}" font-size="12" font-weight="bold">Achieves full edge autonomy with zero cloud dependency.</text>
  </g>
"""
    # Col 2: Dataset Profile (655 135 565 500)
    s += f"""  <g id="col_dataset_profile" data-pptx-bounds="655 135 565 500">
    <rect x="655" y="135" width="565" height="500" rx="10" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="655" y="135" width="565" height="42" rx="10" fill="{C_CARD_ALT}"/>
    <text x="675" y="162" fill="{C_CYAN}" font-size="14" font-weight="bold">DATASET PROFILE: NASA POWER SATELLITE API</text>
    
    <text x="675" y="210" fill="{C_TEXT_WHITE}" font-size="15" font-weight="bold">Geographic &amp; Climatic Parameters</text>
    <text x="675" y="235" fill="{C_TEXT_MUTED}" font-size="13">• Target Location: Ho Chi Minh City, Vietnam (10.82°N, 106.63°E).</text>
    <text x="675" y="255" fill="{C_TEXT_MUTED}" font-size="13">• Climate Zone: Tropical Monsoon (pronounced dry &amp; wet rainy seasons).</text>
    <text x="675" y="275" fill="{C_TEXT_MUTED}" font-size="13">• Telemetry: Hourly Surface Temperature at 2 Meters (T2M) in °C.</text>
    
    <text x="675" y="315" fill="{C_TEXT_WHITE}" font-size="15" font-weight="bold">Chronological Partition &amp; Scale</text>
    <text x="675" y="340" fill="{C_TEXT_MUTED}" font-size="13">• Total Dataset Span: 5 Full Years (2021 – 2025), 43,800+ hourly points.</text>
    <text x="675" y="360" fill="{C_TEXT_MUTED}" font-size="13">• Training Set: 2021–2023 (26,280 samples) for offline OLS fitting.</text>
    <text x="675" y="380" fill="{C_TEXT_MUTED}" font-size="13">• Held-Out Test Set: 2024–2025 (17,520 samples) for hardware validation.</text>
    
    <rect x="675" y="415" width="525" height="200" rx="8" fill="{C_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="695" y="443" fill="{C_CYAN}" font-size="13" font-weight="bold">STATISTICAL DATA DISTRIBUTION &amp; DYNAMICS</text>
    
    <rect x="695" y="460" width="245" height="60" rx="6" fill="{C_CARD_ALT}"/>
    <text x="710" y="482" fill="{C_TEXT_MUTED}" font-size="11">MIN / MAX RANGE</text>
    <text x="710" y="506" fill="{C_TEXT_WHITE}" font-size="16" font-weight="bold">+16.4°C to +40.8°C</text>
    
    <rect x="955" y="460" width="245" height="60" rx="6" fill="{C_CARD_ALT}"/>
    <text x="970" y="482" fill="{C_TEXT_MUTED}" font-size="11">MEAN &amp; STD DEV</text>
    <text x="970" y="506" fill="{C_CYAN}" font-size="16" font-weight="bold">28.12°C | σ = 3.65°C</text>
    
    <text x="695" y="545" fill="{C_TEXT_WHITE}" font-size="12" font-weight="bold">Diurnal Dynamic:</text>
    <text x="805" y="545" fill="{C_TEXT_MUTED}" font-size="12">Peak solar heating ~13:00; minimum ~05:00.</text>
    
    <text x="695" y="568" fill="{C_TEXT_WHITE}" font-size="12" font-weight="bold">Monsoon Dynamic:</text>
    <text x="815" y="568" fill="{C_TEXT_MUTED}" font-size="12">Afternoon rain drops temperature by 4°C–6°C in 2 hrs.</text>
    
    <text x="695" y="595" fill="{C_GREEN}" font-size="12" font-weight="bold">→ Rigorous testbed for testing both periodic and sudden thermal transients.</text>
  </g>
"""
    s += standard_footer("ftr_04", "Forecast Horizon: 3 Hours Ahead | Latency: 5 Clock Cycles @ 50 MHz (100 ns) vs Multi-Second Cloud REST APIs")
    s += svg_footer()
    write_slide("04_problem_formulation.svg", s)

# ==========================================
# SLIDE 05: MATHEMATICAL FORMULATION
# ==========================================
def gen_slide_05():
    s = svg_header("content")
    s += standard_header("hdr_05", "MATHEMATICAL FORMULATION", "Diurnal Residual Modeling: Mathematical Decomposition", "Physics-informed time-series equation isolating periodic diurnal heating, inter-day shifts, and short-term trends")
    
    # Top Equation Callout Box (60 130 1160 145)
    s += f"""  <g id="box_equation" data-pptx-bounds="60 130 1160 145">
    <rect x="60" y="130" width="1160" height="145" rx="10" fill="{C_CARD_BG}" stroke="{C_CYAN}" stroke-width="1.5"/>
    <text x="90" y="160" fill="{C_CYAN}" font-size="13" font-weight="bold" letter-spacing="1">CORE LINEAR PREDICTION EQUATION (OLS FORMULATION)</text>
    
    <rect x="90" y="175" width="1100" height="52" rx="6" fill="{C_BG}"/>
    <text x="110" y="210" fill="{C_TEXT_WHITE}" font-size="22" font-weight="bold">
      T_hat(t+3) = <tspan fill="{C_CYAN}">T(t-21)</tspan> + <tspan fill="{C_AMBER}">a</tspan>·[T(t) - T(t-24)] + <tspan fill="{C_GREEN}">b</tspan>·[T(t) - T(t-3)] + <tspan fill="{C_TEXT_MUTED}">c</tspan>
    </text>
    
    <text x="90" y="255" fill="{C_TEXT_MUTED}" font-size="12">
      Trained offline via Ordinary Least Squares on 26,280 samples (2021–2023) to globally minimize Mean Squared Error (MSE).
    </text>
  </g>
"""
    # 3 Term Decomposition Cards (60 295 365 345, 455 295 365 345, 850 295 370 345)
    s += f"""  <g id="term_anchor" data-pptx-bounds="60 295 365 345">
    <rect x="60" y="295" width="365" height="345" rx="10" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="60" y="295" width="365" height="40" rx="10" fill="{C_CARD_ALT}"/>
    <text x="80" y="321" fill="{C_CYAN}" font-size="14" font-weight="bold">TERM 1: DIURNAL ANCHOR T(t-21)</text>
    
    <text x="80" y="365" fill="{C_TEXT_WHITE}" font-size="14" font-weight="bold">Temporal Index Derivation:</text>
    <text x="80" y="387" fill="{C_TEXT_MUTED}" font-size="13">• Target hour: (t + 3).</text>
    <text x="80" y="407" fill="{C_TEXT_MUTED}" font-size="13">• Exactly 24 hours prior to target:</text>
    <text x="80" y="427" fill="{C_CYAN}" font-size="14" font-weight="bold">  (t + 3) - 24 = t - 21</text>
    
    <text x="80" y="465" fill="{C_TEXT_WHITE}" font-size="14" font-weight="bold">Physical Insight:</text>
    <text x="80" y="487" fill="{C_TEXT_MUTED}" font-size="13">• Captures identical solar elevation angle</text>
    <text x="80" y="507" fill="{C_TEXT_MUTED}" font-size="13">  from yesterday's diurnal cycle.</text>
    <text x="80" y="527" fill="{C_TEXT_MUTED}" font-size="13">• Serves as the base baseline pedestal.</text>
    
    <rect x="80" y="555" width="325" height="65" rx="6" fill="{C_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="580" fill="{C_GREEN}" font-size="12" font-weight="bold">Error Reduction Alone:</text>
    <text x="95" y="600" fill="{C_TEXT_MUTED}" font-size="12">Slashes MAE from 2.08°C down to 0.83°C!</text>
  </g>
"""
    s += f"""  <g id="term_trend" data-pptx-bounds="455 295 365 345">
    <rect x="455" y="295" width="365" height="345" rx="10" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="455" y="295" width="365" height="40" rx="10" fill="{C_CARD_ALT}"/>
    <text x="475" y="321" fill="{C_AMBER}" font-size="14" font-weight="bold">TERM 2: INTER-DAY TREND</text>
    
    <text x="475" y="365" fill="{C_TEXT_WHITE}" font-size="14" font-weight="bold">Difference Formulation: D1</text>
    <text x="475" y="387" fill="{C_AMBER}" font-size="14" font-weight="bold">D1 = T(t) - T(t-24)</text>
    <text x="475" y="410" fill="{C_TEXT_MUTED}" font-size="13">• Compares current observation T(t) to the</text>
    <text x="475" y="430" fill="{C_TEXT_MUTED}" font-size="13">  exact same hour yesterday T(t-24).</text>
    
    <text x="475" y="465" fill="{C_TEXT_WHITE}" font-size="14" font-weight="bold">Physical Insight &amp; Weight a:</text>
    <text x="475" y="487" fill="{C_TEXT_MUTED}" font-size="13">• Captures multi-day weather fronts,</text>
    <text x="475" y="507" fill="{C_TEXT_MUTED}" font-size="13">  heatwaves, or persistent cloud cover.</text>
    
    <rect x="475" y="535" width="325" height="85" rx="6" fill="{C_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="490" y="560" fill="{C_AMBER}" font-size="12" font-weight="bold">Optimal OLS Weight: a ≈ 0.745502</text>
    <text x="490" y="582" fill="{C_TEXT_MUTED}" font-size="12">• Strongest predictive parameter in model.</text>
    <text x="490" y="602" fill="{C_TEXT_WHITE}" font-size="12">• Hardware Q2.14: A = 12214 (0.745483)</text>
  </g>
"""
    s += f"""  <g id="term_gradient" data-pptx-bounds="850 295 370 345">
    <rect x="850" y="295" width="370" height="345" rx="10" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="850" y="295" width="370" height="40" rx="10" fill="{C_CARD_ALT}"/>
    <text x="870" y="321" fill="{C_GREEN}" font-size="14" font-weight="bold">TERM 3: SHORT-TERM GRADIENT</text>
    
    <text x="870" y="365" fill="{C_TEXT_WHITE}" font-size="14" font-weight="bold">Difference Formulation: D2</text>
    <text x="870" y="387" fill="{C_GREEN}" font-size="14" font-weight="bold">D2 = T(t) - T(t-3)</text>
    <text x="870" y="410" fill="{C_TEXT_MUTED}" font-size="13">• Rate of temperature change over the</text>
    <text x="870" y="430" fill="{C_TEXT_MUTED}" font-size="13">  immediate past 3 observation hours.</text>
    
    <text x="870" y="465" fill="{C_TEXT_WHITE}" font-size="14" font-weight="bold">Physical Insight &amp; Weight b, c:</text>
    <text x="870" y="487" fill="{C_TEXT_MUTED}" font-size="13">• Captures sudden morning solar ramps or</text>
    <text x="870" y="507" fill="{C_TEXT_MUTED}" font-size="13">  afternoon rainstorm temperature drops.</text>
    
    <rect x="870" y="535" width="330" height="85" rx="6" fill="{C_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="885" y="560" fill="{C_GREEN}" font-size="12" font-weight="bold">Optimal OLS Weight: b ≈ 0.009139</text>
    <text x="885" y="582" fill="{C_TEXT_MUTED}" font-size="12">• Fine short-term damping gradient.</text>
    <text x="885" y="602" fill="{C_TEXT_WHITE}" font-size="12">• Hardware Q2.14: B = 150 (0.009155)</text>
  </g>
"""
    s += standard_footer("ftr_05", "Parameter Weights: a = 0.745502 (Day Trend) | b = 0.009139 (3-hr Gradient) | c = 0.001147 (DC Thermal Bias)")
    s += svg_footer()
    write_slide("05_math_formulation.svg", s)

print("Slides 1-5 complete.")
