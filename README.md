# FPGA-Based 3-Hour Temperature Predictor

Edge DSP coprocessor for short-term hourly temperature forecasting deployed on an Altera Cyclone II FPGA (DE2 Board) with bit-exact verification and real-time UART streaming.

---

## 1. Project Overview

This project implements a 3-hour-ahead discrete-time temperature predictor on FPGA using a diurnal residual linear regression architecture:

$$
\widehat{T}(t+3) = T(t-21) + a\big(T(t) - T(t-24)\big) + b\big(T(t) - T(t-3)\big) + c
$$

### Mathematical Definitions:
* $T(t-21)$: Diurnal anchor (temperature at the same hour on the previous day, since $(t+3) - 24 = t-21$).
* $T(t) - T(t-24)$: Inter-day trend difference across 24 hours.
* $T(t) - T(t-3)$: Short-term rate-of-change over the last 3 hours.
* $a, b, c$: Learned coefficients ($a \approx 0.7455, b \approx 0.0091, c \approx 0.0011$).

---

## 2. Directory Structure

```text
fpga-temp-predictor/
├── data/                               # Dataset pipeline & test vectors
│   ├── raw/                            # 5-year raw NASA POWER JSON files (2021-2025)
│   ├── processed/                      # Cleaned continuous hourly time-series (temperature.csv)
│   └── testvectors/                    # 8,760+ test vectors for bit-exact DV (test_vectors_float.csv)
│
├── software/                           # Student 1: Algorithm & DSP Modeling
│   ├── data_pipeline/                  # data_fetch.py (queries NASA POWER API)
│   ├── training/                       # train_ols_basic.py (OLS 3-param), train_ridge6.py
│   ├── models_cpp/                     # c_model_basic.cpp, c_model_ridge6.cpp, model.json, model_ridge6.json
│   ├── benchmarks/                     # ML comparative studies (MLP, RBF, Boosted Trees) + metrics
│   └── Makefile                        # Compiles C++ golden models
│
├── hardware/                           # Student 2: RTL Design & Student 3: Design Verification
│   ├── speed_optimized/                # Fully pipelined, II=1 RTL architecture & standalone testbenches
│   ├── resource_optimized/             # Time-multiplexed, 1-MAC FSM RTL architecture & standalone testbenches
│   ├── tb/                             # Unified SystemVerilog DPI-C verification testbenches & driver
│   └── constrs/                        # Pin constraints (DE2 Cyclone II .qsf pin assignments)
│
├── docs/                               # Project documentation & presentations
│   ├── presentation/                   # 15-slide deck (bao_cao_de_xuat_buoi_1_15_slides_EN.pptx) & speaker notes
│   ├── papers/                         # Academic reference papers (Ridge, MLP, RBF, Comparative Study)
│   ├── specs/                          # Architectural specifications (speed/resource optimized, comparison spreadsheet)
│   └── figures/                        # Forecast plots & architecture diagrams
│
├── .gitignore                          # Clean Git exclusion rules
└── README.md                           # Master project guide
```

---

## 3. Team Responsibilities & Workflow

| Role / Track | Lead | Key Deliverables & Directory Scope |
| :--- | :--- | :--- |
| **Track 1: DSP Algorithm & Data** | Student 1 | `data/`, `software/training/`, `software/models_cpp/`<br>• NASA POWER data preprocessing and train/validation/test splitting.<br>• OLS/Ridge model training and fixed-point quantization analysis ($Q8.8$).<br>• Host-PC Python serial communication tool. |
| **Track 2: Digital RTL Design** | Student 2 | `hardware/speed_optimized/`, `hardware/resource_optimized/`, `hardware/constrs/`<br>• Synthesizable Verilog datapath, shift register / circular buffer for 25 taps.<br>• Shared-MAC FSM, multiplier integration, and saturation arithmetic unit.<br>• Quartus II synthesis and timing closure ($F_{\max}$) on Altera DE2. |
| **Track 3: Design Verification (DV)** | Student 3 | `hardware/tb/`, `data/testvectors/`<br>• Bit-exact C++ reference model alignment.<br>• Self-checking SystemVerilog testbenches consuming `test_vectors_float.csv`.<br>• SystemVerilog Assertions (SVA) for FSM handshakes and saturation bounds.<br>• UART hardware-in-the-loop scoreboard. |

---

## 4. Quick Start & Build Instructions

### C++ Golden Models
Compile and run the C++ reference models:
```bash
cd software
make
./bin/c_model_basic
./bin/c_model_ridge6
```

### Python Training & Data Pipeline
Run the OLS 3-parameter model training:
```bash
python3 software/training/train_ols_basic.py
```

### Hardware Simulation (Icarus Verilog)
```bash
# Resource-optimized standalone testbench:
iverilog -g2012 -o sim_resource.vvp hardware/resource_optimized/temp_predictor_resource.v hardware/resource_optimized/ols_shared_datapath.v hardware/resource_optimized/temp_history_buffer.v hardware/resource_optimized/tb_temp_predictor_resource.v
vvp sim_resource.vvp

# Speed-optimized standalone testbench:
iverilog -g2012 -o sim_speed.vvp hardware/speed_optimized/temp_predictor_speed.v hardware/speed_optimized/tb_temp_predictor_speed.v
vvp sim_speed.vvp
```
