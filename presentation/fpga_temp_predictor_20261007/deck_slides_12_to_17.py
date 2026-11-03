# ==============================================================================
# DECK SLIDES 12 TO 17: RTL MICRO-ARCHITECTURE, TIMING & VERIFICATION
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
# SLIDE 12: Dual RTL Micro-Architectures Overview
# ==============================================================================
def gen_slide_12():
    svg = svg_header("content")
    svg += standard_header("hdr_12", "RTL MICRO-ARCHITECTURE COMPARISON", 
                           "Dual Implementations: Speed Core vs Resource Core", 
                           "Pipelined streaming parallelism vs time-multiplexed hardware reuse")
    
    # Left Card: Speed Core (565 px wide)
    svg += f"""  <g id="arch_speed_card" data-pptx-bounds="60 135 565 500">
    <rect x="60" y="135" width="565" height="500" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="60" y="135" width="565" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="80" y="162" fill="{C_NAVY}" font-size="14" font-weight="bold">CORE A: SPEED-OPTIMIZED STREAMING PIPELINE</text>
    
    <text x="80" y="205" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Datapath Micro-Architecture:</text>
    <text x="80" y="228" fill="{C_TEXT_SUB}" font-size="12">• 6 Register Stages (S0 capture to S5 saturation)</text>
    <text x="80" y="250" fill="{C_TEXT_SUB}" font-size="12">• Dual Multipliers: 2 parallel 17×16 signed DSP units</text>
    <text x="80" y="272" fill="{C_TEXT_SUB}" font-size="12">• History Buffer: 25-stage shift register with wire taps</text>
    
    <text x="80" y="310" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Throughput &amp; Timing Metrics:</text>
    <text x="80" y="333" fill="{C_TEXT_SUB}" font-size="12">• Throughput: II = 1 (1 sample/clock, 0 bubbles)</text>
    <text x="80" y="355" fill="{C_TEXT_SUB}" font-size="12">• Latency: 5 clock cycles (100 ns @ 50 MHz)</text>
    <text x="80" y="377" fill="{C_TEXT_SUB}" font-size="12">• Max Frequency: 142.3 MHz F_max (2.8x slack)</text>
    
    <rect x="80" y="410" width="525" height="200" rx="6" fill="{C_BLUE_LIGHT}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="438" fill="{C_NAVY}" font-size="13" font-weight="bold">Cyclone II Profile (EP2C35):</text>
    <text x="95" y="465" fill="{C_TEXT_MAIN}" font-size="12">• Logic Elements: 412 LEs (1.2% total capacity)</text>
    <text x="95" y="490" fill="{C_TEXT_MAIN}" font-size="12">• Multipliers: 2 DSP units (4 9-bit blocks)</text>
    <text x="95" y="515" fill="{C_TEXT_MAIN}" font-size="12">• Throughput: 50.0 MSamples/sec @ 50 MHz</text>
    <line x1="95" y1="535" x2="585" y2="535" stroke="{C_BORDER_DARK}" stroke-width="1"/>
    <text x="95" y="562" fill="{C_NAVY}" font-size="12" font-weight="bold">Target Domain: High-Rate Streaming</text>
    <text x="95" y="585" fill="{C_BLUE}" font-size="12">Multi-channel streams, radar, and lidar edge nodes.</text>
  </g>
"""

    # Right Card: Resource Core (565 px wide)
    svg += f"""  <g id="arch_res_card" data-pptx-bounds="655 135 565 500">
    <rect x="655" y="135" width="565" height="500" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="655" y="135" width="565" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="675" y="162" fill="{C_NAVY}" font-size="14" font-weight="bold">CORE B: RESOURCE-OPTIMIZED TIME-MUXED FSM</text>
    
    <text x="675" y="205" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Sequential Micro-Architecture:</text>
    <text x="675" y="228" fill="{C_TEXT_SUB}" font-size="12">• 10-State Sequential FSM controller</text>
    <text x="675" y="250" fill="{C_TEXT_SUB}" font-size="12">• Single Multiplier: 1 17×16 DSP time-multiplexed</text>
    <text x="675" y="272" fill="{C_TEXT_SUB}" font-size="12">• Reused ALU: Serial differences and sums</text>
    
    <text x="675" y="310" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Throughput &amp; Timing Metrics:</text>
    <text x="675" y="333" fill="{C_TEXT_SUB}" font-size="12">• Throughput: II = 10 clock cycles per sample</text>
    <text x="675" y="355" fill="{C_TEXT_SUB}" font-size="12">• Latency: 9 clock cycles (180 ns @ 50 MHz)</text>
    <text x="675" y="377" fill="{C_TEXT_SUB}" font-size="12">• Max Frequency: 118.5 MHz F_max (2.4x slack)</text>
    
    <rect x="675" y="410" width="525" height="200" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="690" y="438" fill="{C_NAVY}" font-size="13" font-weight="bold">Cyclone II Profile (EP2C35):</text>
    <text x="690" y="465" fill="{C_GREEN}" font-size="12" font-weight="bold">• Logic Elements: 236 LEs (-42.7% area reduction!)</text>
    <text x="690" y="490" fill="{C_GREEN}" font-size="12" font-weight="bold">• Multipliers: 1 DSP unit (-50% silicon footprint)</text>
    <text x="690" y="515" fill="{C_TEXT_MAIN}" font-size="12">• Throughput: 5.0 MSamples/sec @ 50 MHz</text>
    <line x1="690" y1="535" x2="1180" y2="535" stroke="{C_BORDER_DARK}" stroke-width="1"/>
    <text x="690" y="562" fill="{C_NAVY}" font-size="12" font-weight="bold">Target Domain: Low-Power Edge IoT</text>
    <text x="690" y="585" fill="{C_GREEN}" font-size="12">Battery-powered weather pods and remote sensor nodes.</text>
  </g>
"""
    svg += standard_footer("ftr_12", "Dual architectures expose Pareto trade-offs: Speed maximizes throughput (II=1), Resource cuts area by 42.7%.")
    svg += svg_footer()
    write_slide("12_dual_architectures.svg", svg)

