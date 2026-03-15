#!/usr/bin/env python3
"""
Build a complete searchable PDF for:
"Funkcionalne zahteve podpora revizijam ZVRK"
19 pages of Slovenian legal document content.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.platypus.flowables import Flowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

# Register Liberation Sans fonts for Unicode/Slovenian support
pdfmetrics.registerFont(TTFont('LiberationSans', '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'))
pdfmetrics.registerFont(TTFont('LiberationSans-Bold', '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('LiberationSans-Italic', '/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf'))
pdfmetrics.registerFontFamily('LiberationSans',
    normal='LiberationSans',
    bold='LiberationSans-Bold',
    italic='LiberationSans-Italic',
)

PAGE_W, PAGE_H = A4
MARGIN = 20 * mm
DOC_TITLE = "Funkcionalne zahteve podpora revizijam ZVRK"

# ── Styles ────────────────────────────────────────────────────────────────────

def S(name, **kw):
    defaults = dict(fontName='LiberationSans', fontSize=10, leading=14,
                    spaceAfter=4, spaceBefore=2, alignment=TA_JUSTIFY)
    defaults.update(kw)
    return ParagraphStyle(name, **defaults)

sNormal      = S('Normal')
sNormalLeft  = S('NormalLeft', alignment=TA_LEFT)
sH1          = S('H1', fontName='LiberationSans-Bold', fontSize=13, leading=17,
                 spaceBefore=10, spaceAfter=6, alignment=TA_LEFT)
sH2          = S('H2', fontName='LiberationSans-Bold', fontSize=11, leading=15,
                 spaceBefore=8, spaceAfter=4, alignment=TA_LEFT)
sH3          = S('H3', fontName='LiberationSans-Bold', fontSize=10, leading=14,
                 spaceBefore=6, spaceAfter=3, alignment=TA_LEFT)
sTitle       = S('Title', fontName='LiberationSans-Bold', fontSize=16, leading=20,
                 spaceAfter=8, alignment=TA_CENTER)
sSubtitle    = S('Subtitle', fontName='LiberationSans-Bold', fontSize=12, leading=16,
                 spaceAfter=6, alignment=TA_CENTER)
sBullet      = S('Bullet', leftIndent=12, alignment=TA_LEFT, spaceAfter=3)
sSubBullet   = S('SubBullet', leftIndent=24, alignment=TA_LEFT, spaceAfter=2)
sItalic      = S('Italic', fontName='LiberationSans-Italic', alignment=TA_LEFT)
sSmall       = S('Small', fontSize=8, leading=11, alignment=TA_LEFT)
sFootnote    = S('Footnote', fontSize=7.5, leading=10, alignment=TA_LEFT)
sTableHdr    = S('TableHdr', fontName='LiberationSans-Bold', fontSize=9, leading=12,
                 alignment=TA_CENTER)
sTableCell   = S('TableCell', fontSize=9, leading=12, alignment=TA_LEFT)
sTableCellC  = S('TableCellC', fontSize=9, leading=12, alignment=TA_CENTER)
sTOC         = S('TOC', fontSize=10, leading=14, alignment=TA_LEFT)
sTOCSub      = S('TOCSub', fontSize=10, leading=14, leftIndent=12, alignment=TA_LEFT)
sTOCSub2     = S('TOCSub2', fontSize=10, leading=14, leftIndent=24, alignment=TA_LEFT)
sBoxText     = S('BoxText', fontSize=9.5, leading=13, alignment=TA_LEFT)
sBoxBullet   = S('BoxBullet', fontSize=9.5, leading=13, leftIndent=12, alignment=TA_LEFT)
sBoxTitle    = S('BoxTitle', fontName='LiberationSans-Bold', fontSize=9.5, leading=13, alignment=TA_LEFT)
sSectionHdr  = S('SectionHdr', fontName='LiberationSans-Bold', fontSize=9, leading=12,
                 spaceBefore=6, spaceAfter=3, alignment=TA_LEFT)

# ── Helpers ───────────────────────────────────────────────────────────────────

def P(text, style=None):
    """Paragraph shorthand"""
    if style is None:
        style = sNormal
    return Paragraph(text, style)

def bullet(text, style=None):
    if style is None:
        style = sBullet
    return Paragraph(f'• {text}', style)

def subbullet(text, prefix='–'):
    return Paragraph(f'{prefix} {text}', sSubBullet)

def italic_item(num, text):
    return Paragraph(f'{num}. <i>{text}</i>', sNormalLeft)

def section_header(text):
    return Paragraph(f'<b>{text}</b>', sSectionHdr)

def fn(num, text):
    """Footnote paragraph"""
    return Paragraph(f'<super><font size=7>{num}</font></super> {text}', sFootnote)

def spacer(h=4):
    return Spacer(1, h * mm)

def hr():
    return HRFlowable(width='100%', thickness=0.5, color=colors.grey)

# Shaded box using a Table wrapper
def shaded_box(items):
    """items: list of Paragraphs/flowables to put inside a light grey box"""
    inner = []
    for item in items:
        inner.append(item)
    tbl = Table([[inner]], colWidths=[PAGE_W - 2*MARGIN])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0f0f0')),
        ('BOX',        (0,0), (-1,-1), 0.5, colors.grey),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
    ]))
    return tbl

def simple_table(headers, rows, col_widths=None):
    """Build a simple bordered table"""
    usable = PAGE_W - 2*MARGIN
    data = []
    if headers:
        data.append([Paragraph(h, sTableHdr) for h in headers])
    for row in rows:
        data.append([Paragraph(str(c), sTableCell) for c in row])
    if col_widths is None:
        n = len(data[0])
        col_widths = [usable / n] * n
    tbl = Table(data, colWidths=col_widths, repeatRows=1 if headers else 0)
    style = [
        ('GRID',        (0,0), (-1,-1), 0.4, colors.grey),
        ('BACKGROUND',  (0,0), (-1, 0 if headers else -1), colors.HexColor('#e0e0e0')),
        ('VALIGN',      (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING',  (0,0), (-1,-1), 3),
        ('BOTTOMPADDING',(0,0),(-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING',(0,0), (-1,-1), 4),
    ]
    tbl.setStyle(TableStyle(style))
    return tbl

# ── Header / Footer ───────────────────────────────────────────────────────────

def on_page(canvas, doc):
    canvas.saveState()
    # Header text
    canvas.setFont('LiberationSans', 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(MARGIN, PAGE_H - MARGIN + 4*mm, DOC_TITLE)
    # Header HR line
    canvas.setStrokeColor(colors.grey)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, PAGE_H - MARGIN + 2*mm, PAGE_W - MARGIN, PAGE_H - MARGIN + 2*mm)
    # Page number
    canvas.setFont('LiberationSans', 8)
    canvas.setFillColor(colors.grey)
    canvas.drawCentredString(PAGE_W/2, MARGIN/2, str(doc.page))
    canvas.restoreState()

# ── Document build ────────────────────────────────────────────────────────────

def build():
    import os
    os.makedirs('/workspace/tmp', exist_ok=True)

    doc = SimpleDocTemplate(
        '/workspace/tmp/ZVRK-complete.pdf',
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN + 6*mm,  # extra for header
        bottomMargin=MARGIN + 4*mm,
        title=DOC_TITLE,
        author='Računsko sodišče RS',
        subject='Funkcionalne zahteve podpora revizijam ZVRK',
        creator='build_full_pdf.py',
    )

    story = []

    # ── PAGE 1: Naslovnica + Kazalo ─────────────────────────────────────────
    story.append(spacer(20))
    story.append(P(DOC_TITLE, sTitle))
    story.append(spacer(12))
    story.append(P('KAZALO', sSubtitle))
    story.append(spacer(4))
    story.append(hr())
    story.append(spacer(4))

    toc_items = [
        ('1. Uvod', '4', 0),
        ('2. Revizije po ZVRK', '5', 0),
        ('2.1 Opis vrste revizij', '5', 1),
        ('2.2 Glavna cilja revizij', '5', 1),
        ('2.3 Tveganja na podlagi preteklih revizij in tveganja, ki izhajajo iz zakonskih določil', '5', 1),
        ('2.4 Obseg revizij', '7', 1),
        ('2.5 Dodatni pregledi', '7', 1),
        ('3. Naloge v revizijskem postopku in možnosti za njihovo avtomatizacijo', '8', 0),
        ('3.1 Zbiranje podatkov in pregled poročil o financiranju volilnih in referendumskih kampanj', '8', 1),
        ('3.1.1 Skupno poročilo – priloga 1', '8', 2),
        ('3.1.2 Skupni izdatki - priloga 3', '10', 2),
        ('3.2 Drugi viri podatkov za izvedo revizije in njihova priprava za revizijske korake', '13', 1),
        ('3.3 Priprava PNR', '14', 1),
        ('3.4 Izvedba preizkusov podatkov na prihodkovni strani', '16', 1),
        ('3.5 Izvedba preizkusov podatkov na odhodkovni strani', '17', 1),
        ('3.6 Priprava ORP', '18', 1),
    ]
    for title, pg, level in toc_items:
        if level == 0:
            st = sTOC
        elif level == 1:
            st = sTOCSub
        else:
            st = sTOCSub2
        row = Table([[Paragraph(title, st), Paragraph(pg, S('pg', fontSize=10, leading=14, alignment=TA_RIGHT))]],
                    colWidths=[PAGE_W - 2*MARGIN - 15*mm, 15*mm])
        row.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 1),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(row)

    story.append(PageBreak())

    # ── PAGE 2: Avtorizacija ────────────────────────────────────────────────
    story.append(P('AVTORIZACIJA ZAHTEVE', sH1))
    story.append(spacer(2))
    story.append(P(
        'Previdno sem pregledal/-a dokument funkcionalnih zahtev za projekt rešitve, '
        'ki bi podpirala izvajanje revizij volilnih kampanj na podlagi Zakona o volilni '
        'in referendumski kampanji<super><font size=7>1</font></super> (v nadaljevanju: ZVRK).',
        sNormal))
    story.append(spacer(4))
    story.append(P('<b>Avtorizacija odgovorne osebe</b> – Prosimo, označite ustrezno izjavo.', sNormalLeft))
    story.append(spacer(2))
    story.append(P('____ Dokument je sprejet.', sNormalLeft))
    story.append(P('____ Dokument je sprejet, vendar z upoštevanjem navedenih sprememb.', sNormalLeft))
    story.append(P('____ Dokument ni sprejet.', sNormalLeft))
    story.append(spacer(4))
    story.append(P(
        'Popolnoma sprejemamo spremembe kot potrebne izboljšave in pooblaščamo začetek dela. '
        'Na podlagi naše avtoritete in presoje je nadaljnje delovanje tega sistema odobreno.',
        sNormal))
    story.append(spacer(6))

    # Signature table
    sig_data = [
        [Paragraph('<b>IME</b>', sTableHdr), Paragraph('<b>DATUM</b>', sTableHdr)],
        [Paragraph('Vodja projekta', sTableCell), Paragraph('', sTableCell)],
        [Paragraph('<b>IME</b>', sTableHdr), Paragraph('<b>DATUM</b>', sTableHdr)],
        [Paragraph('Direktor', sTableCell), Paragraph('', sTableCell)],
    ]
    sig_col = [(PAGE_W - 2*MARGIN) / 2] * 2
    sig_tbl = Table(sig_data, colWidths=sig_col)
    sig_tbl.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e0e0e0')),
        ('BACKGROUND', (0,2), (-1,2), colors.HexColor('#e0e0e0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(sig_tbl)
    story.append(spacer(4))
    story.append(P('Po potrebi dodajte druga imena in vloge.', sSmall))
    story.append(spacer(8))
    story.append(hr())
    story.append(fn('1', 'Uradni list RS, št. 41/07, 103/07 – ZPolS-D, 11/11, 28/11 – odl. US in 98/13.'))
    story.append(PageBreak())

    # ── PAGE 3: Uvod ────────────────────────────────────────────────────────
    story.append(P('1. Uvod', sH1))
    story.append(P(
        'Dokument povzema revizijske naloge pri revizijah po ZVRK, ki bi mogoče potencialno '
        'avtomatiziirati.',
        sNormal))
    story.append(P(
        'Poleg naštetih, bi bilo mogoče avtomatiziirati tudi druge naloge (npr. različne '
        'preverbe v zvezi z organizatorji volilne kampanje in TRR kampanje, ki jih pridobimo '
        'iz AJPES), vendar bi bilo to smiselno izvesti v drugi fazi avtomatizacije.',
        sNormal))
    story.append(P(
        'Natančni koraki avtomatizacije bodo pripravljeni v dokumentih Use case, ki bodo '
        'izdelani za vsako posamezno funkcionalnost. V Use Case dokumentih bomo priložili '
        'tudi primere dokumentacije.',
        sNormal))
    story.append(PageBreak())

    # ── PAGE 4: Revizije po ZVRK ─────────────────────────────────────────────
    story.append(P('2. Revizije po ZVRK', sH1))
    story.append(P('2.1 Opis vrste revizij', sH2))
    story.append(P(
        'Predmet teh revizij je financiranje volilnih kampanj političnih strank, list ali '
        'drugih organizatorjev volilnih kampanj. Revizije obsegajo pregled zbranih in '
        'porabljenih sredstev za volilno kampanjo, pravilnost njihovega zbiranja in porabe, '
        'skladnost poročanja z zakonodajnimi zahtevami ter pregled drugih vidikov poslovanja '
        'organizatorjev, ki jih določajo relevantni zakoni in predpisi.',
        sNormal))
    story.append(spacer(2))
    story.append(P('2.2 Glavna cilja revizij', sH2))
    story.append(bullet('Podati mnenje o skladnosti poslovanja z veljavno zakonodajo, ki ureja financiranje volilnih kampanj.'))
    story.append(bullet('Podati mnenje o pravilnosti in skladnosti poročanja o financiranju volilnih kampanj.'))
    story.append(spacer(2))
    story.append(P('2.3 Tveganja na podlagi preteklih revizij in tveganja, ki izhajajo iz zakonskih določil', sH2))
    story.append(P(
        'Analiza ugotovitev iz preteklih revizij in analiza tveganj, ki izhajajo iz ZVRK, '
        'kaže, da pri financiranju volilne kampanje obstajajo naslednja tveganja:',
        sNormal))
    tveganja_1 = [
        'organizator volilne kampanje ni odprl posebnega računa;',
        'organizator volilne kampanje je prepozno odprl posebni račun;',
        'organizator volilne kampanje ni zaprl posebnega računa;',
        'organizator volilne kampanje je prepozno zaprl posebni račun;',
        'organizator volilne kampanje ni poravnal vseh stroškov financiranja kampanje, posebni račun pa je zaprl;',
        'organizator volilne kampanje ni na AJPES poslal poročila o kampanji;',
        'organizator volilne kampanje je na AJPES prepozno poslal poročilo o kampanji;',
        'organizator volilne kampanje ni na AJPES poslal poročila o kampanji v predpisani obliki (na predpisanih obrazcih);',
        'organizator volilne kampanje ni na AJPES poslal popolnega poročila o kampanji (organizator ni poročal o vseh obveznih zneskih in ni navedel vseh podatkov na obveznih obrazcih);',
        'organizator volilne kampanje ni zbral vseh sredstev za volilno kampanjo na posebnem računu;',
        'organizator volilne kampanje med zbranimi sredstvi za volilno kampanjo ni upošteval vseh nedenarnih prispevkov;',
        'organizator volilne kampanje ni poravnal vseh stroškov volilne kampanje s posebnega računa;',
    ]
    for t in tveganja_1:
        story.append(bullet(t))
    story.append(PageBreak())

    # ── PAGE 5 ───────────────────────────────────────────────────────────────
    tveganja_2 = [
        'organizator volilne kampanje je prejel prispevke fizičnih oseb (v denarju ali druge oblike prispevkov), ki so višji kot 10 povprečnih plač na delavca v Republiki Sloveniji po podatkih SURS za preteklo leto in jih ni nakazal v humanitarne namene v 30 dneh od prejema;',
        'organizator volilne kampanje je prejel prispevke fizičnih oseb v gotovini, ki so višji od 50 EUR in niso bili vplačani preko bank, hranilnic ali drugih oseb, ki opravljajo plačilne storitve, in jih ni nakazal v humanitarne namene v 30 dneh od prejema;',
        'organizator volilne kampanje je prejel prispevek državnih organov, organov lokalnih skupnosti, pravnih oseb javnega in zasebnega prava ter samostojnih podjetnikov posameznikov in posameznikov, ki samostojno opravljajo dejavnost in jih ni nakazal v humanitarne namene v 30 dneh od prejema;',
        'organizator volilne kampanje je prejel prispevke tujih pravnih oseb in fizičnih oseb, ki ne izpolnjujejo pogojev iz šestega odstavka 14. člena ZVRK, in jih ni nakazal v humanitarne namene v 30 dneh od prejema;',
        'organizator volilne kampanje ni zagotovil zadostnih podatkov za potrditev, da je dajalec prispevka državljan Republike Slovenije oziroma državljan države članice Evropske unije (šesti odstavek 14. člena ZVRK);',
        'organizator volilne kampanje je prenesel sredstva s svojega transakcijskega računa na posebni račun v nasprotju z ZVRK in jih ni nakazal v humanitarne namene v 30 dneh od prejema;',
        'organizator volilne kampanje med stroške volilne kampanje šteje tudi stroške, ki ne sodijo med stroške volilne kampanje;',
        'organizator volilne kampanje med stroške volilne kampanje ni štel vseh stroškov, ki sodijo med stroške volilne kampanje;',
        'organizator volilne kampanje in fizične osebe, ki so zanj opravile storitev ali mu prodale blago, niso sklenili ustrezne pogodbe v pisni obliki;',
        'organizator volilne kampanje, ki ni politična stranka, ob zaprtju posebnega računa ni nakazal presežka zbranih sredstev v humanitarne namene;',
        'organizator volilne kampanje je prejel posojilo od osebe, ki ni banka ali hranilnica;',
        'organizator volilne kampanje je prejel posojilo pod ugodnejšimi pogoji kot druge osebe;',
        'datum zapadlosti prejetega posojila je bil daljši od 30 dni pred rokom za zaprtje posebnega računa;',
        'stroški volilne kampanje so presegli dovoljeno mejo 0,40 EUR na volilnega upravičenca;',
    ]
    for t in tveganja_2:
        story.append(bullet(t))
    story.append(bullet('podatki v poročilu o kampanji niso točni:'))
    nepravilnosti = [
        'organizator volilne kampanje je nepravilno izkazal višino zbranih sredstev (priloga 1, priloga 2);',
        'organizatorji volilne kampanje je nepravilno izkazal skupno višino porabljenih sredstev (priloga 1, priloga 3);',
        'organizator volilne kampanje je nepravilno izkazal presežek zbranih sredstev (priloga 1);',
        'organizator volilne kampanje, ki ni politična stranka, je nepravilno izkazal nakazilo presežka zbranih sredstev v humanitarne namene (priloga 1);',
        'organizator volilne kampanje je nepravilno izkazal neplačane obveznosti (priloga 1);',
    ]
    for n in nepravilnosti:
        story.append(subbullet(n))
    story.append(PageBreak())

    # ── PAGE 6 ───────────────────────────────────────────────────────────────
    nepravilnosti_2 = [
        'organizator volilne kampanje je nepravilno izkazal skupni znesek posojil (priloga 1, priloga 4);',
        'organizator volilne kampanje je nepravilno izkazal skupni znesek prispevkov, ki so zbrani v nasprotju z ZVRK (priloga 1, priloga 5);',
        'organizator volilne kampanje je nepravilno izkazal skupni znesek nakazil prispevkov, ki so bili zbrani v nasprotju z ZVRK, v humanitarne namene (priloga 1, priloga 6);',
        'organizator volilne kampanje je v poročilu o kampanji napačno navedel druge podatke, ki izhajajo iz obveznih prilog 2–6.',
    ]
    for n in nepravilnosti_2:
        story.append(subbullet(n))
    story.append(spacer(4))

    story.append(P('2.4 Obseg revizij', sH2))
    story.append(P(
        'Revizije se načrtujejo in izvajajo z namenom pridobitve razumnega zagotovila za '
        'presojo pravilnosti financiranja volilne kampanje. Obseg preverjanja temelji na '
        'določbah zakonodaje in predpisov, kar vključuje:',
        sNormal))
    story.append(bullet('Analizo višine zbranih in porabljenih sredstev za volilne kampanje.'))
    story.append(bullet('Preverjanje skladnosti pridobivanja in uporabe sredstev z zakonodajnimi zahtevami.'))
    story.append(bullet('Preverjanje točnosti poročil o financiranju volilnih kampanj.'))
    story.append(bullet('Preverjanje pravočasnega odpiranja in zapiranja posebnih računov ter predložitve poročil v zahtevanih rokih.'))
    story.append(spacer(2))
    story.append(P('2.5 Dodatni pregledi', sH2))
    story.append(P(
        'Revizije vključujejo tudi izračun višine povračil stroškov volilnih kampanj, do '
        'katerih so organizatorji upravičeni, in preverjanje skladnosti z omejitvami glede '
        'maksimalne porabe sredstev. Obenem se preverja, ali organizatorji zaradi prekoračitve '
        'omejitev izgubijo pravico do financiranja iz javnih sredstev.',
        sNormal))
    story.append(PageBreak())

    # ── PAGE 7 ───────────────────────────────────────────────────────────────
    story.append(P('3. Naloge v revizijskem postopku in možnosti za njihovo avtomatizacijo', sH1))
    story.append(P('3.1 Zbiranje podatkov in pregled poročil o financiranju volilnih in referendumskih kampanj', sH2))
    story.append(P('3.1.1 Skupno poročilo – priloga 1', sH3))
    story.append(P(
        'Glavni vir podatkov za izvedbo revizije so poročila o financiranju volilnih in '
        'referendumskih kampanj. Organizator volilne kampanje je v skladu s prvim odstavkom '
        '18. člena ZVRK dolžan najpozneje v 15 dneh po zaprtju posebnega računa predložiti '
        'poročilo o kampanji AJPES preko spletnega portala AJPES.',
        sNormal))
    story.append(P(
        'Skladno z drugim odstavkom 18. člena ZVRK mora organizator volilne kampanje v '
        'poročilu o kampanji poročati o:',
        sNormal))
    porocati_items = [
        ('1.', 'skupni višini zbranih in porabljenih sredstev za volilno kampanjo,'),
        ('2.', 'višini prispevkov, ki jih je organizator volilne kampanje s svojega transakcijskega računa prenesel na posebni transakcijski račun v skladu s sedmim odstavkom 14. člena ZVRK,'),
        ('3.', 'vseh posameznih prispevkih fizičnih oseb, ki na dan glasovanja presegajo povprečno bruto mesečno plačo na delavca v Republiki Sloveniji po podatkih SURS za preteklo leto, vključno z navedbo imena, priimka in naslova fizične osebe ter višine prispevka,'),
        ('4.', 'vseh posameznih izdatkih, ki jih je organizator volilne kampanje namenil za financiranje volilne kampanje, vključno z navedbo zneska, ne glede na njegovo višino, skupaj z namenom in izvajalcem storitev oziroma prodajalcem izdelka,'),
        ('5.', 'vseh posameznih posojilih, ki jih organizatorju volilne kampanje da banka ali posojilnica, vključno z navedbo podatkov o firmi, sedežu, poslovnem naslovu in matični številki banke ali posojilnice, obrestni meri, odplačilni dobi ter višini posojila,'),
        ('6.', 'vseh posameznih prispevkih, ki so bili organizatorju volilne kampanje dani v nasprotju z ZVRK, ter njihove vrednosti, vključno z navedbo podatkov o firmi oziroma imenu in sedežu pravne osebe ali samostojnega podjetnika oziroma podatkov o osebnem imenu in naslovu posameznika, ki je dal prispevek,'),
        ('7.', 'vseh nakazilih presežkov zbranih sredstev organizatorja volilne kampanje iz prvega odstavka 22. člena ZVRK in prispevkov, ki so bili organizatorju volilne kampanje dani v nasprotju z ZVRK, v humanitarne namene.'),
    ]
    for num, text in porocati_items:
        row = Table([[Paragraph(num, sNormalLeft), Paragraph(text, sNormal)]],
                    colWidths=[8*mm, PAGE_W - 2*MARGIN - 8*mm])
        row.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(row)
    story.append(PageBreak())

    # ── PAGE 8 ───────────────────────────────────────────────────────────────
    story.append(P(
        'V skladu s Pravilnikom o vsebini in obrazcih poročil o zbranih in porabljenih '
        'sredstvih za volilno in referendumsko kampanjo<super><font size=7>2</font></super> '
        '(v nadaljevanju: pravilnik) mora organizator volilne kampanje poročilo o kampanji '
        'pripraviti na posebnih obrazcih<super><font size=7>3</font></super>. Obrazec za '
        'poročilo o kampanji, ki ga mora predložiti organizator volilne kampanje, prikazuje Tabela 1.',
        sNormal))
    story.append(spacer(2))
    story.append(P('<b>Tabela 1</b> Poročilo o kampanji (Obrazec 3)', sNormalLeft))
    story.append(spacer(2))

    # Table 1 - Porocilo o kampanji
    usable = PAGE_W - 2*MARGIN
    t1_data = [
        [Paragraph('<b>Vsebina</b>', sTableHdr), Paragraph('<b>Znesek</b>', sTableHdr)],
        [Paragraph('<b>I. SKUPNA VIŠINA ZBRANIH SREDSTEV (1 + 2 + 3 + 4)</b>', sTableCell), ''],
        [Paragraph('1. Denarni prispevki (1.1 + 1.2)', sTableCell), ''],
        [Paragraph('   1.1 Prispevki v gotovini', sTableCell), ''],
        [Paragraph('   1.2 Prispevki, vplačani na posebni transakcijski račun', sTableCell), ''],
        [Paragraph('2. Druge oblike prispevkov (2.1 + 2.2 + 2.3 + 2.4)', sTableCell), ''],
        [Paragraph('   2.1 Brezplačne storitve', sTableCell), ''],
        [Paragraph('   2.2 Izredni popusti', sTableCell), ''],
        [Paragraph('   2.3 Prevzem obveznosti', sTableCell), ''],
        [Paragraph('   2.4 Druge oblike nedenarnih prispevkov', sTableCell), ''],
        [Paragraph('3. Sredstva, ki jih je organizator kampanje prenesel s svojega transakcijskega računa na posebni transakcijski račun', sTableCell), ''],
        [Paragraph('   3.1 Lastna sredstva organizatorja, ki je politična stranka', sTableCell), ''],
        [Paragraph('   3.2 Nakazila sredstev političnih strank na redni račun politične stranke, ki je organizator kampanje, ko več političnih strank vloži skupno listo', sTableCell), ''],
        [Paragraph('4. Obresti sredstev avista', sTableCell), ''],
        [Paragraph('<b>II. SKUPNA VIŠINA PORABLJENIH SREDSTEV (1 + 2 + 3 + 4 + 5 + 6 + 7 + 8)</b>', sTableCell), ''],
        [Paragraph('1. Stroški oblikovanja, tiskanja, razobešanja in odstranjevanja plakatov', sTableCell), ''],
        [Paragraph('2. Stroški oblikovanja in objavljanja predvolilnih oglaševalskih vsebin v medijih', sTableCell), ''],
        [Paragraph('3. Stroški organizacije in izvedbe predvolilnih shodov', sTableCell), ''],
        [Paragraph('4. Stroški oblikovanja, tiskanja, reprodukcije in razpošiljanja predvolilnega materiala iz 7. člena ZVRK', sTableCell), ''],
        [Paragraph('5. Stroški odprtja, vodenja in zaprtja posebnega transakcijskega računa', sTableCell), ''],
        [Paragraph('6. Stroški svetovanja za načrtovanje strategije ali posamičnih delov volilne kampanje', sTableCell), ''],
        [Paragraph('7. Drugi sorodni stroški, ki so nastali zaradi dejanj volilne kampanje', sTableCell), ''],
        [Paragraph('8. Obresti in drugi stroški za posojila', sTableCell), ''],
        [Paragraph('<b>III. PRESEŽEK ZBRANIH SREDSTEV (I–II)</b>', sTableCell), ''],
        [Paragraph('<b>IV. NAKAZILO PRESEŽKA ZBRANIH SREDSTEV V HUMANITARNE NAMENE</b>', sTableCell), ''],
        [Paragraph('<b>V. NEPLAČANE OBVEZNOSTI</b>', sTableCell), ''],
    ]
    t1 = Table(t1_data, colWidths=[usable * 0.78, usable * 0.22])
    t1.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#d0d0d0')),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#e8e8e8')),
        ('BACKGROUND', (0,14), (-1,14), colors.HexColor('#e8e8e8')),
        ('BACKGROUND', (0,23), (-1,25), colors.HexColor('#e8e8e8')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t1)
    story.append(spacer(4))
    story.append(hr())
    story.append(fn('2', 'Uradni list RS, št. 36/14.'))
    story.append(fn('3', 'Organizator volilne kampanje mora v skladu s pravilnikom poleg poročila o kampanji predložiti še Prilogo 2 – Seznam prispevkov fizičnih oseb, Prilogo 3 – Seznam izdatkov, Prilogo 4 – Seznam posojil, Prilogo 5 – Seznam prispevkov, zbranih v nasprotju z ZVRK, in Prilogo 6 – Seznam nakazil v humanitarne namene.'))
    story.append(PageBreak())

    # ── PAGE 9 ───────────────────────────────────────────────────────────────
    # Continuation of table 1
    t1b_data = [
        [Paragraph('<b>Vsebina</b>', sTableHdr), Paragraph('<b>Znesek</b>', sTableHdr)],
        [Paragraph('<b>VI. SKUPNI ZNESEK PRISPEVKOV, KI NA DAN GLASOVANJA PRESEGAJO POVPREČNO BRUTO MESEČNO PLAČO NA DELAVCA V RS PO PODATKIH SURS ZA PRETEKLO LETO</b>', sTableCell), ''],
        [Paragraph('<b>VII. SKUPNI ZNESEK POSOJIL, KI SO ODOBRENA ORGANIZATORJU KAMPANJE</b>', sTableCell), ''],
        [Paragraph('<b>VIII. SKUPNI ZNESEK PRISPEVKOV, KI SO ZBRANI V NASPROTJU Z ZVRK</b>', sTableCell), ''],
        [Paragraph('<b>IX. SKUPNI ZNESEK NAKAZIL PRISPEVKOV, KI SO ZBRANI V NASPROTJU Z ZVRK V HUMANITARNE NAMENE</b>', sTableCell), ''],
    ]
    t1b = Table(t1b_data, colWidths=[usable * 0.78, usable * 0.22])
    t1b.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#d0d0d0')),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#e8e8e8')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t1b)
    story.append(P('<i>Vir: Poročilo o kampanji.</i>', sSmall))
    story.append(spacer(6))

    story.append(shaded_box([
        P('<b>Primeri nalog, ki bi jih bilo mogoče avtomatizirati v zvezi z analizo poročil '
          'o financiranju volilnih in referendumskih kampanj:</b>', sBoxTitle),
        bullet('izvoz obrazca 3 v obliko, berljivo programu Excel', sBoxBullet),
        bullet('rekalkulacija vsot v obrazcu in alarmi ob morebitnih manjkajočih podatkih', sBoxBullet),
    ]))
    story.append(spacer(6))

    story.append(P('3.1.2 Skupni izdatki - priloga 3', sH3))
    story.append(P(
        'Organizator volilne kampanje mora poročati tudi o skupnih izdatkih za volilno '
        'kampanjo. Porabljena sredstva za volilno kampanjo so vsi stroški, ki so potrebni '
        'za izvedbo volilne kampanje<super><font size=7>4</font></super>, vključno z drugimi '
        'oblikami prispevkov.<super><font size=7>5</font></super>',
        sNormal))
    story.append(P(
        'Stroški volilne kampanje so glede na določila ZVRK opredeljeni po namenu, času in '
        'vrsti. Namen je določen z zakonsko opredelitvijo volilne kampanje. To so vse politične '
        'oglaševalske vsebine in druge oblike politične propagande, katerih namen je vplivati '
        'na odločanje volivk in volivcev pri glasovanju na volitvah.<super><font size=7>6</font></super>',
        sNormal))
    story.append(P(
        'Stroški so časovno vezani na obdobje volilne kampanje, ki se lahko začne najprej '
        '30 dni pred dnem glasovanja, končati pa se mora najkasneje 24 ur pred dnem '
        'glasovanja. Volilna kampanja za volitve v Evropski parlament v letu 2024 se je '
        'začela 9. 5. 2024 in se je končala 7. 6. 2024 ob 24. uri.',
        sNormal))
    story.append(P(
        'Med stroške volilne kampanje, ki so potrebni za izvedbo volitev, ZVRK<super><font size=7>7</font></super> uvršča:',
        sNormal))
    stroški = [
        'stroške oblikovanja, tiskanja, razobešanja in odstranjevanja plakatov,',
        'stroške oblikovanja in objavljanja predvolilnih oglaševalskih vsebin v medijih,',
        'stroške organizacije in izvedbe predvolilnih shodov,',
        'stroške oblikovanja, tiskanja, reprodukcije in razpošiljanja predvolilnega materiala iz 7. člena ZVRK,',
    ]
    for s in stroški:
        story.append(bullet(s))
    story.append(spacer(4))
    story.append(hr())
    story.append(fn('4', 'Prvi odstavek 15. člena ZVRK.'))
    story.append(fn('5', 'K skupni višini porabljenih sredstev je treba prišteti tudi zneske drugih oblik prispevkov, kot je določeno v 2. točki tretjega odstavka 2. člena pravilnika.'))
    story.append(fn('6', 'Drugi odstavek 1. člena ZVRK.'))
    story.append(fn('7', 'Drugi odstavek 15. člena ZVRK.'))
    story.append(PageBreak())

    # ── PAGE 10 ──────────────────────────────────────────────────────────────
    stroški_2 = [
        'stroške odprtja, vodenja in zaprtja posebnega računa,',
        'stroške svetovanja za načrtovanje strategije ali posamičnih delov volilne kampanje in njihove rabe ter volilne taktike in',
        'druge sorodne stroške, ki so nastali zaradi dejanj volilne kampanje.<super><font size=7>8</font></super>',
    ]
    for s in stroški_2:
        story.append(bullet(s))
    story.append(P(
        'Med stroške volilne kampanje se štejejo vsi navedeni stroški ne glede na to, kdaj '
        'so nastali, kdaj so bili plačani in kdaj so bili sklenjeni posli v zvezi s '
        'posameznimi dejanji volilne kampanje, če se stroški in posli nanašajo na obdobje '
        'volilne kampanje iz 2. člena ZVRK. Med stroške volilne kampanje se ne štejejo '
        'stroški zbiranja podpisov in stroški, nastali po obdobju volilne kampanje, razen '
        'stroškov odstranjevanja plakatov in stroškov vodenja in zaprtja posebnega '
        'računa<super><font size=7>9</font></super>.',
        sNormal))
    story.append(P(
        'Stroški volilne kampanje za volitve v Evropski parlament ne smejo preseči '
        '0,40 EUR na posameznega volilnega upravičenca v državi.<super><font size=7>10</font></super>',
        sNormal))
    story.append(P(
        'Organizator volilne kampanje mora stroške kampanje izkazati v tabeli, ki je '
        'objavljena v prilogi 3 pravilnika.',
        sNormal))
    story.append(spacer(2))
    story.append(P('<b>Tabela 2</b> Izdatki in dobavitelji', sNormalLeft))
    story.append(spacer(2))

    cw3 = [usable * 0.50, usable * 0.25, usable * 0.25]
    t2a_data = [
        [Paragraph('<b>Firma/ime dobavitelja in njegov sedež/naslov</b>', sTableHdr),
         Paragraph('<b>Št. računa</b>', sTableHdr),
         Paragraph('<b>Znesek v EUR s centi</b>', sTableHdr)],
        [Paragraph('<b>I. STROŠKI ZUNANJIH IZVAJALCEV (1 + 2 + 3 + 4 + 5 + 6 + 7 + 8)</b>', sTableCell), '', ''],
        [Paragraph('1. Stroški oblikovanja, tiskanja, razobešanja in odstranjevanja plakatov (skupaj)', sTableCell), '', ''],
        [Paragraph('   1.1', sTableCell), '', ''],
        [Paragraph('   1.2', sTableCell), '', ''],
        [Paragraph('2. Stroški oblikovanja in objavljanja predvolilnih/predreferendumskih oglaševalskih vsebin v medijih (skupaj)', sTableCell), '', ''],
        [Paragraph('   2.1', sTableCell), '', ''],
        [Paragraph('   2.2', sTableCell), '', ''],
    ]
    t2a = Table(t2a_data, colWidths=cw3)
    t2a.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#d0d0d0')),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#e8e8e8')),
        ('SPAN', (0,1), (2,1)),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t2a)
    story.append(spacer(4))
    story.append(hr())
    story.append(fn('8', 'Skladno s 3. členom pravilnika se kot porabljena sredstva štejejo tudi obresti ter drugi stroški za posojila.'))
    story.append(fn('9', 'Četrti odstavek 15. člena ZVRK.'))
    story.append(fn('10', 'Drugi odstavek 16. člena ZVRK.'))
    story.append(PageBreak())

    # ── PAGE 11 ──────────────────────────────────────────────────────────────
    t2b_data = [
        [Paragraph('<b>Firma/ime dobavitelja in njegov sedež/naslov</b>', sTableHdr),
         Paragraph('<b>Št. računa</b>', sTableHdr),
         Paragraph('<b>Znesek v EUR s centi</b>', sTableHdr)],
        [Paragraph('3. Stroški organizacije in izvedbe predvolilnih/predreferendumskih shodov (3. točka drugega odstavka 15. člena Zakona o volilni in referendumski kampanji) (skupaj)', sTableCell), '', ''],
        [Paragraph('   3.1', sTableCell), '', ''],
        [Paragraph('   3.2', sTableCell), '', ''],
        [Paragraph('4. Stroški oblikovanja, tiskanja, reprodukcije in razpošiljanja predvolilnega/predreferendumskega materiala iz 7. člena Zakona o volilni in referendumski kampanji (4. točka drugega odstavka 15. člena Zakona o volilni in referendumski kampanji) (skupaj)', sTableCell), '', ''],
        [Paragraph('   4.1', sTableCell), '', ''],
        [Paragraph('   4.2', sTableCell), '', ''],
        [Paragraph('5. Stroški odprtja, vodenja in zaprtja posebnega transakcijskega računa (5. točka drugega odstavka 15. člena Zakona o volilni in referendumski kampanji) (skupaj)', sTableCell), '', ''],
        [Paragraph('   5.1', sTableCell), '', ''],
        [Paragraph('   5.2', sTableCell), '', ''],
        [Paragraph('6. Stroški svetovanja za načrtovanje strategije ali posamičnih delov volilne/referendumske kampanje in njihove rabe ter volilne taktike (6. točka drugega odstavka 15. člena Zakona o volilni in referendumski kampanji) (skupaj)', sTableCell), '', ''],
        [Paragraph('   6.1', sTableCell), '', ''],
        [Paragraph('   6.2', sTableCell), '', ''],
        [Paragraph('7. Drugi sorodni stroški, ki so nastali zaradi dejanj volilne/referendumske kampanje (7. točka drugega odstavka 15. člena Zakona o volilni in referendumski kampanji) (skupaj)', sTableCell), '', ''],
        [Paragraph('   7.1', sTableCell), '', ''],
        [Paragraph('   7.2', sTableCell), '', ''],
        [Paragraph('8. Obresti in drugi stroški za posojila (skupaj)', sTableCell), '', ''],
        [Paragraph('<b>II. STROŠKI NOTRANJIH ORGANIZACIJSKIH ENOT POLITIČNE STRANKE (skupaj)</b>', sTableCell), '', ''],
        [Paragraph('   1.', sTableCell), '', ''],
        [Paragraph('   2.', sTableCell), '', ''],
    ]
    t2b = Table(t2b_data, colWidths=cw3)
    t2b.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#d0d0d0')),
        ('BACKGROUND', (0,17), (-1,17), colors.HexColor('#e8e8e8')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t2b)
    story.append(PageBreak())

    # ── PAGE 12 ──────────────────────────────────────────────────────────────
    story.append(shaded_box([
        P('<b>Primeri nalog, ki bi jih bilo mogoče avtomatizirati v zvezi z analizo poročil '
          'o financiranju volilnih in referendumskih kampanj:</b>', sBoxTitle),
        bullet('izvoz obrazca 3 v obliko, berljivo programu Excel', sBoxBullet),
        bullet('rekalkulacija vsot v obrazcu in alarmi ob morebitnih manjkajočih podatkih', sBoxBullet),
    ]))
    story.append(spacer(6))

    story.append(P('3.2 Drugi viri podatkov za izvedo revizije in njihova priprava za revizijske korake', sH2))
    story.append(P(
        'Z namenom, da bi izvedba revizije potekala čim bolj časovno učinkovito, revidirance '
        'prosimo, da predložijo naslednjo dokumentacijo in podatke:',
        sNormal))
    doc_items = [
        'poročilo o financiranju volilne kampanje, oddano na AJPES;',
        'akt o imenovanju osebe, odgovorne za finančno in materialno poslovanje politične stranke v obdobju, na katero se nanaša revizija, in v času izvedbe revizije;',
        'statut politične stranke, veljaven v obdobju, na katero se nanaša revizija, in v času izvedbe revizije;',
        'ime, priimek, telefonsko številko in elektronski naslov primarne kontaktne osebe za potrebe revizije;',
        'pogodbo o odprtju posebnega transakcijskega računa za volilno kampanjo (v nadaljevanju: posebni račun) in dokazilo o zaprtju posebnega računa;',
        'bančne izpiske o prometu na posebnem računu v obliki, ki jo uporablja Microsoft Excel (v nadaljevanju: excelova oblika);',
        'originalne bančne izpiske o prometu na posebnem računu v elektronski ali papirni obliki;',
        'vse originalne verodostojne knjigovodske listine, ki se nanašajo na stroške volilne kampanje (račune, pogodbe ipd.) ali pojasnila, zakaj je bilo plačilo stroškov izvedeno brez listin;',
        'dokazila o opravljeni storitvi ali dobavi blaga za volilno kampanjo, ki so priložena knjigovodskim listinam (npr. izvod letaka, specifikacija opravljenih del, kopije oglasov v medijih, podatki o oglaševanju v spletnih medijih, fotografije z volilnih dogodkov, fotografije plakatov, fotografije reklamnega materiala, ki je bil kupljen, naročilnice, dobavnice, ponudbe, elektronska komunikacija ipd.);',
        'excelovo obliko glavne knjige za prihodke in stroške volilne kampanje po kontih ter kartice dobaviteljev (po transakcijah);',
        'excelovo obliko seznama prispevkov po donatorjih, z njihovimi osebnimi podatki (ime in priimek, EMŠO ali davčna številka ter stalni naslov);',
        'seznam morebitnih nezakonitih prispevkov in nakazil v humanitarne namene ter druge evidence, na podlagi katerih je bilo ali bo sestavljeno poročilo o financiranju volilne kampanje (npr. seznam sredstev organizatorja, nakazanih na posebni račun, seznam vplačil prispevkov v gotovini, evidence o blagajniškem poslovanju, vplačila in odplačila po posojilnih pogodbah ipd.);',
        'originale posojilnih pogodb za volilno kampanjo;',
    ]
    for d in doc_items:
        story.append(bullet(d))
    story.append(PageBreak())

    # ── PAGE 13 ──────────────────────────────────────────────────────────────
    doc_items_2 = [
        'seznam prireditev volilne kampanje, ki jih je organizator organiziral, in seznam prireditev, ki so jih organizirali drugi, kjer so se predstavili kandidati organizatorja (npr. sejmi, okrogle mize /ipd.);',
        'drugo dokumentacijo ali pojasnila po presoji organizatorja.',
    ]
    for d in doc_items_2:
        story.append(bullet(d))
    story.append(spacer(6))

    story.append(shaded_box([
        P('<b>Primeri nalog, ki bi jih bilo mogoče avtomatizirati v zvezi z drugimi prejetimi dokumenti:</b>', sBoxTitle),
        P('√ • bančne izpiske iz banke NLB dobimo v formatu .pdf, ki je strukturiran na način, '
          'da jih ni mogoče enostavno pretvoriti v Excel obliko. To povzroča nepotrebne '
          'časovne obremenitve pri preveritvah izplačil iz TRR; xte podatke bi bilo potrebno '
          'smiselno preoblikovati v Excel obliko;', sBoxText),
        P('<b>√ • prenos podatkov o datumu izdaje, datumu opravljene storitve, vsebini opravljene '
          'storitve, dobavitelju, kontaktni osebi dobavitelja in zneskih iz posameznih faktur, '
          'ki jih pridobimo v formatu .pdf v tabelo v formatu Excel (ta korak je zelo časovno '
          'zamuden in če bi ga bilo mogoče izvesti že vsaj deloma, bi predstavljal veliko '
          'časovno razbremenitev).</b>', sBoxText),
    ]))
    story.append(spacer(6))

    story.append(P('3.3 Priprava PNR', sH2))
    story.append(P(
        'PNR revizij ZVRK sledijo pred-opredeljenemu formatu. Vsak PNR je potrebno prilagoditi '
        'konkretnemu revidirancu. Prilagoditve so:',
        sNormal))
    story.append(spacer(2))
    story.append(section_header('NASLOVNA STRAN in KAZALO'))
    pnr_naslovna = [
        ('1.', 'naslov PNR'),
        ('2.', 'SPIS št in datum,'),
        ('3.', 'glava dokumenta'),
        ('4.', 'kazalo (posodobi)'),
    ]
    for num, text in pnr_naslovna:
        story.append(Paragraph(f'{num} <i>{text}</i>', sNormalLeft))
    story.append(spacer(2))
    story.append(section_header('POGLAVJE 1 - Pravne in strokovne podlage za izvedbo revizije'))
    pnr_pog1 = [
        ('5.', 'naziv revidiranca'),
        ('6.', 'naziv revizije'),
        ('7.', 'sklep v SO'),
        ('8.', 'število glasov in delež'),
        ('9.', 'pri manjšincih: pri odstavku "po 24. členu ..." je treba napisati samo alinejo: "organizatorji volilne kampanje za poslance italijanske in madžarske narodne skupnosti, katerih kandidat je dobil mandat ali najmanj 25 % od skupnega števila izračunanih točk za vse kandidate pripadnike italijanske oziroma madžarske narodne skupnosti"'),
    ]
    for num, text in pnr_pog1:
        story.append(Paragraph(f'{num} <i>{text}</i>', sNormalLeft))
    story.append(spacer(2))
    story.append(section_header('POGLAVJE 3 - Pravne in strokovne podlage za izvedbo revizije'))
    pnr_pog3 = [
        ('10.', 'podatki o revidirancu in odgovorni osebi'),
        ('11.', 'podatki o TRR (številka, odprtje, zaprtje)'),
        ('1.', 'Tabela 1: Poročilo o kampanji vnos podatkov iz poročila o kampanji'),
        ('12.', 'pri manjšincih je treba spremeniti znesek v tč. 3.2.4 (stroški) in SO'),
    ]
    for num, text in pnr_pog3:
        story.append(Paragraph(f'{num} <i>{text}</i>', sNormalLeft))
    story.append(PageBreak())

    # ── PAGE 14 ──────────────────────────────────────────────────────────────
    story.append(Paragraph('13. <i>Tabela 2 Predviden znesek delnega poračila stroškov volilne vnesi izračun za delno poračilo</i>', sNormalLeft))
    story.append(spacer(3))
    story.append(P('14. pri manjšincih: pri odstavku o stroških kampanje, je treba napisati:', sNormalLeft))
    story.append(spacer(2))
    story.append(P(
        '"Glede na navedene podatke stroški volilne kampanje za listo kandidatov ne smejo preseči:',
        sNormal))
    story.append(bullet('za kandidata italijanske narodne skupnosti 1.108,40 EUR<super><font size=7>11</font></super> in'))
    story.append(bullet('za kandidata madžarske narodne skupnosti 2.225,20 EUR<super><font size=7>12</font></super>.'))
    story.append(spacer(2))
    story.append(P(
        'Skladno s sedmim odstavkom 23. člena ZVRK bi lahko stroški posamezne volilne kampanje '
        'dosegli višino minimalne plače v Republiki Sloveniji, ki velja 30. dan pred dnem '
        'glasovanja in sicer v primeru, če bi bili po izračunu iz ZVRK dovoljeni stroški volilne '
        'kampanje nižji, kar pa v konkretnem primeru ne pride v '
        'poštev<super><font size=7>13</font></super>.',
        sNormal))
    story.append(P(
        'V skladu s tretjim odstavkom 24. člena ZVRK so do delnega poračila stroškov volilne '
        'kampanje v višini 0,33 EUR za vsak dobljeni glas upravičeni organizatorji volilne '
        'kampanje za poslance italijanske in madžarske narodne skupnosti, katerih kandidat je '
        'dobil mandat ali najmanj 25 % od skupnega števila izračunanih točk za vse kandidate '
        'pripadnike italijanske oziroma madžarske narodne skupnosti.',
        sNormal))
    story.append(P(
        'Po četrtem odstavku 24. člena ZVRK se za potrebe izračuna višine delnega poračila '
        'stroškov volilne kampanje število dobljenih glasov, ki jih je prejel posamezni '
        'kandidat, izračuna tako, da se njegovo število točk deli s skupnim številom točk, '
        'ki so jih prejeli vsi kandidati, tako dobljeni delež pa se pomnoži s številom vseh '
        'veljavnih glasovnic.',
        sNormal))
    story.append(P(
        'V letu 2021 je bil sprejet Zakon o spremembah in dopolnitvah Zakona o volitvah v '
        'državni zbor<super><font size=7>14</font></super> (v nadaljevanju: ZVDZ-D) na '
        'podlagi katerega je prišlo do sprememb pri ugotavljanju izida volitev. Od uveljavitve '
        'sprememb dalje velja<super><font size=7>15</font></super>, da volilna komisija posebne '
        'volilne enote za volitve poslancev italijanske oziroma madžarske narodne skupnosti '
        'ugotovi, koliko volivcev je vpisano v volilni imenik, koliko od njih je glasovalo, '
        'koliko jih je glasovalo po pošti, koliko glasovnic je bilo neveljavnih in število '
        'glasov, ki so jih dobili posamezni kandidati. Za poslanca italijanske oziroma madžarske '
        'narodne skupnosti je izvoljen tisti kandidat, ki je dobil največje število glasov.',
        sNormal))
    story.append(P(
        'Na podlagi navedenega ugotavljamo, da je ZVDZ-D ukinil točkovanje prednostnega reda '
        'kandidatov, pri tem pa so določbe ZVRK, na podlagi katerih računsko sodišče izvaja '
        'revizije financiranja volilne kampanje, ostale nespremenjene.',
        sNormal))
    story.append(P(
        'Pri organizatorjih volilnih kampanj obeh izvoljenih kandidatov mora računsko sodišče, '
        'v skladu s prvim odstavkom 24. člena ZVRK, v povezavi s prvim odstavkom 29. člena '
        'ZVRK izvesti revizijo',
        sNormal))
    story.append(spacer(4))
    story.append(hr())
    story.append(fn('11', '2.771 volilnih upravičencev z volilno pravico državljana Republike Slovenije, pripadnika avtohtone italijanske narodne skupnosti * 0,4 evra = 1.108,40 EUR'))
    story.append(fn('12', '5.563 volilnih upravičencev z volilno pravico državljana Republike Slovenije, pripadnika avtohtone madžarske narodne skupnosti * 0,4 evra = 2.225,20 EUR.'))
    story.append(fn('13', 'Minimalna plača v Republiki Sloveniji za delo s polnim delovnim časom je 30. dan pred dnem glasovanja znašala 1.074,43 EUR (to je znesek minimalne plače, kot ga je določil minister za delo, družino, socialne zadeve in enake možnosti, Uradni list RS, št. 5/22).'))
    story.append(fn('14', 'Uradni list RS, št. 29/21.'))
    story.append(fn('15', '95. in 96. člen Zakona o volitvah v Državni zbor, Uradni list RS, št. 109/06 – uradno prečiščeno besedilo, 54/07 – odl. US, 23/17 in 29/21.'))
    story.append(PageBreak())

    # ── PAGE 15 ──────────────────────────────────────────────────────────────
    story.append(P(
        'financiranja volilne kampanje in izračunati višino delnega povračila stroškov volilne '
        'kampanje. Zapisnik o ugotovitvi izida volitev pa ne vsebuje podatkov, ki jih računsko '
        'sodišče na podlagi določb ZVRK potrebuje za izračun višine delnega povračila '
        'organizatorjem volilnih kampanj, saj se je način ugotavljanja izida volitev na podlagi '
        'sprememb ZVDZ-D spremenil in zato niso na voljo podatki, ki jih za izračun potrebujemo. '
        'V zapisniku o ugotovitvi izida volitev namreč ni podatka o številu prejetih točk. '
        'Prav tako tudi niso na voljo podatki o skupnem številu izračunanih točk za druge '
        'kandidate pri italijanski in madžarski narodni skupnosti, kar se posledično odraža v '
        'tem, da računsko sodišče ne more nedvoumno določiti vseh organizatorjev volilne '
        'kampanje, pri katerih mora izvesti revizijo.',
        sNormal))
    story.append(P(
        'Zaradi navedenega bomo revizijo izvedli pri obeh izvoljenih predstavnikih narodne '
        'skupnosti, pri čemer v revizijskem poročilu ne bomo izračunali delnega povračila '
        'stroškov volilne kampanje. Bomo pa v revizijskem poročilu navedli višino delnega '
        'povračila stroškov, ki naj bi pripadala organizatorju volilne kampanje, če bi za '
        'izračun uporabili metodologijo, ki jo predlaga Ministrstvo za javno upravo v svojem '
        'mnenju z dne 8. 6. 2022. Poleg tega Pri ostalih 3 organizatorjih volilne kampanje za '
        'predstavnike manjšinske narodne skupnosti, katerih kandidati niso bili izvoljeni v '
        'Državni zbor, ne bomo uvedli revizije, saj menimo, da pravne podlage tega dovoljujejo '
        '(ni podatkov, ki bi omogočali določitev točk in posledično določitev praga nad katerim '
        'mora računsko sodišče opraviti '
        'revizijo)<super><font size=7>16</font></super>.',
        sNormal))
    story.append(spacer(4))
    story.append(section_header('POGLAVJE 5 - Kriteriji za presojo nepravilnosti in napak ter določitev pomembnosti'))
    story.append(Paragraph('15. <i>izračun osnove za določitev pomembnosti v poglavju 5.2.2 Določitev pomembnosti za napake</i>', sNormalLeft))
    story.append(P('16. točka 5.4: navedi, da bomo preverili vse (100%)', sNormalLeft))
    story.append(spacer(2))
    story.append(section_header('POGLAVJE 6 - Viri in časovni okvir izvedbe revizije'))
    story.append(P('17. popravi podatke v tabeli 3: Revizijska skupina z načrtovanim časom za izvedbo revizije', sNormalLeft))
    story.append(P('18. popravi datume pod tabelo', sNormalLeft))
    story.append(P('19. napiši, kdo je pravil načrt', sNormalLeft))
    story.append(spacer(6))

    story.append(shaded_box([
        P('<b>Primeri nalog, ki bi jih bilo mogoče avtomatizirati v zvezi s PNR</b>', sBoxTitle),
        P('√ • Vodja revizij bi lahko kreirala osnutke PNR, v katere bi bili že vneseni podatki, '
          'ki so v zgornjem zapisu označeni v poševnem tisku (morda tudi druge)', sBoxText),
    ]))
    story.append(spacer(6))

    story.append(P('3.4 Izvedba preizkusov podatkov na prihodkovni strani', sH2))
    story.append(P(
        'Preizkusi podatkov na prihodkovni strani zahtevajo vpoglede v osebne podatke in '
        'jih brez povezave v CRP ali AJPES zbirko TRR fizičnih oseb verjetno ni mogoče '
        'pomembno avtomatizirati.',
        sNormal))
    story.append(spacer(4))
    story.append(hr())
    story.append(fn('16', 'Zapis dogovora na sestanku pri predsednici, SPIS št. 425-1/2022/26.'))
    story.append(PageBreak())

    # ── PAGE 16 ──────────────────────────────────────────────────────────────
    story.append(P('3.5 Izvedba preizkusov podatkov na odhodkovni strani', sH2))
    story.append(P(
        'Na odhodkovni strani izvajamo preizkuse podatkov da bi potrdili ali ovrgli '
        'naslednja tveganja:',
        sNormal))
    odh_tveganja = [
        'organizator volilne kampanje ni zbral vseh sredstev za volilno kampanjo na posebnem računu;',
        'organizator volilne kampanje ni poravnal vseh stroškov volilne kampanje s posebnega računa;',
        'organizator volilne kampanje je prenesel sredstva s svojega transakcijskega računa na posebni račun v nasprotju z ZVRK in jih ni nakazal v humanitarne namene v 30 dneh od prejema;',
        'organizator volilne kampanje je med stroške volilne kampanje štel tudi stroške, ki ne sodijo med stroške volilne kampanje;',
        'organizator volilne kampanje med stroške volilne kampanje ni štel vseh stroškov, ki sodijo med stroške volilne kampanje;',
        'organizator volilne kampanje in fizične osebe, ki so zanj opravile storitev ali mu prodale blago, niso sklenili ustrezne pogodbe v pisni obliki;',
        'organizator volilne kampanje, ki ni politična stranka, ob zaprtju posebnega računa ni nakazal presežka zbranih sredstev v humanitarne namene;',
        'stroški volilne kampanje so presegli dovoljeno mejo 0,40 EUR na volilnega upravičenca;',
    ]
    for t in odh_tveganja:
        story.append(bullet(t))
    story.append(bullet('podatki v poročilu o kampanji niso točni:'))
    odh_nepravilnosti = [
        'organizator volilne kampanje je nepravilno izkazal višino zbranih sredstev (priloga 1, priloga 2);',
        'organizatorji volilne kampanje je nepravilno izkazal skupno višino porabljenih sredstev (priloga 1, priloga 3);',
        'organizator volilne kampanje je nepravilno izkazal presežek zbranih sredstev (priloga 1);',
        'organizator volilne kampanje, ki ni politična stranka, je nepravilno izkazal nakazilo presežka zbranih sredstev v humanitarne namene (priloga 1);',
        'organizator volilne kampanje je nepravilno izkazal neplačane obveznosti (priloga 1);',
        'organizator volilne kampanje je nepravilno izkazal skupni znesek posojil (priloga 1, priloga 4);',
        'organizator volilne kampanje je nepravilno izkazal skupni znesek prispevkov, ki so zbrani v nasprotju z ZVRK (priloga 1, priloga 5);',
        'organizator volilne kampanje je nepravilno izkazal skupni znesek nakazil prispevkov, ki so bili zbrani v nasprotju z ZVRK, v humanitarne namene (priloga 1, priloga 6);',
        'organizator volilne kampanje je v poročilu o kampanji napačno navedel druge podatke, ki izhajajo iz obveznih prilog 2-6.',
    ]
    for n in odh_nepravilnosti:
        story.append(subbullet(n, '•'))
    story.append(spacer(4))

    story.append(shaded_box([
        P('<b>Primeri preizkusov podatkov, ki bi jih bilo mogoče avtomatizirati:</b>', sBoxTitle),
        P('• Uskladitev tabele Skupnih izdatkov v prilogi 3 poročila o financiranju volilne kampanje z:', sBoxText),
        P('√ • vnosom te fakture v kontokartico dobaviteljev v GK,', sBoxText),
        P('• podatki na fakturi,', sBoxText),
        P('• podatki o izplačilu iz TRR.', sBoxText),
    ]))
    story.append(PageBreak())

    # ── PAGE 17 ──────────────────────────────────────────────────────────────
    story.append(shaded_box([
        P('√ • označba neujemajočih se podatkov za ročno preverjanje,', sBoxText),
        P('(ta korak je zelo časovno zamuden in če bi ga bilo mogoče izvesti že vsaj deloma, '
          'bi predstavljal veliko časovno razbremenitev).', sBoxText),
        P('• priprava standardnih elektronskih sporočil dobaviteljem s prošnjo za cenike in '
          'podporno dokumentacijo na podlagi izvozov številk faktur in njihovih kontaktnih '
          'elektronskih naslovov (za pošiljanje po presoji in potrebah revizorja)', sBoxText),
        P('• priprava dokumenta "Sledenje pojasnilom", ki bi za vsako poslano poizvedbo '
          'zabeležil ključne podatke o izhodni pošti in podatke o prejetih pojasnilih.', sBoxText),
    ]))
    story.append(spacer(6))

    story.append(P('3.6 Priprava ORP', sH2))
    story.append(P(
        'ORP revizij ZVRK sledijo pred-opredeljenemu formatu. Vsak ORP je potrebno prilagoditi '
        'konkretnemu revidirancu. Prilagoditve so:',
        sNormal))
    story.append(spacer(2))
    story.append(section_header('NASLOVNA STRAN in KAZALO'))
    orp_naslovna = [
        ('1.', 'naslov ORP'),
        ('2.', 'SPIS št in datum,'),
        ('3.', 'glava dokumenta'),
        ('4.', 'kazalo (posodobi)'),
    ]
    for num, text in orp_naslovna:
        story.append(Paragraph(f'{num} <i>{text}</i>', sNormalLeft))
    story.append(spacer(2))
    story.append(section_header('POGLAVJE 1 – Uvod'))
    orp_pog1 = [
        ('5.', 'naziv revidiranca'),
        ('6.', 'naziv revizije'),
        ('7.', 'sklep v SO'),
    ]
    for num, text in orp_pog1:
        story.append(Paragraph(f'{num} <i>{text}</i>', sNormalLeft))
    story.append(spacer(2))
    story.append(section_header('Predstavitev organizatorja volilne kampanje'))
    orp_pred = [
        ('8.', 'naziv in naslov revidiranca in kampanje'),
        ('9.', 'podatki o odgovorni osebi'),
        ('10.', 'število glasov in delež'),
    ]
    for num, text in orp_pred:
        story.append(Paragraph(f'{num} <i>{text}</i>', sNormalLeft))
    story.append(spacer(2))
    story.append(section_header('Predstavitev revizije'))
    story.append(Paragraph('11. <i>naziv in naslov revidiranca in kampanje</i>', sNormalLeft))
    story.append(spacer(2))
    story.append(section_header('POGLAVJE 2 – Ugotovitve'))
    story.append(section_header('Pravilnost zbiranja sredstev v skladu z ZVRK'))
    story.append(Paragraph('12. <i>izkaz pridobljenih sredstev</i>', sNormalLeft))
    story.append(Paragraph('13. <i>Tabela 1 Viri zbranih sredstev iz poročila o volilni kampanji</i>', sNormalLeft))
    story.append(PageBreak())

    # ── PAGE 18 ──────────────────────────────────────────────────────────────
    story.append(section_header('Pravilnost porabe sredstev v skladu z ZVRK'))
    story.append(Paragraph('14. <i>izkaz porabljenih sredstev</i>', sNormalLeft))
    story.append(Paragraph('15. <i>Tabela 2 Stroški volilne kampanje</i>', sNormalLeft))
    story.append(spacer(2))
    story.append(section_header('Pravilnost poslovanja, ki ni povezano z zbiranjem in s porabo sredstev'))
    story.append(P('16. Preverbe povezane s TRR', sNormalLeft))
    story.append(spacer(6))

    story.append(shaded_box([
        P('<b>Primeri nalog, ki bi jih bilo mogoče avtomatizirati v zvezi s PNR</b>', sBoxTitle),
        P('• Vodja revizij bi lahko kreirala osnutke PNR, v katere bi bili že vneseni podatki, '
          'ki so v zgornjem zapisu označeni v poševnem tisku (morda tudi druge)', sBoxText),
    ]))
    story.append(spacer(6))

    story.append(P('<b>Višina delnega povračila stroškov volilne kampanje</b>', sH3))
    story.append(Paragraph('• <i>Izračun delnega povračila</i>', sNormalLeft))

    # Build the document
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print("PDF built successfully: /workspace/tmp/ZVRK-complete.pdf")

if __name__ == '__main__':
    build()
