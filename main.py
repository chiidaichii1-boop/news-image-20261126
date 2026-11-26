#!/usr/bin/env python3
"""The World, 26 November 2026 -- one image summing up the day's news.

Pure standard library: draws a newspaper front page (1024x1024 PNG)
with a hand-rolled 5x7 bitmap font and a from-scratch PNG encoder.
No network, no randomness, no timestamps in the output: two runs
produce byte-identical files.
"""

import binascii
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 243, 234)
INK = (26, 26, 26)
NAVY = (16, 35, 63)
GOLD = (201, 162, 39)
RED = (179, 35, 42)
TEAL = (14, 107, 107)
DARKRED = (122, 20, 28)
AMBER = (176, 118, 14)
GREEN = (46, 110, 58)
GREY = (90, 86, 78)
WHITE = (255, 255, 255)
BOX = (255, 255, 255)

# 5x7 bitmap font. Each glyph is 7 rows of 5 bits (MSB = left pixel).
FONT = {
    "A": (0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "B": (0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110),
    "C": (0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110),
    "D": (0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110),
    "E": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111),
    "F": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000),
    "G": (0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01111),
    "H": (0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "I": (0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "J": (0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100),
    "K": (0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001),
    "L": (0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111),
    "M": (0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001),
    "N": (0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001),
    "O": (0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "P": (0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000),
    "Q": (0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101),
    "R": (0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001),
    "S": (0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110),
    "T": (0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    "U": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "V": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    "W": (0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b10101, 0b01010),
    "X": (0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001),
    "Y": (0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100),
    "Z": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111),
    "0": (0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110),
    "1": (0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "2": (0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111),
    "3": (0b11111, 0b00010, 0b00100, 0b00010, 0b00001, 0b10001, 0b01110),
    "4": (0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010),
    "5": (0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110),
    "6": (0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110),
    "7": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000),
    "8": (0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110),
    "9": (0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0b01100, 0b01100),
    ",": (0, 0, 0, 0, 0b01100, 0b00100, 0b01000),
    ":": (0, 0b01100, 0b01100, 0, 0b01100, 0b01100, 0),
    ";": (0, 0b01100, 0b01100, 0, 0b01100, 0b00100, 0b01000),
    "'": (0b00100, 0b00100, 0b01000, 0, 0, 0, 0),
    "-": (0, 0, 0, 0b01110, 0, 0, 0),
    "/": (0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000),
    "(": (0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0b00100, 0b00010),
    ")": (0b01000, 0b00100, 0b00010, 0b00010, 0b00010, 0b00100, 0b01000),
    "&": (0b01100, 0b10010, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101),
    "%": (0b11001, 0b11010, 0b00010, 0b00100, 0b01000, 0b01011, 0b10011),
    "!": (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0, 0b00100),
    "?": (0b01110, 0b10001, 0b00001, 0b00110, 0b00100, 0, 0b00100),
    "$": (0b00100, 0b01111, 0b10100, 0b01110, 0b00101, 0b11110, 0b00100),
    "+": (0, 0b00100, 0b00100, 0b11111, 0b00100, 0b00100, 0),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.rect(0, 0, w, h, bg)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(max(0, y), min(self.h, y + h)):
            base = (yy * self.w + max(0, x)) * 3
            for xx in range(max(0, x), min(self.w, x + w)):
                i = (yy * self.w + xx) * 3
                self.px[i:i + 3] = bytes(color)

    def border(self, x, y, w, h, color, t=2):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def text_width(self, text, scale):
        return len(text) * 6 * scale - scale

    def text(self, x, y, text, scale, color):
        cx = x
        for ch in text:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale

    def text_center(self, y, text, scale, color, cx0=0, cx1=None):
        if cx1 is None:
            cx1 = self.w
        w = self.text_width(text, scale)
        self.text(cx0 + (cx1 - cx0 - w) // 2, y, text, scale, color)

    def wrap(self, text, scale, max_w):
        lines, cur = [], ""
        for word in text.split(" "):
            trial = (cur + " " + word).strip()
            if self.text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


def png_bytes(canvas):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(ctype, data):
        c = struct.pack(">I", len(data)) + ctype + data
        return c + struct.pack(">I", binascii.crc32(ctype + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def story_box(cv, x, y, w, h, tab_color, tab, headline, summary):
    cv.rect(x, y, w, h, BOX)
    cv.border(x, y, w, h, NAVY, 2)
    cv.rect(x + 2, y + 2, w - 4, 26, tab_color)
    cv.text(x + 12, y + 8, tab, 2, WHITE)
    lines = cv.wrap(headline, 2, w - 24)
    yy = y + 38
    for ln in lines[:2]:
        cv.text(x + 12, yy, ln, 2, INK)
        yy += 16
    slines = cv.wrap(summary, 2, w - 24)
    yy += 4
    for ln in slines[:3]:
        cv.text(x + 12, yy, ln, 2, GREY)
        yy += 16


def draw():
    cv = Canvas(W, H, PAPER)

    # Masthead.
    cv.rect(0, 0, W, 104, NAVY)
    cv.text_center(14, "THE WORLD", 9, WHITE)
    cv.text_center(84, "THURSDAY, 26 NOVEMBER 2026", 2, GOLD)
    cv.rect(0, 104, W, 4, GOLD)

    # Lead story: US tariffs.
    cv.text_center(124, "TRADE WAR ESCALATES", 3, RED)
    cv.text_center(152, "US UNVEILS NEW", 6, INK)
    cv.text_center(200, "TARIFFS ON 14", 6, INK)
    cv.text_center(248, "ECONOMIES", 6, INK)
    cv.text_center(306, "EU, CHINA, JAPAN AND TAIWAN TARGETED AFTER AN 8-MONTH", 2, INK)
    cv.text_center(324, "PROBE INTO FACTORY OVERCAPACITY", 2, INK)

    # Markets panel: falling bars.
    cv.rect(24, 352, 976, 148, BOX)
    cv.border(24, 352, 976, 148, NAVY, 2)
    cv.text(44, 366, "MARKETS SLIDE AS AI SELL-OFF DEEPENS", 2, RED)
    cv.text(44, 386, "S&P 500 AND DOW JONES INTO CORRECTION TERRITORY", 2, GREY)
    base_y = 486
    heights = [78, 72, 64, 55, 47, 38, 29, 20]
    bx = 60
    for ht in heights:
        cv.rect(bx, base_y - ht, 64, ht, RED)
        bx += 108
    cv.rect(44, base_y, 936, 3, NAVY)

    # Story grid: 2 columns x 3 rows.
    stories = [
        (RED, "UKRAINE WAR", "PEACE TALKS STALL IN ABU DHABI",
         "RUSSIA HOLDS ITS TERRITORIAL CLAIMS AS KYIV HITS AN AIR BASE AND TWO REFINERIES."),
        (TEAL, "ENERGY", "TWO TANKERS HIT MINES IN HORMUZ",
         "THE SHIPS CATCH FIRE IN THE STRAIT AS IRAN WARNS VESSELS TO PLAN SAFE PASSAGE."),
        (DARKRED, "NUCLEAR", "KIM ORDERS MORE TACTICAL NUKES",
         "NORTH KOREA'S LEADER CALLS FOR A WIDER DEPLOYMENT OF TACTICAL NUCLEAR WEAPONS."),
        (NAVY, "ISRAEL", "NETANYAHU CHARGES MAY BE DROPPED",
         "ISRAELI JUDGES RECOMMEND DROPPING THE MOST SERIOUS CHARGES AGAINST THE PM."),
        (AMBER, "EGYPT", "CAIRO TANKER FIRE KILLS 30",
         "A FUEL TANKER CRASHES AND BURNS ON A CROWDED HIGHWAY; 15 MORE ARE HURT."),
        (GREEN, "THANKSGIVING", "PARADE POSTPONED AS STORMS HIT",
         "MACY'S DELAYS ITS PARADE AND CALIFORNIA WARNS OF FLOODING AS KING TIDES PEAK."),
    ]
    xs = (24, 524)
    ys = (516, 668, 820)
    for i, (tab_color, tab, headline, summary) in enumerate(stories):
        story_box(cv, xs[i % 2], ys[i // 2], 476, 144,
                  tab_color, tab, headline, summary)

    # Footer.
    cv.rect(24, 976, 976, 2, GOLD)
    cv.text_center(988, "THE WORLD - 26 NOVEMBER 2026 - SUMMED UP IN ONE IMAGE", 2, GREY)
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    data = png_bytes(draw())
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