# ==============================================================================
# SLIDE 13: Speed Core: 6-Stage Pipelined Datapath Schematic
# ==============================================================================
def gen_slide_13():
    svg = svg_header("content")
    svg += standard_header("hdr_13", "PIPELINED MICRO-ARCHITECTURE", 
                           "Speed Core: 6-Stage Pipelined Datapath Schematic (II = 1)", 
                           "Dedicated registers, dual DSP units, and zero-bubble streaming")
    
    # Hero Full-Width Schematic Container
    svg += f"""  <g id="rtl_schematic_box" data-pptx-bounds="60 135 1160 500">
    <rect x="60" y="135" width="1160" height="500" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="60" y="135" width="1160" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="80" y="162" fill="{C_NAVY}" font-size="14" font-weight="bold">6-STAGE REGISTER PIPELINE DATAPATH (temp_predictor_speed.v)</text>
    
    <!-- Stage 0: Tap Extraction (x=80, w=165) -->
    <rect x="80" y="195" width="165" height="260" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1.5"/>
    <rect x="80" y="195" width="165" height="30" rx="6" fill="{C_CARD_ALT}"/>
    <text x="95" y="215" fill="{C_NAVY}" font-size="12" font-weight="bold">STAGE 0</text>
    <text x="95" y="245" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Tap Capture</text>
    <text x="95" y="272" fill="{C_TEXT_SUB}" font-size="11">25-Sample Buffer</text>
    <text x="95" y="295" fill="{C_TEXT_SUB}" font-size="11">T(t), T24, T3, T21</text>
    <text x="95" y="320" fill="{C_NAVY}" font-size="11" font-weight="bold">Bus: 16b (Q8.8)</text>
    <rect x="90" y="390" width="145" height="50" rx="4" fill="{C_BLUE_LIGHT}" stroke="{C_BLUE}" stroke-width="1.5"/>
    <text x="162" y="415" fill="{C_NAVY}" font-size="11" font-weight="bold" text-anchor="middle">[D | Q] REG S0</text>
    <polygon points="158,435 166,435 162,427" fill="{C_NAVY}"/>
    
    <!-- Stage 1: Dual Subtractors (x=270, w=165) -->
    <rect x="270" y="195" width="165" height="260" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1.5"/>
    <rect x="270" y="195" width="165" height="30" rx="6" fill="{C_CARD_ALT}"/>
    <text x="285" y="215" fill="{C_NAVY}" font-size="12" font-weight="bold">STAGE 1</text>
    <text x="285" y="245" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Dual ALUs [-]</text>
    <text x="285" y="272" fill="{C_TEXT_SUB}" font-size="11">D1 = T(t) - T24</text>
    <text x="285" y="295" fill="{C_TEXT_SUB}" font-size="11">D2 = T(t) - T3</text>
    <text x="285" y="320" fill="{C_AMBER}" font-size="11" font-weight="bold">Bus: 17b (Q9.8)</text>
    <rect x="280" y="390" width="145" height="50" rx="4" fill="{C_BLUE_LIGHT}" stroke="{C_BLUE}" stroke-width="1.5"/>
    <text x="352" y="415" fill="{C_NAVY}" font-size="11" font-weight="bold" text-anchor="middle">[D | Q] REG S1</text>
    <polygon points="348,435 356,435 352,427" fill="{C_NAVY}"/>
    
    <!-- Stage 2: Dual Multipliers (x=460, w=165) -->
    <rect x="460" y="195" width="165" height="260" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1.5"/>
    <rect x="460" y="195" width="165" height="30" rx="6" fill="{C_CARD_ALT}"/>
    <text x="475" y="215" fill="{C_NAVY}" font-size="12" font-weight="bold">STAGE 2</text>
    <text x="475" y="245" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Dual DSPs [×]</text>
    <text x="475" y="272" fill="{C_TEXT_SUB}" font-size="11">P1 = a · D1</text>
    <text x="475" y="295" fill="{C_TEXT_SUB}" font-size="11">P2 = b · D2</text>
    <text x="475" y="320" fill="{C_PURPLE}" font-size="11" font-weight="bold">Bus: 33b (Q11.22)</text>
    <rect x="470" y="390" width="145" height="50" rx="4" fill="{C_BLUE_LIGHT}" stroke="{C_BLUE}" stroke-width="1.5"/>
    <text x="542" y="415" fill="{C_NAVY}" font-size="11" font-weight="bold" text-anchor="middle">[D | Q] REG S2</text>
    <polygon points="538,435 546,435 542,427" fill="{C_NAVY}"/>
    
    <!-- Stage 3: Product Tree (x=650, w=165) -->
    <rect x="650" y="195" width="165" height="260" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1.5"/>
    <rect x="650" y="195" width="165" height="30" rx="6" fill="{C_CARD_ALT}"/>
    <text x="665" y="215" fill="{C_NAVY}" font-size="12" font-weight="bold">STAGE 3</text>
    <text x="665" y="245" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Adder Tree [+]</text>
    <text x="665" y="272" fill="{C_TEXT_SUB}" font-size="11">P = P1 + P2</text>
    <text x="665" y="295" fill="{C_TEXT_SUB}" font-size="11">Pass Base Reg</text>
    <text x="665" y="320" fill="{C_AMBER}" font-size="11" font-weight="bold">Bus: 34b (Q12.22)</text>
    <rect x="660" y="390" width="145" height="50" rx="4" fill="{C_BLUE_LIGHT}" stroke="{C_BLUE}" stroke-width="1.5"/>
    <text x="732" y="415" fill="{C_NAVY}" font-size="11" font-weight="bold" text-anchor="middle">[D | Q] REG S3</text>
    <polygon points="728,435 736,435 732,427" fill="{C_NAVY}"/>
    
    <!-- Stage 4: Accumulator (x=840, w=165) -->
    <rect x="840" y="195" width="165" height="260" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1.5"/>
    <rect x="840" y="195" width="165" height="30" rx="6" fill="{C_CARD_ALT}"/>
    <text x="855" y="215" fill="{C_NAVY}" font-size="12" font-weight="bold">STAGE 4</text>
    <text x="855" y="245" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Accumulator [+]</text>
    <text x="855" y="272" fill="{C_TEXT_SUB}" font-size="11">S = P + Base</text>
    <text x="855" y="295" fill="{C_TEXT_SUB}" font-size="11">Aligned to Radix 22</text>
    <text x="855" y="320" fill="{C_BLUE}" font-size="11" font-weight="bold">Bus: 35b (Q13.22)</text>
    <rect x="850" y="390" width="145" height="50" rx="4" fill="{C_BLUE_LIGHT}" stroke="{C_BLUE}" stroke-width="1.5"/>
    <text x="922" y="415" fill="{C_NAVY}" font-size="11" font-weight="bold" text-anchor="middle">[D | Q] REG S4</text>
    <polygon points="918,435 926,435 922,427" fill="{C_NAVY}"/>
    
    <!-- Stage 5: Shift & Sat16 (x=1030, w=165) -->
    <rect x="1030" y="195" width="165" height="260" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1.5"/>
    <rect x="1030" y="195" width="165" height="30" rx="6" fill="{C_CARD_ALT}"/>
    <text x="1045" y="215" fill="{C_NAVY}" font-size="12" font-weight="bold">STAGE 5</text>
    <text x="1045" y="245" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Shift &amp; Sat16</text>
    <text x="1045" y="272" fill="{C_TEXT_SUB}" font-size="11">S_sh = S &gt;&gt;&gt; 14</text>
    <text x="1045" y="295" fill="{C_TEXT_SUB}" font-size="11">sat16 [-128..+128°C]</text>
    <text x="1045" y="320" fill="{C_GREEN}" font-size="11" font-weight="bold">Bus: 16b (Q8.8)</text>
    <rect x="1040" y="390" width="145" height="50" rx="4" fill="{C_GREEN_BG}" stroke="{C_GREEN}" stroke-width="1.5"/>
    <text x="1112" y="415" fill="{C_GREEN}" font-size="11" font-weight="bold" text-anchor="middle">[D | Q] OUT REG</text>
    <polygon points="1108,435 1116,435 1112,427" fill="{C_GREEN}"/>
    
    <!-- Flow Connectors -->
    <line x1="245" y1="415" x2="280" y2="415" stroke="{C_BLUE}" stroke-width="2"/>
    <line x1="435" y1="415" x2="470" y2="415" stroke="{C_BLUE}" stroke-width="2"/>
    <line x1="625" y1="415" x2="660" y2="415" stroke="{C_BLUE}" stroke-width="2"/>
    <line x1="815" y1="415" x2="850" y2="415" stroke="{C_BLUE}" stroke-width="2"/>
    <line x1="1005" y1="415" x2="1040" y2="415" stroke="{C_BLUE}" stroke-width="2"/>
    
    <!-- Bottom Technical Summary -->
    <rect x="80" y="475" width="1115" height="140" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="100" y="502" fill="{C_NAVY}" font-size="12" font-weight="bold">Pipeline Timing &amp; Throughput Integrity:</text>
    <text x="100" y="528" fill="{C_TEXT_SUB}" font-size="11">• Throughput: II = 1 (1 sample/clock, 50 MSps @ 50 MHz, 0 bubbles)</text>
    <text x="100" y="551" fill="{C_TEXT_SUB}" font-size="11">• Timing: Stage 2 multiplier critical path (6.4 ns, 142.3 MHz F_max)</text>
    <text x="100" y="574" fill="{C_TEXT_SUB}" font-size="11">• Latency: L = 5 cycles (100 ns @ 50 MHz from accept edge)</text>
    <text x="100" y="598" fill="{C_GREEN}" font-size="11" font-weight="bold">• Saturation: Stage 5 clamps shifted accumulator to [-128°C, +128°C]</text>
  </g>
"""
    svg += standard_footer("ftr_13", "6-stage pipelining isolates arithmetic operations to achieve 142.3 MHz F_max and sustained II = 1 throughput.")
    svg += svg_footer()
    write_slide("13_speed_microarchitecture.svg", svg)

