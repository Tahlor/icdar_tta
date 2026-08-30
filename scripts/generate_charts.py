#!/usr/bin/env python3
"""Generate the offline C1-C9 presentation charts using only the stdlib.

The committed CSV files are the only numeric inputs.  SVG uses native vector
text and primitives.  PNG uses the deterministic bitmap renderer below.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import math
import pathlib
import struct
import zlib

WIDTH, HEIGHT = 1200, 675
BG = "#f8fafc"
INK = "#172033"
MUTED = "#596579"
GRID = "#d9e0ea"
BLUE = "#2563eb"
ORANGE = "#e87924"
GREEN = "#17875d"
RED = "#c23b4a"
PURPLE = "#7557b8"
TEAL = "#168a99"
PALE_BLUE = "#dbeafe"
PALE_ORANGE = "#ffedd5"
PALE_RED = "#fee2e2"
PALE_GREEN = "#dcfce7"

BASENAMES = (
    "01_useful_diversity",
    "02_effective_sample_size",
    "03_precision_coverage",
    "04_cost_review_frontier",
    "05_shift_periodicity",
    "06_cross_model_coverage",
    "07_augmentation_contribution",
    "08_ensemble_size",
    "09_failure_examples",
)
TABLE_MAP = {
    BASENAMES[0]: ("strategy_summary.csv",),
    BASENAMES[1]: ("error_correlation_summary.csv",),
    BASENAMES[2]: ("precision_coverage.csv",),
    BASENAMES[3]: ("cost_by_run.csv", "review_frontier.csv"),
    BASENAMES[4]: ("shift_agreement.csv",),
    BASENAMES[5]: ("cross_model_operating_points.csv",),
    BASENAMES[6]: ("augmentation_contribution.csv",),
    BASENAMES[7]: ("ensemble_size.csv",),
    BASENAMES[8]: ("failure_examples.csv",),
}
TAKEAWAYS = {
    BASENAMES[0]: "Useful ensembles need informative members that make different mistakes; modern and historical coordinates are labelled by source.",
    BASENAMES[1]: "Adding correlated samples has rapidly diminishing informational value.",
    BASENAMES[2]: "Grid Warp can be useful as a selective confidence generator, but raw agreement is not a calibrated probability.",
    BASENAMES[3]: "The production objective is fewer human reviews for known quality; modern usage is measured, but pricing is unavailable.",
    BASENAMES[4]: "Transcription agreement exhibits periodic sensitivity to image alignment, consistent with but not proof of patch or grid effects.",
    BASENAMES[5]: "Modern transfer is measured at a fixed descriptive precision target, with unresolved or unavailable routes shown explicitly.",
    BASENAMES[6]: "Historical validation selection frequency describes which families appeared often; it does not establish causal contribution.",
    BASENAMES[7]: "Historical aggregates plus modern points show diminishing gains with more members under explicit denominators.",
    BASENAMES[8]: "Qualitative failure examples remain blocked until stable redacted lineage and release-authorized crops exist.",
}

# Compact 5x7 bitmap alphabet for deterministic PNG labels.
_FONT_ROWS = {
    " ": ("00000",) * 7,
    "A": ("01110","10001","10001","11111","10001","10001","10001"),
    "B": ("11110","10001","10001","11110","10001","10001","11110"),
    "C": ("01111","10000","10000","10000","10000","10000","01111"),
    "D": ("11110","10001","10001","10001","10001","10001","11110"),
    "E": ("11111","10000","10000","11110","10000","10000","11111"),
    "F": ("11111","10000","10000","11110","10000","10000","10000"),
    "G": ("01111","10000","10000","10111","10001","10001","01111"),
    "H": ("10001","10001","10001","11111","10001","10001","10001"),
    "I": ("11111","00100","00100","00100","00100","00100","11111"),
    "J": ("00111","00010","00010","00010","10010","10010","01100"),
    "K": ("10001","10010","10100","11000","10100","10010","10001"),
    "L": ("10000","10000","10000","10000","10000","10000","11111"),
    "M": ("10001","11011","10101","10101","10001","10001","10001"),
    "N": ("10001","11001","10101","10011","10001","10001","10001"),
    "O": ("01110","10001","10001","10001","10001","10001","01110"),
    "P": ("11110","10001","10001","11110","10000","10000","10000"),
    "Q": ("01110","10001","10001","10001","10101","10010","01101"),
    "R": ("11110","10001","10001","11110","10100","10010","10001"),
    "S": ("01111","10000","10000","01110","00001","00001","11110"),
    "T": ("11111","00100","00100","00100","00100","00100","00100"),
    "U": ("10001","10001","10001","10001","10001","10001","01110"),
    "V": ("10001","10001","10001","10001","10001","01010","00100"),
    "W": ("10001","10001","10001","10101","10101","10101","01010"),
    "X": ("10001","10001","01010","00100","01010","10001","10001"),
    "Y": ("10001","10001","01010","00100","00100","00100","00100"),
    "Z": ("11111","00001","00010","00100","01000","10000","11111"),
    "0": ("01110","10001","10011","10101","11001","10001","01110"),
    "1": ("00100","01100","00100","00100","00100","00100","01110"),
    "2": ("01110","10001","00001","00010","00100","01000","11111"),
    "3": ("11110","00001","00001","01110","00001","00001","11110"),
    "4": ("00010","00110","01010","10010","11111","00010","00010"),
    "5": ("11111","10000","10000","11110","00001","00001","11110"),
    "6": ("01110","10000","10000","11110","10001","10001","01110"),
    "7": ("11111","00001","00010","00100","01000","01000","01000"),
    "8": ("01110","10001","10001","01110","10001","10001","01110"),
    "9": ("01110","10001","10001","01111","00001","00001","01110"),
    ".": ("00000","00000","00000","00000","00000","00110","00110"),
    ",": ("00000","00000","00000","00000","00110","00110","00100"),
    ":": ("00000","00110","00110","00000","00110","00110","00000"),
    ";": ("00000","00110","00110","00000","00110","00110","00100"),
    "-": ("00000","00000","00000","11111","00000","00000","00000"),
    "_": ("00000","00000","00000","00000","00000","00000","11111"),
    "/": ("00001","00010","00010","00100","01000","01000","10000"),
    "(": ("00010","00100","01000","01000","01000","00100","00010"),
    ")": ("01000","00100","00010","00010","00010","00100","01000"),
    "[": ("01110","01000","01000","01000","01000","01000","01110"),
    "]": ("01110","00010","00010","00010","00010","00010","01110"),
    "%": ("11001","11010","00010","00100","01000","01011","10011"),
    "+": ("00000","00100","00100","11111","00100","00100","00000"),
    "=": ("00000","11111","00000","11111","00000","00000","00000"),
    "<": ("00010","00100","01000","10000","01000","00100","00010"),
    ">": ("01000","00100","00010","00001","00010","00100","01000"),
    "?": ("01110","10001","00001","00010","00100","00000","00100"),
    "|": ("00100","00100","00100","00100","00100","00100","00100"),
    "'": ("00100","00100","00000","00000","00000","00000","00000"),
}


def _rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))


class Canvas:
    def __init__(self, chart_id: str, title: str, takeaway: str, sources: tuple[str, ...], limitations: list[str]):
        self.chart_id = chart_id
        self.title_value = title
        self.takeaway = takeaway
        self.sources = sources
        self.limitations = limitations
        self.ops: list[tuple] = []
        self.rect(0, 0, WIDTH, HEIGHT, BG)

    def line(self, x1, y1, x2, y2, color=INK, width=1, dash=""):
        self.ops.append(("line", float(x1), float(y1), float(x2), float(y2), color, int(width), dash))

    def rect(self, x, y, w, h, fill="none", stroke="none", width=1):
        self.ops.append(("rect", float(x), float(y), float(w), float(h), fill, stroke, int(width)))

    def circle(self, x, y, r, fill=BLUE, stroke="none", width=1):
        self.ops.append(("circle", float(x), float(y), float(r), fill, stroke, int(width)))

    def polyline(self, points, color=BLUE, width=2, dash=""):
        self.ops.append(("polyline", tuple((float(x), float(y)) for x, y in points), color, int(width), dash))

    def polygon(self, points, fill=PALE_BLUE, stroke="none", width=1):
        self.ops.append(("polygon", tuple((float(x), float(y)) for x, y in points), fill, stroke, int(width)))

    def text(self, x, y, value, size=16, color=INK, anchor="start", weight="normal"):
        self.ops.append(("text", float(x), float(y), str(value), int(size), color, anchor, weight))

    def save(self, svg_path: pathlib.Path, png_path: pathlib.Path):
        svg_path.parent.mkdir(parents=True, exist_ok=True)
        metadata = {
            "chart_id": self.chart_id,
            "dimensions": [WIDTH, HEIGHT],
            "numeric_inputs": list(self.sources),
            "renderer": "python-standard-library-svg-and-deterministic-bitmap-png",
            "takeaway": self.takeaway,
            "limitations": self.limitations,
        }
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img">',
            f"<title>{html.escape(self.title_value)}</title>",
            f"<desc>{html.escape(self.takeaway)}</desc>",
            f"<metadata>{html.escape(json.dumps(metadata, sort_keys=True, separators=(',', ':')))}</metadata>",
        ]
        for op in self.ops:
            kind = op[0]
            if kind == "line":
                _, x1, y1, x2, y2, color, width, dash = op
                d = f' stroke-dasharray="{dash}"' if dash else ""
                lines.append(f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{color}" stroke-width="{width}"{d}/>' )
            elif kind == "rect":
                _, x, y, w, h, fill, stroke, width = op
                lines.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')
            elif kind == "circle":
                _, x, y, r, fill, stroke, width = op
                lines.append(f'<circle cx="{x:g}" cy="{y:g}" r="{r:g}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')
            elif kind in ("polyline", "polygon"):
                _, points, color, stroke, width = op if kind == "polygon" else (op[0], op[1], "none", op[2], op[3])
                dash = "" if kind == "polygon" else op[4]
                pts = " ".join(f"{x:g},{y:g}" for x, y in points)
                d = f' stroke-dasharray="{dash}"' if dash else ""
                lines.append(f'<{kind} points="{pts}" fill="{color}" stroke="{stroke}" stroke-width="{width}"{d}/>' )
            elif kind == "text":
                _, x, y, value, size, color, anchor, weight = op
                lines.append(f'<text x="{x:g}" y="{y:g}" fill="{color}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{html.escape(value)}</text>')
        lines.append("</svg>")
        svg_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        self._save_png(png_path)

    def _save_png(self, path: pathlib.Path):
        bg = _rgb(BG)
        pixels = bytearray(bg * (WIDTH * HEIGHT))

        def pixel(x, y, color):
            x, y = int(x), int(y)
            if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                i = (y * WIDTH + x) * 3
                pixels[i:i+3] = bytes(color)

        def disk(cx, cy, radius, color):
            radius = max(0, int(radius))
            for yy in range(int(cy) - radius, int(cy) + radius + 1):
                for xx in range(int(cx) - radius, int(cx) + radius + 1):
                    if (xx - cx) ** 2 + (yy - cy) ** 2 <= radius ** 2:
                        pixel(xx, yy, color)

        def line(x1, y1, x2, y2, color, width=1, dashed=False):
            dx, dy = x2 - x1, y2 - y1
            steps = max(1, int(max(abs(dx), abs(dy))))
            for i in range(steps + 1):
                if dashed and (i // 7) % 2:
                    continue
                t = i / steps
                disk(round(x1 + dx * t), round(y1 + dy * t), max(0, width // 2), color)

        def fill_rect(x, y, w, h, color):
            x0, x1 = max(0, int(x)), min(WIDTH, int(math.ceil(x + w)))
            y0, y1 = max(0, int(y)), min(HEIGHT, int(math.ceil(y + h)))
            row = bytes(color) * max(0, x1 - x0)
            for yy in range(y0, y1):
                i = (yy * WIDTH + x0) * 3
                pixels[i:i+len(row)] = row

        def fill_polygon(points, color):
            if not points:
                return
            lo = max(0, int(min(y for _, y in points)))
            hi = min(HEIGHT - 1, int(max(y for _, y in points)))
            for yy in range(lo, hi + 1):
                intersections = []
                for i, (x1, y1) in enumerate(points):
                    x2, y2 = points[(i + 1) % len(points)]
                    if y1 == y2:
                        continue
                    if min(y1, y2) <= yy < max(y1, y2):
                        intersections.append(x1 + (yy - y1) * (x2 - x1) / (y2 - y1))
                intersections.sort()
                for i in range(0, len(intersections) - 1, 2):
                    fill_rect(intersections[i], yy, intersections[i+1] - intersections[i] + 1, 1, color)

        def text(x, y, value, size, color, anchor):
            scale = max(1, min(4, size // 7))
            value = value.upper()
            char_w = 6 * scale
            total = max(0, len(value) * char_w - scale)
            if anchor == "middle":
                x -= total / 2
            elif anchor == "end":
                x -= total
            y -= 7 * scale
            for ch in value:
                rows = _FONT_ROWS.get(ch, _FONT_ROWS["?"])
                for ry, bits in enumerate(rows):
                    for rx, bit in enumerate(bits):
                        if bit == "1":
                            fill_rect(x + rx * scale, y + ry * scale, scale, scale, color)
                x += char_w

        for op in self.ops:
            kind = op[0]
            if kind == "line":
                _, x1, y1, x2, y2, color, width, dash = op
                line(x1, y1, x2, y2, _rgb(color), width, bool(dash))
            elif kind == "rect":
                _, x, y, w, h, fill, stroke, width = op
                if fill != "none": fill_rect(x, y, w, h, _rgb(fill))
                if stroke != "none":
                    line(x, y, x+w, y, _rgb(stroke), width); line(x+w, y, x+w, y+h, _rgb(stroke), width)
                    line(x+w, y+h, x, y+h, _rgb(stroke), width); line(x, y+h, x, y, _rgb(stroke), width)
            elif kind == "circle":
                _, x, y, r, fill, stroke, width = op
                if fill != "none": disk(x, y, r, _rgb(fill))
                if stroke != "none":
                    for a in range(0, 360, 2): pixel(x+r*math.cos(math.radians(a)), y+r*math.sin(math.radians(a)), _rgb(stroke))
            elif kind == "polyline":
                _, points, color, width, dash = op
                for a, b in zip(points, points[1:]): line(*a, *b, _rgb(color), width, bool(dash))
            elif kind == "polygon":
                _, points, fill, stroke, width = op
                if fill != "none": fill_polygon(points, _rgb(fill))
                if stroke != "none":
                    for a, b in zip(points, points[1:] + points[:1]): line(*a, *b, _rgb(stroke), width)
            elif kind == "text":
                _, x, y, value, size, color, anchor, _weight = op
                text(x, y, value, size, _rgb(color), anchor)

        raw = b"".join(b"\x00" + bytes(pixels[y*WIDTH*3:(y+1)*WIDTH*3]) for y in range(HEIGHT))
        def chunk(kind, data):
            return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)
        png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0))
               + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
        path.write_bytes(png)


class Axes:
    def __init__(self, c: Canvas, x, y, w, h, xmin, xmax, ymin, ymax):
        self.c, self.x, self.y, self.w, self.h = c, x, y, w, h
        self.xmin, self.xmax, self.ymin, self.ymax = xmin, xmax, ymin, ymax

    def px(self, value): return self.x + (value - self.xmin) / (self.xmax - self.xmin) * self.w
    def py(self, value): return self.y + self.h - (value - self.ymin) / (self.ymax - self.ymin) * self.h

    def draw(self, xticks, yticks, xlabel, ylabel, xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}"):
        for v in yticks:
            yy = self.py(v); self.c.line(self.x, yy, self.x+self.w, yy, GRID)
            self.c.text(self.x-10, yy+5, yfmt(v), 13, MUTED, "end")
        for v in xticks:
            xx = self.px(v); self.c.line(xx, self.y, xx, self.y+self.h, GRID)
            self.c.text(xx, self.y+self.h+22, xfmt(v), 13, MUTED, "middle")
        self.c.line(self.x, self.y, self.x, self.y+self.h, INK, 2)
        self.c.line(self.x, self.y+self.h, self.x+self.w, self.y+self.h, INK, 2)
        self.c.text(self.x+self.w/2, self.y+self.h+52, xlabel, 16, INK, "middle", "bold")
        self.c.text(self.x, self.y-12, ylabel, 15, INK, "start", "bold")


def rows(path: pathlib.Path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def number(row, key):
    value = row.get(key, "")
    return float(value) if value != "" else None


def heading(c: Canvas, title: str, subtitle: str):
    # Wrap long headings within the 1,200 px deterministic bitmap canvas.
    title_lines = wrap(title, 58)
    for i, line_value in enumerate(title_lines):
        c.text(55, 40 + i * 26, line_value, 21, INK, "start", "bold")
    subtitle_y = 72 + (len(title_lines) - 1) * 26
    for i, line_value in enumerate(wrap(subtitle, 86)):
        c.text(55, subtitle_y + i * 20, line_value, 15, MUTED)


def wrap(value: str, width: int):
    words, lines, current = value.split(), [], []
    for word in words:
        if current and len(" ".join(current + [word])) > width:
            lines.append(" ".join(current)); current = [word]
        else:
            current.append(word)
    if current: lines.append(" ".join(current))
    return lines


def footer(c: Canvas, text_value: str):
    c.text(55, 654, text_value, 12, MUTED)


def short_warp(name: str):
    std = name.rsplit("std", 1)[-1]
    std = {"15": "1.5", "2": "2", "3": "3"}.get(std, std)
    if name == "shift_only": return "Pad/shift"
    if name.startswith("dont_warp"): return "GW masked " + std
    if name.startswith("warp_all"): return "GW all " + std
    return "GW hw-only " + std


def chart_1(data, out):
    valid = [r for r in data if number(r, "individual_cer") is not None and number(r, "error_correlation") is not None]
    categories = [r for r in data if number(r, "individual_cer") is None]
    c = Canvas(BASENAMES[0], "Useful diversity: historical and modern coordinates", TAKEAWAYS[BASENAMES[0]], TABLE_MAP[BASENAMES[0]],
               ["Only WARP per-condition rows contain both individual CER and error correlation.", "v7 category rows contain consensus CER only and are not plotted as individual metrics."])
    heading(c, "Useful diversity: accuracy and different mistakes", TAKEAWAYS[BASENAMES[0]])
    y_values = [number(r, "individual_cer") for r in valid]
    ymin = max(0.0, min(y_values) - .005) if y_values else .0
    ymax = min(1.0, max(y_values) + .005) if y_values else 1.0
    y_ticks = [ymin + (ymax - ymin) * i / 4 for i in range(5)]
    a = Axes(c, 90, 145, 690, 410, .60, 1.00, ymin, ymax)
    a.draw([.6,.7,.8,.9,1.0], y_ticks, "Mean pairwise field-error correlation (lower is more diverse)", "Mean individual CER (lower is better)", lambda v:f"{v:.1f}", lambda v:f"{v:.2f}")
    label_rows = {min(valid, key=lambda q: number(q, "error_correlation"))["strategy"], "shift_only"}
    for r in valid:
        x, y = a.px(number(r,"error_correlation")), a.py(number(r,"individual_cer"))
        is_modern = not str(r["model_id"]).startswith("models/")
        color = (PURPLE if is_modern else ORANGE) if r["family"] == "pad" else (TEAL if is_modern else BLUE)
        c.circle(x, y, 7, color, "#ffffff", 2)
        if r["strategy"] in label_rows:
            c.text(x + (8 if x < 700 else -8), y-9, short_warp(r["strategy"]), 11, INK, "start" if x < 700 else "end")
    c.text(105, 166, f"MEASURED CONDITIONS (n={len(valid)} rows; historical + modern)", 12, BLUE, "start", "bold")
    c.rect(815, 145, 335, 410, "#ffffff", GRID, 1)
    c.text(835, 174, "V7 CATEGORY CONSENSUS", 16, PURPLE, "start", "bold")
    c.text(835, 196, "Not individual CER; x coordinate unavailable", 12, MUTED)
    c.text(835, 214, "Plot: historical blue/orange; modern teal/purple", 10, MUTED)
    wanted = [("Baseline",1),("Pad",10),("Grid Warp",10),("Resize",10),("Temperature = 1.0",10)]
    selected = []
    for name, n in wanted:
        match = next((r for r in categories if r["strategy"] == name and int(r["n_samples"]) == n), None)
        if match: selected.append(match)
    for i, r in enumerate(selected):
        yy = 250 + i*48
        c.text(835, yy, f"{r['strategy']} (n={r['n_samples']})", 13, INK)
        c.text(835, yy+18, f"consensus CER {100*number(r,'consensus_cer'):.2f}%", 11, PURPLE)
        c.line(835, yy+28, 1128, yy+28, GRID)
    c.rect(835, 500, 293, 35, PALE_ORANGE, "none")
    c.text(849, 514, "LIMITATION", 10, ORANGE, "start", "bold")
    c.text(849, 529, "No shared x/y metric across sources", 10, INK)
    footer(c, "MEASURED aggregate rows | Historical and modern denominators; metric roles preserved from CSV notes")
    c.save(out/(BASENAMES[0]+".svg"), out/(BASENAMES[0]+".png"))


def chart_2(data, out):
    measured = [r for r in data if number(r,"error_correlation") is not None]
    blocked = [r for r in data if number(r,"error_correlation") is None]
    c = Canvas(BASENAMES[1], "Stylized effective sample size", TAKEAWAYS[BASENAMES[1]], TABLE_MAP[BASENAMES[1]],
               ["The N=10 curve is theoretical intuition, not measured effective sample count.", "Family-level Grid Warp and Resize correlations are blocked in the source table."])
    heading(c, "Ten calls can behave like barely more than one", TAKEAWAYS[BASENAMES[1]])
    a = Axes(c, 90, 145, 760, 420, 0, 1, 1, 10)
    a.draw([0,.2,.4,.6,.8,1], [1,2,4,6,8,10], "Pairwise error correlation rho", "Stylized N_eff for N=10", lambda v:f"{v:.1f}")
    curve=[]
    for i in range(101):
        rho=i/100; neff=10/(1+9*rho); curve.append((a.px(rho),a.py(neff)))
    c.polyline(curve, PURPLE, 4)
    c.text(390, 176, "THEORETICAL: N_eff = 10 / (1 + 9 rho)", 14, PURPLE, "start", "bold")
    for r in measured:
        rho=number(r,"error_correlation"); projected=10/(1+9*rho)
        color=ORANGE if r["family"]=="pad" else BLUE
        c.circle(a.px(rho),a.py(projected),6,color,"#ffffff",2)
    lo=min(measured,key=lambda r:number(r,"error_correlation")); pad=next(r for r in measured if r["family"]=="pad")
    for r,dy in ((lo,-12),(pad,24)):
        rho=number(r,"error_correlation"); projected=10/(1+9*rho)
        c.text(a.px(rho)-5,a.py(projected)+dy,f"{short_warp(r['strategy'])}: rho={rho:.3f}",12,INK,"end")
    c.rect(885,145,265,420,"#ffffff",GRID)
    c.text(905,176,"EMPIRICAL OVERLAY",15,BLUE,"start","bold")
    c.text(905,199,f"{len(measured)} measured",13,INK)
    c.text(905,219,"historical/modern correlations",13,INK)
    c.text(905,252,"Points are projected onto",12,MUTED)
    c.text(905,270,"the N=10 theory curve.",12,MUTED)
    c.rect(905,310,225,126,PALE_RED,"none")
    c.text(920,334,"BLOCKED FAMILY ROWS",13,RED,"start","bold")
    for i,r in enumerate(blocked): c.text(920,360+i*25,f"{r['strategy']}: no rho",12,INK)
    c.text(920,420,"No prose values promoted",11,MUTED)
    footer(c,"THEORETICAL curve + MEASURED correlations | Historical ~4,920 fields; modern raw six-name 3,718 cells")
    c.save(out/(BASENAMES[1]+".svg"), out/(BASENAMES[1]+".png"))


def chart_3(data, out):
    c = Canvas(BASENAMES[2], "Raw-agreement precision and coverage", TAKEAWAYS[BASENAMES[2]], TABLE_MAP[BASENAMES[2]],
               ["Historical and modern rows retain their denominator status in the CSV.", "Intervals are two-sided 95% Wilson bounds supplied by the CSV.", "Raw consensus character agreement is not calibrated probability."])
    heading(c,"Raw agreement can triage review",TAKEAWAYS[BASENAMES[2]])
    numeric = [r for r in data if number(r,"coverage") is not None and number(r,"precision") is not None]
    ymin = max(0.0, min(number(r,"precision") for r in numeric) - .03) if numeric else .60
    ymax = min(1.0, max(number(r,"precision") for r in numeric) + .02) if numeric else 1.0
    if ymax - ymin < .10:
        ymin, ymax = max(0.0, ymin - .05), min(1.0, ymax + .05)
    a=Axes(c,90,145,850,420,0.0,1.0,ymin,ymax)
    yticks=[ymin+(ymax-ymin)*i/4 for i in range(5)]
    a.draw([0,.25,.5,.75,1],yticks,"Automatic coverage (accepted fields / source denominator)","Accepted-field precision",lambda v:f"{100*v:.0f}%",lambda v:f"{100*v:.0f}%")
    colors={"Grid Warp":BLUE,"Pad":ORANGE,"Resize":GREEN,"unchanged_3":MUTED,"visual_mixed_6":PURPLE,"all_views_9":TEAL,"single":RED}
    series_keys = sorted({
        (r["model_id"], r["strategy"])
        for r in data
        if number(r, "coverage") is not None and number(r, "precision") is not None
    })
    strategies = sorted({strategy for _, strategy in series_keys})
    for model_id, strategy in series_keys:
        # Keep each model's curve separate. Sorting only by strategy would
        # connect historical and modern rows into a fictitious trajectory.
        series=sorted((r for r in data if r["model_id"]==model_id and r["strategy"]==strategy),key=lambda r:number(r,"coverage"))
        upper=[(a.px(number(r,"coverage")),a.py(number(r,"precision_ci_high"))) for r in series]
        lower=[(a.px(number(r,"coverage")),a.py(number(r,"precision_ci_low"))) for r in reversed(series)]
        c.polygon(upper+lower,{"Grid Warp":"#dbeafe","Pad":"#ffedd5","Resize":"#dcfce7","unchanged_3":"#eef2f7","visual_mixed_6":"#ede9fe","all_views_9":"#cffafe","single":"#fee2e2"}.get(strategy,"#f1f5f9"))
        pts=[(a.px(number(r,"coverage")),a.py(number(r,"precision"))) for r in series]
        dash = "8,5" if str(model_id).startswith("gemini-") else ""
        c.polyline(pts,colors.get(strategy,BLUE),3,dash)
    for i,name in enumerate(strategies):
        x=955; y=183+i*35; c.line(x,y,x+32,y,colors[name],4); c.text(x+42,y+5,name,14,INK)
    caution_y=183+len(strategies)*35+25
    c.text(975,caution_y,"SHADED: 95% WILSON",12,MUTED,"start","bold")
    c.text(975,caution_y+20,"dashed = modern model",11,MUTED)
    c.rect(970,caution_y+35,180,115,PALE_ORANGE,"none")
    c.text(985,caution_y+60,"CAUTION",13,ORANGE,"start","bold")
    c.text(985,caution_y+84,"raw agreement",12,INK)
    c.text(985,caution_y+104,"not calibrated",12,INK)
    c.text(985,caution_y+128,"source denominators labelled",10,RED,"start","bold")
    footer(c,"RECOMPUTED historical + modern sweeps | Correct = normalized CER equals zero | Every distinct threshold plotted")
    c.save(out/(BASENAMES[2]+".svg"), out/(BASENAMES[2]+".png"))


def chart_4(cost_data, frontier, out):
    numeric=[r for r in frontier if number(r,"review_fields_per_1000") is not None]
    c=Canvas(BASENAMES[3],"Review frontier with blocked cost axis",TAKEAWAYS[BASENAMES[3]],TABLE_MAP[BASENAMES[3]],
             ["Historical usage/pricing is unavailable; modern usage is measured without a pricing snapshot.", "Only numeric review burden is rendered; no dollar coordinate is invented."])
    heading(c,"Human review is measurable; inference cost is not",TAKEAWAYS[BASENAMES[3]])
    c.rect(65,145,660,430,"#ffffff",GRID)
    c.text(90,178,"NUMERIC REVIEW BURDEN AT CSV TARGET",15,BLUE,"start","bold")
    maxv=1000
    for i,r in enumerate(numeric):
        value=number(r,"review_fields_per_1000"); y=246+i*90
        c.text(90,y-28,r["strategy"]+f" (n={r['n_samples']})",15,INK,"start","bold")
        c.rect(90,y-19,580,28,"#eef2f7","none")
        c.rect(90,y-19,580*value/maxv,28,BLUE,"none")
        c.text(655,y+2,f"{value:.1f} reviews / 1,000",13,INK,"end")
        c.text(90,y+30,f"coverage {100*number(r,'coverage'):.1f}% | observed precision {100*number(r,'observed_precision'):.2f}%",12,MUTED)
    for r in frontier:
        if r not in numeric:
            y=360+(0 if r["strategy"]=="Pad" else 52)
            c.rect(90,y-25,580,38,PALE_RED,"none")
            c.text(105,y,f"{r['strategy']}: target/cost coordinate blocked",13,RED,"start","bold")
    c.rect(760,145,390,430,PALE_ORANGE,ORANGE,2)
    c.text(790,183,"COST AXIS: BLOCKED",18,ORANGE,"start","bold")
    c.text(790,214,"Historical usage not located",14,INK)
    c.text(790,238,"Modern usage is measured",14,INK)
    c.text(790,262,"No pricing/cost snapshot",14,INK)
    c.line(790,292,1120,292,ORANGE,2,"8,6")
    c.text(790,320,f"Blocked run/model rows: {len(cost_data)}",13,INK)
    for i,r in enumerate(cost_data):
        c.text(790,348+i*31,r["model_id"],11,INK)
        c.text(1120,348+i*31,r["cost_status"].replace("_"," "),10,RED,"end")
    c.text(790,500,"NO DOLLARS INVENTED",15,RED,"start","bold")
    footer(c,"PARTIAL frontier | Descriptive target from CSV | Legacy/public v7 denominator: 3,682 fields; paper v9/v10 row target: 3,684")
    c.save(out/(BASENAMES[3]+".svg"),out/(BASENAMES[3]+".png"))


def chart_5(data,out):
    c=Canvas(BASENAMES[4],"Shift periodicity",TAKEAWAYS[BASENAMES[4]],TABLE_MAP[BASENAMES[4]],
             ["Agreement is a reported historical aggregate.", "The observed periodicity does not prove a proprietary architecture."])
    heading(c,"Alignment changes transcription agreement",TAKEAWAYS[BASENAMES[4]])
    a=Axes(c,90,145,850,420,-64,64,.74,1.01)
    a.draw([-64,-48,-32,-16,0,16,32,48,64],[.75,.80,.85,.90,.95,1],"Relative shift (pixels); guides every 16 px","Mean pairwise transcription agreement",lambda v:f"{int(v)}",lambda v:f"{v:.2f}")
    for v in range(-64,65,16): c.line(a.px(v),a.y,a.px(v),a.y+a.h,PURPLE,1,"5,5")
    colors={"horizontal":BLUE,"vertical":ORANGE}
    for direction in ("horizontal","vertical"):
        series=sorted((r for r in data if r["direction"]==direction),key=lambda r:number(r,"relative_shift_px"))
        pts=[(a.px(number(r,"relative_shift_px")),a.py(number(r,"agreement"))) for r in series]
        c.polyline(pts,colors[direction],3)
        for r in series:
            if r["is_multiple_of_16"]=="true": c.circle(a.px(number(r,"relative_shift_px")),a.py(number(r,"agreement")),4,colors[direction],"#ffffff",1)
    c.rect(975,160,175,120,"#ffffff",GRID)
    for i,name in enumerate(("horizontal","vertical")):
        y=194+i*35;c.line(993,y,1026,y,colors[name],4);c.text(1038,y+5,name,13,INK)
    c.text(985,325,"16-PIXEL GUIDES",13,PURPLE,"start","bold")
    c.text(985,350,"65 points/direction",12,INK)
    c.text(985,373,"-64 to +64 by 2 px",12,INK)
    c.rect(975,420,175,85,PALE_ORANGE,"none")
    c.text(990,445,"OBSERVATIONAL",12,ORANGE,"start","bold")
    c.text(990,468,"not architecture proof",11,INK)
    footer(c,"REPORTED historical aggregate | Zero is identical-view agreement | 130 source rows")
    c.save(out/(BASENAMES[4]+".svg"),out/(BASENAMES[4]+".png"))


def model_label(value):
    return value.replace("models/","")


def chart_6(data,out):
    c=Canvas(BASENAMES[5],"Cross-model auto-acceptance",TAKEAWAYS[BASENAMES[5]],TABLE_MAP[BASENAMES[5]],
             ["Operating points are descriptive rows at the predeclared target precision.", "Unavailable routes or targets remain explicit rather than being filled with estimates."])
    heading(c,"Cross-model transfer at a fixed precision target",TAKEAWAYS[BASENAMES[5]])
    models=[]
    for r in data:
        if r["model_id"] not in models: models.append(r["model_id"])
    strategies=("unchanged_3","Pad","Grid Warp","visual_mixed_6")
    c.text(70,158,"MODEL / EXACT ID",13,MUTED,"start","bold")
    for j,s in enumerate(strategies): c.text(565+j*140,158,s,12,MUTED,"middle","bold")
    for i,m in enumerate(models):
        y=205+i*94
        c.rect(55,y-30,1095,73,"#ffffff" if i%2==0 else "#f1f5f9","none")
        c.text(70,y,model_label(m),12,INK,"start","bold")
        model_rows=[r for r in data if r["model_id"]==m]
        for j,s in enumerate(strategies):
            x=565+j*140
            r=next((q for q in model_rows if q["strategy"]==s),None)
            if r and number(r,"coverage") is not None:
                c.circle(x,y-4,18,GREEN,"#ffffff",2)
                c.text(x,y+1,f"{100*number(r,'coverage'):.1f}%",11,"#ffffff","middle","bold")
                c.text(x,y+29,f"P={100*number(r,'observed_precision'):.2f}%",10,GREEN,"middle")
            elif r:
                c.rect(x-32,y-19,64,28,PALE_RED,RED,1)
                if r["evidence_status"]=="recomputed_historical_target_not_met":
                    label="NO POINT"
                elif r["evidence_status"]=="modern_measured_target_not_met":
                    label="TARGET NOT MET"
                else:
                    label="ROUTE BLOCKED"
                c.text(x,y+1,label,10,RED,"middle","bold")
            else:
                c.text(x,y,"-",14,MUTED,"middle")
    c.rect(55,585,1095,42,PALE_ORANGE,"none")
    numeric=sum(1 for r in data if number(r,"coverage") is not None)
    unavailable=sum(1 for r in data if number(r,"coverage") is None)
    measured_models=len({r["model_id"] for r in data if number(r,"coverage") is not None})
    c.text(72,611,f"NUMERIC POINTS: {numeric} across {measured_models} models | UNAVAILABLE/TARGET NOT MET: {unavailable}",13,INK,"start","bold")
    footer(c,"Target precision is the predeclared descriptive 95% target | Source denominators remain explicit in the table")
    c.save(out/(BASENAMES[5]+".svg"),out/(BASENAMES[5]+".png"))


def chart_7(data,out):
    ordered=sorted(data,key=lambda r:number(r,"selection_count"),reverse=True)
    c=Canvas(BASENAMES[6],"Descriptive augmentation selection",TAKEAWAYS[BASENAMES[6]],TABLE_MAP[BASENAMES[6]],
             ["Selection frequency across CV folds is descriptive, not causal leave-one-family-out contribution."])
    heading(c,"Which families appeared in validation selections?",TAKEAWAYS[BASENAMES[6]])
    maxv=max(number(r,"selection_count") for r in ordered)
    for i,r in enumerate(ordered):
        y=165+i*79
        c.text(70,y+25,r["family"].replace("_"," "),15,INK,"start","bold")
        c.rect(255,y,720,34,"#e9eef5","none")
        c.rect(255,y,720*number(r,"selection_count")/maxv,34,BLUE,"none")
        c.text(990,y+24,f"{int(number(r,'selection_count'))} selections",14,INK)
        c.text(255,y+55,f"{r['candidate_transform_count']} candidate transforms | mean MRR {number(r,'mean_mrr'):.3f}",11,MUTED)
    c.rect(850,568,300,55,PALE_ORANGE,"none")
    c.text(865,590,"DESCRIPTIVE, NOT CAUSAL",13,ORANGE,"start","bold")
    c.text(865,610,"5 folds; 55 CV-rank summary rows",11,INK)
    footer(c,"RECOMPUTED family sums from source-reported CV summary | Counts are not accuracy effects")
    c.save(out/(BASENAMES[6]+".svg"),out/(BASENAMES[6]+".png"))


def chart_8(data,out):
    key_names=("baseline","shift_only","dont_warp_text_and_lines_d003_r30_s10_std15","warp_all_d003_r30_s10_std15","warp_hw_only_dont_warp_text_and_lines_d003_r30_s10_std15")
    colors=(MUTED,ORANGE,BLUE,GREEN,PURPLE)
    labels=("unchanged baseline","Pad / shift","GW masked 1.5","GW all 1.5","GW hw-only 1.5")
    selected=[r for r in data if r["strategy"] in key_names]
    modern=[r for r in data if str(r["model_id"]).startswith("gemini-3.5-")]
    selected.extend(modern)
    ymin=min(number(r,"consensus_cer") for r in selected)-.003; ymax=max(number(r,"consensus_cer") for r in selected)+.003
    max_samples=max(number(r,"n_samples") for r in selected)
    c=Canvas(BASENAMES[7],"Ensemble size and diminishing returns",TAKEAWAYS[BASENAMES[7]],TABLE_MAP[BASENAMES[7]],
             ["Historical source-reported series and modern measured strategy points are shown.", "Evaluated-field counts vary around the noncanonical source denominators."])
    heading(c,"More members help, but gains are not monotonic",TAKEAWAYS[BASENAMES[7]])
    a=Axes(c,90,145,760,420,1,max(5,max_samples),ymin,ymax)
    yticks=[ymin+(ymax-ymin)*i/4 for i in range(5)]
    a.draw(list(range(1,int(max(5,max_samples))+1)),yticks,"Ensemble members (source aggregate k)","Consensus CER",lambda v:f"{int(v)}",lambda v:f"{100*v:.1f}%")
    for name,color,label in zip(key_names,colors,labels):
        series=sorted((r for r in selected if r["strategy"]==name),key=lambda r:number(r,"n_samples"))
        pts=[(a.px(number(r,"n_samples")),a.py(number(r,"consensus_cer"))) for r in series]
        c.polyline(pts,color,3)
        for x,y in pts:c.circle(x,y,4,color,"#ffffff",1)
    modern_colors={"unchanged_3":TEAL,"Pad":ORANGE,"Grid Warp":BLUE,"visual_mixed_6":PURPLE,"all_views_9":RED,"single":GREEN}
    modern_keys=sorted({(r["model_id"],r["strategy"]) for r in modern})
    for model_id,name in modern_keys:
        color=modern_colors.get(name,TEAL)
        for r in modern:
            if r["model_id"]==model_id and r["strategy"]==name:
                x,y=a.px(number(r,"n_samples")),a.py(number(r,"consensus_cer"))
                c.circle(x,y,6,color,"#ffffff",2)
    c.rect(885,145,265,390,"#ffffff",GRID)
    c.text(905,174,"SOURCE-REPORTED",14,TEAL,"start","bold")
    for i,(color,label) in enumerate(zip(colors,labels)):
        y=207+i*36;c.line(905,y,935,y,color,4);c.text(945,y+5,label,12,INK)
    c.text(905,397,"MODERN MEASURED POINTS",14,TEAL,"start","bold")
    for i,(model_id,name) in enumerate(modern_keys[:5]):
        y=428+i*25; color=modern_colors.get(name,TEAL)
        c.circle(920,y,5,color,"#ffffff",1); c.text(935,y+4,model_id+" / "+name,10,INK)
    c.rect(905,552,225,42,PALE_ORANGE,"none")
    c.text(918,577,"NONCANONICAL DENOMINATORS",11,ORANGE,"start","bold")
    footer(c,"Historical curves + modern strategy points | Modern points are not connected into a fictitious curve")
    c.save(out/(BASENAMES[7]+".svg"),out/(BASENAMES[7]+".png"))


def chart_9(data,out):
    row=data[0]
    c=Canvas(BASENAMES[8],"Failure examples unavailable",TAKEAWAYS[BASENAMES[8]],TABLE_MAP[BASENAMES[8]],
             [row["notes"], "No prediction, ground truth, image path, or crop is rendered."])
    heading(c,"Qualitative failure panel: evidence gate not cleared",TAKEAWAYS[BASENAMES[8]])
    c.rect(90,155,1020,390,"#ffffff",GRID,2)
    c.rect(120,190,250,250,"#eef2f7",MUTED,2)
    c.line(145,215,345,415,MUTED,3);c.line(345,215,145,415,MUTED,3)
    c.text(245,470,"NO AUTHORIZED CROP",14,MUTED,"middle","bold")
    c.text(430,220,"BLOCKED EVIDENCE PANEL",20,RED,"start","bold")
    c.text(430,260,"release_status",12,MUTED)
    for i,line_value in enumerate(wrap(row["release_status"].replace("_"," "),45)):
        c.text(430,282+i*20,line_value,14,INK)
    c.text(430,345,"Private values intentionally omitted",15,INK,"start","bold")
    c.text(430,378,"- prediction: not copied",13,MUTED)
    c.text(430,404,"- ground truth: not copied",13,MUTED)
    c.text(430,430,"- image path / crop: not copied",13,MUTED)
    c.rect(430,470,620,45,PALE_RED,"none")
    c.text(448,498,"Requires stable redacted IDs + release-authorized crop lineage",13,RED,"start","bold")
    footer(c,"BLOCKED source row | Portable and privacy-safe | No qualitative claim made")
    c.save(out/(BASENAMES[8]+".svg"),out/(BASENAMES[8]+".png"))


def generate(derived: pathlib.Path, figure: pathlib.Path):
    missing=sorted({name for names in TABLE_MAP.values() for name in names if not (derived/name).is_file()})
    if missing: raise FileNotFoundError("Missing required derived table(s): "+", ".join(missing))
    loaded={name:rows(derived/name) for names in TABLE_MAP.values() for name in names}
    chart_1(loaded["strategy_summary.csv"],figure)
    chart_2(loaded["error_correlation_summary.csv"],figure)
    chart_3(loaded["precision_coverage.csv"],figure)
    chart_4(loaded["cost_by_run.csv"],loaded["review_frontier.csv"],figure)
    chart_5(loaded["shift_agreement.csv"],figure)
    chart_6(loaded["cross_model_operating_points.csv"],figure)
    chart_7(loaded["augmentation_contribution.csv"],figure)
    chart_8(loaded["ensemble_size.csv"],figure)
    chart_9(loaded["failure_examples.csv"],figure)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--derived-dir",type=pathlib.Path,required=True)
    parser.add_argument("--figure-dir",type=pathlib.Path,required=True)
    args=parser.parse_args(argv)
    generate(args.derived_dir,args.figure_dir)
    print(f"Generated {len(BASENAMES)*2} deterministic chart files in {args.figure_dir}")


if __name__=="__main__":
    main()
