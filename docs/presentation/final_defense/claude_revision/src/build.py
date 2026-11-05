"""Final-defense deck built on the SlidesCarnival "Automotive Training Center" template (CC BY 4.0).

The template's master, theme, embedded fonts (League Spartan, Poppins) and visual language
(orange / ink / warm grey, uppercase League Spartan titles, black label bars, numbered squares,
orange bands) are kept; its sample slides and stock photos are removed. All content is ours.

Usage: python3 build.py <project_root> <claude_revision_dir> <output.pptx>
"""
import copy
import json
import math
import sys
import uuid

from lxml import etree
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_TICK_LABEL_POSITION, XL_TICK_MARK
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

ROOT, REV, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
SHOTS = f"{ROOT}/docs/reports/defense_session/screenshots"
A = f"{REV}/assets"
win = json.load(open(f"{A}/window.json"))

# ---------- template palette and type ----------------------------------------------------------
ORANGE, INK, BLACK, BG, GREY, MUTED, WHITE = "FF6B00", "232222", "000000", "F6F4F4", "D9D9D9", "5E5A5A", "FFFFFF"
SOFT = "FFE4D1"   # light orange tint for highlighted rows
MIDGREY = "9A9696"
TITLE, LABEL, BODY, MONO = "League Spartan ExtraBold", "League Spartan", "Poppins", "Consolas"

prs = Presentation(f"{REV}/template/Automotive_Training_Center_SlidesCarnival.pptx")
SW, SH = prs.slide_width, prs.slide_height  # 20 in x 11.25 in

# remove the template's sample slides (their photos are dropped with them)
sldIdLst = prs.slides._sldIdLst
for sldId in list(sldIdLst):
    prs.part.drop_rel(sldId.rId)
    sldIdLst.remove(sldId)
# drop unused layouts that still carry the template's stock photos
for lay in list(prs.slide_layouts):
    if lay.name != "BLANK" and any("image" in r.reltype for r in lay.part.rels.values()):
        prs.slide_layouts.remove(lay)
BLANK = next(l for l in prs.slide_layouts if l.name == "BLANK")


def rgb(h):
    return RGBColor.from_string(h)


# ---------- drawing helpers --------------------------------------------------------------------
def new_slide(bg=BG, hidden=False):
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = rgb(bg)
    if hidden:
        s._element.set("show", "0")
    return s


def text(s, x, y, w, h, content, size=24, font=BODY, color=INK, bold=False, align="l", anchor="t",
         spacing=None, italic=False):
    """content: str (\n = new paragraph) or list of paragraphs, each a list of (text, {overrides})."""
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}[anchor]
    paras = content if isinstance(content, list) else [[(line, {})] for line in content.split("\n")]
    for i, runs in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[align]
        if spacing:
            p.space_after = Pt(spacing)
        for t, o in runs:
            r = p.add_run()
            r.text = t
            f = r.font
            f.name = o.get("font", font)
            f.size = Pt(o.get("size", size))
            f.bold = o.get("bold", bold)
            f.italic = o.get("italic", italic)
            f.color.rgb = rgb(o.get("color", color))
            if o.get("sub"):
                r._r.get_or_add_rPr().set("baseline", "-25000")
            if o.get("sup"):
                r._r.get_or_add_rPr().set("baseline", "30000")
    return tb


def rect(s, x, y, w, h, fill=None, line=None, lw=1.0, shape=MSO_SHAPE.RECTANGLE, dash=None):
    sh = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.shadow.inherit = False
    if fill:
        sh.fill.solid()
        sh.fill.fore_color.rgb = rgb(fill)
    else:
        sh.fill.background()
    if line:
        sh.line.color.rgb = rgb(line)
        sh.line.width = Pt(lw)
        if dash:
            sh.line.dash_style = dash
    else:
        sh.line.fill.background()
    sh.text_frame.margin_left = sh.text_frame.margin_right = 0
    return sh


def oval(s, cx, cy, r, fill=None, line=None, lw=1.25):
    return rect(s, cx - r, cy - r, 2 * r, 2 * r, fill, line, lw, MSO_SHAPE.OVAL)


def seg(s, x1, y1, x2, y2, color=INK, w=1.5, head=False, tail=False, dash=None):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = rgb(color)
    c.line.width = Pt(w)
    if dash:
        c.line.dash_style = dash
    ln = c.line._get_or_add_ln()
    if tail:
        etree.SubElement(ln, qn("a:headEnd")).set("type", "triangle")
    if head:
        etree.SubElement(ln, qn("a:tailEnd")).set("type", "triangle")
    return c


def picture(s, path, x, y, w, crop=None, size=None):
    """crop=(left, top, right, bottom) in source pixels; size=(px_w, px_h). Bytes are untouched."""
    if crop:
        l, t, r, b = crop
        pw, ph = size
        h = w * (b - t) / (r - l)
        p = s.shapes.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h))
        p.crop_left, p.crop_top = l / pw, t / ph
        p.crop_right, p.crop_bottom = 1 - r / pw, 1 - b / ph
    else:
        p = s.shapes.add_picture(path, Inches(x), Inches(y), width=Inches(w))
        h = p.height / 914400
    return p, h


def label_bar(s, x, y, w, h, t, size=28, fill=BLACK, color=WHITE, font=LABEL):
    rect(s, x, y, w, h, fill)
    text(s, x + 0.3, y, w - 0.6, h, t, size=size, font=font, color=color, bold=True, anchor="m")


def num_square(s, x, y, n, size=0.62, fill=BLACK, color=WHITE, fs=22):
    rect(s, x, y, size, size, fill)
    text(s, x, y, size, size, f"{n:02d}" if isinstance(n, int) else n, size=fs, bold=True, color=color, align="c", anchor="m")


def header(s, title, takeaway=None, color=ORANGE, tcolor=INK, x=1.12, w=17.8, y=0.72):
    text(s, x, y, w, 1.15, title.upper(), size=66, font=TITLE, color=color)
    if takeaway:
        text(s, x, y + 1.2, w, 0.62, takeaway, size=26, color=tcolor)


SECTIONS = ["Task", "Model", "Hardware", "Results", "Scope"]
SECTION_OF = {2: 0, 3: 0, 4: 0, 5: 1, 6: 2, 7: 2, 8: 2, 9: 2, 10: 3, 11: 3, 12: 3, 13: 3, 14: 3, 15: 3, 16: 4}
TRACKER_ON = {3: "orange", 13: "orange", 15: "dark"}   # slides whose top-right corner is not the light page


def page(s, n, color=MUTED):
    text(s, 17.9, 10.55, 1.5, 0.4, str(n), size=16, color=color, align="r")
    if n not in SECTION_OF:
        return
    bgk = TRACKER_ON.get(n, "light")
    on, off = {"light": (ORANGE, MIDGREY), "orange": (INK, INK), "dark": (ORANGE, GREY)}[bgk]
    runs = []
    for i, name in enumerate(SECTIONS):
        active = i == SECTION_OF[n]
        runs.append((name, {"color": on if active else off, "bold": active}))
        if i < len(SECTIONS) - 1:
            runs.append(("  ·  ", {"color": off}))
    text(s, 11.4, 0.3, 7.5, 0.4, [runs], size=15, align="r")


def edge(s):  # the template's orange edge band (used on list-style slides)
    rect(s, 0, 0, 0.40, 11.25, ORANGE)


def set_table_style_none(tbl):
    tblPr = tbl._tbl.tblPr
    sid = tblPr.find(qn("a:tableStyleId"))
    if sid is None:
        sid = etree.SubElement(tblPr, qn("a:tableStyleId"))
    sid.text = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"  # No Style, No Grid
    for a in ("firstRow", "bandRow"):
        tblPr.set(a, "0")


def cell_border(cell, side, color=GREY, w=1.0):
    tcPr = cell._tc.get_or_add_tcPr()
    tag = {"b": "a:lnB", "t": "a:lnT", "l": "a:lnL", "r": "a:lnR"}[side]
    for old in tcPr.findall(qn(tag)):
        tcPr.remove(old)
    ln = etree.SubElement(tcPr, qn(tag), w=str(int(Pt(w))), cap="flat", cmpd="sng", algn="ctr")
    sf = etree.SubElement(ln, qn("a:solidFill"))
    etree.SubElement(sf, qn("a:srgbClr"), val=color)
    etree.SubElement(ln, qn("a:prstDash"), val="solid")
    # schema order inside tcPr: lnL, lnR, lnT, lnB, ..., fill — move fills to the end
    for f in [c for c in tcPr if c.tag in (qn("a:solidFill"), qn("a:noFill"))]:
        tcPr.remove(f)
        tcPr.append(f)
    order = [qn("a:lnL"), qn("a:lnR"), qn("a:lnT"), qn("a:lnB")]
    lines = sorted([c for c in tcPr if c.tag in order], key=lambda c: order.index(c.tag))
    for c in lines:
        tcPr.remove(c)
    for i, c in enumerate(lines):
        tcPr.insert(i, c)


def table(s, x, y, colw, rows, rowh=0.62, size=20, header_fill=INK, header_color=WHITE, mono_cols=(),
          zebra=False, highlight_rows=(), first_bold=False, fills=None):
    t = s.shapes.add_table(len(rows), len(colw), Inches(x), Inches(y), Inches(sum(colw)), Inches(rowh * len(rows))).table
    set_table_style_none(t)
    for j, cw in enumerate(colw):
        t.columns[j].width = Inches(cw)
    for i, r in enumerate(rows):
        t.rows[i].height = Inches(rowh)
        for j, v in enumerate(r):
            c = t.cell(i, j)
            c.margin_left = c.margin_right = Inches(0.14)
            c.margin_top = c.margin_bottom = Inches(0.04)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = c.text_frame
            tf.word_wrap = True
            runs = v if isinstance(v, list) else [(str(v), {})]
            p = tf.paragraphs[0]
            for tx, o in runs:
                rn = p.add_run()
                rn.text = tx
                f = rn.font
                head = i == 0 and header_fill
                f.name = o.get("font", LABEL if head else (MONO if j in mono_cols else BODY))
                f.size = Pt(o.get("size", size - 2 if head else size))
                f.bold = o.get("bold", bool(head) or (first_bold and j == 0))
                f.color.rgb = rgb(o.get("color", header_color if head else INK))
            fill = header_fill if (i == 0 and header_fill) else (SOFT if i in highlight_rows else
                    (fills[i] if fills else (BG if zebra and i % 2 == 0 else WHITE)))
            c.fill.solid()
            c.fill.fore_color.rgb = rgb(fill)
            cell_border(c, "b", GREY if i else (header_fill or INK), 1.0)
            for side in "ltr":
                cell_border(c, side, fill, 0.25)
    return t


def notes(s, *paras):
    s.notes_slide.notes_text_frame.text = "\n\n".join(paras)


# =================================================================================================
# 1  Cover
s = new_slide(ORANGE)
# illustration (editable shapes): hourly weather -> FPGA chip -> 3-hour forecast
rect(s, 12.6, 0, 7.4, 11.25, INK)
cx = 16.3


def wind(x1, x2, y):
    c = seg(s, x1, y, x2, y, WHITE, 5)
    c.line._get_or_add_ln().set("cap", "rnd")


rect(s, 15.25, 0.5, 2.4, 2.4, ORANGE, shape=MSO_SHAPE.SUN)
rect(s, 17.25, 1.05, 1.75, 1.05, "6E6A6A", shape=MSO_SHAPE.CLOUD)
rect(s, 13.3, 1.5, 4.0, 2.4, WHITE, shape=MSO_SHAPE.CLOUD)
wind(17.6, 19.35, 2.75)
wind(17.25, 18.75, 3.2)
wind(17.9, 19.0, 3.65)
text(s, 12.6, 4.05, 7.4, 0.45, "hourly weather observations", size=18, color=GREY, align="c")
seg(s, cx, 4.6, cx, 5.12, ORANGE, 2.5, head=True, dash=MSO_LINE_DASH_STYLE.DASH)
# FPGA chip with pins
for i in range(7):
    o = 14.96 + i * 0.42  # centred on the 3.0 in chip body
    rect(s, o, 5.22, 0.16, 0.38, GREY)
    rect(s, o, 8.6, 0.16, 0.38, GREY)
    rect(s, 14.42, 5.8 + i * 0.4, 0.38, 0.16, GREY)
    rect(s, 17.8, 5.8 + i * 0.4, 0.38, 0.16, GREY)
