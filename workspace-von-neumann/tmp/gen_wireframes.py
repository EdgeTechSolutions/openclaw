#!/usr/bin/env python3
"""Generate Document Anonymizer wireframes using Pillow."""

from PIL import Image, ImageDraw, ImageFont
import os

# ── Colours ──────────────────────────────────────────────────────────────────
BG          = "#0B1120"
SURFACE     = "#141E2F"
SURF_ELEV   = "#1C2B42"
ACCENT      = "#00B4D8"
SUCCESS     = "#22C55E"
WARNING     = "#F59E0B"
DANGER      = "#EF4444"
TEXT_PRI    = "#F0F4F8"
TEXT_SEC    = "#94A3B8"
BORDER      = "#1E3A5F"
PURPLE      = "#A855F7"
PINK        = "#EC4899"
ORANGE      = "#F97316"
CYAN        = "#00B4D8"

W, H = 1400, 900
HEADER_H = 56

# ── Font helpers ─────────────────────────────────────────────────────────────
def load_font(size, bold=False):
    """Try common system fonts, fall back to default."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def load_mono(size):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

# ── Drawing helpers ───────────────────────────────────────────────────────────
def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def hex_rgba(h, a=255):
    return hex_rgb(h) + (a,)

def rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    x0, y0, x1, y1 = xy
    if fill:
        draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)
    else:
        draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def dashed_rect(draw, xy, dash=8, gap=6, color="#1E3A5F", width=2):
    x0, y0, x1, y1 = xy
    # top
    x = x0
    while x < x1:
        draw.line([(x, y0), (min(x+dash, x1), y0)], fill=color, width=width)
        x += dash + gap
    # bottom
    x = x0
    while x < x1:
        draw.line([(x, y1), (min(x+dash, x1), y1)], fill=color, width=width)
        x += dash + gap
    # left
    y = y0
    while y < y1:
        draw.line([(x0, y), (x0, min(y+dash, y1))], fill=color, width=width)
        y += dash + gap
    # right
    y = y0
    while y < y1:
        draw.line([(x1, y), (x1, min(y+dash, y1))], fill=color, width=width)
        y += dash + gap

def badge(draw, x, y, text, bg, fg=TEXT_PRI, font=None, radius=4):
    if font is None:
        font = load_font(11, bold=True)
    tw = font.getlength(text)
    pad = 6
    bx0, by0 = x, y
    bx1, by1 = x + tw + pad*2, y + 18
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=radius, fill=bg)
    draw.text((bx0+pad, by0+2), text, fill=fg, font=font)
    return bx1  # right edge

def pill_button(draw, x, y, text, bg, fg=TEXT_PRI, font=None, w=None, h=32, radius=8):
    if font is None:
        font = load_font(13, bold=True)
    tw = font.getlength(text)
    bw = w if w else (tw + 24)
    draw.rounded_rectangle([x, y, x+bw, y+h], radius=radius, fill=bg)
    draw.text((x + (bw - tw)/2, y + (h - 14)/2), text, fill=fg, font=font)
    return x + bw

def centered_text(draw, text, y, font, color, x0=0, x1=W):
    tw = font.getlength(text)
    draw.text(((x0+x1-tw)/2, y), text, fill=color, font=font)

# ─────────────────────────────────────────────────────────────────────────────
# WIREFRAME 1: DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
def draw_dashboard():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Fonts
    f_sm   = load_font(11)
    f_sm_b = load_font(11, bold=True)
    f_md   = load_font(13)
    f_md_b = load_font(13, bold=True)
    f_lg   = load_font(16, bold=True)
    f_xl   = load_font(20, bold=True)
    f_hdr  = load_font(18, bold=True)

    # ── Header bar ────────────────────────────────────────────────────────────
    draw.rectangle([0, 0, W, HEADER_H], fill=SURF_ELEV)
    draw.line([(0, HEADER_H), (W, HEADER_H)], fill=BORDER, width=1)

    # Logo circle
    draw.ellipse([16, 12, 44, 44], fill=ACCENT)
    draw.text((22, 18), "DA", fill=BG, font=f_md_b)

    # Title
    draw.text((56, 16), "Document Anonymizer", fill=TEXT_PRI, font=f_xl)
    draw.text((W - 48, 20), "v1.0", fill=TEXT_SEC, font=f_md)

    # ── Column layout ─────────────────────────────────────────────────────────
    col_w = W // 3   # ~466px each
    body_top = HEADER_H
    col_h = H - body_top

    COL_TITLES = ["UPLOAD", "QUEUE", "HISTORY"]
    for i, title in enumerate(COL_TITLES):
        cx0 = i * col_w
        cx1 = cx0 + col_w

        # Column title bar
        draw.rectangle([cx0, body_top, cx1, body_top + 44], fill=SURF_ELEV)
        tw = f_lg.getlength(title)
        draw.text((cx0 + (col_w - tw)/2, body_top + 12), title, fill=ACCENT, font=f_lg)

        # Vertical divider (between cols)
        if i > 0:
            draw.line([(cx0, body_top), (cx0, H)], fill=BORDER, width=1)

    col_top = body_top + 44  # content starts below title bars

    # ═══ COLUMN 1: UPLOAD ═══════════════════════════════════════════════════
    cx0, cx1 = 0, col_w
    pad = 24

    # Drag-drop zone
    dz_x0 = cx0 + pad
    dz_y0 = col_top + 24
    dz_x1 = cx1 - pad
    dz_y1 = dz_y0 + 220
    draw.rounded_rectangle([dz_x0, dz_y0, dz_x1, dz_y1], radius=10, fill=SURFACE)
    dashed_rect(draw, [dz_x0, dz_y0, dz_x1, dz_y1], color=ACCENT, dash=12, gap=8, width=2)

    # Upload arrow icon (circle + arrow)
    ic_cx = (cx0 + cx1) // 2
    ic_cy = dz_y0 + 72
    draw.ellipse([ic_cx-28, ic_cy-28, ic_cx+28, ic_cy+28], fill=ACCENT)
    # Arrow: shaft
    draw.rectangle([ic_cx-4, ic_cy-14, ic_cx+4, ic_cy+10], fill=BG)
    # Arrowhead
    draw.polygon([
        (ic_cx, ic_cy-22),
        (ic_cx-12, ic_cy-8),
        (ic_cx+12, ic_cy-8),
    ], fill=BG)

    # Labels
    lbl = "Drop files here or click to browse"
    tw = f_md_b.getlength(lbl)
    draw.text(((cx0+cx1-tw)/2, ic_cy+38), lbl, fill=TEXT_PRI, font=f_md_b)
    ext = ".pdf  .txt  .md  .doc  .docx"
    tw2 = f_sm.getlength(ext)
    draw.text(((cx0+cx1-tw2)/2, ic_cy+60), ext, fill=TEXT_SEC, font=f_sm)

    # Browse Files button
    btn_y = dz_y1 + 20
    btn_w = 160
    btn_x = (cx0 + cx1 - btn_w) // 2
    pill_button(draw, btn_x, btn_y, "Browse Files", ACCENT, BG, f_md_b, w=btn_w, h=36, radius=10)

    # Sub-hint
    hint = "Or drag and drop anywhere in this column"
    tw3 = f_sm.getlength(hint)
    draw.text(((cx0+cx1-tw3)/2, btn_y+46), hint, fill=TEXT_SEC, font=f_sm)

    # ═══ COLUMN 2: QUEUE ════════════════════════════════════════════════════
    cx0, cx1 = col_w, 2*col_w
    pad = 16

    # Processing section
    sec_y = col_top + 18
    draw.text((cx0+pad, sec_y), "Processing", fill=TEXT_SEC, font=f_md_b)

    # Running row
    row_y = sec_y + 28
    row_h = 52
    draw.rounded_rectangle([cx0+pad, row_y, cx1-pad, row_y+row_h], radius=6, fill=SURFACE, outline=BORDER, width=1)
    # Amber pulse dot
    dot_x = cx0 + pad + 16
    dot_y = row_y + row_h//2
    draw.ellipse([dot_x-6, dot_y-6, dot_x+6, dot_y+6], fill=WARNING)
    # Filename
    draw.text((dot_x+14, row_y+8), "report_q1.pdf", fill=TEXT_PRI, font=f_md_b)
    # PDF badge
    bx = badge(draw, dot_x+14, row_y+28, "PDF", SURF_ELEV, TEXT_SEC, f_sm_b)
    # RUNNING badge
    badge(draw, bx+6, row_y+28, "RUNNING", WARNING + "33", WARNING, f_sm_b)
    # Timestamp
    ts_x = cx1 - pad - 44
    draw.text((ts_x, row_y+18), "09:14", fill=TEXT_SEC, font=f_sm)

    # Divider
    div_y = row_y + row_h + 16
    draw.line([(cx0+pad, div_y), (cx1-pad, div_y)], fill=BORDER, width=1)

    # Queued section
    sec2_y = div_y + 12
    draw.text((cx0+pad, sec2_y), "Queued (2)", fill=TEXT_SEC, font=f_md_b)

    # Queued rows
    queued = [("contract.docx", "DOCX"), ("notes.txt", "TXT")]
    for qi, (fname, ftype) in enumerate(queued):
        qrow_y = sec2_y + 28 + qi * 62
        draw.rounded_rectangle([cx0+pad, qrow_y, cx1-pad, qrow_y+52], radius=6, fill=SURFACE, outline=BORDER, width=1)
        # Grey dot
        qdx = cx0 + pad + 16
        qdy = qrow_y + 26
        draw.ellipse([qdx-5, qdy-5, qdx+5, qdy+5], fill=TEXT_SEC)
        draw.text((qdx+14, qrow_y+8), fname, fill=TEXT_PRI, font=f_md_b)
        bx2 = badge(draw, qdx+14, qrow_y+28, ftype, SURF_ELEV, TEXT_SEC, f_sm_b)
        badge(draw, bx2+6, qrow_y+28, "ENQUEUED", SURF_ELEV, TEXT_SEC, f_sm_b)

    # Hint at bottom
    hint2 = "Drop files in the Upload column to add them to the queue."
    draw.text((cx0+pad, sec2_y+170), hint2, fill=TEXT_SEC, font=f_sm)

    # ═══ COLUMN 3: HISTORY ══════════════════════════════════════════════════
    cx0, cx1 = 2*col_w, W
    pad = 16

    # Search bar
    sb_y = col_top + 16
    draw.rounded_rectangle([cx0+pad, sb_y, cx1-pad, sb_y+36], radius=8, fill=SURF_ELEV, outline=BORDER, width=1)
    draw.text((cx0+pad+12, sb_y+10), "🔍  Search by name or date...", fill=TEXT_SEC, font=f_md)

    # History rows
    hist = [
        ("report_q1.pdf",   "Mar 9 2026  ·  14 entities anonymized", SUCCESS),
        ("invoice_feb.pdf",  "Mar 8 2026  ·  9 entities anonymized",  SUCCESS),
        ("letter_draft.docx","Mar 7 2026  ·  22 entities anonymized", SUCCESS),
    ]
    row_y = sb_y + 52
    for fname, sub, _ in hist:
        row_h = 60
        draw.rounded_rectangle([cx0+pad, row_y, cx1-pad, row_y+row_h], radius=6, fill=SURFACE, outline=BORDER, width=1)
        # Doc icon
        draw.rounded_rectangle([cx0+pad+10, row_y+14, cx0+pad+28, row_y+46], radius=3, fill=SURF_ELEV, outline=BORDER, width=1)
        draw.text((cx0+pad+13, row_y+22), "📄", fill=TEXT_SEC, font=f_sm)
        # Text
        draw.text((cx0+pad+38, row_y+10), fname, fill=TEXT_PRI, font=f_md_b)
        draw.text((cx0+pad+38, row_y+30), sub, fill=TEXT_SEC, font=f_sm)
        # Buttons
        btn_area_x = cx1 - pad - 160
        pill_button(draw, btn_area_x, row_y+14, "↓ Download", SUCCESS, BG, f_sm_b, w=72, h=26, radius=6)
        pill_button(draw, btn_area_x+78, row_y+14, "⊞ Compare", ACCENT, BG, f_sm_b, w=72, h=26, radius=6)
        row_y += row_h + 10

    img.save("/workspace/tmp/wireframe-dashboard.png", "PNG")
    print("Saved wireframe-dashboard.png")

# ─────────────────────────────────────────────────────────────────────────────
# WIREFRAME 2: COMPARISON VIEW
# ─────────────────────────────────────────────────────────────────────────────
def draw_comparison():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    f_sm   = load_font(11)
    f_sm_b = load_font(11, bold=True)
    f_md   = load_font(13)
    f_md_b = load_font(13, bold=True)
    f_lg   = load_font(15, bold=True)
    f_xl   = load_font(18, bold=True)
    f_mono = load_mono(12)

    # ── Header ────────────────────────────────────────────────────────────────
    draw.rectangle([0, 0, W, HEADER_H], fill=SURF_ELEV)
    draw.line([(0, HEADER_H), (W, HEADER_H)], fill=BORDER, width=1)

    pill_button(draw, 16, 12, "← Back", SURF_ELEV, ACCENT, f_md_b, w=80, h=32, radius=8)
    # Outline for back button
    draw.rounded_rectangle([16, 12, 96, 44], radius=8, outline=BORDER, width=1)

    centered_text(draw, "contract.docx", 16, f_xl, TEXT_PRI)
    pill_button(draw, W-130, 12, "↓ Download", SUCCESS, BG, f_md_b, w=110, h=32, radius=8)

    # ── Pane layout ───────────────────────────────────────────────────────────
    body_top = HEADER_H
    LEFT_W  = int(W * 0.35)
    MID_W   = int(W * 0.35)
    RIGHT_W = W - LEFT_W - MID_W

    left_x0,  left_x1  = 0,            LEFT_W
    mid_x0,   mid_x1   = LEFT_W,       LEFT_W + MID_W
    right_x0, right_x1 = LEFT_W+MID_W, W

    # Dividers
    draw.line([(left_x1, body_top), (left_x1, H)], fill=BORDER, width=1)
    draw.line([(mid_x1,  body_top), (mid_x1,  H)], fill=BORDER, width=1)

    # Pane title bars
    pane_title_h = 40
    for px0, px1, title in [
        (left_x0, left_x1, "ORIGINAL DOCUMENT"),
        (mid_x0,  mid_x1,  "ANONYMIZED DOCUMENT"),
        (right_x0, right_x1, "ENTITY SUMMARY"),
    ]:
        draw.rectangle([px0, body_top, px1, body_top+pane_title_h], fill=SURF_ELEV)
        draw.line([(px0, body_top+pane_title_h), (px1, body_top+pane_title_h)], fill=BORDER, width=1)
        tw = f_lg.getlength(title)
        draw.text((px0+(px1-px0-tw)/2, body_top+12), title, fill=TEXT_PRI, font=f_lg)

    content_top = body_top + pane_title_h
    pad = 20

    # ─── Helper: draw inline text with highlighted spans ──────────────────────
    def draw_inline(draw, x, y, parts, font):
        """parts: list of (text, highlight_color or None)"""
        cx = x
        for text, hl in parts:
            if hl:
                tw = font.getlength(text)
                hl_rgb = hex_rgb(hl)
                # Semi-transparent highlight box
                draw.rounded_rectangle(
                    [cx-2, y-2, cx+tw+2, y+16],
                    radius=3,
                    fill=(hl_rgb[0], hl_rgb[1], hl_rgb[2], 80)
                )
                draw.text((cx, y), text, fill=hl, font=font)
            else:
                draw.text((cx, y), text, fill=TEXT_PRI, font=font)
            cx += font.getlength(text)
        return cx

    # ─── LEFT PANE: Original ──────────────────────────────────────────────────
    tx = left_x0 + pad
    ty = content_top + pad
    lh = 20  # line height

    para1 = [
        [("This agreement is entered into between ", None),
         ("John Doe", WARNING), (" and", None)],
        [("representatives of ", None),
         ("Acme Corp", ACCENT), (", a company", None)],
        [("registered in ", None),
         ("Ljubljana", PURPLE), (", Slovenia. The", None)],
        [("parties agree to the following terms and", None)],
        [("conditions effective March 1, 2026.", None)],
    ]
    for line_parts in para1:
        draw_inline(draw, tx, ty, line_parts, f_mono)
        ty += lh

    ty += lh//2
    draw.text((tx, ty), "1. CONFIDENTIALITY", fill=TEXT_PRI, font=load_font(12, bold=True))
    ty += lh+4

    conf_lines = [
        "The Employee shall not disclose any",
        "proprietary information obtained during",
        "the course of employment.",
    ]
    for cl in conf_lines:
        draw.text((tx, ty), cl, fill=TEXT_PRI, font=f_mono)
        ty += lh

    ty += lh//2
    draw.text((tx, ty), "2. SCOPE OF WORK", fill=TEXT_PRI, font=load_font(12, bold=True))
    ty += lh+4

    scope_lines = [
        [("Work will be performed at the primary", None)],
        [("office and may involve travel to client", None)],
        [("sites as required by the project.", None)],
    ]
    for line_parts in scope_lines:
        draw_inline(draw, tx, ty, line_parts, f_mono)
        ty += lh

    # Email & phone lines in original doc
    ty += lh//2
    draw.text((tx, ty), "Contact: ", fill=TEXT_PRI, font=f_mono)
    cx_e = tx + f_mono.getlength("Contact: ")
    draw_inline(draw, cx_e, ty, [("john.doe@acme.com", PINK)], f_mono)
    ty += lh
    draw.text((tx, ty), "Phone: ", fill=TEXT_PRI, font=f_mono)
    cx_p = tx + f_mono.getlength("Phone: ")
    draw_inline(draw, cx_p, ty, [("+386 1 234 567", ORANGE)], f_mono)

    # ─── MIDDLE PANE: Anonymized ──────────────────────────────────────────────
    tx2 = mid_x0 + pad
    ty2 = content_top + pad
    CYAN_HL = "#00B4D8"

    anon_para1 = [
        [("This agreement is entered into between ", None),
         ("PERSON_001", CYAN_HL), (" and", None)],
        [("representatives of ", None),
         ("ORG_001", CYAN_HL), (", a company", None)],
        [("registered in ", None),
         ("LOCATION_001", CYAN_HL), (", Slovenia. The", None)],
        [("parties agree to the following terms and", None)],
        [("conditions effective March 1, 2026.", None)],
    ]
    for line_parts in anon_para1:
        draw_inline(draw, tx2, ty2, line_parts, f_mono)
        ty2 += lh

    ty2 += lh//2
    draw.text((tx2, ty2), "1. CONFIDENTIALITY", fill=TEXT_PRI, font=load_font(12, bold=True))
    ty2 += lh+4

    for cl in conf_lines:
        draw.text((tx2, ty2), cl, fill=TEXT_PRI, font=f_mono)
        ty2 += lh

    ty2 += lh//2
    draw.text((tx2, ty2), "2. SCOPE OF WORK", fill=TEXT_PRI, font=load_font(12, bold=True))
    ty2 += lh+4

    for line_parts in scope_lines:
        draw_inline(draw, tx2, ty2, line_parts, f_mono)
        ty2 += lh

    ty2 += lh//2
    draw.text((tx2, ty2), "Contact: ", fill=TEXT_PRI, font=f_mono)
    cx_e2 = tx2 + f_mono.getlength("Contact: ")
    draw_inline(draw, cx_e2, ty2, [("EMAIL_001", CYAN_HL)], f_mono)
    ty2 += lh
    draw.text((tx2, ty2), "Phone: ", fill=TEXT_PRI, font=f_mono)
    cx_p2 = tx2 + f_mono.getlength("Phone: ")
    draw_inline(draw, cx_p2, ty2, [("PHONE_001", CYAN_HL)], f_mono)

    # ─── RIGHT SIDEBAR: Entity Summary ───────────────────────────────────────
    rx = right_x0 + pad
    ry = content_top + pad

    # "17 entities anonymized" card
    draw.rounded_rectangle([rx, ry, right_x1-pad, ry+54], radius=8, fill=SURF_ELEV, outline=BORDER, width=1)
    draw.text((rx+14, ry+6), "17", fill=ACCENT, font=load_font(28, bold=True))
    draw.text((rx+14, ry+36), "entities anonymized", fill=TEXT_SEC, font=f_sm)
    ry += 64

    # Filter chips
    chips = [("All", ACCENT, BG), ("Person", SURF_ELEV, TEXT_SEC),
             ("Org", SURF_ELEV, TEXT_SEC), ("Location", SURF_ELEV, TEXT_SEC),
             ("Date", SURF_ELEV, TEXT_SEC), ("Phone", SURF_ELEV, TEXT_SEC)]
    chip_x = rx
    for clabel, cbg, cfg in chips:
        tw = f_sm_b.getlength(clabel) + 14
        draw.rounded_rectangle([chip_x, ry, chip_x+tw, ry+22], radius=6, fill=cbg)
        if cbg == SURF_ELEV:
            draw.rounded_rectangle([chip_x, ry, chip_x+tw, ry+22], radius=6, outline=BORDER, width=1)
        draw.text((chip_x+7, ry+4), clabel, fill=cfg, font=f_sm_b)
        chip_x += tw + 6
        if chip_x > right_x1 - pad - 30:
            chip_x = rx
            ry += 28

    ry += 30

    # Entity rows
    entity_rows = [
        ("John Doe",          "→ PERSON_001",   "Person",   WARNING,  False),
        ("Acme Corp",         "→ ORG_001",       "Org",      ACCENT,   False),
        ("Ljubljana",         "→ LOCATION_001",  "Location", PURPLE,   True),   # selected
        ("Jane Smith",        "→ PERSON_002",    "Person",   WARNING,  False),
        ("TechCorp Ltd",      "→ ORG_002",       "Org",      ACCENT,   False),
        ("March 1, 2026",     "→ DATE_001",       "Date",     SUCCESS,  False),
        ("+386 1 234 5678",   "→ PHONE_001",     "Phone",    PINK,     False),
        ("Acme Corp HQ",      "→ ORG_003",       "Org",      ACCENT,   False),
    ]
    for orig, repl, etype, ecolor, selected in entity_rows:
        er_h = 48
        outline_col = ACCENT if selected else BORDER
        ol_w = 2 if selected else 1
        fill_col = "#1A2E48" if selected else SURFACE
        draw.rounded_rectangle([rx, ry, right_x1-pad, ry+er_h], radius=6, fill=fill_col, outline=outline_col, width=ol_w)
        draw.text((rx+10, ry+6), orig, fill=TEXT_PRI, font=f_sm_b)
        draw.text((rx+10, ry+26), repl, fill=TEXT_SEC, font=f_sm)
        # Type badge on right
        bw = f_sm_b.getlength(etype) + 12
        badge(draw, right_x1-pad-bw-6, ry+14, etype, ecolor + "33" if len(ecolor)==7 else SURF_ELEV, ecolor, f_sm_b, radius=4)
        ry += er_h + 6

    img.save("/workspace/tmp/wireframe-comparison.png", "PNG")
    print("Saved wireframe-comparison.png")

if __name__ == "__main__":
    draw_dashboard()
    draw_comparison()
    print("Done.")
