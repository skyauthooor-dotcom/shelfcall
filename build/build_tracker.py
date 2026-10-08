from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter
from openpyxl.comments import Comment

import os
# written to out/ at the repo root (git-ignored); needs: pip install openpyxl
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "out", "shelfcall-supply-test-tracker.xlsx")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

INK = "15222A"
MUTED = "6F858C"
ACCENT = "1A6754"
BLUE = "0000FF"
HEAD_FILL = PatternFill("solid", fgColor="E7ECEC")
TITLE_FILL = PatternFill("solid", fgColor="1A6754")
INPUT_FILL = PatternFill("solid", fgColor="FFFFCC")
EG_FILL = PatternFill("solid", fgColor="F1F4F4")
PASS_FILL = PatternFill("solid", fgColor="E1EFE9")

thin = Side(style="thin", color="D2DADB")
BORDER = Border(bottom=thin)

F = "Arial"
def font(size=10, bold=False, color=INK, italic=False):
    return Font(name=F, size=size, bold=bold, color=color, italic=italic)

wb = Workbook()

# ---------------------------------------------------------------- START HERE
ws = wb.active
ws.title = "Start here"
ws.sheet_view.showGridLines = False
ws.column_dimensions["A"].width = 3
ws.column_dimensions["B"].width = 34
ws.column_dimensions["C"].width = 78

ws["B2"] = "SHELFCALL — SUPPLY TEST TRACKER"
ws["B2"].font = Font(name=F, size=16, bold=True, color=INK)
ws["B3"] = "Two weeks on WhatsApp. Fill this in as you go, not at the end."
ws["B3"].font = font(11, color=MUTED, italic=True)

rows = [
    ("", ""),
    ("HOW TO USE", ""),
    ("Yellow cells", "You type in these. Everything else is calculated — leave it alone."),
    ("Row 3 of each log", "An example, in the right format. Type over it with your first real entry."),
    ("Requests", "One row per request, filled in the moment you send it out, then updated as offers land."),
    ("Shops", "One row per shop you visited — including the ones that said no."),
    ("Questions", "Every clarification a shop needed before they could quote. The most valuable sheet here."),
    ("Gate", "Reads the other sheets and tells you PASS or FAIL against thresholds set before the test."),
    ("", ""),
    ("THE RULES THAT KEEP IT HONEST", ""),
    ("Requests must be real", "From people who actually want the book and will actually pay. Invented asks teach you nothing."),
    ("Send to each shop separately", "Never a group chat — it creates herd behaviour and hides who ignored what."),
    ("Forward offers unedited", "Don't fix the photo, the price or the wording. You're measuring unassisted offers."),
    ("Wait the full 72 hours", "before you count a request as unanswered."),
    ("Don't move the thresholds", "They were set on the Gate sheet before you had data. That's the whole point of them."),
    ("", ""),
    ("WHAT A RESULT MEANS", ""),
    ("All four PASS", "Build M1. Onboard the shops that answered before launch day."),
    ("Some PASS", "Fixable spec change — but fix it before writing code, not after."),
    ("Under 30% answered", "Stop. The product is a different one: seeded supply, a catalogue you build, or a paid answer."),
]
r = 5
for label, text in rows:
    if label and not text:
        ws.cell(r, 2, label).font = Font(name=F, size=10, bold=True, color=ACCENT)
    elif label:
        ws.cell(r, 2, label).font = font(10, bold=True)
        ws.cell(r, 3, text).font = font(10, color="44585F")
    r += 1

ws.cell(r + 1, 2, "Companion to the Shelfcall supply-test playbook. Thresholds set 22 Sep 2026.").font = font(9, color=MUTED, italic=True)

# ---------------------------------------------------------------- REQUESTS
rq = wb.create_sheet("Requests")
rq.sheet_view.showGridLines = False
NROWS = 200
FIRST, LAST = 3, 2 + NROWS

cols = [
    ("id", 6, None),
    ("posted at", 16, "yyyy-mm-dd hh:mm"),
    ("what they asked for", 40, None),
    ("kind", 11, None),
    ("budget", 10, "#,##0"),
    ("city", 12, None),
    ("first offer at", 16, "yyyy-mm-dd hh:mm"),
    ("offers in 24h", 12, "0"),
    ("offers in 72h", 12, "0"),
    ("shops that answered", 26, None),
    ("hrs to 1st offer", 14, "0.0"),
    ("photo usable", 12, None),
    ("bought", 9, None),
    ("if not, why", 26, None),
]
rq["A1"] = "REQUEST LOG — one row per request"
rq["A1"].font = Font(name=F, size=13, bold=True, color=INK)
rq.cell(1, 11, "calculated →").font = font(9, color=MUTED, italic=True)