rect(s, 14.8, 5.6, 3.0, 3.0, "3B3939")
rect(s, 15.15, 5.95, 2.3, 2.3, None, ORANGE, 2.5)
text(s, 15.15, 6.35, 2.3, 0.9, "FPGA", size=46, font=TITLE, color=WHITE, align="c", anchor="m")
text(s, 15.15, 7.3, 2.3, 0.45, "Cyclone II", size=16, color=GREY, align="c")
seg(s, cx, 9.1, cx, 9.62, ORANGE, 2.5, head=True, dash=MSO_LINE_DASH_STYLE.DASH)
# forecast card
rect(s, 13.55, 9.75, 5.5, 1.15, WHITE, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
rect(s, 13.8, 9.93, 0.8, 0.8, ORANGE, shape=MSO_SHAPE.SUN)
text(s, 14.8, 9.83, 4.1, 0.5, "Forecast, 3 hours ahead", size=20, bold=True)
text(s, 14.8, 10.3, 4.2, 0.45, "five weather quantities", size=16, color=MUTED)
text(s, 0.65, 0.55, 12.4, 1.85, "WEATHER", size=150, font=TITLE, color=WHITE)
text(s, 0.65, 2.35, 12.0, 1.6, "FORECASTING", size=104, font=TITLE, color=WHITE)
label_bar(s, 0.65, 4.55, 5.3, 1.35, "ON FPGA", size=72)
text(s, 0.65, 6.35, 11.4, 1.3, "Fixed-point inference of five weather quantities, three hours ahead, on a Terasic DE2 Cyclone II board",
     size=30, color=INK)
label_bar(s, 0.65, 8.65, 11.6, 0.95, "CE436  ·  DISCRETE-TIME SIGNAL PROCESSING", size=28)
text(s, 0.65, 9.8, 11, 0.5, "Final defense", size=24, color=INK)
notes(s, "Timing: 0:00–0:30.",
      "Good morning. We are presenting a weather forecaster that runs its inference on an FPGA. It predicts temperature, surface pressure, relative humidity, wind speed and wind direction three hours after the latest hourly observation.",
      "The picture on the right is the whole project in one line: recorded hourly weather observations go into the FPGA, and a forecast for three hours later comes out.",
      "Transition: first, what exactly the system does and where its boundary is.")

# 2  System boundary --------------------------------------------------------------------------------
s = new_slide()
edge(s)
header(s, "What we forecast", "Five quantities, three hours after the latest recorded hourly frame")
qs = [("Temperature", "°C"), ("Surface pressure", "kPa"), ("Relative humidity", "%"), ("Wind speed", "m/s"), ("Wind direction", "degrees")]
for i, (q, u) in enumerate(qs):
    y = 3.25 + i * 1.12
    num_square(s, 1.12, y, i + 1)
    rect(s, 1.86, y, 5.9, 0.62, GREY)
    text(s, 2.1, y, 4.2, 0.62, q, size=24, anchor="m")
    text(s, 6.0, y, 1.6, 0.62, u, size=20, color=MUTED, anchor="m", align="r")
# system diagram
rect(s, 9.0, 3.25, 3.0, 2.3, BLACK)
text(s, 9.2, 3.45, 2.6, 0.5, "HOST PC", size=30, font=TITLE, color=WHITE)
text(s, 9.2, 4.05, 2.7, 1.4, "Replays recorded hourly frames over USB-Blaster\nC++ golden reference", size=18, color=WHITE)
rect(s, 13.1, 3.0, 5.8, 5.25, None, ORANGE, 4)
text(s, 13.45, 3.15, 5.3, 0.5, "DE2 · CYCLONE II EP2C35", size=24, font=TITLE, color=ORANGE)
blocks = [("JTAG mailbox", "128-bit source · 256-bit probe", GREY), ("Six-lane predictor", "7 lags + bias per lane", WHITE),
          ("CORDIC angle unit", "16 iterations, vectoring mode", WHITE)]
for i, (b1, b2, f) in enumerate(blocks):
    y = 3.85 + i * 1.42
    rect(s, 13.5, y, 5.0, 1.0, f, INK if f == WHITE else None, 1.25)
    text(s, 13.75, y + 0.08, 4.6, 0.45, b1, size=22, bold=True)
    text(s, 13.75, y + 0.5, 4.6, 0.4, b2, size=17, color=MUTED)
    if i < 2:
        seg(s, 16.0, y + 1.0, 16.0, y + 1.42, INK, 1.75, head=True)
seg(s, 12.0, 4.35, 13.5, 4.35, INK, 2, head=True)
text(s, 12.0, 3.85, 1.1, 0.4, "JTAG", size=15, color=MUTED, align="c")
seg(s, 13.5, 7.25, 10.5, 7.25, INK, 2)
seg(s, 10.5, 7.25, 10.5, 5.55, INK, 2, head=True)
text(s, 10.65, 6.6, 2.7, 0.45, "forecast read back", size=17, color=MUTED)
# horizon vs replay
seg(s, 9.0, 9.05, 18.9, 9.05, INK, 1.5)
oval(s, 9.1, 9.05, 0.11, INK)
oval(s, 18.8, 9.05, 0.15, ORANGE)
text(s, 9.0, 8.45, 4, 0.45, "latest hourly frame  t", size=20, bold=True)
text(s, 14.9, 8.45, 4, 0.45, "forecast  t + 3 h", size=20, bold=True, color=ORANGE, align="r")
text(s, 9.0, 9.3, 9.9, 0.9, "The 3-hour horizon belongs to the data timestamps. Replaying frames faster than real time does not change it.",
     size=18, color=MUTED)
text(s, 1.12, 9.3, 7.2, 1.2, "Outside our scope: training on the FPGA, live sensors, rainfall probability, LED or LCD output.",
     size=18, color=MUTED)
page(s, 2)
notes(s, "Timing: 0:30–1:25.",
      "We forecast five quantities: temperature, surface pressure, relative humidity, wind speed and wind direction, all three hours after the latest recorded hourly frame.",
      "The system boundary: a host PC replays recorded frames through the USB-Blaster into a JTAG mailbox built with In-System Sources and Probes. The FPGA runs six arithmetic lanes and a CORDIC angle unit with coefficients trained offline, and the host reads the result back and compares it with our C++ reference.",
      "Two clarifications we want to make early. The three-hour horizon comes from the timestamps of the data, not from the hardware clock: replaying frames quickly does not shorten it. And the board does not train, does not read live sensors, does not predict rain, and does not drive the LEDs or LCD.",
      "Sources: hardware/jtag/README.md; versions/weather_v2/rtl/weather_system_speed.v.",
      "Transition: this system grew out of a temperature-only prototype.")

# 3  Development -----------------------------------------------------------------------------------
s = new_slide()
rect(s, 0, 0, 20, 3.55, ORANGE)
header(s, "From one quantity to five", "The temperature prototype set up the workflow; the weather design changed the model and the datapath",
       color=WHITE, tcolor=INK)
rows = [
    ["", "Temperature prototype", "Current weather design"],
    ["Model", "T̂(t+3) = T(t−21) + a·Δdaily + b·Δrecent + c", "x̂(t+3) = bias + Σ wₖ·x(t − ℓₖ),  ℓ ∈ {0,1,3,6,12,21,24} h"],
    ["Learned parameters", "3 (a, b, c)", "7 weights + 1 bias per lane, 6 lanes"],
    ["Outputs", "Temperature", "Temperature, pressure, humidity, wind speed, direction"],
    ["Arithmetic", "One lane, signed 16-bit Q8", "Six lanes, signed 18-bit Q8 samples, Q14 weights"],
    ["Wind direction", "Not modelled", "Cosine and sine lanes + 16-iteration CORDIC"],
    ["Test MAE, temperature", "0.538 °C", [("0.508 °C", {"bold": True, "color": INK})]],
]
table(s, 1.12, 4.05, [3.6, 6.4, 7.8], rows, rowh=0.86, size=20, first_bold=True, zebra=True)
text(s, 1.12, 10.25, 17.8, 0.5, "Unchanged: hourly input frames, the three-hour horizon, offline training, and the C++ bit-exact reference flow.",
     size=18, color=MUTED)
page(s, 3)
notes(s, "Timing: 1:25–2:15.",
      "Our first design only forecast temperature. It anchored on the same hour yesterday, T(t−21), and added two learned corrections for the daily change and the recent three-hour change, plus a constant. Three parameters, one arithmetic lane, 16-bit Q8.",
      "The current design is not the old a, b, c reused. Every quantity now has its own seven-lag regression with a bias, there are six lanes, the arithmetic is 18-bit, and wind direction needed a new path. On the same 2025 test period the temperature MAE improved from 0.538 to 0.508 °C (fixed-point results).",
      "What stayed the same: hourly frames, the three-hour horizon, offline training, and our habit of checking the hardware bit-for-bit against a C++ model.",
      "Sources: software/models_cpp/model.json; docs/reports/temperature_metrics.csv; versions/weather_v2/models/model.json; versions/weather_v2/reports/metrics.csv.")

# 4  Data -----------------------------------------------------------------------------------------
s = new_slide()
header(s, "Chronological evaluation", "Fit on 2021–2023, choose on 2024, report once on 2025")
p, h = picture(s, f"{A}/split_chart.png", 1.12, 3.0, 17.76)
text(s, 1.12, 3.0 + h - 0.05, 17.76, 0.4, "Daily range and daily mean of the hourly 2 m temperature, Ho Chi Minh City (NASA POWER, UTC)",
     size=15, color=MUTED, align="r")
segs = [(0.6, INK, "2021–2023", "26,253", "Training", "Fits the coefficients"),
        (0.2, MIDGREY, "2024", "8,781", "Validation", "Chooses lags and ridge penalty"),
        (0.2, ORANGE, "2025", "8,757", "Test", "Reported once, model frozen")]
x = 1.12
by = 3.0 + h + 0.5
for f, c, yr, n, role, d in segs:
    w = 17.76 * f - 0.08
    rect(s, x, by, w, 0.14, c)
    text(s, x, by + 0.3, w, 0.4, yr, size=20, color=c if c != MIDGREY else MUTED, bold=True)
    text(s, x, by + 0.75, w, 0.8, n, size=48, font=TITLE, color=INK if c != ORANGE else ORANGE)
    text(s, x, by + 1.55, w, 0.45, role + " examples", size=22, bold=True)
    text(s, x, by + 2.0, w, 0.45, d, size=18, color=MUTED)
    x += 17.76 * f
page(s, 4)
notes(s, "Timing: 2:15–3:05.",
      "Our data are NASA POWER hourly observations for Ho Chi Minh City, 2021 to 2025, in UTC. The chart is the real record: the band is each day's range and the line is the daily mean.",
      "We split it by time, never randomly. 2021 to 2023 fits the coefficients, 2024 chooses among candidate models — lags and ridge penalty — and 2025 is used once, after the coefficients are frozen.",
      "The counts, 26,253, 8,781 and 8,757, are usable examples, not raw hours: each example needs 25 hours of valid history and a target three hours later.",
      "Sources: versions/weather_v2/data/weather.csv; versions/weather_v2/software/train_models.py; model.json split_counts.")

# 5  Seven-lag regression -------------------------------------------------------------------------
s = new_slide()
header(s, "Seven-lag regression", "Each lane predicts its own variable from seven past values and a bias")
rect(s, 1.12, 3.05, 13.4, 1.0, BLACK)
text(s, 1.42, 3.05, 13.0, 1.0, [[("x̂(t+3) = bias + Σ", {}), ("k", {"sub": True}), ("  w", {}), ("k", {"sub": True}),
                                  (" · x(t − ℓ", {}), ("k", {"sub": True}), (")      ℓ ∈ {0, 1, 3, 6, 12, 21, 24} h", {})]],
     size=30, color=WHITE, anchor="m")
lags = [0, 1, 3, 6, 12, 21, 24]
wts = win["weights"]
hist = win["history"]
px, pw = 1.6, 17.0
sx = lambda lag: px + pw - lag / 24 * pw
lo, hi = min(hist) - 0.5, max(hist) + 0.5
base, ph = 7.05, 2.35
sy = lambda v: base - (v - lo) / (hi - lo) * ph
seg(s, px - 0.2, base, px + pw + 0.2, base, MIDGREY, 1)
for lag in range(25):
    v, on = hist[24 - lag], lag in lags
    seg(s, sx(lag), sy(v), sx(lag), base, ORANGE if on else MIDGREY, 3 if on else 1)
    oval(s, sx(lag), sy(v), 0.12 if on else 0.06, ORANGE if on else MIDGREY)
    if on:
        text(s, sx(lag) - 0.4, base + 0.1, 0.8, 0.4, str(lag), size=20, bold=True, align="c")
text(s, px - 0.2, base + 0.55, 2.5, 0.4, "← older (lag, hours)", size=16, color=MUTED)
text(s, 5.0, 4.2, 9.0, 0.4, "Hourly temperature, °C · 25-hour window ending 12:00 local, 24 Mar 2025", size=16, color=MUTED)
zy, sc = 8.85, 0.85
text(s, 5.0, zy - 0.45, 6.0, 0.4, "Deployed weights wₖ of the temperature lane", size=16, color=MUTED)
seg(s, px - 0.2, zy, px + pw + 0.2, zy, GREY, 1)
for lag, v in zip(lags, wts):
    hgt = max(abs(v) * sc, 0.03)
    rect(s, sx(lag) - 0.2, zy - hgt if v >= 0 else zy, 0.4, hgt, ORANGE if v >= 0 else INK)
    ty = zy + 0.08 if v >= 0 else zy - 0.42
    text(s, sx(lag) - 0.7, ty, 1.4, 0.35, f"{v:+.2f}".replace("-", "−") if abs(v) >= 0.01 else f"{v:+.4f}".replace("-", "−"),
         size=16, color=MUTED, align="c")
text(s, 1.12, 10.2, 17.8, 0.55, "Temperature lane: deployed float weights over a real 2025 test window. The largest weights sit at 0–1 h and 21–24 h.",
     size=18, color=MUTED)
page(s, 5)
notes(s, "Timing: 3:05–4:05.",
      "This is the model in every lane: a bias plus seven weighted past values of the same variable, at lags 0, 1, 3, 6, 12, 21 and 24 hours. Temperature does not use humidity or pressure in the selected model; each channel uses its own history.",
      "The stems are a real 25-hour window from the 2025 test set (24 March 2025, ending 12:00 local time). The orange stems are the seven taps. The bars underneath are the deployed temperature weights: the biggest ones are at the last one or two hours and at 21 to 24 hours, which is the same time yesterday — the daily cycle.",
      "Training is ridge-regularised least squares done offline in Python; the penalty only shrinks coefficients during fitting. The FPGA only evaluates the fixed sum.",
      "Sources: versions/weather_v2/models/model.json (lags_hours, weights); validation_candidates.csv.")

# 6  Fixed point -------------------------------------------------------------------------------------
s = new_slide()
header(s, "Fixed-point datapath", "Keep full precision through the sum; shift once at the end")
bp, cell = 9.6, 0.19
rws = [("Sample", "18-bit, Q8", 10, 8, INK), ("Weight", "18-bit, Q14", 4, 14, INK), ("Product", "36-bit, Q22", 14, 22, INK),
       ("Bias, aligned", "32-bit Q8, × 2¹⁴", 24, 22, MIDGREY), ("Accumulator", "48-bit, Q22", 26, 22, INK),
       ("Output", "18-bit Q8 after >>> 14", 10, 8, ORANGE)]
y0, gap = 3.35, 0.9
for i, (nm, fmt, ib, fb, c) in enumerate(rws):
    y = y0 + i * gap
    text(s, 1.12, y - 0.07, 2.9, 0.42, nm, size=22, bold=True, color=ORANGE if c == ORANGE else INK)
    text(s, 1.12, y + 0.33, 3.2, 0.38, fmt, size=16, color=MUTED, font=MONO)
    for b in range(ib + fb):
        xx = bp - ib * cell + b * cell
        rect(s, xx + 0.015, y, cell - 0.03, 0.42, (GREY if b < ib else (c if c != INK else "5E5A5A")))
seg(s, bp, y0 - 0.4, bp, y0 + 5 * gap + 0.65, ORANGE, 2.25, dash=MSO_LINE_DASH_STYLE.DASH)
text(s, bp - 1.2, y0 - 0.85, 2.4, 0.4, "binary point", size=18, color=ORANGE, align="c")
text(s, bp - 2.6, y0 + 6 * gap - 0.2, 2.45, 0.4, "integer bits", size=16, color=MUTED, align="r")
text(s, bp + 0.15, y0 + 6 * gap - 0.2, 2.45, 0.4, "fraction bits", size=16, color=MUTED)
# limits panel
rect(s, 14.55, 3.0, 4.35, 5.95, BLACK)
text(s, 14.85, 3.2, 3.9, 0.5, "AFTER THE SHIFT", size=26, font=TITLE, color=ORANGE)
lim = [("Humidity", "0 … 100 %"), ("Wind speed", "≥ 0"), ("cos, sin", "−1.0 … +1.0"), ("All outputs", "saturate to 18 bits")]
for i, (k, v) in enumerate(lim):
    yy = 3.95 + i * 1.18
    text(s, 14.85, yy, 3.9, 0.42, k, size=20, bold=True, color=WHITE)
    text(s, 14.85, yy + 0.45, 3.9, 0.42, v, size=20, color=GREY)
rect(s, 1.12, 9.55, 17.78, 0.95, BG, GREY, 1)
text(s, 1.42, 9.55, 17.3, 0.95, [[("30 °C × 2⁸ = 7680 raw.  ", {"font": MONO, "bold": True}),
                                  ("Floor scaling by arithmetic shift; the C++ reference uses the same rules, so any mismatch is an implementation bug, not forecast error.", {"color": MUTED})]],
     size=19, anchor="m")
page(s, 6)
notes(s, "Timing: 4:05–5:05.",
      "Q8 means eight fractional bits. A sample is signed 18-bit Q8 — 30 °C is 7680 raw. Weights are signed 18-bit Q14. Their product is 36 bits with 22 fractional bits.",
      "The bias is stored as signed 32-bit Q8 and multiplied by 2 to the 14 so it lines up with the products. We add seven products into a 48-bit accumulator, then do a single arithmetic shift right by 14 to return to Q8.",
      "After the shift we apply the physical limits — humidity 0 to 100 percent, wind speed not negative, cosine and sine within plus or minus one — and saturate every output to the 18-bit range.",
      "The binary point is a convention, not a wire. Because the C++ reference uses identical floor and limit rules, a mismatch means a hardware bug, not a forecasting error.",
      "Sources: versions/weather_v2/rtl/weather_ar_channel.v (acc, scaled = acc >>> 14, limited); versions/weather_v2/tb/weather_reference.cpp.")

# 7  Architecture: one lane in detail, then six in parallel ----------------------------------------
s = new_slide()
edge(s)
header(s, "Six parallel lanes", "Each lane owns one multiplier and reuses it for all seven taps — 6 multipliers, not 42")
# ---- A: inside one lane (weather_ar_channel.v) ------------------------------------------------------
text(s, 1.12, 2.95, 12, 0.45, [[("Inside one lane", {"bold": True}), ("   weather_ar_channel.v", {"font": MONO, "size": 17, "color": MUTED})]], size=22)
ry, rh, cw = 4.15, 0.55, 0.2
for k in range(25):  # hist[24] (oldest) on the left ... hist[0] (newest) on the right
    lag = 24 - k
    rect(s, 1.12 + k * cw, ry, cw - 0.04, rh, ORANGE if lag in lags else GREY)
for lag in lags:
    text(s, 1.12 + (24 - lag) * cw - 0.15, ry + rh + 0.05, 0.5, 0.35, str(lag), size=15, color=ORANGE, bold=True, align="c")
text(s, 1.12, ry - 0.45, 5.0, 0.4, "25-frame history, 7 taps (lag in h)", size=16, color=MUTED)
text(s, 1.12, ry + rh + 0.42, 5.0, 0.4, "shifts left on each accepted frame", size=15, color=MUTED)
# datapath stages, laid out left to right with equal gaps
def stage(x, w, t1, t2, fill=WHITE, line=INK):
    rect(s, x, ry - 0.2, w, rh + 0.4, fill, line, 1.5)
    text(s, x, ry - 0.13, w, 0.42, t1, size=16, bold=True, align="c")
    text(s, x, ry + 0.3, w, 0.4, t2, size=15, color=INK if fill == ORANGE else MUTED, align="c", font=MONO)


def op(cx, sym):
    oval(s, cx, ry + rh / 2, 0.4, WHITE, ORANGE, 2.5)
    text(s, cx - 0.4, ry + rh / 2 - 0.3, 0.8, 0.6, sym, size=28, bold=True, color=ORANGE, align="c", anchor="m")


widths = [("box", 2.0), ("op", 0.8), ("box", 1.55), ("op", 0.8), ("box", 1.85), ("box", 2.1), ("box", 1.6)]
x0, x1 = 6.55, 18.9
gapw = (x1 - x0 - sum(w for _, w in widths)) / (len(widths) - 1)
xs, x = [], x0
for _, w in widths:
    xs.append(x)
    x += w + gapw
mid = ry + rh / 2
seg(s, 6.12, mid, xs[0], mid, INK, 2, head=True)
stage(xs[0], 2.0, "Tap select", "hist[lag(term)]")
op(xs[1] + 0.4, "×")
stage(xs[2], 1.55, "Product", "36-bit Q22")
op(xs[3] + 0.4, "+")
stage(xs[4], 1.85, "Accumulator", "48-bit Q22")
stage(xs[5], 2.1, "Scale, limit", ">>>14, saturate")
stage(xs[6], 1.6, "Result", "18-bit Q8", fill=ORANGE, line=ORANGE)
for i in range(6):
    xa = xs[i] + widths[i][1]
    seg(s, xa, mid, xs[i + 1], mid, INK, 2, head=True)
# weight constant into the multiplier, bias into the accumulator
rect(s, xs[1] - 0.5, 2.9, 1.8, 0.72, BLACK)
text(s, xs[1] - 0.5, 2.9, 1.8, 0.72, "weight[term]\nQ14 constant", size=15, color=WHITE, align="c", anchor="m")
seg(s, xs[1] + 0.4, 3.62, xs[1] + 0.4, mid - 0.4, INK, 2, head=True)
rect(s, xs[4], 2.9, 1.85, 0.72, BG, MIDGREY, 1)
text(s, xs[4], 2.9, 1.85, 0.72, "starts at\nbias × 2¹⁴", size=15, align="c", anchor="m")
seg(s, xs[4] + 0.92, 3.62, xs[4] + 0.92, ry - 0.2, MIDGREY, 1.5, head=True)
# feedback loop: accumulator back into the adder, once per tap
fy = ry + rh + 0.55
seg(s, xs[4] + 0.92, ry + rh + 0.2, xs[4] + 0.92, fy, INK, 1.5)
seg(s, xs[4] + 0.92, fy, xs[3] + 0.4, fy, INK, 1.5)
seg(s, xs[3] + 0.4, fy, xs[3] + 0.4, mid + 0.4, INK, 1.5, head=True)
text(s, xs[3] - 1.9, fy - 0.2, 2.1, 0.4, "7 passes", size=15, color=MUTED, align="r")
text(s, 1.12, 5.85, 17.8, 0.45, [[("Per tap: ", {"bold": True}), ("operand → product → accumulate, 3 cycles.  ", {}),
                                 ("Seven taps plus accept and publish: lane result at N + 22.", {"color": MUTED})]], size=16)
# ---- B: six copies in parallel ---------------------------------------------------------------------
seg(s, 1.12, 6.75, 18.9, 6.75, GREY, 1)
text(s, 1.12, 6.95, 9, 0.45, [[("Six copies in parallel", {"bold": True}), ("   weather_predictor_speed.v", {"font": MONO, "size": 17, "color": MUTED})]], size=22)
lanes = ["Temperature", "Pressure", "Humidity", "Wind speed", "Cosine", "Sine"]
ly0, lg = 7.55, 0.5
text(s, 4.1, ly0 + 6 * lg - 0.05, 3.2, 0.38, "same datapath, own weights", size=15, color=MUTED, align="c")
for i, ln in enumerate(lanes):
    y = ly0 + i * lg
    d = i >= 4
    num_square(s, 1.12, y, i + 1, size=0.4, fill=ORANGE if d else BLACK, fs=14)
    text(s, 1.7, y, 2.4, 0.4, ln, size=17, anchor="m", bold=not d)
    rect(s, 4.1, y + 0.04, 3.2, 0.32, GREY)
    if not d:
        seg(s, 7.3, y + 0.2, 10.85, y + 0.2, MIDGREY, 1.25, head=True)
ya, yb = ly0 + 4 * lg + 0.2, ly0 + 5 * lg + 0.2
for yy in (ya, yb):
    seg(s, 7.3, yy, 7.8, yy, ORANGE, 1.25)
seg(s, 7.8, ya, 7.8, yb, ORANGE, 1.25)
seg(s, 7.8, (ya + yb) / 2, 8.1, (ya + yb) / 2, ORANGE, 1.25, head=True)
rect(s, 8.1, ya - 0.3, 2.0, yb - ya + 0.6, ORANGE)
text(s, 8.1, ya - 0.3, 2.0, yb - ya + 0.6, "CORDIC\n18 cycles", size=15, bold=True, align="c", anchor="m")
seg(s, 10.1, (ya + yb) / 2, 10.85, (ya + yb) / 2, ORANGE, 1.25, head=True)
rect(s, 10.85, ly0 - 0.05, 1.75, 6 * lg, BLACK)
text(s, 10.85, ly0 - 0.05, 1.75, 6 * lg, "Output\nregisters\n\nvalid at\nN + 40", size=15, bold=True, color=WHITE, align="c", anchor="m")
notes_r = [("Handshake", "History shifts only when valid and ready are both high; idle clocks change nothing."),
           ("Warm-up", "Frames 1–24 fill the history. Frame 25 gives the first forecast."),
           ("Multipliers", "Each 18 × 18 multiplier uses two 9-bit elements: 12 in the Quartus fit.")]
for i, (h1, h2) in enumerate(notes_r):
    y = 7.0 + i * 1.12
    text(s, 13.3, y, 5.6, 0.4, h1, size=19, bold=True, color=ORANGE)
    text(s, 13.3, y + 0.4, 5.6, 0.7, h2, size=16)
page(s, 7)
notes(s, "Timing: 5:05–6:00.",
      "Top half: one lane, exactly as weather_ar_channel.v is written. The lane keeps a 25-frame history. A counter called term runs from 0 to 6; for each value it selects one tapped sample, multiplies it by that tap's Q14 weight — a constant in the RTL — and adds the 36-bit product into a 48-bit accumulator. The accumulator starts from the bias shifted into alignment. That is three cycles per tap: operand, product, accumulate. After seven taps the lane shifts right by 14, applies the limits and saturates to an 18-bit Q8 result, ready at N+22.",
      "So a lane has one multiplier, used seven times. Bottom half: six identical lanes with their own weights run in parallel — six multipliers, not 42. In the Quartus fit each 18-by-18 multiplier is two 9-bit elements, which is why the report shows 12.",
      "Lanes 1 to 4 go straight to the output registers. Lanes 5 and 6, cosine and sine, go to the CORDIC, which needs another 18 cycles. The wrapper holds the scalar results, and forecast_valid rises together with the angle at N+40, so all five quantities leave the core at once.",
      "History moves only when a frame is accepted — valid and ready both high; idle clocks do not shift anything. The first 24 frames fill the history; frame 25 is the first that produces a forecast.",
      "Sources: versions/weather_v2/rtl/weather_ar_channel.v (hist[0:24], term, operand, product, acc, scaled = acc >>> 14, limited); weather_predictor_speed.v; weather_system_speed.v (output registers loaded on core_valid, forecast_valid from the CORDIC).")

# 8  Direction: how the CORDIC computes the angle ----------------------------------------------------
ATAN_Q16 = [2949120, 1740967, 919879, 466945, 234379, 117304, 58666, 29335, 14668, 7334, 3667, 1833, 917, 458, 229, 115]


def rtl_cordic(c, s_):
    """Bit-accurate copy of wind_direction_cordic.v: returns (angle_out raw Q8, per-step trace)."""
    if c < 0:
        x, y, ang = -c * 65536, -s_ * 65536, (-11796480 if s_ < 0 else 11796480)
    else:
        x, y, ang = c * 65536, s_ * 65536, 0
    tr = [(x, y, ang)]
    for i in range(16):
        if y > 0:
            x, y, ang = x + (y >> i), y - (x >> i), ang + ATAN_Q16[i]
        elif y < 0:
            x, y, ang = x - (y >> i), y + (x >> i), ang - ATAN_Q16[i]
        tr.append((x, y, ang))
    w = ang + 23592960 if ang < 0 else ang
    return (w >> 8) & 0x3FFFF, tr


COS_RAW, SIN_RAW = 0x0E7, 0x016  # direction_cos_out_q8 / direction_sin_out_q8 in the SignalTap capture
angle_raw, trace = rtl_cordic(COS_RAW, SIN_RAW)
assert angle_raw == 0x570  # the captured direction_angle_out_q8

s = new_slide()
edge(s)
header(s, "Wind direction: CORDIC", "Sixteen shift-and-add rotations turn the predicted (cos, sin) into an angle")
# --- left: the angle estimate θ after each step, closing in on the predicted vector -----------------
text(s, 1.12, 3.0, 8.2, 0.45, f"Board example: cos θ = {COS_RAW / 256:.3f},  sin θ = {SIN_RAW / 256:.3f}", size=22, bold=True)
ox, oy, R = 1.45, 8.1, 5.6              # origin and arrow length, inches
P = lambda deg, r=R: (ox + r * math.cos(math.radians(deg)), oy - r * math.sin(math.radians(deg)))
seg(s, ox - 0.15, oy, ox + R + 0.9, oy, MIDGREY, 1.25, head=True)
seg(s, ox, oy + 0.15, ox, 3.75, MIDGREY, 1.25, head=True)
text(s, ox + R + 0.95, oy - 0.22, 0.4, 0.4, "x", size=18, color=MUTED)
text(s, ox + 0.12, 3.6, 0.6, 0.4, "y", size=18, color=MUTED)
for i in range(1, 5):  # running angle estimate after steps 1-4
    th = trace[i][2] / 65536
    tx, ty = P(th)
    seg(s, ox, oy, tx, ty, MIDGREY, 1.5, head=True)
    text(s, tx + 0.1, ty - 0.22, 1.9, 0.4, f"step {i}: {th:.1f}°", size=15, color=MUTED)
true_deg = math.degrees(math.atan2(SIN_RAW, COS_RAW))
tx, ty = P(true_deg, R * 0.78)
seg(s, ox, oy, tx, ty, ORANGE, 4.5, head=True)
th16 = trace[16][2] / 65536
tx, ty = P(th16, R * 0.5)
seg(s, ox, oy, tx, ty, INK, 2.5, head=True)
text(s, 1.12, oy + 0.15, 8.2, 0.4, [[("━ predicted (cos, sin) vector, 5.44°", {"color": ORANGE, "bold": True}),
                                     (f"     ━ θ after 16 steps, {th16:.2f}°", {"color": INK, "bold": True})]], size=15)
text(s, 1.12, 8.75, 8.2, 0.9, "Grey arrows: the hardware's angle estimate θ after steps 1–4. It overshoots to 45°, then swings back in halving steps until it lands on the predicted vector.",
     size=17, color=MUTED)
# --- right top: convergence of the accumulated angle (native chart) --------------------------------
text(s, 10.0, 3.0, 8.9, 0.45, "Accumulated angle θ after each step, degrees", size=22, bold=True)
cd = CategoryChartData()
cd.categories = [str(i) for i in range(17)]
cd.add_series("Hardware CORDIC", [t[2] / 65536 for t in trace])
cd.add_series("Ideal atan2 = 5.44°", [math.degrees(math.atan2(SIN_RAW, COS_RAW))] * 17)
gf = s.shapes.add_chart(XL_CHART_TYPE.LINE_MARKERS, Inches(9.85), Inches(3.45), Inches(9.1), Inches(3.1), cd)
ch = gf.chart
ch.font.name, ch.font.size = BODY, Pt(14)
ch.has_title = False
ch.has_legend = True
ch.legend.include_in_layout = False
ch.legend.position = 2  # XL_LEGEND_POSITION.TOP
ch.legend.font.size = Pt(14)
va = ch.value_axis
va.minimum_scale, va.maximum_scale, va.major_unit = 0, 50, 10
va.has_major_gridlines = True
va.major_gridlines.format.line.color.rgb = rgb(GREY)
va.tick_labels.font.size = Pt(14)
va.tick_labels.font.color.rgb = rgb(MUTED)
va.format.line.fill.background()
ca = ch.category_axis
ca.tick_labels.font.size = Pt(14)
ca.tick_labels.font.color.rgb = rgb(MUTED)
ca.format.line.color.rgb = rgb(MIDGREY)
hw, ideal = ch.plots[0].series
hw.format.line.color.rgb = rgb(ORANGE)
hw.format.line.width = Pt(2.5)
hw.smooth = False
hw.marker.style = 8  # circle
hw.marker.size = 7
hw.marker.format.fill.solid()
hw.marker.format.fill.fore_color.rgb = rgb(ORANGE)
hw.marker.format.line.color.rgb = rgb(ORANGE)
ideal.format.line.color.rgb = rgb(INK)
ideal.format.line.width = Pt(1.25)
ideal.format.line.dash_style = MSO_LINE_DASH_STYLE.DASH
ideal.marker.style = -4142  # none
ideal.smooth = False
for el in (ch._chartSpace, ch._chartSpace.chart.plotArea):  # transparent backgrounds
    spPr = el.find(qn("c:spPr"))
    if spPr is None:
        spPr = etree.SubElement(el, qn("c:spPr"))
        el.remove(spPr)
        if el is ch._chartSpace.chart.plotArea:
            el.append(spPr)
        else:
            el.insert(list(el).index(el.find(qn("c:chart"))) + 1, spPr)
    for c in list(spPr):
        spPr.remove(c)
    etree.SubElement(spPr, qn("a:noFill"))
    etree.SubElement(etree.SubElement(spPr, qn("a:ln")), qn("a:noFill"))
# --- right bottom: the rule implemented in wind_direction_cordic.v ---------------------------------
rect(s, 10.0, 6.85, 8.9, 2.55, BLACK)
text(s, 10.3, 6.98, 8.4, 0.45, "One step i = 0 … 15 in wind_direction_cordic.v", size=18, bold=True, color=ORANGE)
text(s, 10.3, 7.5, 8.4, 1.0, "y > 0:  x += y>>>i   y −= x>>>i   θ += atan(2⁻ⁱ)\ny < 0:  x −= y>>>i   y += x>>>i   θ −= atan(2⁻ⁱ)",
     size=17, font=MONO, color=WHITE, spacing=4)
text(s, 10.3, 8.45, 8.4, 0.95, "Step 1: y = 0.086 > 0, the true angle is above the estimate 0°, so θ += 45°. Internally (x, y) is turned back by the same 45°, so the next step can test the new estimate. Only shifts, adds and a 16-entry table, no multiplier.",
     size=15, color=GREY)
# --- bottom: result and checks --------------------------------------------------------------------
rect(s, 1.12, 9.65, 17.78, 1.0, BG, GREY, 1)
text(s, 1.42, 9.65, 17.3, 1.0, [[("Result: ", {"bold": True}), ("the turns add up to θ = 5.44°, a wind from just east of north. ", {}),
                                  (f"The board reported {angle_raw / 256:.4f}°, {abs(angle_raw / 256 - math.degrees(math.atan2(SIN_RAW, COS_RAW))):.3f}° from the exact value. ", {"bold": True}),
                                  ("Over every possible input pair the worst error is 0.0056°.", {"color": MUTED})]],
     size=16, anchor="m")
page(s, 8)
notes(s, "Timing: 6:00–7:00.",
      "The two direction lanes give us a predicted cosine and sine. Why components at all: 1 degree and 359 degrees are only 2 degrees apart, but a regression on raw angles would see 358. Predicting cos and sin avoids that wrap.",
      "To get the angle back, wind_direction_cordic.v runs a vectoring CORDIC. The idea is to rotate the vector onto the x-axis and add up how much we rotated. At step i, if y is positive we rotate clockwise by atan of 2 to the minus i, otherwise counter-clockwise. A rotation by exactly that angle needs only shifts by i and additions, plus a table of 16 arctangent constants stored as degrees times 2 to the 16. No multiplier is used. The vector length grows by about 1.647, but we only keep the angle, so that does not matter.",
      "This is a real forecast from our SignalTap capture. The two lanes predicted cos θ = 0.902 and sin θ = 0.086, a vector pointing 5.4 degrees above the x-axis. The arrows show the hardware's estimate θ after each step. It starts at 0. Step 1: the remaining y is positive, so the true angle is above the estimate and θ jumps up by 45 degrees — an overshoot. Step 2: the residual is now negative, so θ comes back down by 26.6 to 18.4 degrees. Step 3 goes down 14.0 to 4.4; step 4 up 7.1 to 11.5. Each correction is about half the previous one, so θ closes in on 5.44 degrees.",
      "How the hardware knows which way to go: it keeps rotating the (x, y) vector back by each correction, so y always holds what is still left over. When y is positive the estimate is too small, when it is negative the estimate is too big.",
      "After 16 steps the board reported 5.4375 degrees; the exact value is 5.4403, a difference of 0.003 degrees. Since the dataset measures direction clockwise from north, 5.4 degrees is a wind from just east of north. (In the RTL these values are Q8 integers: 231 and 22 in, 0x570 out.)",
      "Two details in the RTL: if the cosine is negative the vector is negated first and the angle starts at plus or minus 180 degrees, because the iterations only converge within about ±99 degrees. The result is wrapped into 0 to 360 degrees and output in Q8; an all-zero vector has no direction and is flagged undefined.",
      "We tested every integer input pair from −256 to 256: 263,169 vectors, maximum error 0.005635 degrees. The forecast-accuracy numbers use ideal atan2, so this conversion error is reported separately.",
      "Sources: versions/weather_v2/rtl/wind_direction_cordic.v; docs/reports/defense_session/screenshots/weather_speed_signaltap_detail.png (direction_cos_out_q8 000E7h, direction_sin_out_q8 00016h, direction_angle_out_q8 00570h); versions/weather_v2/reports/direction_exhaustive.log. The step values on this slide are computed by a bit-accurate Python copy of the RTL inside the build script.",
      "Transition: the CORDIC's 18 cycles are part of the total latency — next slide.")

# 9  Timing ---------------------------------------------------------------------------------------------
s = new_slide()
header(s, "Latency vs. initiation interval", "A forecast takes 40 cycles; a new frame can enter every 23 cycles")
gx, gw, span = 3.2, 15.7, 46
cxp = lambda c: gx + c / span * gw
seg(s, gx, 3.55, gx + gw, 3.55, MIDGREY, 1)
for c in range(span + 1):
    major = c in (0, 22, 23, 40)
    seg(s, cxp(c), 3.55 - (0.18 if major else 0.08), cxp(c), 3.55, INK if major else MIDGREY, 1)
for c, l in ((0, "N"), (22, "N+22"), (40, "N+40")):
    text(s, cxp(c) - 0.7, 3.0, 1.4, 0.35, l, size=16, font=MONO, align="c")
text(s, 1.12, 3.95, 2.0, 0.6, "Frame A", size=20, bold=True, anchor="m")
rect(s, cxp(0), 3.95, cxp(22) - cxp(0) - 0.03, 0.6, ORANGE)
text(s, cxp(0) + 0.2, 3.95, 7, 0.6, "7 × (operand · multiply · accumulate) + publish", size=18, bold=True, anchor="m")
rect(s, cxp(22), 3.95, cxp(40) - cxp(22), 0.6, INK)
text(s, cxp(22) + 0.2, 3.95, 5, 0.6, "CORDIC, 16 iterations", size=18, bold=True, color=WHITE, anchor="m")
text(s, 1.12, 4.85, 2.0, 0.6, "Frame B", size=20, bold=True, anchor="m")
rect(s, cxp(23), 4.85, cxp(span) - cxp(23), 0.6, "FFB27F")
text(s, cxp(23) + 0.2, 4.85, 5, 0.6, "accepted at N+23 …", size=18, bold=True, anchor="m")
seg(s, cxp(23), 3.55, cxp(23), 6.2, INK, 1.25, dash=MSO_LINE_DASH_STYLE.DASH)
seg(s, cxp(40), 3.55, cxp(40), 6.2, ORANGE, 1.25, dash=MSO_LINE_DASH_STYLE.DASH)
seg(s, cxp(0), 5.9, cxp(23), 5.9, INK, 1.5, head=True, tail=True)
text(s, cxp(0), 5.95, cxp(23) - cxp(0), 0.4, "initiation interval 23", size=17, align="c")
seg(s, cxp(0), 6.6, cxp(40), 6.6, ORANGE, 1.5, head=True, tail=True)
text(s, cxp(0), 6.65, cxp(40) - cxp(0), 0.4, "latency 40 → forecast_valid", size=17, color=ORANGE, align="c", bold=True)
rows = [["Forecast horizon", "Sampling interval", "Clock period", "Prediction latency", "Initiation interval"],
        ["3 h", "1 h", "20 ns", "40 cycles = 0.80 µs", "23 cycles = 0.46 µs"],
        ["data timestamps", "NASA POWER hourly", "50 MHz board clock", "22 lane + 18 CORDIC", "lane ready again"]]
t = table(s, 1.12, 7.55, [3.55] * 5, rows, rowh=0.78, size=20)
for j in range(5):
    for rr in t.cell(2, j).text_frame.paragraphs[0].runs:
        rr.font.color.rgb, rr.font.size = rgb(MUTED), Pt(17)
    for rr in t.cell(1, j).text_frame.paragraphs[0].runs:
        rr.font.bold = True
page(s, 9)
notes(s, "Timing: 7:00–7:55.",
      "Five different time scales appear in this project and we keep them apart: the three-hour forecast horizon and the one-hour sampling interval come from the data; the 20-nanosecond clock period comes from the 50 MHz board clock; and two hardware numbers describe throughput and delay.",
      "A frame accepted at edge N goes through seven operand–multiply–accumulate steps and publishes the lane results at N+22. The CORDIC then needs until N+40, so the full latency is 40 cycles, 0.80 microseconds at 50 MHz.",
      "But the lanes are free again earlier: the next eligible frame can be accepted at N+23. So the sustained initiation interval is 23 cycles, while latency is 40. The cycle-by-cycle table is in backup B4.",
      "Sources: weather_ar_channel.v state machine; wind_direction_cordic.v; speed_dpi.log (latency=40).")

# 10  Verification -----------------------------------------------------------------------------------------
s = new_slide()
edge(s)
header(s, "Verification", "One C++ golden model, three increasingly physical checks")
ver = [("RTL + DPI-C", "Verilator, C++ reference called per cycle", "1,124", "forecasts checked bit-exact",
        "1,200 accepted frames · 4 pending forecasts cancelled by reset · warm-up repeated · latency 40"),
       ("Predictor-core SDF", "ModelSim, post-fit netlist + SDF delays, 20 ns clock", "264", "forecasts checked",
        "288 input frames · predictor core only, not the JTAG transport"),
       ("Physical JTAG", "DE2 board at 50 MHz through USB-Blaster", "104", "forecasts checked",
        "128 recorded frames · scalars and components bit-exact · angle within 5 Q8 units")]
for i, (nm, how, n, nlab, det) in enumerate(ver):
    y = 3.2 + i * 2.15
    if i:
        seg(s, 1.12, y - 0.3, 18.9, y - 0.3, GREY, 1)
    num_square(s, 1.12, y, i + 1, fill=ORANGE if i == 2 else BLACK)
    text(s, 2.05, y - 0.08, 7.6, 0.5, nm, size=28, bold=True)
    text(s, 2.05, y + 0.48, 7.6, 0.45, how, size=18, color=MUTED)
    text(s, 2.05, y + 0.98, 7.6, 0.8, det, size=17, color=INK)
    text(s, 10.2, y - 0.15, 3.0, 1.0, n, size=60, font=TITLE, color=ORANGE if i == 2 else INK, align="r")
    text(s, 13.4, y + 0.1, 5.5, 0.9, nlab, size=20, color=MUTED)
text(s, 1.12, 9.85, 17.8, 0.7, "Agreement with the reference shows the hardware computes the model correctly. Forecast accuracy against real observations is a separate question — next slide.",
     size=18, color=MUTED)
page(s, 10)
notes(s, "Timing: 7:55–8:55.",
      "Every stage compares against the same C++ reference, which uses 64-bit integer sums and explicit floor division.",
      "First, RTL with a DPI-C call in Verilator: 1,200 accepted frames and 1,124 completed forecasts, all bit-exact. The test also resets during processing — four pending forecasts were cancelled — and checks that warm-up restarts. The count is not simply 1,200 minus 24, because every reset needs a fresh warm-up.",
      "Second, the fitted predictor core as a gate-level netlist with SDF delays at a 20 ns clock: 288 frames, 264 forecasts. This covers the core, not the proprietary JTAG transport.",
      "Third, the real board: 128 recorded frames through the JTAG mailbox, 104 forecasts. Scalars and components match bit-for-bit; the angle is allowed five Q8 units of tolerance.",
      "These tests show the hardware computes our model correctly. Whether the model forecasts the weather well is a different question, on the next slide.",
      "Sources: versions/weather_v2/reports/speed_dpi.log; quartus/speed/build/modelsim_timing/simulation.log; docs/reports/defense_session/weather_speed_physical_replay.txt.")

# 11  Accuracy -------------------------------------------------------------------------------------------------
s = new_slide()
header(s, "Forecast accuracy", "Lower test error than both baselines for all five quantities (2025)")
data = [("Temperature", "°C", [0.5079058538883179, 2.08036884777892, 0.8322804613452095], "0.00"),
        ("Pressure", "kPa", [0.03459953465798802, 0.13516729473564004, 0.08577480872444905], "0.000"),
        ("Humidity", "percentage points", [2.614291513217997, 8.831186479387918, 3.8042366107114307], "0.00"),
        ("Wind speed", "m/s", [0.5668776764302843, 0.8304944615735983, 0.8912173118647939], "0.00"),
        ("Direction", "degrees", [18.084597954304055, 21.42381007797044, 35.2922727801699], "0.0")]
cw, gap = 3.32, 0.29
for i, (nm, unit, v, fmt) in enumerate(data):
    x = 1.12 + i * (cw + gap)
    text(s, x, 3.05, cw, 0.45, nm, size=24, bold=True)
    text(s, x, 3.52, cw, 0.4, f"MAE, {unit}", size=16, color=MUTED)
    cd = CategoryChartData()
    cd.categories = ["Model", "Latest", "Prev. day"]
    cd.add_series("MAE", v)
    gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(x - 0.1), Inches(4.0), Inches(cw + 0.2), Inches(4.9), cd)
    ch = gf.chart
    ch.has_legend = False
    ch.has_title = False
    ch.font.name, ch.font.size = BODY, Pt(15)
    va = ch.value_axis
    va.visible = False
    va.tick_label_position = XL_TICK_LABEL_POSITION.NONE
    va.major_tick_mark = XL_TICK_MARK.NONE
    va.format.line.fill.background()
    va.has_major_gridlines = False
    va.minimum_scale = 0
    va.maximum_scale = max(v) * 1.2
    ca = ch.category_axis
    ca.tick_labels.font.size = Pt(15)
    ca.tick_labels.font.color.rgb = rgb(MUTED)
    ca.format.line.color.rgb = rgb(MIDGREY)
    ca.has_major_gridlines = False
    plot = ch.plots[0]
    plot.gap_width = 45
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.number_format, dl.number_format_is_linked = fmt, False
    dl.position = XL_LABEL_POSITION.OUTSIDE_END
    dl.font.size, dl.font.bold = Pt(16), True
    dl.font.color.rgb = rgb(INK)
    for el in (ch._chartSpace, ch._chartSpace.chart.plotArea):  # transparent chart and plot area
        spPr = el.find(qn("c:spPr"))
        if spPr is None:
            spPr = etree.SubElement(el, qn("c:spPr"))
            if el is ch._chartSpace.chart.plotArea:  # spPr must follow the axes inside plotArea
                el.remove(spPr)
                el.append(spPr)
            else:  # chartSpace: spPr goes right after c:chart
                el.remove(spPr)
                el.insert(list(el).index(el.find(qn("c:chart"))) + 1, spPr)
        for c in list(spPr):
            spPr.remove(c)
        etree.SubElement(spPr, qn("a:noFill"))
        ln = etree.SubElement(spPr, qn("a:ln"))
        etree.SubElement(ln, qn("a:noFill"))
    ser = plot.series[0]
    for k, c in enumerate((ORANGE, INK, "BDB8B8")):
        pt = ser.points[k]
        pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = rgb(c)
    gain = round((1 - v[0] / min(v[1], v[2])) * 100)
    text(s, x, 9.0, cw, 0.42, f"−{gain}% vs best baseline", size=17, bold=True, color=ORANGE)
