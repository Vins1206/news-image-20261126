#!/usr/bin/env python3
"""World news in one image: Thursday 26 November 2026.

Pure Python standard library. Draws a 1024x1024 newspaper front page
with a hand-built 5x7 bitmap font and writes it as a PNG to
/output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png). Deterministic:
no network, no clock, no randomness. Every story below was reported
on 26 November 2026 (or on 25 November and carried as the day's news).
"""
import binascii
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (253, 251, 247)
INK = (17, 24, 39)
NAVY = (15, 42, 68)
NAVY2 = (23, 58, 94)
RED = (185, 28, 28)
ORANGE = (234, 88, 12)
GOLD = (180, 130, 29)
GOLD_L = (245, 158, 11)
TEAL = (13, 148, 136)
GREEN = (21, 128, 61)
BLUE = (29, 78, 216)
GREY = (100, 116, 139)
LIGHT = (226, 232, 240)
WHITE = (255, 255, 255)
CREAM = (255, 248, 220)

# 5x7 bitmap font, uppercase only. Each glyph is 7 rows of 5 bits.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
}


def char_width(scale):
    return (5 + 1) * scale


def text_width(text, scale):
    return len(text) * char_width(scale) - scale


def make_canvas():
    buf = bytearray(W * H * 3)
    for i in range(W * H):
        buf[i * 3] = PAPER[0]
        buf[i * 3 + 1] = PAPER[1]
        buf[i * 3 + 2] = PAPER[2]
    return buf