for i, (name, width, fmt) in enumerate(cols, start=1):
    c = rq.cell(2, i, name)
    c.font = font(9, bold=True, color=INK)
    c.fill = HEAD_FILL
    c.alignment = Alignment(wrap_text=True, vertical="bottom")
    c.border = BORDER
    rq.column_dimensions[get_column_letter(i)].width = width

example = [1, "2026-10-05 09:40", "a book about a crazy scientist, fiction, not heavy",
           "open", 6000, "Yerevan", "2026-10-05 14:10", 2, 4,
           "Aram; Nairi; Grigor", None, "yes", "yes", None]
for i, v in enumerate(example, start=1):
    c = rq.cell(FIRST, i, v)
    c.font = font(10, italic=True, color=MUTED)
    c.fill = EG_FILL

for row in range(FIRST, LAST + 1):
    for i, (name, width, fmt) in enumerate(cols, start=1):
        c = rq.cell(row, i)
        if row > FIRST:
            c.font = font(10)
        if fmt:
            c.number_format = fmt
        if i != 11:
            c.fill = INPUT_FILL if row > FIRST else EG_FILL
    rq.cell(row, 11).value = f'=IF(OR(B{row}="",G{row}=""),"",(G{row}-B{row})*24)'
    rq.cell(row, 11).font = font(10)
    rq.cell(row, 11).number_format = "0.0"

rq.cell(2, 4).comment = Comment('Type exactly "open" or "concrete" — the Gate sheet counts on it.', "Shelfcall")
rq.cell(2, 9).comment = Comment("Offers received within 72 hours of posting. This drives the headline metric.", "Shelfcall")
rq.freeze_panes = "A3"

dv_kind = DataValidation(type="list", formula1='"open,concrete"', allow_blank=True)
dv_yn = DataValidation(type="list", formula1='"yes,no"', allow_blank=True)
rq.add_data_validation(dv_kind); rq.add_data_validation(dv_yn)
dv_kind.add(f"D{FIRST}:D{LAST}")
dv_yn.add(f"L{FIRST}:L{LAST}")
dv_yn.add(f"M{FIRST}:M{LAST}")

# ---------------------------------------------------------------- SHOPS
sh = wb.create_sheet("Shops")
sh.sheet_view.showGridLines = False
SROWS = 40
SFIRST, SLAST = 3, 2 + SROWS

scols = [
    ("shop name", 22, None),
    ("type", 16, None),
    ("locations", 10, "0"),
    ("visited", 12, "yyyy-mm-dd"),
    ("said yes", 10, None),
    ("whatsapp", 16, None),
    ("requests sent", 13, "0"),
    ("offers made", 12, "0"),
    ("answer rate", 12, "0%"),
    ("median response hrs", 14, "0.0"),
    ("books sold", 11, "0"),
    ("value sold", 12, "#,##0"),
    ("12% would have been", 16, "#,##0"),
    ("still answering wk2", 14, None),
]
sh["A1"] = "SHOP LOG — one row per shop you visited, including the noes"
sh["A1"].font = Font(name=F, size=13, bold=True, color=INK)

for i, (name, width, fmt) in enumerate(scols, start=1):
    c = sh.cell(2, i, name)
    c.font = font(9, bold=True, color=INK)
    c.fill = HEAD_FILL
    c.alignment = Alignment(wrap_text=True, vertical="bottom")
    c.border = BORDER
    sh.column_dimensions[get_column_letter(i)].width = width

sexample = ["Aram Books", "general second-hand", 2, "2026-10-01", "yes", "+374 ...",
            18, 7, None, 5.5, 3, 13700, None, "yes"]
for i, v in enumerate(sexample, start=1):
    c = sh.cell(SFIRST, i, v)
    c.font = font(10, italic=True, color=MUTED)
    c.fill = EG_FILL

for row in range(SFIRST, SLAST + 1):
    for i, (name, width, fmt) in enumerate(scols, start=1):
        c = sh.cell(row, i)
        if row > SFIRST:
            c.font = font(10)
        if fmt:
            c.number_format = fmt
        if i not in (9, 13):
            c.fill = INPUT_FILL if row > SFIRST else EG_FILL
    sh.cell(row, 9).value = f'=IFERROR(H{row}/G{row},"")'
    sh.cell(row, 9).number_format = "0%"
    sh.cell(row, 9).font = font(10)
    sh.cell(row, 13).value = f'=IF(L{row}="","",L{row}*Gate!$C$28)'
    sh.cell(row, 13).number_format = "#,##0"
    sh.cell(row, 13).font = font(10)