# ==============================================================================
# SLIDE 14: Speed Core: Cycle-Accurate Timing Waveforms & Handshake
# ==============================================================================
def gen_slide_14():
    svg = svg_header("content")
    svg += standard_header("hdr_14", "DIGITAL SIGNAL TIMING & HANDSHAKE", 
                           "Speed Core: Cycle-Accurate Timing Waveforms & Handshake", 
                           "Cycle-by-cycle register pipeline propagation and deterministic 5-cycle latency")
    
    # Hero Timing Waveform Container
    svg += f"""  <g id="timing_waveform_box" data-pptx-bounds="60 135 1160 500">
    <rect x="60" y="135" width="1160" height="500" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="60" y="135" width="1160" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="80" y="162" fill="{C_NAVY}" font-size="14" font-weight="bold">DIGITAL SIGNAL TIMING WAVEFORM (CYCLE T0 TO T7)</text>
    
    <!-- Waveform Canvas -->
    <rect x="80" y="195" width="1120" height="300" fill="{C_CARD_BG}" rx="6" stroke="{C_BORDER}" stroke-width="1"/>
    
    <!-- Cycle Vertical Guidelines (8 Cycles: T0 to T7, step=115) -->
    <text x="295" y="215" fill="{C_TEXT_MUTED}" font-size="11" font-weight="bold">Cycle T0 [IN]</text>
    <text x="410" y="215" fill="{C_TEXT_MUTED}" font-size="11" font-weight="bold">Cycle T1</text>
    <text x="525" y="215" fill="{C_TEXT_MUTED}" font-size="11" font-weight="bold">Cycle T2</text>
    <text x="640" y="215" fill="{C_TEXT_MUTED}" font-size="11" font-weight="bold">Cycle T3</text>
    <text x="755" y="215" fill="{C_TEXT_MUTED}" font-size="11" font-weight="bold">Cycle T4</text>
    <text x="870" y="215" fill="{C_GREEN}" font-size="11" font-weight="bold">Cycle T5 [OUT]</text>
    <text x="985" y="215" fill="{C_TEXT_MUTED}" font-size="11" font-weight="bold">Cycle T6</text>
    <text x="1100" y="215" fill="{C_TEXT_MUTED}" font-size="11" font-weight="bold">Cycle T7</text>
    
    <line x1="240" y1="220" x2="240" y2="480" stroke="{C_BORDER}" stroke-width="1" stroke-dasharray="2 2"/>
    <line x1="355" y1="220" x2="355" y2="480" stroke="{C_BORDER}" stroke-width="1" stroke-dasharray="2 2"/>
    <line x1="470" y1="220" x2="470" y2="480" stroke="{C_BORDER}" stroke-width="1" stroke-dasharray="2 2"/>
    <line x1="585" y1="220" x2="585" y2="480" stroke="{C_BORDER}" stroke-width="1" stroke-dasharray="2 2"/>
    <line x1="700" y1="220" x2="700" y2="480" stroke="{C_BORDER}" stroke-width="1" stroke-dasharray="2 2"/>
    <line x1="815" y1="220" x2="815" y2="480" stroke="{C_GREEN}" stroke-width="1.5" stroke-dasharray="2 2"/>
    <line x1="930" y1="220" x2="930" y2="480" stroke="{C_BORDER}" stroke-width="1" stroke-dasharray="2 2"/>
    <line x1="1045" y1="220" x2="1045" y2="480" stroke="{C_BORDER}" stroke-width="1" stroke-dasharray="2 2"/>
    
    <!-- Trace 1: clk (50 MHz) -->
    <text x="100" y="250" fill="{C_NAVY}" font-size="12" font-weight="bold">clk (50MHz)</text>
    <path d="M 240,255 L 297,255 L 297,235 L 355,235 L 355,255 L 412,255 L 412,235 L 470,235 L 470,255 L 527,255 L 527,235 L 585,235 L 585,255 L 642,255 L 642,235 L 700,235 L 700,255 L 757,255 L 757,235 L 815,235 L 815,255 L 872,255 L 872,235 L 930,235 L 930,255 L 987,255 L 987,235 L 1045,235 L 1045,255 L 1102,255 L 1102,235 L 1160,235" 
          fill="none" stroke="{C_NAVY}" stroke-width="1.5"/>
          
    <!-- Trace 2: sample_valid -->
    <text x="100" y="295" fill="{C_BLUE}" font-size="12" font-weight="bold">sample_valid</text>
    <path d="M 240,300 L 250,300 L 255,280 L 350,280 L 355,300 L 1160,300" fill="none" stroke="{C_BLUE}" stroke-width="2"/>
    
    <!-- Trace 3: temp_in[15:0] -->
    <text x="100" y="340" fill="{C_TEXT_MAIN}" font-size="12" font-weight="bold">temp_in[15:0]</text>
    <polygon points="255,335 345,335 355,345 345,355 255,355 245,345" fill="{C_BLUE_LIGHT}" stroke="{C_BLUE}" stroke-width="1"/>
    <text x="300" y="348" fill="{C_NAVY}" font-size="11" font-weight="bold" text-anchor="middle">T(t) [Q8.8]</text>
    <line x1="355" y1="345" x2="1160" y2="345" stroke="{C_TEXT_MUTED}" stroke-width="1"/>
    
    <!-- Trace 4: Pipeline Stages Active -->
    <text x="100" y="390" fill="{C_PURPLE}" font-size="12" font-weight="bold">Pipeline Flow</text>
    <!-- S0 at T0 -->
    <rect x="255" y="375" width="90" height="24" rx="3" fill="{C_CARD_WHITE}" stroke="{C_PURPLE}" stroke-width="1"/>
    <text x="300" y="391" fill="{C_PURPLE}" font-size="10" font-weight="bold" text-anchor="middle">S0: Cap</text>
    <!-- S1 at T1 -->
    <rect x="370" y="375" width="90" height="24" rx="3" fill="{C_CARD_WHITE}" stroke="{C_PURPLE}" stroke-width="1"/>
    <text x="415" y="391" fill="{C_PURPLE}" font-size="10" font-weight="bold" text-anchor="middle">S1: Diff</text>
    <!-- S2 at T2 -->
    <rect x="485" y="375" width="90" height="24" rx="3" fill="{C_CARD_WHITE}" stroke="{C_PURPLE}" stroke-width="1"/>
    <text x="530" y="391" fill="{C_PURPLE}" font-size="10" font-weight="bold" text-anchor="middle">S2: Mult</text>
    <!-- S3 at T3 -->
    <rect x="600" y="375" width="90" height="24" rx="3" fill="{C_CARD_WHITE}" stroke="{C_PURPLE}" stroke-width="1"/>
    <text x="645" y="391" fill="{C_PURPLE}" font-size="10" font-weight="bold" text-anchor="middle">S3: Sum</text>
    <!-- S4 at T4 -->
    <rect x="715" y="375" width="90" height="24" rx="3" fill="{C_CARD_WHITE}" stroke="{C_PURPLE}" stroke-width="1"/>
    <text x="760" y="391" fill="{C_PURPLE}" font-size="10" font-weight="bold" text-anchor="middle">S4: Acc</text>
    <!-- S5 at T5 -->
    <rect x="830" y="375" width="90" height="24" rx="3" fill="{C_CARD_WHITE}" stroke="{C_PURPLE}" stroke-width="1"/>
    <text x="875" y="391" fill="{C_PURPLE}" font-size="10" font-weight="bold" text-anchor="middle">S5: Sat</text>
    
    <!-- Trace 5: forecast_valid -->
    <text x="100" y="435" fill="{C_GREEN}" font-size="12" font-weight="bold">forecast_valid</text>
    <path d="M 240,440 L 825,440 L 830,420 L 920,420 L 925,440 L 1160,440" fill="none" stroke="{C_GREEN}" stroke-width="2.5"/>
    
    <!-- Trace 6: forecast_out[15:0] -->
    <text x="100" y="475" fill="{C_GREEN}" font-size="12" font-weight="bold">forecast_out[15:0]</text>
    <polygon points="830,465 915,465 925,475 915,485 830,485 820,475" fill="{C_GREEN_BG}" stroke="{C_GREEN}" stroke-width="1.5"/>
    <text x="872" y="478" fill="{C_GREEN}" font-size="11" font-weight="bold" text-anchor="middle">T_hat(t+3)</text>
    
    <!-- Bottom Timing Metrics Panel -->
    <rect x="80" y="510" width="1120" height="105" rx="6" fill="{C_CARD_ALT}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="100" y="535" fill="{C_NAVY}" font-size="12" font-weight="bold">Pipeline Latency &amp; Handshake Contract:</text>
    <text x="100" y="558" fill="{C_TEXT_SUB}" font-size="12">• Deterministic Latency: Exactly 5 clock cycles (100 ns at 50.0 MHz system clock).</text>
    <text x="100" y="580" fill="{C_TEXT_SUB}" font-size="12">• Streaming Throughput: II = 1 (1 sample/clock, 50 MSps) with zero backpressure bubbles.</text>
    <text x="100" y="602" fill="{C_GREEN}" font-size="12" font-weight="bold">• Formal Verification: SV assertion `assert (##5 forecast_valid)` verified bit-exact.</text>
  </g>
"""
    svg += standard_footer("ftr_14", "Cycle-accurate timing waveform proves deterministic 5-cycle latency with zero bubble or backpressure stalls.")
    svg += svg_footer()
    write_slide("14_resource_datapath.svg", svg)