def set_px(buf, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = color[0]
        buf[i + 1] = color[1]
        buf[i + 2] = color[2]


def fill_rect(buf, x, y, w, h, color):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            buf[i] = color[0]
            buf[i + 1] = color[1]
            buf[i + 2] = color[2]


def rect_outline(buf, x, y, w, h, color, t=3):
    fill_rect(buf, x, y, w, t, color)
    fill_rect(buf, x, y + h - t, w, t, color)
    fill_rect(buf, x, y, t, h, color)
    fill_rect(buf, x + w - t, y, t, h, color)


def draw_line(buf, x0, y0, x1, y1, color, t=2):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        fill_rect(buf, x - t // 2, y - t // 2, t, t, color)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def fill_circle(buf, cx, cy, r, color):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                set_px(buf, xx, yy, color)


def draw_text(buf, x, y, text, scale, color):
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT["?"])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    fill_rect(buf, cx + col * scale, y + row * scale,
                              scale, scale, color)
        cx += char_width(scale)
    return cx


def wrap(text, max_w, scale):
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(buf, x, y, text, scale, color, max_w, leading=None):
    if leading is None:
        leading = 7 * scale + 4
    yy = y
    for line in wrap(text, max_w, scale):
        draw_text(buf, x, yy, line, scale, color)
        yy += leading
    return yy


def box(buf, x, y, w, h, accent):
    fill_rect(buf, x, y, w, h, WHITE)
    rect_outline(buf, x, y, w, h, INK, 3)
    fill_rect(buf, x, y, w, 10, accent)


def kicker(buf, x, y, text, color):
    draw_text(buf, x, y, text, 2, color)


def draw():
    buf = make_canvas()

    # ---- Masthead ----
    fill_rect(buf, 0, 0, W, 148, NAVY)
    fill_rect(buf, 0, 148, W, 6, GOLD_L)
    draw_text(buf, 40, 18, "MAKE.FUN - WORLD NEWS IN ONE IMAGE", 2, GOLD_L)
    draw_text(buf, 40, 48, "WORLD IN ONE DAY", 8, WHITE)
    draw_text(buf, 40, 118, "THURSDAY - 26 NOVEMBER 2026", 3, WHITE)
    # Date badge, right.
    fill_rect(buf, 862, 16, 122, 116, GOLD_L)
    rect_outline(buf, 862, 16, 122, 116, WHITE, 3)
    draw_text(buf, 892, 26, "NOV", 3, NAVY)
    draw_text(buf, 880, 58, "26", 7, NAVY)
    draw_text(buf, 876, 112, "2026", 2, NAVY)

    # ---- Lead story: oil ----
    box(buf, 32, 164, 960, 252, RED)
    kicker(buf, 52, 186, "LEAD STORY - MIDDLE EAST - OIL", RED)
    draw_text(buf, 52, 210, "OIL SHOCK", 8, INK)
    draw_wrapped(buf, 52, 280, "HOUTHIS CLAIM STRIKE ON SAUDI RAS TANURA REFINERY", 3, NAVY, 560)
    draw_wrapped(buf, 52, 338, "BRENT JUMPS TO $94.61. RIYADH SHOT DOWN 4 DRONES. CLAIM NOT CONFIRMED.", 3, INK, 560)
    # Oil illustration, right side.
    fill_rect(buf, 660, 184, 312, 212, CREAM)
    rect_outline(buf, 660, 184, 312, 212, INK, 2)
    # Derrick, taller and thicker than v1.
    draw_line(buf, 695, 388, 728, 212, INK, 6)
    draw_line(buf, 765, 388, 742, 212, INK, 6)
    draw_line(buf, 704, 336, 758, 336, INK, 4)
    draw_line(buf, 712, 288, 750, 288, INK, 4)
    draw_line(buf, 695, 388, 758, 336, INK, 3)
    draw_line(buf, 765, 388, 704, 336, INK, 3)
    # Flame, bigger than v1.
    fill_circle(buf, 800, 232, 34, ORANGE)
    fill_circle(buf, 800, 244, 22, GOLD_L)
    fill_circle(buf, 800, 254, 10, WHITE)
    # Price tag.
    fill_rect(buf, 812, 300, 148, 76, NAVY)
    draw_text(buf, 822, 310, "$94.61", 3, WHITE)
    draw_text(buf, 822, 344, "+3.5%", 3, GOLD_L)

    # ---- Row 2: tariffs + AI markets ----
    box(buf, 32, 432, 464, 220, TEAL)
    kicker(buf, 52, 452, "TRADE - WASHINGTON", TEAL)
    draw_text(buf, 52, 476, "NEW US TARIFFS", 4, INK)
    draw_wrapped(buf, 52, 516, "14 PARTNERS HIT. CHINA 20%. EU, JAPAN 15%.", 3, INK, 424)
    # Bars: CHINA 20, EU 15, VIETNAM 35 (if talks fail). Country
    # labels sit inside the bars, clear of the body text.
    bx, by = 70, 640
    for i, (label, val, col) in enumerate(
            [("CHINA", 20, TEAL), ("EU", 15, BLUE), ("VIETNAM", 35, RED)]):
        x = bx + i * 145
        hgt = int(val * 1.8)
        fill_rect(buf, x, by - hgt, 60, hgt, col)
        draw_text(buf, x + 8, by - 12, label, 1, WHITE)

    box(buf, 528, 432, 464, 220, BLUE)
    kicker(buf, 548, 452, "MARKETS - AI", BLUE)
    draw_text(buf, 548, 476, "NVIDIA ON WATCH", 4, INK)
    draw_wrapped(buf, 548, 516, "S&P: DOWNGRADE WATCH. AI SELLOFF. TAIWAN -1,927.", 3, INK, 424)
    # Falling chart, thicker and steeper than v1.
    draw_line(buf, 560, 592, 630, 608, RED, 5)
    draw_line(buf, 630, 608, 700, 602, RED, 5)
    draw_line(buf, 700, 602, 770, 622, RED, 5)
    draw_line(buf, 770, 622, 840, 638, RED, 5)
    draw_line(buf, 840, 638, 872, 646, RED, 5)
    draw_line(buf, 872, 646, 872, 626, RED, 5)
    draw_line(buf, 872, 646, 852, 646, RED, 5)
    draw_text(buf, 888, 628, "DOWN", 2, RED)

    # ---- Row 3: space, parade, sport ----
    box(buf, 32, 668, 304, 220, NAVY2)
    kicker(buf, 48, 688, "SPACE", NAVY2)
    draw_wrapped(buf, 48, 712, "FIRST PAKISTANI ASTRONAUT", 3, INK, 272)
    draw_wrapped(buf, 48, 772, "ALI TO FLY TO TIANGONG ON SHENZHOU-24.", 2, INK, 272)
    # Rocket lying flat, big and centred in the strip below the text.
    fill_circle(buf, 92, 846, 12, ORANGE)
    fill_circle(buf, 92, 846, 6, GOLD_L)
    fill_rect(buf, 104, 832, 140, 28, WHITE)
    rect_outline(buf, 104, 832, 140, 28, INK, 2)
    draw_line(buf, 244, 832, 278, 846, INK, 3)
    draw_line(buf, 244, 860, 278, 846, INK, 3)
    fill_circle(buf, 190, 846, 9, BLUE)
    draw_line(buf, 120, 860, 104, 878, INK, 3)
    draw_line(buf, 120, 832, 104, 814, INK, 3)

    box(buf, 360, 668, 304, 220, GOLD)
    kicker(buf, 376, 688, "USA - HOLIDAY", GOLD)
    draw_wrapped(buf, 376, 712, "100TH MACY'S PARADE", 3, INK, 272)
    draw_wrapped(buf, 376, 772, "A CENTURY OF THANKSGIVING. US MARKETS CLOSED.", 2, INK, 272)
    # Big balloon with 100 on it, centred below the text.
    fill_circle(buf, 512, 852, 26, RED)
    draw_text(buf, 494, 844, "100", 2, WHITE)

    box(buf, 688, 668, 304, 220, GREEN)
    kicker(buf, 704, 688, "SPORT - INDIA", GREEN)
    draw_wrapped(buf, 704, 712, "15-YEAR-OLD MAKES HISTORY", 3, INK, 272)
    draw_wrapped(buf, 704, 772, "204 OFF 53 BALLS. WORLD RECORD. INDIA MARKS 18 YEARS SINCE 26/11.", 2, INK, 272)
    # Big bat and ball in the strip below the text.
    draw_line(buf, 740, 880, 820, 848, INK, 7)
    fill_circle(buf, 940, 862, 16, RED)
    draw_line(buf, 928, 852, 952, 872, WHITE, 2)

    # ---- Footer: also today ----
    fill_rect(buf, 0, 904, W, 120, NAVY)
    draw_text(buf, 40, 918, "ALSO TODAY", 2, GOLD_L)
    draw_wrapped(buf, 40, 944, "CAIRO TANKER FIRE KILLS 31 - ISRAEL STRIKES IN GAZA AS CEASEFIRE STRAINS - UKRAINE HITS RUSSIAN REFINERIES - NORTH KOREA EXPELS SWISS DIPLOMAT", 2, WHITE, 944)
    draw_text(buf, 40, 996, "ALL STORIES REPORTED ON THURSDAY 26 NOVEMBER 2026", 2, GOLD_L)

    return buf


def png_bytes(buf):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw.extend(buf[y * stride:(y + 1) * stride])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(draw())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