for k, (c, l) in enumerate(((ORANGE, "Selected model, fixed point"), (INK, "Latest value (persistence)"), ("BDB8B8", "Same hour yesterday"))):
    x = 1.12 + k * 5.2
    rect(s, x, 9.72, 0.3, 0.3, c)
    text(s, x + 0.45, 9.62, 4.6, 0.5, l, size=17, anchor="m")
text(s, 1.12, 10.25, 17.8, 0.5, "8,757 scalar targets. Direction: 8,593 targets with wind ≥ 0.5 m/s, ideal angle decoding of quantised components.",
     size=15, color=MUTED)
page(s, 11)
notes(s, "Timing: 8:55–9:45.",
      "Each chart has its own unit and scale, so compare bars within a chart, not across charts. Orange is our fixed-point model on 2025; dark is persistence — the latest value; grey is the same hour yesterday.",
      "Our model has the lowest MAE for every quantity: 0.508 °C for temperature, 0.035 kPa, 2.61 percentage points of humidity, 0.567 m/s, and 18.1 degrees for direction. The improvement over the better baseline ranges from about 16 percent for direction to about 60 percent for pressure.",
      "Direction is evaluated only when the true wind speed is at least 0.5 m/s, 8,593 targets, using ideal atan2 of the quantised components; the hardware CORDIC is verified separately.",
      "Full MAE and RMSE are in backup B3. Source: versions/weather_v2/reports/metrics.csv, split=test, models selected_fixed, persistence, diurnal.")