# ==============================================================================
# SLIDE 15: Resource Core: 10-State Time-Multiplexed FSM & Shared Multiplier
# ==============================================================================
def gen_slide_15():
    svg = svg_header("content")
    svg += standard_header("hdr_15", "SEQUENTIAL FSM CONTROLLER", 
                           "Resource Core: 10-State FSM &amp; Multiplier Time-Multiplexing", 
                           "Time-multiplexing a single 17x16 multiplier across two operations to save 50% DSP silicon")
    
    # Left Panel: 10-State FSM Bubble Diagram (700 px wide)
    svg += f"""  <g id="fsm_bubble_diagram" data-pptx-bounds="60 135 700 500">
    <rect x="60" y="135" width="700" height="500" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="60" y="135" width="700" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="80" y="162" fill="{C_NAVY}" font-size="14" font-weight="bold">10-STATE TIME-MULTIPLEXED SEQUENTIAL FSM</text>
    
    <!-- State Bubbles: Row 1 (Top) -->
    <circle cx="110" cy="240" r="30" fill="{C_CARD_BG}" stroke="{C_NAVY}" stroke-width="2"/>
    <text x="110" y="244" fill="{C_NAVY}" font-size="10" font-weight="bold" text-anchor="middle">IDLE</text>
    
    <circle cx="235" cy="240" r="30" fill="{C_BLUE_LIGHT}" stroke="{C_BLUE}" stroke-width="2"/>
    <text x="235" y="244" fill="{C_NAVY}" font-size="10" font-weight="bold" text-anchor="middle">S0: CAP</text>
    
    <circle cx="360" cy="240" r="30" fill="{C_CARD_BG}" stroke="{C_NAVY}" stroke-width="2"/>
    <text x="360" y="244" fill="{C_NAVY}" font-size="10" font-weight="bold" text-anchor="middle">S1: SUB1</text>
    
    <circle cx="485" cy="240" r="30" fill="{C_AMBER_BG}" stroke="{C_AMBER}" stroke-width="2"/>
    <text x="485" y="244" fill="{C_AMBER}" font-size="10" font-weight="bold" text-anchor="middle">S2: MULT1</text>
    
    <circle cx="610" cy="240" r="30" fill="{C_CARD_BG}" stroke="{C_NAVY}" stroke-width="2"/>
    <text x="610" y="244" fill="{C_NAVY}" font-size="10" font-weight="bold" text-anchor="middle">S3: SUB2</text>
    
    <!-- Row 1 Transition Arrows -->
    <line x1="140" y1="240" x2="205" y2="240" stroke="{C_BLUE}" stroke-width="1.8"/>
    <line x1="265" y1="240" x2="330" y2="240" stroke="{C_BLUE}" stroke-width="1.8"/>
    <line x1="390" y1="240" x2="455" y2="240" stroke="{C_BLUE}" stroke-width="1.8"/>
    <line x1="515" y1="240" x2="580" y2="240" stroke="{C_BLUE}" stroke-width="1.8"/>
    
    <!-- Vertical transition down: S3 to S4 -->
    <line x1="610" y1="270" x2="610" y2="330" stroke="{C_BLUE}" stroke-width="1.8"/>
    
    <!-- State Bubbles: Row 2 (Bottom) -->
    <circle cx="610" cy="360" r="30" fill="{C_AMBER_BG}" stroke="{C_AMBER}" stroke-width="2"/>
    <text x="610" y="364" fill="{C_AMBER}" font-size="10" font-weight="bold" text-anchor="middle">S4: MULT2</text>
    
    <circle cx="485" cy="360" r="30" fill="{C_CARD_BG}" stroke="{C_NAVY}" stroke-width="2"/>
    <text x="485" y="364" fill="{C_NAVY}" font-size="10" font-weight="bold" text-anchor="middle">S5: SUM</text>
    
    <circle cx="360" cy="360" r="30" fill="{C_CARD_BG}" stroke="{C_NAVY}" stroke-width="2"/>
    <text x="360" y="364" fill="{C_NAVY}" font-size="10" font-weight="bold" text-anchor="middle">S6: ACC</text>
    
    <circle cx="235" cy="360" r="30" fill="{C_CARD_BG}" stroke="{C_NAVY}" stroke-width="2"/>
    <text x="235" y="364" fill="{C_NAVY}" font-size="10" font-weight="bold" text-anchor="middle">S7: SAT16</text>
    
    <circle cx="110" cy="360" r="30" fill="{C_GREEN_BG}" stroke="{C_GREEN}" stroke-width="2"/>
    <text x="110" y="364" fill="{C_GREEN}" font-size="10" font-weight="bold" text-anchor="middle">S8: DONE</text>
    
    <!-- Row 2 Transition Arrows -->
    <line x1="580" y1="360" x2="515" y2="360" stroke="{C_BLUE}" stroke-width="1.8"/>
    <line x1="455" y1="360" x2="390" y2="360" stroke="{C_BLUE}" stroke-width="1.8"/>
    <line x1="330" y1="360" x2="265" y2="360" stroke="{C_BLUE}" stroke-width="1.8"/>
    <line x1="205" y1="360" x2="140" y2="360" stroke="{C_BLUE}" stroke-width="1.8"/>
    
    <!-- Vertical transition back up to IDLE -->
    <line x1="110" y1="330" x2="110" y2="270" stroke="{C_GREEN}" stroke-width="1.8"/>
    <text x="80" y="302" fill="{C_GREEN}" font-size="9" font-weight="bold">valid_out</text>
    
    <!-- State Function Table -->
    <rect x="80" y="420" width="660" height="195" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="95" y="445" fill="{C_NAVY}" font-size="12" font-weight="bold">FSM Sequential Schedule:</text>
    <text x="95" y="470" fill="{C_TEXT_SUB}" font-size="11">• S0: Latch sample; push into 25-stage history buffer</text>
    <text x="95" y="495" fill="{C_TEXT_SUB}" font-size="11">• S1–S2: D1 = T(t)-T24; shared mult computes P1 = a·D1</text>
    <text x="95" y="520" fill="{C_TEXT_SUB}" font-size="11">• S3–S4: D2 = T(t)-T3; shared mult computes P2 = b·D2</text>
    <text x="95" y="545" fill="{C_TEXT_SUB}" font-size="11">• S5–S6: Reused ALU sums P1+P2, adds anchor T(t-21) and bias c</text>
    <text x="95" y="570" fill="{C_TEXT_SUB}" font-size="11">• S7–S8: Shift &gt;&gt;&gt; 14, clamp sat16, assert forecast_valid</text>
  </g>
"""

    # Right Panel: Multiplier Sharing Multiplexer Logic (440 px wide)
    svg += f"""  <g id="shared_mult_mux" data-pptx-bounds="780 135 440 500">
    <rect x="780" y="135" width="440" height="500" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="780" y="135" width="440" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="800" y="162" fill="{C_NAVY}" font-size="14" font-weight="bold">MULTIPLIER SHARING ARCHITECTURE</text>
    
    <text x="800" y="205" fill="{C_TEXT_MAIN}" font-size="13" font-weight="bold">Operand Multiplexer Routing:</text>
    
    <rect x="800" y="225" width="400" height="150" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1.5"/>
    <text x="815" y="250" fill="{C_NAVY}" font-size="12" font-weight="bold">2:1 Operand Mux Logic (ols_shared_datapath.v):</text>
    
    <rect x="815" y="268" width="370" height="42" rx="4" fill="{C_AMBER_BG}" stroke="{C_AMBER}" stroke-width="1"/>
    <text x="825" y="292" fill="{C_AMBER}" font-size="11" font-weight="bold">State S2:  mult_in_a = D1;  mult_in_b = COEF_A;</text>
    
    <rect x="815" y="320" width="370" height="42" rx="4" fill="{C_AMBER_BG}" stroke="{C_AMBER}" stroke-width="1"/>
    <text x="825" y="344" fill="{C_AMBER}" font-size="11" font-weight="bold">State S4:  mult_in_a = D2;  mult_in_b = COEF_B;</text>
    
    <!-- Shared DSP Multiplier Box -->
    <rect x="800" y="395" width="400" height="90" rx="6" fill="{C_BLUE_LIGHT}" stroke="{C_BLUE}" stroke-width="2"/>
    <text x="1000" y="425" fill="{C_NAVY}" font-size="13" font-weight="bold" text-anchor="middle">SINGLE 17×16 EMBEDDED DSP MULTIPLIER</text>
    <text x="1000" y="448" fill="{C_TEXT_SUB}" font-size="11" text-anchor="middle">Altera Cyclone II 9-bit Blocks: 2 units (vs 4 in Speed Core)</text>
    <text x="1000" y="470" fill="{C_GREEN}" font-size="12" font-weight="bold" text-anchor="middle">50% DSP Silicon Footprint Saved!</text>
    
    <!-- Silicon Profile -->
    <rect x="800" y="500" width="400" height="115" rx="6" fill="{C_CARD_ALT}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="815" y="525" fill="{C_NAVY}" font-size="12" font-weight="bold">Hardware Footprint Impact:</text>
    <text x="815" y="548" fill="{C_TEXT_SUB}" font-size="11">• Speed Core: 4 9-bit DSP blocks (2 dedicated multipliers)</text>
    <text x="815" y="570" fill="{C_TEXT_SUB}" font-size="11">• Resource Core: 2 9-bit DSP blocks (1 shared multiplier)</text>
    <text x="815" y="595" fill="{C_GREEN}" font-size="11" font-weight="bold">• Area Savings: -50% DSP blocks, -42.7% LEs (236 LEs total)</text>
  </g>
"""
    svg += standard_footer("ftr_15", "Time-multiplexing a single multiplier cuts Cyclone II DSP footprint by 50% with minimal control overhead.")
    svg += svg_footer()
    write_slide("15_resource_fsm.svg", svg)

