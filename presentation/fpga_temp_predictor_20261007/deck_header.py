#!/usr/bin/env python3
"""
Academic Presentation Generator for CE436 Capstone Defense
Project: FPGA-Based Edge Temperature Predictor
Course: CE436 - Discrete-Time Signal Processing & Applications
Theme: Clean Academic White / IEEE Silicon (Pure White, Deep Navy, Engineering Blue, Crisp Gray, Zero Neon)
All slides updated for high information density, factual accuracy, and concise phrasing.
"""

from pathlib import Path
import re

PROJECT_DIR = Path("/home/khoale/Documents/University/Semester_5/CE436_Discrete-Time_Signal_Processing/fpga-temp-predictor/presentation/fpga_temp_predictor_20261007")
OUTPUT_DIR = PROJECT_DIR / "svg_output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# PALETTE: Clean Academic & IEEE Silicon (Strictly Non-Neon, Pure Academic)
C_BG          = "#FFFFFF"  # Pure White Canvas
C_BG_PAGE     = C_BG       # Alias for page background
C_CARD_BG     = "#F8FAFC"  # Light Slate 50 container
C_CARD_ALT    = "#F1F5F9"  # Light Slate 100 card
C_CARD_WHITE  = "#FFFFFF"  # White container
C_BORDER      = "#E2E8F0"  # Subtle Border (Slate 200)
C_BORDER_DARK = "#CBD5E1"  # Structural Border (Slate 300)
C_NAVY        = "#1E3A8A"  # Primary Academic Navy (Blue 900)
C_BLUE        = "#2563EB"  # Solid Engineering Blue (Blue 600)
C_BLUE_LIGHT  = "#EFF6FF"  # Soft Blue tint (Blue 50)
C_TEXT_MAIN   = "#0F172A"  # Primary Typography: Ink Charcoal (Slate 900)
C_TEXT_SUB    = "#334155"  # Secondary Typography (Slate 700)
C_TEXT_MUTED  = "#64748B"  # Muted Metadata (Slate 500)
C_GREEN       = "#16A34A"  # Solid Forest Green (Pass/Hardware Verified)
C_GREEN_BG    = "#F0FDF4"  # Soft Green tint
C_AMBER       = "#D97706"  # Solid Warm Amber (Warning/Saturation/Sign Bit)
C_AMBER_BG    = "#FFFBEB"  # Soft Amber tint
C_RED         = "#DC2626"  # Solid Crimson (Baseline/Error)
C_PURPLE      = "#4F46E5"  # Academic Indigo Accent

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
    <rect x="60" y="30" width="1160" height="85" fill="{C_CARD_BG}" rx="8" stroke="{C_BORDER}" stroke-width="1"/>
    <text x="80" y="52" fill="{C_NAVY}" font-size="12" font-weight="bold" letter-spacing="1">{eyebrow}</text>
    <text x="80" y="82" fill="{C_TEXT_MAIN}" font-size="24" font-weight="bold">{title}</text>
    <text x="80" y="104" fill="{C_TEXT_MUTED}" font-size="13">{subtitle}</text>
  </g>
"""

def standard_footer(gid, takeaway, badge="CE436 CAPSTONE"):
    return f"""  <g id="{gid}" data-pptx-bounds="60 655 1160 40">
    <rect x="60" y="655" width="1160" height="38" rx="6" fill="{C_CARD_ALT}" stroke="{C_BORDER}" stroke-width="1"/>
    <rect x="72" y="663" width="140" height="22" rx="4" fill="{C_NAVY}"/>
    <text x="142" y="678" fill="#FFFFFF" font-size="11" font-weight="bold" text-anchor="middle">{badge}</text>
    <text x="230" y="679" fill="{C_TEXT_MAIN}" font-size="13" font-weight="500">{takeaway}</text>
  </g>
"""

def clean_xml(svg_str):
    # Only escape bare & not already part of valid XML entities
    return re.sub(r'&(?!(?:amp|lt|gt|quot|apos);)', '&amp;', svg_str)

def write_slide(filename, content):
    filepath = OUTPUT_DIR / filename
    filepath.write_text(clean_xml(content), encoding="utf-8")
    print(f"Generated: {filename}")