sh.cell(2, 2).comment = Comment("general second-hand / antiquarian / specialist / stall / online-only — you are testing which shop types the model fits.", "Shelfcall")
sh.cell(2, 14).comment = Comment("The novelty check. A shop that answered in week 1 and went quiet in week 2 is the result that matters most.", "Shelfcall")
sh.freeze_panes = "A3"

dv_yn2 = DataValidation(type="list", formula1='"yes,no"', allow_blank=True)
sh.add_data_validation(dv_yn2)
dv_yn2.add(f"E{SFIRST}:E{SLAST}")
dv_yn2.add(f"N{SFIRST}:N{SLAST}")

# ---------------------------------------------------------------- QUESTIONS
qs = wb.create_sheet("Questions")
qs.sheet_view.showGridLines = False
qs["A1"] = "QUESTIONS LOG — everything a shop had to ask before they could quote"
qs["A1"].font = Font(name=F, size=13, bold=True, color=INK)
qs["A2"] = "With no chat in the product, each line here is either a missing field on the offer form, or evidence the no-chat rule breaks."
qs["A2"].font = font(10, color=MUTED, italic=True)

qcols = [("date", 12, "yyyy-mm-dd"), ("shop", 20, None), ("request id", 11, "0"),
         ("what they asked", 46, None), ("what it implies", 40, None)]
for i, (name, width, fmt) in enumerate(qcols, start=1):
    c = qs.cell(4, i, name)
    c.font = font(9, bold=True, color=INK); c.fill = HEAD_FILL
    c.border = BORDER
    qs.column_dimensions[get_column_letter(i)].width = width

qex = ["2026-10-06", "Aram Books", 1, "Fiction or a real biography of a scientist?",
       "Open requests need a 'fiction / non-fiction' hint on the request form (S-03)"]
for i, v in enumerate(qex, start=1):
    c = qs.cell(5, i, v); c.font = font(10, italic=True, color=MUTED); c.fill = EG_FILL

for row in range(5, 85):
    for i, (name, width, fmt) in enumerate(qcols, start=1):
        c = qs.cell(row, i)
        if row > 5:
            c.font = font(10); c.fill = INPUT_FILL
        if fmt:
            c.number_format = fmt
qs.freeze_panes = "A5"

# ---------------------------------------------------------------- GATE
g = wb.create_sheet("Gate")
g.sheet_view.showGridLines = False
for col, w in zip("ABCDE", [3, 44, 14, 14, 42]):
    g.column_dimensions[col].width = w

g["B2"] = "THE GATE"
g["B2"].font = Font(name=F, size=16, bold=True, color=INK)
g["B3"] = "Thresholds were written down before the test began. Do not renegotiate them now."
g["B3"].font = font(10, color=MUTED, italic=True)

hdr = ["metric", "threshold", "actual", "verdict"]
for i, h in enumerate(hdr, start=2):
    c = g.cell(5, i, h)
    c.font = font(9, bold=True); c.fill = HEAD_FILL; c.border = BORDER
g.cell(5, 6, "what it tells you").font = font(9, bold=True)
g.cell(5, 6).fill = HEAD_FILL; g.cell(5, 6).border = BORDER

RQ_ID = f"Requests!$A${FIRST}:$A${LAST}"
RQ_72 = f"Requests!$I${FIRST}:$I${LAST}"
RQ_KIND = f"Requests!$D${FIRST}:$D${LAST}"
RQ_HRS = f"Requests!$K${FIRST}:$K${LAST}"
RQ_BOUGHT = f"Requests!$M${FIRST}:$M${LAST}"
RQ_PHOTO = f"Requests!$L${FIRST}:$L${LAST}"
SH_OFF = f"Shops!$H${SFIRST}:$H${SLAST}"