# 12  Simpler on purpose: same data, more complex models ------------------------------------------
s = new_slide()
header(s, "Simpler on purpose", "On the same data, larger models forecast temperature better — we chose the one that fits hardware")
models = [("MLP, 12–16–1", "225 parameters, ReLU hidden layer", 0.3815901608558603, False),
          ("Boosted trees", "32 trees, depth 3", 0.4732473808863282, False),
          ("RBF network, 16 centres", "210 parameters, exp() kernels", 0.5050139081386191, False),
          ("Our 7-lag model (deployed)", "8 parameters, fixed point, on FPGA", 0.5079058538883179, True),
          ("Temperature prototype", "3 parameters, seasonal OLS", 0.5379726187767988, False),
          ("Same hour yesterday", "baseline", 0.8322804613452095, False)]
text(s, 1.12, 3.0, 10.5, 0.45, "Temperature test MAE, 2025, °C — lower is better", size=20, bold=True)
bx, bw, scale = 5.9, 5.6, 0.9
for i, (name, desc, v, ours) in enumerate(models):
    y = 3.7 + i * 0.98
    text(s, 1.12, y, 4.7, 0.42, name, size=19, bold=True, color=ORANGE if ours else INK)
    text(s, 1.12, y + 0.42, 4.7, 0.38, desc, size=15, color=MUTED)
    w = bw * v / scale
    rect(s, bx, y + 0.12, w, 0.55, ORANGE if ours else (MIDGREY if v < 0.8 else GREY))
    text(s, bx + w + 0.15, y + 0.12, 1.2, 0.55, f"{v:.3f}", size=18, bold=True, anchor="m")