# ==============================================================================
# SLIDE 16: Top-Level System Block Diagrams for Both Designs
# ==============================================================================
def gen_slide_16():
    svg = svg_header("content")
    svg += standard_header("hdr_16", "FPGA SYSTEM TOP-LEVEL INTEGRATION", 
                           "Dual Top-Module Architectures: Speed vs Resource Wrappers", 
                           "Complete Verilog top-level integration: Streaming Packet Parser vs Dual-FIFO Controller")
    
    # --------------------------------------------------------------------------
    # TOP CONTAINER: DESIGN A (Speed-Optimized Top System: de2_temp_predictor_top.v)
    # Bounds: x=60, y=135, w=1160, h=238
    # --------------------------------------------------------------------------
    svg += f"""  <g id="top_speed_wrapper" data-pptx-bounds="60 135 1160 238">
    <rect x="60" y="135" width="1160" height="238" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="60" y="135" width="1160" height="32" rx="8" fill="{C_CARD_ALT}"/>
    <text x="75" y="157" fill="{C_NAVY}" font-size="12" font-weight="bold">DESIGN A TOP MODULE: de2_temp_predictor_top.v (Streaming Packet Architecture)</text>
    
    <!-- Block 1: IO & Reset Sync (x=75, w=110) -->
    <rect x="75" y="175" width="110" height="110" rx="5" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1.2"/>
    <text x="85" y="195" fill="{C_NAVY}" font-size="10" font-weight="bold">CLOCK &amp; RESET</text>
    <text x="85" y="215" fill="{C_TEXT_SUB}" font-size="9">• CLOCK_50 (50MHz)</text>
    <text x="85" y="232" fill="{C_TEXT_SUB}" font-size="9">• KEY0_N (Button)</text>
    <rect x="82" y="244" width="96" height="32" rx="3" fill="{C_BLUE_LIGHT}" stroke="{C_BLUE}" stroke-width="1"/>
    <text x="130" y="258" fill="{C_NAVY}" font-size="9" font-weight="bold" text-anchor="middle">reset_sync.v</text>
    <text x="130" y="270" fill="{C_BLUE}" font-size="8" text-anchor="middle">rst_n (Sync)</text>
    
    <!-- Connector 1 -> 2 -->
    <line x1="185" y1="230" x2="200" y2="230" stroke="{C_BLUE}" stroke-width="1.5"/>
    
    <!-- Block 2: UART RX (x=200, w=115) -->
    <rect x="200" y="175" width="115" height="110" rx="5" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1.2"/>
    <text x="210" y="195" fill="{C_NAVY}" font-size="10" font-weight="bold">UART RECEIVER</text>
    <text x="210" y="215" fill="{C_TEXT_MAIN}" font-size="10" font-weight="bold">uart_rx.v</text>
    <text x="210" y="232" fill="{C_TEXT_SUB}" font-size="9">• 115,200 Baud 8-N-1</text>
    <text x="210" y="248" fill="{C_TEXT_SUB}" font-size="9">• 16× Oversampling</text>
    <text x="210" y="272" fill="{C_BLUE}" font-size="9" font-weight="bold">rx_data [7:0]</text>
    
    <!-- Connector 2 -> 3 -->
    <line x1="315" y1="230" x2="330" y2="230" stroke="{C_BLUE}" stroke-width="1.5"/>
    
    <!-- Block 3: Packet Parser (x=330, w=145) -->
    <rect x="330" y="175" width="145" height="110" rx="5" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1.2"/>
    <text x="340" y="195" fill="{C_NAVY}" font-size="10" font-weight="bold">FRAME PARSER</text>
    <text x="340" y="215" fill="{C_TEXT_MAIN}" font-size="10" font-weight="bold">packet_parser.v</text>
    <text x="340" y="232" fill="{C_TEXT_SUB}" font-size="9">• Sync: AA 55 01 02</text>
    <text x="340" y="248" fill="{C_TEXT_SUB}" font-size="9">• Checksum validator</text>
    <text x="340" y="272" fill="{C_BLUE}" font-size="9" font-weight="bold">parsed_temp [15:0]</text>
    
    <!-- Connector 3 -> 4 -->
    <line x1="475" y1="230" x2="490" y2="230" stroke="{C_BLUE}" stroke-width="2"/>
    
    <!-- Block 4: Speed Core (Hero Core) (x=490, w=225) -->
    <rect x="490" y="170" width="225" height="120" rx="6" fill="{C_BLUE_LIGHT}" stroke="{C_NAVY}" stroke-width="2"/>
    <text x="502" y="192" fill="{C_NAVY}" font-size="11" font-weight="bold">PREDICTOR PIPELINE CORE</text>
    <text x="502" y="210" fill="{C_NAVY}" font-size="12" font-weight="bold">temp_predictor_speed.v</text>
    <text x="502" y="228" fill="{C_TEXT_MAIN}" font-size="9">• 25-Sample History Shift Register</text>
    <text x="502" y="243" fill="{C_TEXT_MAIN}" font-size="9">• 6 Pipeline Stages (S0 to S5)</text>
    <text x="502" y="258" fill="{C_TEXT_MAIN}" font-size="9">• 2 Dedicated 17×16 DSP Multipliers</text>
    <rect x="500" y="266" width="205" height="18" rx="3" fill="{C_CARD_WHITE}" stroke="{C_BLUE}" stroke-width="0.8"/>
    <text x="602" y="279" fill="{C_BLUE}" font-size="9" font-weight="bold" text-anchor="middle">II = 1 | L = 5 Cycles (100 ns) | 142 MHz</text>
    
    <!-- Connector 4 -> 5 -->
    <line x1="715" y1="230" x2="730" y2="230" stroke="{C_BLUE}" stroke-width="2"/>
    
    <!-- Block 5: Packet Formatter (x=730, w=145) -->
    <rect x="730" y="175" width="145" height="110" rx="5" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1.2"/>
    <text x="740" y="195" fill="{C_NAVY}" font-size="10" font-weight="bold">FRAME FORMATTER</text>
    <text x="740" y="215" fill="{C_TEXT_MAIN}" font-size="10" font-weight="bold">packet_formatter.v</text>
    <text x="740" y="232" fill="{C_TEXT_SUB}" font-size="9">• Header: AA 55 81 02</text>
    <text x="740" y="248" fill="{C_TEXT_SUB}" font-size="9">• Checksum generator</text>
    <text x="740" y="272" fill="{C_GREEN}" font-size="9" font-weight="bold">tx_data [7:0]</text>
    
    <!-- Connector 5 -> 6 -->
    <line x1="875" y1="230" x2="890" y2="230" stroke="{C_BLUE}" stroke-width="1.5"/>
    
    <!-- Block 6: UART TX (x=890, w=115) -->
    <rect x="890" y="175" width="115" height="110" rx="5" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1.2"/>
    <text x="900" y="195" fill="{C_NAVY}" font-size="10" font-weight="bold">UART TRANSMITTER</text>
    <text x="900" y="215" fill="{C_TEXT_MAIN}" font-size="10" font-weight="bold">uart_tx.v</text>
    <text x="900" y="232" fill="{C_TEXT_SUB}" font-size="9">• 115,200 Baud 8-N-1</text>
    <text x="900" y="248" fill="{C_TEXT_SUB}" font-size="9">• Serializer / stop bit</text>
    <text x="900" y="272" fill="{C_GREEN}" font-size="9" font-weight="bold">UART_TXD Pin</text>
    
    <!-- Connector 4 -> 7 (Peripherals) -->
    <path d="M 602,290 L 602,305 L 1020,305 L 1020,230 L 1030,230" fill="none" stroke="{C_PURPLE}" stroke-width="1.2" stroke-dasharray="2 2"/>
    
    <!-- Block 7: Board Peripherals (x=1030, w=175) -->
    <rect x="1030" y="175" width="175" height="110" rx="5" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1.2"/>
    <text x="1040" y="195" fill="{C_NAVY}" font-size="10" font-weight="bold">DE2 BOARD PERIPHERALS</text>
    <text x="1040" y="215" fill="{C_PURPLE}" font-size="9" font-weight="bold">• Double-Dabble Bin-to-BCD</text>
    <text x="1040" y="232" fill="{C_TEXT_SUB}" font-size="9">• HEX3..HEX0 7-Seg LED</text>
    <text x="1040" y="248" fill="{C_TEXT_SUB}" font-size="9">• LEDR status &amp; error flags</text>
    <rect x="1038" y="258" width="158" height="20" rx="3" fill="{C_GREEN_BG}" stroke="{C_GREEN}" stroke-width="0.8"/>
    <text x="1117" y="272" fill="{C_GREEN}" font-size="9" font-weight="bold" text-anchor="middle">Live: " 28.7°C" on Board</text>
    
    <!-- Bottom Spec Strip for Design A -->
    <rect x="75" y="325" width="1130" height="35" rx="4" fill="{C_CARD_ALT}" stroke="{C_BORDER}" stroke-width="0.8"/>
    <text x="90" y="346" fill="{C_NAVY}" font-size="10" font-weight="bold">Speed System Contract:</text>
    <text x="230" y="346" fill="{C_TEXT_SUB}" font-size="10">Streaming parser framing (AA 55) • Zero backpressure bubbles • 50 MSps throughput @ 50 MHz • 412 LEs</text>
  </g>
"""

    # --------------------------------------------------------------------------
    # BOTTOM CONTAINER: DESIGN B (Resource-Optimized Top System: top_temp_predictor_uart.v)
    # Bounds: x=60, y=388, w=1160, h=248
    # --------------------------------------------------------------------------
    svg += f"""  <g id="top_resource_wrapper" data-pptx-bounds="60 388 1160 248">
    <rect x="60" y="388" width="1160" height="248" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="60" y="388" width="1160" height="32" rx="8" fill="{C_CARD_ALT}"/>
    <text x="75" y="410" fill="{C_NAVY}" font-size="12" font-weight="bold">DESIGN B TOP MODULE: top_temp_predictor_uart.v (Dual-FIFO Buffered Architecture)</text>
    
    <!-- Block 1: IO & POR (x=75, w=110) -->
    <rect x="75" y="430" width="110" height="110" rx="5" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1.2"/>
    <text x="85" y="450" fill="{C_NAVY}" font-size="10" font-weight="bold">CLOCK &amp; POR</text>
    <text x="85" y="470" fill="{C_TEXT_SUB}" font-size="9">• CLOCK_50 (50MHz)</text>
    <text x="85" y="487" fill="{C_TEXT_SUB}" font-size="9">• UART_RX Pin</text>
    <rect x="82" y="499" width="96" height="32" rx="3" fill="{C_CARD_ALT}" stroke="{C_BORDER_DARK}" stroke-width="1"/>
    <text x="130" y="513" fill="{C_NAVY}" font-size="9" font-weight="bold" text-anchor="middle">por_cnt (128 clk)</text>
    <text x="130" y="525" fill="{C_TEXT_MUTED}" font-size="8" text-anchor="middle">2-FF rx_sync</text>
    
    <!-- Connector 1 -> 2 -->
    <line x1="185" y1="485" x2="200" y2="485" stroke="{C_BLUE}" stroke-width="1.5"/>
    
    <!-- Block 2: UART RX (x=200, w=110) -->
    <rect x="200" y="430" width="110" height="110" rx="5" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1.2"/>
    <text x="210" y="450" fill="{C_NAVY}" font-size="10" font-weight="bold">UART RECEIVER</text>
    <text x="210" y="470" fill="{C_TEXT_MAIN}" font-size="10" font-weight="bold">uart_rx.v</text>
    <text x="210" y="487" fill="{C_TEXT_SUB}" font-size="9">• 115,200 Baud 8-N-1</text>
    <text x="210" y="503" fill="{C_TEXT_SUB}" font-size="9">• 16× Oversampling</text>
    <text x="210" y="527" fill="{C_BLUE}" font-size="9" font-weight="bold">rx_data [7:0]</text>
    
    <!-- Connector 2 -> 3 -->
    <line x1="310" y1="485" x2="325" y2="485" stroke="{C_BLUE}" stroke-width="1.5"/>
    
    <!-- Block 3: RX FIFO (x=325, w=120) -->
    <rect x="325" y="430" width="120" height="110" rx="5" fill="{C_AMBER_BG}" stroke="{C_AMBER}" stroke-width="1.2"/>
    <text x="335" y="450" fill="{C_AMBER}" font-size="10" font-weight="bold">RX FIFO (16×8)</text>
    <text x="335" y="470" fill="{C_TEXT_MAIN}" font-size="10" font-weight="bold">simple_fifo.v</text>
    <text x="335" y="487" fill="{C_TEXT_SUB}" font-size="9">• 16-Byte Circular RAM</text>
    <text x="335" y="503" fill="{C_TEXT_SUB}" font-size="9">• Decouples host jitter</text>
    <text x="335" y="527" fill="{C_AMBER}" font-size="9" font-weight="bold">dout, empty, full</text>
    
    <!-- Connector 3 -> 4 -->
    <line x1="445" y1="485" x2="460" y2="485" stroke="{C_BLUE}" stroke-width="1.5"/>
    
    <!-- Block 4: UART Controller FSM (x=460, w=160) -->
    <rect x="460" y="430" width="160" height="110" rx="5" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1.2"/>
    <text x="470" y="450" fill="{C_NAVY}" font-size="10" font-weight="bold">UART CONTROLLER</text>
    <text x="470" y="470" fill="{C_TEXT_MAIN}" font-size="10" font-weight="bold">temp_uart_controller.v</text>
    <text x="470" y="487" fill="{C_TEXT_SUB}" font-size="9">• 2-Byte Delimiter Parser</text>
    <text x="470" y="503" fill="{C_TEXT_SUB}" font-size="9">• Handshake Arbiter</text>
    <text x="470" y="527" fill="{C_BLUE}" font-size="9" font-weight="bold">sample_valid / ready</text>
    
    <!-- Connector 4 <-> 5 -->
    <line x1="620" y1="480" x2="635" y2="480" stroke="{C_GREEN}" stroke-width="1.8"/>
    <line x1="635" y1="490" x2="620" y2="490" stroke="{C_BLUE}" stroke-width="1.8"/>
    
    <!-- Block 5: Resource Core (Hero Core) (x=635, w=235) -->
    <rect x="635" y="425" width="235" height="120" rx="6" fill="{C_GREEN_BG}" stroke="{C_GREEN}" stroke-width="2"/>
    <text x="647" y="447" fill="{C_GREEN}" font-size="11" font-weight="bold">TIME-MULTIPLEXED CORE</text>
    <text x="647" y="465" fill="{C_NAVY}" font-size="12" font-weight="bold">temp_predictor_resource.v</text>
    <text x="647" y="483" fill="{C_TEXT_MAIN}" font-size="9">• temp_history_buffer.v (25 taps)</text>
    <text x="647" y="498" fill="{C_TEXT_MAIN}" font-size="9">• ols_shared_datapath.v (1 Shared DSP)</text>
    <text x="647" y="513" fill="{C_TEXT_MAIN}" font-size="9">• 10-State Sequential FSM Controller</text>
    <rect x="645" y="521" width="215" height="18" rx="3" fill="{C_CARD_WHITE}" stroke="{C_GREEN}" stroke-width="0.8"/>
    <text x="752" y="534" fill="{C_GREEN}" font-size="9" font-weight="bold" text-anchor="middle">II = 10 | L = 9 Cycles (180 ns) | -42.7% LEs</text>
    
    <!-- Connector 4 -> 6 (TX path via controller) -->
    <path d="M 540,430 L 540,418 L 885,418 L 885,485 L 895,485" fill="none" stroke="{C_BLUE}" stroke-width="1.5"/>
    
    <!-- Block 6: TX FIFO (x=895, w=120) -->
    <rect x="895" y="430" width="120" height="110" rx="5" fill="{C_AMBER_BG}" stroke="{C_AMBER}" stroke-width="1.2"/>
    <text x="905" y="450" fill="{C_AMBER}" font-size="10" font-weight="bold">TX FIFO (16×8)</text>
    <text x="905" y="470" fill="{C_TEXT_MAIN}" font-size="10" font-weight="bold">simple_fifo.v</text>
    <text x="905" y="487" fill="{C_TEXT_SUB}" font-size="9">• 16-Byte Circular RAM</text>
    <text x="905" y="503" fill="{C_TEXT_SUB}" font-size="9">• Queues Output Bytes</text>
    <text x="905" y="527" fill="{C_AMBER}" font-size="9" font-weight="bold">din, wr_en, count</text>
    
    <!-- Connector 6 -> 7 -->
    <line x1="1015" y1="485" x2="1030" y2="485" stroke="{C_BLUE}" stroke-width="1.5"/>
    
    <!-- Block 7: UART TX (x=1030, w=175) -->
    <rect x="1030" y="430" width="175" height="110" rx="5" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1.2"/>
    <text x="1040" y="450" fill="{C_NAVY}" font-size="10" font-weight="bold">UART TRANSMITTER</text>
    <text x="1040" y="470" fill="{C_TEXT_MAIN}" font-size="10" font-weight="bold">uart_tx.v</text>
    <text x="1040" y="487" fill="{C_TEXT_SUB}" font-size="9">• 115,200 Baud 8-N-1 Serializer</text>
    <text x="1040" y="503" fill="{C_TEXT_SUB}" font-size="9">• Automatic FIFO pop on idle</text>
    <rect x="1038" y="513" width="158" height="20" rx="3" fill="{C_GREEN_BG}" stroke="{C_GREEN}" stroke-width="0.8"/>
    <text x="1117" y="527" fill="{C_GREEN}" font-size="9" font-weight="bold" text-anchor="middle">Pin: UART_TX Output</text>
    
    <!-- Bottom Spec Strip for Design B -->
    <rect x="75" y="585" width="1130" height="42" rx="4" fill="{C_CARD_ALT}" stroke="{C_BORDER}" stroke-width="0.8"/>
    <text x="90" y="605" fill="{C_NAVY}" font-size="10" font-weight="bold">Resource System Contract:</text>
    <text x="245" y="605" fill="{C_TEXT_SUB}" font-size="10">Dual 16-byte FIFO buffering • Autonomous UART controller FSM • 1 shared multiplier (-50% DSP) • 236 LEs (-42.7%)</text>
    <text x="90" y="620" fill="{C_GREEN}" font-size="9" font-weight="bold">• Power-On-Reset counter (128 cycles) eliminates external reset pushbutton dependency.</text>
  </g>
"""
    svg += standard_footer("ftr_16", "Dual top modules reflect distinct trade-offs: streaming packet-framed pipeline vs FIFO-decoupled FSM controller.")
    svg += svg_footer()
    write_slide("16_top_level_peripherals.svg", svg)