gate_rows = [
    ("Requests answered within 72 hours", 0.6, "0%",
     f'=IFERROR(COUNTIF({RQ_72},">0")/COUNT({RQ_ID}),"")', "higher",
     "The headline. Below 60% and demand is not reaching supply."),
    ("Median hours to first offer", 24, "0.0",
     f'=IFERROR(MEDIAN({RQ_HRS}),"")', "lower",
     "Speed. A reader will not wait two days for a first answer."),
    ("Open requests that got an offer", 0.4, "0%",
     f'=IFERROR(COUNTIFS({RQ_KIND},"open",{RQ_72},">0")/COUNTIF({RQ_KIND},"open"),"")', "higher",
     "The vague half of the product — the part nobody else serves."),
    ("Shops that answered more than 3 times", 4, "0",
     f'=COUNTIF({SH_OFF},">3")', "higher",
     "Repeat answering is supply. One polite reply is courtesy."),
]

r = 6
for label, threshold, fmt, formula, direction, note in gate_rows:
    g.cell(r, 2, label).font = font(10, bold=True)
    tc = g.cell(r, 3, threshold); tc.number_format = fmt; tc.font = font(10, color=BLUE); tc.fill = INPUT_FILL
    ac = g.cell(r, 4, formula); ac.number_format = fmt; ac.font = font(10)
    op = ">=" if direction == "higher" else "<="
    vc = g.cell(r, 5, f'=IF(D{r}="","—",IF(D{r}{op}C{r},"PASS","FAIL"))')
    vc.font = font(10, bold=True); vc.alignment = Alignment(horizontal="center")
    g.cell(r, 6, note).font = font(9, color=MUTED)
    for col in range(2, 7):
        g.cell(r, col).border = BORDER
    r += 1

g.cell(11, 2, "VERDICT").font = font(11, bold=True, color=ACCENT)
g.cell(11, 4, '=IF(COUNTIF(E6:E9,"PASS")=4,"GO — build M1",'
              'IF(OR(D6="",D6<Gate!C13),"STOP — rethink the product","PARTIAL — fix the spec before building"))')
g.cell(11, 4).font = Font(name=F, size=12, bold=True, color=ACCENT)
g.cell(11, 4).fill = PASS_FILL
g.cell(11, 4).alignment = Alignment(horizontal="left")
g.merge_cells("D11:F11")

g.cell(13, 2, "hard-no line (answer rate below this = stop)").font = font(9, color=MUTED)
g.cell(13, 3, 0.3).number_format = "0%"
g.cell(13, 3).font = font(10, color=BLUE); g.cell(13, 3).fill = INPUT_FILL

# secondary
g.cell(16, 2, "WORTH WATCHING").font = font(11, bold=True, color=ACCENT)
sec = [
    ("Requests logged", f'=COUNT({RQ_ID})', "0"),
    ("Requests with at least one offer", f'=COUNTIF({RQ_72},">0")', "0"),
    ("Average offers per request", f'=IFERROR(SUM({RQ_72})/COUNT({RQ_ID}),"")', "0.0"),
    ("Order rate (bought / answered)", f'=IFERROR(COUNTIF({RQ_BOUGHT},"yes")/COUNTIF({RQ_72},">0"),"")', "0%"),
    ("Offers with a usable photo", f'=IFERROR(COUNTIF({RQ_PHOTO},"yes")/COUNTIF({RQ_PHOTO},"<>"),"")', "0%"),
    ("Shops recruited", f'=COUNTIF(Shops!$E${SFIRST}:$E${SLAST},"yes")', "0"),
    ("Still answering in week 2", f'=COUNTIF(Shops!$N${SFIRST}:$N${SLAST},"yes")', "0"),
    ("Total value sold", f'=SUM(Shops!$L${SFIRST}:$L${SLAST})', "#,##0"),
    ("Commission that would have been due", f'=SUM(Shops!$M${SFIRST}:$M${SLAST})', "#,##0"),
    ("Questions shops had to ask", '=COUNTA(Questions!$D$5:$D$84)', "0"),
]
r = 17
for label, formula, fmt in sec:
    g.cell(r, 2, label).font = font(10)
    c = g.cell(r, 4, formula); c.number_format = fmt; c.font = font(10)
    for col in range(2, 5):
        g.cell(r, col).border = BORDER
    r += 1

g.cell(28, 2, "commission rate used above").font = font(9, color=MUTED)
g.cell(28, 3, 0.12).number_format = "0%"
g.cell(28, 3).font = font(10, color=BLUE); g.cell(28, 3).fill = INPUT_FILL
g.cell(28, 5, "Nothing is charged during the test — this is only what it would have been.").font = font(9, color=MUTED, italic=True)

g.cell(30, 2, "Blue figures on a yellow fill are the only cells to edit on this sheet.").font = font(9, color=MUTED, italic=True)

wb.save(OUT)
print("saved", OUT)