rect(s, 13.0, 3.0, 5.9, 6.0, BLACK)
text(s, 13.35, 3.2, 5.3, 0.5, "WHY WE KEPT IT LINEAR", size=26, font=TITLE, color=ORANGE)
why = [("Accuracy cost", "The MLP is 0.13 °C better. The RBF is level with ours (0.003 °C). Ours is still 39% better than the best baseline."),
       ("Hardware cost", "A 7-lag sum is one multiplier reused 7 times per lane. The MLP needs 16 hidden neurons; the RBF needs exponentials."),
       ("Verifiability", "Fixed-point sums can be checked bit-for-bit against C++ at every stage.")]
for i, (h1, h2) in enumerate(why):
    y = 3.9 + i * 1.65
    text(s, 13.35, y, 5.3, 0.42, h1, size=19, bold=True, color=WHITE)
    text(s, 13.35, y + 0.45, 5.3, 1.15, h2, size=16, color=GREY)
text(s, 1.12, 9.75, 17.8, 0.75, "Same NASA POWER data, same chronological split, 8,757 test targets. Benchmarks are float software models of temperature only; ours is the deployed fixed-point lane.",
     size=16, color=MUTED)
page(s, 12)
notes(s, "Timing: 9:45–10:25.",
      "We want to be honest about where our model stands. On exactly the same data and the same 2025 test set, we also trained larger temperature models in software. A small MLP is clearly better: 0.38 °C MAE against our 0.51. Boosted trees are also better. An RBF network is about the same as ours.",
      "So we did not pick the seven-lag model because it is the most accurate. We picked it because it is the right size for the hardware: each output is a sum of seven products, which is one multiplier reused seven times, and the fixed-point result can be checked bit-for-bit against C++. An MLP would need a hidden layer of 16 neurons per output, and the RBF needs exponentials.",
      "It is still 39 percent better than the best simple baseline, and a clear step up from our three-parameter prototype. A natural next step would be to put the MLP on the FPGA and measure what its extra accuracy costs in logic and latency.",
      "Sources: software/benchmarks/{mlp,tree,rbf}/metrics.csv (split=test); versions/weather_v2/reports/metrics.csv (selected_fixed, diurnal); docs/reports/temperature_metrics.csv. Benchmarks use temperature only and float arithmetic.")

