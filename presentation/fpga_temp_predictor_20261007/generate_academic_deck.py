#!/usr/bin/env python3
"""
Master Academic Presentation Generator for CE436 Capstone Defense
Project: FPGA-Based Edge Temperature Predictor
Course: CE436 - Discrete-Time Signal Processing & Applications
Theme: Clean Academic White / IEEE Silicon (Pure White, Deep Navy, Crisp Slate, Green, Warm Amber)
Style: "A word to the wise is enough" — Concise, High-Density, Data-Driven, Strictly Valid DrawingML.
"""

from pathlib import Path
import sys

# Import slide modules
import deck_slides_1_to_5 as s1_5
import deck_slides_6_to_11 as s6_11
import deck_slides_12_to_17 as s12_17
import deck_slides_18_to_22 as s18_22

def main():
    print("================================================================================")
    print("CE436 Capstone Defense: Generating 22 Academic Slides (Streamlined Edition)")
    print("Theme: Clean Academic White (Pure White, Navy #1E3A8A, Slate, Green, Amber)")
    print("Style: 'A word to the wise is enough' (Verbum sat sapienti)")
    print("================================================================================")

    slide_dispatch = {
        1: s1_5.gen_slide_01,
        2: s1_5.gen_slide_02,
        3: s1_5.gen_slide_03,
        4: s1_5.gen_slide_04,
        5: s1_5.gen_slide_05,
        6: s6_11.gen_slide_06,
        7: s6_11.gen_slide_07,
        8: s6_11.gen_slide_08,
        9: s6_11.gen_slide_09,
        10: s6_11.gen_slide_10,
        11: s6_11.gen_slide_11,
        12: s12_17.gen_slide_12,
        13: s12_17.gen_slide_13,
        14: s12_17.gen_slide_14,
        15: s12_17.gen_slide_15,
        16: s12_17.gen_slide_16,
        17: s12_17.gen_slide_17,
        18: s18_22.gen_slide_18,
        19: s18_22.gen_slide_19,
        20: s18_22.gen_slide_20,
        21: s18_22.gen_slide_21,
        22: s18_22.gen_slide_22,
    }

    for idx in range(1, 23):
        generator = slide_dispatch[idx]
        print(f"  [+] Generating Slide {idx:02d} ({generator.__name__})...")
        generator()

    print("\n[SUCCESS] Successfully generated all 22 Academic SVGs in svg_output/")

if __name__ == "__main__":
    main()