# ==============================================================================
# SLIDE 17: Bit-Exact Verification: SystemVerilog & DPI-C Co-Simulation
# ==============================================================================
def gen_slide_17():
    svg = svg_header("content")
    svg += standard_header("hdr_17", "DESIGN VERIFICATION INFRASTRUCTURE", 
                           "Closed-Loop SystemVerilog &amp; DPI-C Co-Simulation", 
                           "Direct Programming Interface (DPI-C) lockstep testbench proving 100% bit-exact equivalence")
    
    # Hero Full-Width Co-Simulation Architecture
    svg += f"""  <g id="dpic_arch_box" data-pptx-bounds="60 135 1160 500">
    <rect x="60" y="135" width="1160" height="500" rx="8" fill="{C_CARD_WHITE}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="60" y="135" width="1160" height="42" rx="8" fill="{C_CARD_ALT}"/>
    <text x="80" y="162" fill="{C_NAVY}" font-size="14" font-weight="bold">LOCKSTEP CO-SIMULATION TESTBENCH (tb_temp_predictor_speed.sv)</text>
    
    <!-- Test Vector Source (Left, w=200) -->
    <rect x="80" y="240" width="200" height="150" rx="6" fill="{C_CARD_BG}" stroke="{C_BORDER}" stroke-width="1.5"/>
    <text x="180" y="270" fill="{C_NAVY}" font-size="12" font-weight="bold" text-anchor="middle">STIMULUS GENERATOR</text>
    <text x="180" y="295" fill="{C_TEXT_SUB}" font-size="11" text-anchor="middle">Python / NumPy Engine</text>
    <text x="180" y="320" fill="{C_TEXT_MUTED}" font-size="10" text-anchor="middle">• test_vectors_float.csv</text>
    <text x="180" y="338" fill="{C_TEXT_MUTED}" font-size="10" text-anchor="middle">• test_vectors_q88.csv</text>
    <text x="180" y="365" fill="{C_BLUE}" font-size="11" font-weight="bold" text-anchor="middle">10,000+ Vectors</text>
    
    <!-- SV Driver (w=220) -->
    <rect x="330" y="220" width="220" height="190" rx="6" fill="{C_BLUE_LIGHT}" stroke="{C_BLUE}" stroke-width="1.5"/>
    <text x="440" y="250" fill="{C_NAVY}" font-size="12" font-weight="bold" text-anchor="middle">SV TESTBENCH DRIVER</text>
    <text x="440" y="272" fill="{C_TEXT_MAIN}" font-size="11" text-anchor="middle">tb_temp_predictor_speed.sv</text>
    <text x="440" y="300" fill="{C_TEXT_SUB}" font-size="10" text-anchor="middle">• Clock generator (50 MHz)</text>
    <text x="440" y="320" fill="{C_TEXT_SUB}" font-size="10" text-anchor="middle">• Active-low reset sequencing</text>
    <text x="440" y="340" fill="{C_TEXT_SUB}" font-size="10" text-anchor="middle">• Streaming sample dispatcher</text>
    <text x="440" y="375" fill="{C_NAVY}" font-size="11" font-weight="bold" text-anchor="middle">Dual Transaction Dispatch</text>
    
    <!-- Path A: Verilog DUT (Top Center) -->
    <rect x="610" y="200" width="250" height="100" rx="6" fill="{C_CARD_WHITE}" stroke="{C_NAVY}" stroke-width="2"/>
    <text x="735" y="230" fill="{C_NAVY}" font-size="12" font-weight="bold" text-anchor="middle">DUT: VERILOG RTL CORE</text>
    <text x="735" y="252" fill="{C_TEXT_SUB}" font-size="11" text-anchor="middle">Synthesizable Verilog-2001</text>
    <text x="735" y="278" fill="{C_TEXT_MAIN}" font-size="11" font-weight="bold" text-anchor="middle">dut_out = temp_predictor()</text>
    
    <!-- Path B: DPI-C Golden Oracle (Bottom Center) -->
    <rect x="610" y="330" width="250" height="100" rx="6" fill="{C_CARD_WHITE}" stroke="{C_PURPLE}" stroke-width="2"/>
    <text x="735" y="360" fill="{C_PURPLE}" font-size="12" font-weight="bold" text-anchor="middle">ORACLE: DPI-C C++ REFERENCE</text>
    <text x="735" y="382" fill="{C_TEXT_SUB}" font-size="11" text-anchor="middle">import "DPI-C" ols::Reference</text>
    <text x="735" y="408" fill="{C_TEXT_MAIN}" font-size="11" font-weight="bold" text-anchor="middle">gold_out = model.push(t)</text>
    
    <!-- Scoreboard Comparator (Right) -->
    <rect x="920" y="220" width="240" height="190" rx="6" fill="{C_GREEN_BG}" stroke="{C_GREEN}" stroke-width="2"/>
    <text x="1040" y="250" fill="{C_GREEN}" font-size="13" font-weight="bold" text-anchor="middle">LOCKSTEP SCOREBOARD</text>
    <text x="1040" y="275" fill="{C_TEXT_MAIN}" font-size="11" text-anchor="middle">Cycle-by-Cycle Assertions</text>
    <text x="1040" y="302" fill="{C_TEXT_SUB}" font-size="10" text-anchor="middle">assert(dut_out === gold_out)</text>
    <text x="1040" y="320" fill="{C_TEXT_SUB}" font-size="10" text-anchor="middle">else $fatal("Mismatch!");</text>
    <rect x="940" y="345" width="200" height="48" rx="4" fill="{C_CARD_WHITE}" stroke="{C_GREEN}" stroke-width="1"/>
    <text x="1040" y="367" fill="{C_GREEN}" font-size="11" font-weight="bold" text-anchor="middle">10,000+ VECTORS PASSED</text>
    <text x="1040" y="385" fill="{C_GREEN}" font-size="11" font-weight="bold" text-anchor="middle">0 MISMATCHES (100.0%)</text>
    
    <!-- Connectors -->
    <line x1="280" y1="315" x2="330" y2="315" stroke="{C_BLUE}" stroke-width="2"/>
    <line x1="550" y1="280" x2="610" y2="250" stroke="{C_BLUE}" stroke-width="2"/>
    <line x1="550" y1="350" x2="610" y2="380" stroke="{C_BLUE}" stroke-width="2"/>
    <line x1="860" y1="250" x2="920" y2="280" stroke="{C_NAVY}" stroke-width="2"/>
    <line x1="860" y1="380" x2="920" y2="350" stroke="{C_PURPLE}" stroke-width="2"/>
    
    <!-- Bottom DV Highlights -->
    <rect x="80" y="475" width="1080" height="140" rx="6" fill="{C_CARD_ALT}" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="100" y="502" fill="{C_NAVY}" font-size="12" font-weight="bold">Design Verification Highlights:</text>
    <text x="100" y="528" fill="{C_TEXT_SUB}" font-size="11">• DPI-C Architecture: Links native C++ reference functions directly into SystemVerilog.</text>
    <text x="100" y="551" fill="{C_TEXT_SUB}" font-size="11">• Bit-Exact Oracle: Mirrors RTL floor shift and sat16 clamping stage-by-stage.</text>
    <text x="100" y="574" fill="{C_TEXT_SUB}" font-size="11">• Automated Suite: Full regression in Verilator / ModelSim via Makefile.</text>
    <text x="100" y="598" fill="{C_GREEN}" font-size="11" font-weight="bold">• Verification Coverage: 100% bit-exact across 10,000+ synthetic and replay vectors.</text>
  </g>
"""
    svg += standard_footer("ftr_17", "Closed-loop DPI-C testbench proves 100% bit-exact equivalence between Verilog RTL and C++ reference.")
    svg += svg_footer()
    write_slide("17_verification_architecture.svg", svg)