# 13  Quartus ------------------------------------------------------------------------------------------------------
s = new_slide()
rect(s, 12.6, 0, 7.4, 11.25, ORANGE)
text(s, 1.12, 0.72, 11, 1.15, "QUARTUS FIT", size=66, font=TITLE, color=ORANGE)
text(s, 1.12, 1.92, 11, 0.62, "Uninstrumented JTAG build, Quartus II 13.0 SP1", size=26)
crop = (515, 110, 1400, 562)
p, h = picture(s, f"{SHOTS}/weather_speed_flow_summary.png", 1.12, 3.0, 10.4, crop=crop, size=(2448, 1378))
k = 10.4 / (crop[2] - crop[0])
rect(s, 1.12, 3.0, 10.4, h, None, MIDGREY, 1)
marks = [(335, 1), (414, 2), (518, 3)]
for py, n in marks:
    yy = 3.0 + (py - crop[1]) * k
    seg(s, 11.55, yy, 11.95, yy, INK, 1.25)
    oval(s, 12.2, yy, 0.25, BLACK)
    text(s, 11.95, yy - 0.25, 0.5, 0.5, str(n), size=18, bold=True, color=WHITE, align="c", anchor="m")
text(s, 1.12, 3.0 + h + 0.15, 10.4, 0.4, "Native Flow Summary pane, cropped; no values changed. Full timing panels: backup B5.", size=15, color=MUTED)
ann = [("1", "6,253 logic elements", "19% of 33,216 in the EP2C35F672C6"),
       ("2", "4,571 registers", "mostly the six 25-frame history buffers"),
       ("3", "12 nine-bit multipliers", "six 18 × 18 multipliers, one per lane"),
       ("", "Timing at 50 MHz", "setup slack 7.459 ns, hold slack 0.215 ns"),
       ("", "79.74 MHz Fmax", "static slow-model estimate; the board was tested at 50 MHz only")]
for i, (n, h1, h2) in enumerate(ann):
    y = 1.0 + i * 1.95
    if n:
        oval(s, 13.35, y + 0.27, 0.27, BLACK)
        text(s, 13.08, y, 0.54, 0.54, n, size=18, bold=True, color=WHITE, align="c", anchor="m")
    text(s, 13.95, y - 0.03, 5.6, 0.55, h1, size=26, bold=True, color=INK)
    text(s, 13.95, y + 0.55, 5.6, 1.1, h2, size=19, color=INK)
page(s, 13, INK)
notes(s, "Timing: 10:25–11:15.",
      "This is the native Quartus Flow Summary for the uninstrumented JTAG build — the design that includes the board's JTAG mailbox but not SignalTap. We only cropped the window; no numbers were retyped.",
      "It uses 6,253 logic elements, 19 percent of the Cyclone II, and 4,571 registers. Twelve 9-bit embedded multiplier elements correspond to the six 18-by-18 multipliers, one per lane. Memory bits are zero: the histories are in registers.",
      "TimeQuest reports positive setup slack of 7.459 ns and hold slack of 0.215 ns at 50 MHz. The 79.74 MHz is a static slow-model estimate; we did not sweep the clock on the board, which ran at 50 MHz.",
      "Hardware cost is low: we did not try to minimise logic in this speed-oriented version.",
      "Sources: docs/reports/defense_session/screenshots/weather_speed_flow_summary.png, weather_speed_timing_summary.png, weather_speed_fmax.png; docs/reports/JTAG_IMPLEMENTATION_REPORT.md.")

# 14  How it compares: resources and speed against published FPGA predictors -------------------------
def hbar(s, x, y, w, h, cats, vals, colors, fmt, vmax):
    cd = CategoryChartData()
    cd.categories = cats
    cd.add_series("v", vals)
    ch = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(x), Inches(y), Inches(w), Inches(h), cd).chart
    ch.has_legend = ch.has_title = False
    ch.font.name, ch.font.size = BODY, Pt(16)
    va = ch.value_axis
    va.visible = False
    va.has_major_gridlines = False
    va.minimum_scale, va.maximum_scale = 0, vmax
    va.tick_label_position = XL_TICK_LABEL_POSITION.NONE
    va.major_tick_mark = XL_TICK_MARK.NONE
    va.format.line.fill.background()
    ca = ch.category_axis
    ca.reverse_order = True
    ca.tick_labels.font.size = Pt(16)
    ca.tick_labels.font.color.rgb = rgb(INK)
    ca.format.line.color.rgb = rgb(MIDGREY)
    ca.major_tick_mark = XL_TICK_MARK.NONE
    pl = ch.plots[0]
    pl.gap_width = 40
    pl.has_data_labels = True
    dl = pl.data_labels
    dl.number_format, dl.number_format_is_linked = fmt, False
    dl.position = XL_LABEL_POSITION.OUTSIDE_END
    dl.font.size, dl.font.bold = Pt(16), True
    dl.font.color.rgb = rgb(INK)
    for k, c in enumerate(colors):
        pt = pl.series[0].points[k]
        pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = rgb(c)
    for el in (ch._chartSpace, ch._chartSpace.chart.plotArea):
        spPr = el.find(qn("c:spPr"))
        if spPr is None:
            spPr = etree.SubElement(el, qn("c:spPr"))
            el.remove(spPr)
            if el is ch._chartSpace.chart.plotArea:
                el.append(spPr)
            else:
                el.insert(list(el).index(el.find(qn("c:chart"))) + 1, spPr)
        for c in list(spPr):
            spPr.remove(c)
        etree.SubElement(spPr, qn("a:noFill"))
        etree.SubElement(etree.SubElement(spPr, qn("a:ln")), qn("a:noFill"))


s = new_slide()
header(s, "How it compares", "Fewest multipliers per forecast value, at a similar rate per value")
# chart 1: hardware multipliers per predicted value
text(s, 1.12, 3.0, 8.3, 0.45, "Hardware multipliers per predicted value", size=21, bold=True)
text(s, 1.12, 3.45, 8.3, 0.4, "18 × 18-class multiplier blocks ÷ values produced in parallel", size=15, color=MUTED)
hbar(s, 1.0, 3.85, 8.6, 2.7, ["This work (6 for 6)", "Silva et al. 2022 (9 for 1)", "Ferreira et al. 2019 (≈237 for 8)"],
     [1, 9, 236.74 / 8], [ORANGE, MIDGREY, MIDGREY], "0", 36)
# chart 2: time per predicted value
text(s, 1.12, 6.75, 8.3, 0.45, "Time per predicted value, ns", size=21, bold=True)
text(s, 1.12, 7.2, 8.3, 0.4, "ours: 23-cycle interval ÷ 6 values at 50 MHz", size=15, color=MUTED)
hbar(s, 1.0, 7.6, 8.6, 2.1, ["Silva et al. 2022", "Vásquez et al. 2013", "This work"],
     [40.25, 74, 23 * 20 / 6], [MIDGREY, MIDGREY, ORANGE], "0", 95)
# right: logic and the honest reading
rows = [["", "Logic", "Format", "Evidence"],
        [[("This work", {"bold": True})], "6,253 LEs", "18-bit fixed", "board, 50 MHz"],
        [[("Ferreira 2019", {"bold": True})], "≈9,200 LEs", "32-bit fixed", "“1 cycle”, no Fmax"],
        [[("Silva 2022", {"bold": True})], "3,440 LUT6", "32-bit float", "synthesis"],
        [[("Vásquez 2013", {"bold": True})], "n/a", "fixed point", "abstract only"]]
table(s, 10.3, 3.0, [2.35, 1.95, 1.95, 2.35], rows, rowh=0.62, size=15, highlight_rows=(1,))
rect(s, 10.3, 6.4, 8.6, 2.95, BLACK)
text(s, 10.6, 6.55, 8.0, 0.45, "WHAT THIS SHOWS", size=24, font=TITLE, color=ORANGE)
text(s, 10.6, 7.1, 8.0, 2.5, [[("Cheapest in multipliers: ", {"bold": True, "color": WHITE}), ("one per value, because each is reused for all 7 taps.", {"color": GREY})],
                              [("Comparable rate: ", {"bold": True, "color": WHITE}), ("77 ns per value vs 40–74 ns published.", {"color": GREY})],
                              [("The price: ", {"bold": True, "color": WHITE}), ("0.80 µs latency per frame, far below the 1-hour budget.", {"color": GREY})]],
     size=17, spacing=10)
text(s, 1.12, 9.85, 17.8, 0.75, "Caveats: different devices and tasks — Ferreira and Silva also fit the regression on chip; Ferreira's figures are rounded percentages (8% LEs, 89% of 532 9-bit multipliers). Full table and citations: backups B8–B9.",
     size=15, color=MUTED)
page(s, 14)
notes(s, "Timing: 11:15–12:00.",
      "Judges will ask whether this is a good design, so we compare on two numbers that mean the same thing across vendors: how many hardware multipliers each predicted value costs, and how much time each value takes.",
      "Multipliers: we use six 18-by-18 multipliers for six values, one per value, because each multiplier is reused for all seven taps. Silva et al. use 9 multipliers for one regression output. Ferreira et al. use 89 percent of 532 nine-bit multipliers, about 237 full-size ones, for eight parallel predictions — about 30 per value, because everything runs in one clock cycle.",
      "Time: at our sustained rate a new frame every 23 cycles gives six values, about 77 ns per value. Silva report 40 ns per prediction, Vásquez 74 ns. So we are in the same range while using far fewer multipliers.",
      "The price of reuse is latency: 0.80 microseconds per frame. For an hourly forecast that is negligible.",
      "Be honest about the limits: different devices, number formats and tasks. Ferreira and Silva also fit the regression on the chip, which we do not. Ferreira's numbers are rounded percentages. Vásquez we only know from the abstract. Logic is shown in the table but not charted because LEs and LUT6s are different units; Ferreira's ≈9,200 LEs is the closest comparison, same Altera LE architecture.",
      "Sources: docs/papers/willian-de-assis-pedrobon-ferreira-fpga-hardware.pdf, Table 1; Silva et al., Sensors 22(9):3556, Table 2; Vásquez et al., Cogn. Comput. 2013, abstract; our Quartus Flow Summary. Details: docs/specs/ols_fpga_literature_review.md.")

# 15  SignalTap ----------------------------------------------------------------------------------------------------
s = new_slide()
rect(s, 0, 0, 20, 2.75, INK)
header(s, "On the board", "SignalTap: one accepted frame, and its forecast 41 samples later", color=ORANGE, tcolor=WHITE)
# two native crops at the same scale: signal-name column + waveform window (bytes untouched)
src_ = f"{SHOTS}/weather_speed_signaltap_detail.png"
names, wave = (84, 62, 300, 445), (760, 62, 1950, 445)
k = (17.76 - 0.15) / ((names[2] - names[0]) + (wave[2] - wave[0]))
wn, ww = (names[2] - names[0]) * k, (wave[2] - wave[0]) * k
y0 = 3.05
p, h = picture(s, src_, 1.12, y0, wn, crop=names, size=(2448, 530))
wx = 1.12 + wn + 0.15
picture(s, src_, wx, y0, ww, crop=wave, size=(2448, 530))
rect(s, 1.12, y0, wn, h, None, MIDGREY, 1)
rect(s, wx, y0, ww, h, None, MIDGREY, 1)
for px_, lbl in ((979, "frame accepted · sample 215"), (1542, "forecast_valid · sample 256")):
    ax = wx + (px_ - wave[0]) * k
    seg(s, ax, y0 + h, ax, y0 + h + 0.35, ORANGE, 2)
    text(s, ax - 2.2, y0 + h + 0.38, 4.4, 0.4, lbl, size=17, bold=True, color=ORANGE, align="c")
text(s, 1.12, y0 + h + 0.38, wn + 1.2, 0.4, "Native capture, cropped", size=15, color=MUTED)
yb = 8.75
rows = [["Signal", "Hex", "Raw", "Value"],
        ["temperature_out_q8", "01A72h", "6770", "26.4453125 °C"],
        ["direction_angle_out_q8", "00570h", "1392", "5.4375°"]]
table(s, 1.12, yb, [4.0, 1.7, 1.4, 2.6], rows, rowh=0.58, size=17, mono_cols=(0, 1, 2))
rect(s, 11.4, yb, 7.5, 1.74, WHITE, GREY, 1)
text(s, 11.65, yb + 0.12, 7.05, 1.6, [[("Replay: ", {"bold": True}), ("128 frames → 104 forecasts, all matching.", {})],
                                     [("Timing: ", {"bold": True}), ("41 acquisition intervals = the RTL's 40-cycle post-edge latency.", {})],
                                     [("Separately instrumented build · 512 samples at 20 ns · full view: B6", {"color": MUTED, "size": 15})]],
     size=16, spacing=6)
page(s, 15)
notes(s, "Timing: 12:00–13:00.",
      "This is the native SignalTap capture from the board, from a separately instrumented build: 512 samples at 20 ns. The input buses change when the frame is accepted at sample 215, and forecast_valid pulses at sample 256.",
      "Decoding the captured buses: temperature_out_q8 is 01A72 hex, 6770 raw, 26.4453125 °C; the angle is 570 hex, 1392 raw, 5.4375 degrees. These match the C++ reference for that frame.",
      "SignalTap sees 41 sample intervals between the two events, because it samples before the clock edge; the RTL schedule defines 40 cycles after the accepting edge. Both describe the same transaction.",
      "Separately, the full replay sent 128 frames and checked 104 forecasts, all matching.",
      "Sources: docs/reports/defense_session/screenshots/weather_speed_signaltap_detail.png; SIGNALTAP_CAPTURE_CHECK.json; signaltap/weather_speed.stp and weather_speed_decoded.csv; weather_speed_physical_replay.txt.")

# 16  Scope ---------------------------------------------------------------------------------------------------------
s = new_slide()
edge(s)
header(s, "Scope and limitations", "What our evidence supports, and what it does not")
colx, colw = [1.12, 10.3], 8.6
heads = [("WHAT WE SHOW", ORANGE, "✓"), ("WHAT WE DO NOT CLAIM", INK, "✕")]
items = [["Five quantities forecast 3 h ahead from recorded hourly frames",
          "Bit-exact agreement with the C++ reference in RTL, the core netlist and on the board",
          "50 MHz operation, 40-cycle latency, 23-cycle initiation interval",
          "Lower 2025 test MAE than persistence and same-hour-yesterday"],
         ["Training on the FPGA, live sensors, or other sites and years",
          "Rainfall probability, or LED / LCD output",
          "A measured Fmax or power: 79.74 MHz is a static estimate",
          "Timing simulation of the full JTAG transport (SDF covers the core)"]]
for c in range(2):
    label_bar(s, colx[c], 3.2, colw, 0.85, heads[c][0], size=28, fill=heads[c][1])
    for i, it in enumerate(items[c]):
        y = 4.3 + i * 1.02
        text(s, colx[c], y, 0.6, 0.6, heads[c][2], size=28, bold=True, color=heads[c][1])
        text(s, colx[c] + 0.7, y + 0.02, colw - 0.8, 1.1, it, size=21)
label_bar(s, 1.12, 8.55, 4.0, 0.75, "NEXT STEPS", size=26, fill=BLACK)
nxt = ["Feed live observations instead of replayed frames", "Retrain and test on other sites and years",
       "Measure power and sweep the clock on the board", "Add a rainfall-probability output"]
for i, t_ in enumerate(nxt):
    x = 1.12 + i * 4.47
    num_square(s, x, 9.55, i + 1, size=0.5, fill=ORANGE, fs=16)
    text(s, x + 0.65, 9.5, 3.7, 0.95, t_, size=17)
page(s, 16)
notes(s, "Timing: 13:00–13:40.",
      "To be precise about our claims. We show five quantities forecast three hours ahead from recorded data, bit-exact agreement with the reference at three levels, 50 MHz operation with 40-cycle latency and a 23-cycle interval, and lower test error than the two baselines.",
      "We do not claim training on the FPGA, live sensor input, other locations, rainfall, or a display. The 79.74 MHz figure is an estimate, not a measurement, and we did not measure power. The SDF simulation covers the predictor core, not the full JTAG transport.",
      "Hourly forecasting does not need microsecond latency; the contribution is a verified hardware implementation and a clear schedule.")

# 17  Conclusion / thank you ----------------------------------------------------------------------------------------
s = new_slide(ORANGE)
text(s, 0.9, 0.6, 18, 2.6, "THANK YOU", size=190, font=TITLE, color=WHITE)
concl = ["Seven-lag fixed-point regression forecasts five weather quantities three hours ahead.",
         "Six parallel lanes and a CORDIC give a 0.80 µs latency and a 23-cycle interval at 50 MHz.",
         "The same C++ reference agrees with RTL, the post-fit core and 104 forecasts from the DE2 board."]
for i, c in enumerate(concl):
    y = 4.0 + i * 1.3
    rect(s, 0.95, y + 0.12, 0.28, 0.28, BLACK)
    text(s, 1.5, y, 16.5, 1.1, c, size=28, color=INK)
label_bar(s, 0.95, 8.55, 6.0, 1.15, "QUESTIONS?", size=54)
notes(s, "Timing: 13:40–14:10, then questions.",
      "To conclude: a seven-lag fixed-point regression forecasts five weather quantities three hours ahead; six lanes and a CORDIC give 0.80 microseconds latency with a 23-cycle interval at 50 MHz; and one C++ reference agrees with the RTL, the post-fit core and 104 forecasts from the physical board.",
      "Thank you. We are happy to take questions. Backup slides B1–B9 are hidden; open them from the slide navigator if needed.")

# =================================================================================================
# Hidden backups
def backup(code, title):
    s = new_slide(hidden=True)
    text(s, 1.12, 0.55, 6, 0.45, f"BACKUP {code}", size=24, font=LABEL, bold=True, color=ORANGE)
    text(s, 1.12, 1.05, 17.8, 1.0, title.upper(), size=50, font=TITLE, color=INK)
    return s


s = backup("B1", "Original temperature model")
label_bar(s, 1.12, 2.55, 17.76, 1.05, "T̂(t+3) = T(t−21) + a·[T(t) − T(t−24)] + b·[T(t) − T(t−3)] + c", size=30, font=BODY)
table(s, 1.12, 4.1, [3.0, 5.0], [["Parameter", "Fitted value"], ["a", "0.7454870439"], ["b", "0.0091494450"], ["c", "0.0011295817 °C"]],
      rowh=0.72, size=20, mono_cols=(1,))
text(s, 9.9, 4.1, 9.0, 3.0, "T(t−21) is the same hour yesterday relative to the target (t+3). a corrects with the daily change, b with the recent three-hour change, c is a constant.\n\nOne lane, signed 16-bit Q8.",
     size=20, spacing=8)
text(s, 1.12, 8.0, 17.8, 0.6, [[("Test MAE (2025, fixed point): ", {"bold": True}), ("0.538017 °C prototype → 0.507906 °C current weather temperature lane.", {})]], size=20)
notes(s, "Backup B1. Sources: software/models_cpp/model.json (a, b, c); docs/reports/temperature_metrics.csv (OLS_fixed test MAE 0.538017); versions/weather_v2/reports/metrics.csv (selected_fixed 0.507906).")

s = backup("B2", "Coefficients and a worked calculation")
rows = [["Lag (h)", "Input Q8", "Weight Q14", "Product"]]
inp = [7680, 7552, 7168, 6912, 6656, 7936, 7424]
for lag, x_, w_ in zip(lags, inp, win["weights_q14"]):
    rows.append([str(lag), str(x_), str(w_).replace("-", "−"), str(x_ * w_).replace("-", "−")])
table(s, 1.12, 2.5, [2.0, 2.6, 2.8, 3.6], rows, rowh=0.66, size=19, mono_cols=(0, 1, 2, 3))
tot = sum(x_ * w_ for x_, w_ in zip(inp, win["weights_q14"])) + win["bias_q8"][0] * 16384
rect(s, 12.6, 2.5, 6.3, 5.28, BG, GREY, 1)
text(s, 12.95, 2.75, 5.8, 4.9, [[("Bias: ", {"bold": True}), (f"{win['bias_q8'][0]} (Q8) × 16384", {"font": MONO})],
                                [("Sum S: ", {"bold": True}), (f"{tot}", {"font": MONO})],
                                [("⌊S / 16384⌋ = ", {"bold": True}), (f"{tot // 16384}", {"font": MONO, "color": ORANGE, "bold": True})],
                                [("Value: ", {"bold": True}), (f"{tot // 16384} / 256 = {tot // 16384 / 256:.5f} °C", {"font": MONO})],
                                [("Illustrative input set (temperature lane); deployed weights_q14 and bias_q8.", {"color": MUTED, "size": 16})]],
     size=19, spacing=14)
notes(s, "Backup B2. Temperature lane, deployed integers from versions/weather_v2/models/model.json (weights_q14, bias_q8). The inputs are an illustrative frame set for teaching the arithmetic. Floor division matches the arithmetic right shift of a signed value.")

s = backup("B3", "Full test metrics, 2025")
rows = [["Target", "Model MAE", "Model RMSE", "Latest-value MAE", "Same-hour-yesterday MAE"],
        ["Temperature (°C)", "0.507906", "0.730939", "2.080369", "0.832280"],
        ["Pressure (kPa)", "0.034600", "0.044638", "0.135167", "0.085775"],
        ["Humidity (percentage points)", "2.614292", "3.685767", "8.831186", "3.804237"],
        ["Wind speed (m/s)", "0.566878", "0.750218", "0.830494", "0.891217"],
        ["Direction (degrees)", "18.084598", "30.201056", "21.423810", "35.292273"]]
table(s, 1.12, 2.5, [5.0, 2.9, 2.9, 3.4, 3.56], rows, rowh=0.75, size=19, mono_cols=(1, 2, 3, 4), zebra=True)
text(s, 1.12, 7.25, 17.8, 1.4, "Model = selected_fixed (deployed fixed point). 8,757 scalar targets; direction: 8,593 targets with true wind speed ≥ 0.5 m/s, ideal atan2 of quantised components. CORDIC maximum conversion error 0.005635° (exhaustive).",
     size=18, color=MUTED)
notes(s, "Backup B3. Source: versions/weather_v2/reports/metrics.csv, split=test. Values rounded to six decimals.")

s = backup("B4", "Cycle schedule of one lane")
rows = [["Edge", "Lane state", "Operation"], ["N", "0 → 1", "Accept frame (valid ∧ ready), shift history, load aligned bias"],
        ["N + 1", "1", "Capture operand hist[lag 0]"], ["N + 2", "2", "Capture 36-bit product"], ["N + 3", "3", "Add product to 48-bit accumulator"],
        ["N + 4 … N + 21", "1 → 2 → 3", "Repeat for the remaining six taps"], ["N + 22", "4", "Shift >>> 14, limit, saturate, publish; lanes ready"],
        ["N + 23", "0", "Earliest next accepted frame"], ["N + 22 … N + 40", "CORDIC", "Angle unit runs; system forecast_valid at N + 40"]]
table(s, 1.12, 2.5, [3.4, 2.4, 12.0], rows, rowh=0.7, size=19, mono_cols=(0, 1))
text(s, 1.12, 9.0, 17.8, 1.0, "Synchronous active-low reset clears history eligibility and cancels pending work; a full new warm-up is required.",
     size=18, color=MUTED)
notes(s, "Backup B4. Source: versions/weather_v2/rtl/weather_ar_channel.v (state 0–4), wind_direction_cordic.v, weather_system_speed.v.")

s = backup("B5", "Native timing reports")
c1 = (516, 110, 1492, 330)
p, h1 = picture(s, f"{SHOTS}/weather_speed_timing_summary.png", 1.12, 2.5, 11.0, crop=c1, size=(2448, 1378))
rect(s, 1.12, 2.5, 11.0, h1, None, MIDGREY, 1)
c2 = (516, 110, 1116, 200)
p, h2 = picture(s, f"{SHOTS}/weather_speed_fmax.png", 1.12, 2.5 + h1 + 0.5, 6.8, crop=c2, size=(2448, 1378))
rect(s, 1.12, 2.5 + h1 + 0.5, 6.8, h2, None, MIDGREY, 1)
text(s, 12.8, 2.5, 6.1, 4.5, [[("Physical test clock: ", {"bold": True}), ("50 MHz", {})], [("Setup slack: ", {"bold": True}), ("7.459 ns", {})],
                              [("Hold slack: ", {"bold": True}), ("0.215 ns", {})], [("Slow-model Fmax: ", {"bold": True}), ("79.74 MHz (estimate)", {})]],
     size=22, spacing=14)
text(s, 1.12, 9.7, 17.8, 0.6, "TimeQuest panels of the uninstrumented weather-speed JTAG build, cropped; no values changed.", size=16, color=MUTED)
notes(s, "Backup B5. Sources: docs/reports/defense_session/screenshots/weather_speed_timing_summary.png and weather_speed_fmax.png.")

s = backup("B6", "Original SignalTap acquisition")
p, h = picture(s, f"{SHOTS}/weather_speed_signaltap_waveform.png", 3.0, 2.3, 14.0)
rect(s, 3.0, 2.3, 14.0, h, None, MIDGREY, 1)
notes(s, "Backup B6. Unmodified full application view: docs/reports/defense_session/screenshots/weather_speed_signaltap_waveform.png. Acquisition file: signaltap/weather_speed.stp; decoded buses: signaltap/weather_speed_decoded.csv.")

s = backup("B7", "JTAG mailbox protocol")
steps = ["Stage payload with the old request bit", "Invert the request bit", "Wait for the acknowledgement toggle", "Read a stable probe word"]
for i, st in enumerate(steps):
    y = 2.55 + i * 0.95
    num_square(s, 1.12, y, i + 1, fill=ORANGE)
    text(s, 1.95, y, 6.6, 0.62, st, size=20, anchor="m")
rows = [["Bits", "Host → FPGA (128-bit source)"], ["0", "Request toggle, one change per frame"], ["1", "Reset / clear (level)"],
        ["109:2", "Six signed 18-bit Q8 channels"], ["127:110", "Reserved, zero"]]
table(s, 9.2, 2.5, [2.0, 7.7], rows, rowh=0.62, size=17, mono_cols=(0,))
rows = [["Bits", "FPGA → host (256-bit probe)"], ["107:0", "Six Q8 forecasts"], ["125:108", "Direction angle, degrees Q8"],
        ["143:128 · 159:144", "Accepted / forecast counters"], ["160 · 162 · 163", "Ack toggle · result valid · direction defined"],
        ["255:224", "Signature 46504741h"]]
table(s, 9.2, 5.85, [3.1, 6.6], rows, rowh=0.62, size=17, mono_cols=(0,))
text(s, 1.12, 6.6, 7.6, 2.5, "One outstanding request at a time. Warm-up requests are acknowledged without a forecast. The latest forecast stays latched until the next forecast or reset.",
     size=19, color=MUTED)
notes(s, "Backup B7. Source: hardware/jtag/README.md (source and probe field tables); hardware/jtag/jtag_mailbox.v; scripts/replay_jtag.tcl.")

# B8  Published FPGA predictors (moved from the main talk) ------------------------------------------------------------------------------------------
s = backup("B8", "Published FPGA predictors")
rows = [["Design", "Task", "Device · arithmetic", "Resources", "Timing"],
        [[("This work", {"bold": True})], "5 quantities, 6 lanes × 7 taps", "Cyclone II EP2C35 · 18-bit fixed", "6,253 LEs · 12 × 9-bit mult.", "0.80 µs RTL latency at 50 MHz board clock"],
        [[("Vásquez et al. 2013", {"bold": True})], "Temperature, MLP network", "Xilinx · fixed point", "not in abstract", "74 ns max. delay (abstract)"],
        [[("Ferreira et al. 2019", {"bold": True})], "Linear-regression fit + 8 predictions", "Cyclone IV EP4CE115 · 32-bit fixed", "8% of 114,480 LEs · 89% of 532 mult.", "“one clock cycle”, no Fmax"],
        [[("Silva et al. 2022", {"bold": True})], "Rolling linear-regression predictor", "Virtex-6 · 32-bit float", "3,440 LUTs · 9 mult.", "40.25 ns processing (synthesis)"],
        [[("Royer et al. 2011", {"bold": True})], "Block linear-regression fit", "Xilinx DSP48E · fixed point", "66 slices · 5 DSP48E", "458 MHz Fmax (estimate)"]]
table(s, 1.12, 2.5, [3.3, 3.75, 3.65, 3.45, 3.65], rows, rowh=1.0, size=17, highlight_rows=(1,))
text(s, 1.12, 8.75, 17.8, 0.9, "LEs, LUTs and slices are different units, and the timing evidence ranges from board tests to estimates: context, not a ranking. Citations: backup B9.",
     size=17, color=MUTED)
notes(s, "Backup B8, for questions about related work.",
      "For context, four published FPGA predictors. Vásquez et al. built a temperature predictor with a neural network on a Xilinx FPGA and report 74 ns maximum delay — we only had access to the abstract. The other three implement linear regression: Ferreira et al. on a DE2-115, Silva et al. on Virtex-6 in floating point, Royer et al. with an estimated 458 MHz.",
      "We do not rank these: vendors count resources in different units, the tasks differ, and only some report measured timing. What sets ours apart is the scope — five quantities including a circular one — and the chain of evidence down to the physical board.",
      "Full citations and DOIs: backup B9; details in docs/specs/ols_fpga_literature_review.md.")

s = backup("B9", "Sources and credits")
groups = [("Model and evaluation", "versions/weather_v2/models/model.json · versions/weather_v2/reports/metrics.csv · versions/weather_v2/data/weather.csv · software/models_cpp/model.json · software/benchmarks/"),
          ("Hardware", "versions/weather_v2/rtl/*.v · versions/weather_v2/tb/tb_weather.sv · weather_reference.cpp · hardware/jtag/"),
          ("Evidence", "docs/reports/JTAG_IMPLEMENTATION_REPORT.md · docs/reports/weather_speed_modelsim_timing.json · docs/reports/defense_session/ (screenshots, replay log, SignalTap)"),
          ("Related work", "Vásquez et al. 2013, doi:10.1007/s12559-012-9158-z · Ferreira et al. 2019, doi:10.1145/3338852.3339853 · Silva et al. 2022, doi:10.3390/s22093556 · Royer et al., DCIS 2011"),
          ("Template", "“Automotive Training Center” by SlidesCarnival (slidescarnival.com), CC BY 4.0; adapted, stock photos removed")]
for i, (h1, h2) in enumerate(groups):
    y = 2.6 + i * 1.65
    seg(s, 1.12, y - 0.2, 18.9, y - 0.2, GREY, 1)
    text(s, 1.12, y, 4.2, 0.5, h1, size=24, bold=True, color=ORANGE)
    text(s, 5.5, y, 13.4, 1.4, h2, size=20)
notes(s, "Backup B9. Template credit as required by the CC BY 4.0 licence: https://www.slidescarnival.com/template/automotive-training-center/171796")

# ---------- sections ---------------------------------------------------------------------------------
P14 = "http://schemas.microsoft.com/office/powerpoint/2010/main"
pres_el = prs.part._element
ids = [sid.get("id") for sid in prs.slides._sldIdLst]
extLst = pres_el.find(qn("p:extLst"))
if extLst is None:
    extLst = etree.SubElement(pres_el, qn("p:extLst"))
for e in extLst.findall(qn("p:ext")):
    if e.get("uri") == "{521415D9-36F7-43E2-AB2F-B90AF26B5E84}":
        extLst.remove(e)
ext = etree.Element(qn("p:ext"), uri="{521415D9-36F7-43E2-AB2F-B90AF26B5E84}")
sl = etree.SubElement(ext, f"{{{P14}}}sectionLst", nsmap={"p14": P14})
for name, part in (("Talk", ids[:17]), ("Backup", ids[17:])):
    sec = etree.SubElement(sl, f"{{{P14}}}section", name=name, id="{" + str(uuid.uuid4()).upper() + "}")
    lst = etree.SubElement(sec, f"{{{P14}}}sldIdLst")
    for i in part:
        etree.SubElement(lst, f"{{{P14}}}sldId", id=i)
extLst.insert(0, ext)

prs.core_properties.title = "Weather forecasting on FPGA — final defense"
prs.core_properties.subject = "CE436 Discrete-Time Signal Processing"
prs.save(OUT)
print("saved", OUT, len(prs.slides), "slides")
