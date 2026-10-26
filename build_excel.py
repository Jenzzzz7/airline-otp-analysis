"""Build airline_otp.xlsx — a formula-driven Excel dashboard from the aggregate tables."""
import pickle
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.utils import get_column_letter

agg = pickle.load(open('/tmp/agg.pkl', 'rb'))

# ---- palette ----
NAVY   = "1F3A5F"; BLUE = "2E6DB4"; RED = "C0392B"; LIGHT = "EAF0F7"
GREY   = "6B7280"; WHITE = "FFFFFF"
FONT   = "Arial"
thin   = Side(style="thin", color="D0D7E2")
border = Border(left=thin, right=thin, top=thin, bottom=thin)

def style_header(ws, row, c1, c2):
    for c in range(c1, c2 + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = Font(name=FONT, bold=True, color=WHITE, size=10)
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border

def write_table(ws, start_row, headers, rows, pct_cols=(), num_cols=(), dec_cols=(), start_col=1):
    r = start_row
    for j, h in enumerate(headers):
        ws.cell(row=r, column=start_col + j, value=h)
    style_header(ws, r, start_col, start_col + len(headers) - 1)
    for i, row in enumerate(rows, 1):
        for j, val in enumerate(row):
            cell = ws.cell(row=r + i, column=start_col + j, value=val)
            cell.font = Font(name=FONT, size=10)
            cell.border = border
            col = start_col + j
            if col in pct_cols:
                cell.number_format = '0.0"%"'
            elif col in dec_cols:
                cell.number_format = '0.0'
            elif col in num_cols:
                cell.number_format = '#,##0'
            if j == 0:
                cell.alignment = Alignment(horizontal="left")
            else:
                cell.alignment = Alignment(horizontal="center")
    return r + len(rows)  # last data row

wb = Workbook()

# ============================= DASHBOARD =============================
dash = wb.active
dash.title = "Dashboard"
dash.sheet_view.showGridLines = False
dash.column_dimensions["A"].width = 2
for col in "BCDEF":
    dash.column_dimensions[col].width = 20

dash["B2"] = "Airline On-Time Performance Dashboard"
dash["B2"].font = Font(name=FONT, bold=True, size=18, color=NAVY)
dash["B3"] = "336,776 flights · NYC airports (JFK/LGA/EWR), 2013 · US DOT–style operations data"
dash["B3"].font = Font(name=FONT, size=10, italic=True, color=GREY)

# KPI cards — pull live from the By Carrier sheet (SUMPRODUCT weighted roll-ups = real formulas)
# By Carrier layout (built below): headers row 1, data rows 2..12, cols A..E
#   A carrier_name | B flights | C avg_arr_delay | D pct_delayed | E cancel_rate
C = "'By Carrier'"
# Column F = Arrived (flights with a recorded arrival) — the correct weight for delay averages.
kpis = [
    ("Total Flights",      f"=SUM({C}!B2:B17)",                                             '#,##0'),
    ("Avg Arrival Delay",  f"=ROUND(SUMPRODUCT({C}!F2:F17,{C}!C2:C17)/SUM({C}!F2:F17),1)", '0.0" min"'),
    ("% Delayed (15m+)",   f"=ROUND(SUMPRODUCT({C}!B2:B17,{C}!D2:D17)/SUM({C}!B2:B17),1)", '0.0"%"'),
    ("Avg Cancel Rate",    f"=ROUND(SUMPRODUCT({C}!B2:B17,{C}!E2:E17)/SUM({C}!B2:B17),2)", '0.0"%"'),
]
col = 2  # B
for label, formula, fmt in kpis:
    ws = dash
    lab = ws.cell(row=5, column=col, value=label)
    lab.font = Font(name=FONT, bold=True, size=10, color=WHITE)
    lab.fill = PatternFill("solid", fgColor=BLUE)
    lab.alignment = Alignment(horizontal="center", vertical="center")
    val = ws.cell(row=6, column=col, value=formula)
    val.font = Font(name=FONT, bold=True, size=20, color=NAVY)
    val.fill = PatternFill("solid", fgColor=LIGHT)
    val.alignment = Alignment(horizontal="center", vertical="center")
    val.number_format = fmt
    ws.cell(row=5, column=col).border = border
    ws.cell(row=6, column=col).border = border
    col += 1
dash.row_dimensions[6].height = 34

# Highlight cards — worst hour / worst month via INDEX/MATCH (demonstrates lookup skill)
H = "'By Hour'"; M = "'By Month'"
dash["B9"] = "Peak delay hour (dep)"
dash["B9"].font = Font(name=FONT, bold=True, size=10, color=RED)
dash["B10"] = f"=INDEX({H}!A2:A20,MATCH(MAX({H}!D2:D20),{H}!D2:D20,0))"
dash["B10"].number_format = '0"​:00"'
dash["C9"] = "…its delay rate"
dash["C9"].font = Font(name=FONT, bold=True, size=10, color=RED)
dash["C10"] = f"=MAX({H}!D2:D20)"
dash["C10"].number_format = '0.0"%"'
dash["D9"] = "Worst month"
dash["D9"].font = Font(name=FONT, bold=True, size=10, color=RED)
dash["D10"] = f"=INDEX({M}!A2:A13,MATCH(MAX({M}!D2:D13),{M}!D2:D13,0))"
dash["E9"] = "…its delay rate"
dash["E9"].font = Font(name=FONT, bold=True, size=10, color=RED)
dash["E10"] = f"=MAX({M}!D2:D13)"
dash["E10"].number_format = '0.0"%"'
for cell in ["B10","C10","D10","E10"]:
    dash[cell].font = Font(name=FONT, bold=True, size=16, color=NAVY)
    dash[cell].alignment = Alignment(horizontal="center")

dash["B12"] = ("Key insight: delays cascade through the day — early flights run early, "
               "evening flights are worst. Late departures recover only ~7% of the time, "
               "so on-time performance is won at the gate, not in the air.")
dash["B12"].font = Font(name=FONT, size=10, italic=True, color=GREY)
dash.merge_cells("B12:F13")
dash["B12"].alignment = Alignment(wrap_text=True, vertical="top")

# ============================= DETAIL SHEETS =============================
def sheet_from_df(name, df, headers, pct_cols, num_cols, dec_cols=()):
    ws = wb.create_sheet(name)
    ws.sheet_view.showGridLines = False
    rows = df.values.tolist()
    last = write_table(ws, 1, headers, rows, pct_cols=pct_cols, num_cols=num_cols, dec_cols=dec_cols)
    widths = [26] + [15] * (len(headers) - 1)
    for i, w in enumerate(widths):
        ws.column_dimensions[get_column_letter(i + 1)].width = w
    return ws, last

# By Carrier (A..E)
cdf = agg['carrier'][['carrier_name','flights','avg_arr_delay','pct_delayed','cancel_rate','arrived']]
ws_c, last_c = sheet_from_df("By Carrier", cdf,
    ["Carrier","Flights","Avg Arr Delay (min)","% Delayed 15m+","Cancel Rate %","Arrived (weight)"],
    pct_cols=(4,5), num_cols=(2,6), dec_cols=(3,))
ch = BarChart(); ch.type = "bar"; ch.title = "% Delayed (15m+) by Carrier"
data = Reference(ws_c, min_col=4, min_row=1, max_row=last_c)
cats = Reference(ws_c, min_col=1, min_row=2, max_row=last_c)
ch.add_data(data, titles_from_data=True); ch.set_categories(cats)
ch.height = 9; ch.width = 18; ch.legend = None
ws_c.add_chart(ch, "G2")

# By Hour (A..D)
hdf = agg['hour'][['dep_hour','flights','avg_arr_delay','pct_delayed']]
ws_h, last_h = sheet_from_df("By Hour", hdf,
    ["Dep Hour","Flights","Avg Arr Delay (min)","% Delayed 15m+"],
    pct_cols=(4,), num_cols=(2,))
ch = LineChart(); ch.title = "% Delayed by Scheduled Departure Hour (the cascade)"
data = Reference(ws_h, min_col=4, min_row=1, max_row=last_h)
cats = Reference(ws_h, min_col=1, min_row=2, max_row=last_h)
ch.add_data(data, titles_from_data=True); ch.set_categories(cats)
ch.height = 9; ch.width = 18; ch.legend = None
ws_h.add_chart(ch, "F2")

# By Month (A..D)
mdf = agg['month'][['month','flights','avg_arr_delay','pct_delayed']]
ws_m, last_m = sheet_from_df("By Month", mdf,
    ["Month","Flights","Avg Arr Delay (min)","% Delayed 15m+"],
    pct_cols=(4,), num_cols=(2,), dec_cols=(3,))
ch = LineChart(); ch.title = "% Delayed by Month"
data = Reference(ws_m, min_col=4, min_row=1, max_row=last_m)
cats = Reference(ws_m, min_col=1, min_row=2, max_row=last_m)
ch.add_data(data, titles_from_data=True); ch.set_categories(cats)
ch.height = 9; ch.width = 18; ch.legend = None
ws_m.add_chart(ch, "F2")

# By Weekday (A..E)
wdf = agg['weekday'][['day_of_week','flights','avg_arr_delay','pct_delayed']]
ws_w, last_w = sheet_from_df("By Weekday", wdf,
    ["Weekday","Flights","Avg Arr Delay (min)","% Delayed 15m+"],
    pct_cols=(4,), num_cols=(2,))
ch = BarChart(); ch.type="col"; ch.title = "% Delayed by Weekday"
data = Reference(ws_w, min_col=4, min_row=1, max_row=last_w)
cats = Reference(ws_w, min_col=1, min_row=2, max_row=last_w)
ch.add_data(data, titles_from_data=True); ch.set_categories(cats)
ch.height = 9; ch.width = 16; ch.legend = None
ws_w.add_chart(ch, "F2")

# Weather + Routes on one sheet
wx = agg['weather'][['condition','flights','avg_arr_delay','pct_delayed']]
ws_x = wb.create_sheet("Weather & Routes")
ws_x.sheet_view.showGridLines = False
last_wx = write_table(ws_x, 1, ["Condition","Flights","Avg Arr Delay (min)","% Delayed 15m+"],
    wx.values.tolist(), pct_cols=(4,), num_cols=(2,))
rt = agg['route'][['route','flights','avg_arr_delay','pct_delayed']]
start_rt = last_wx + 3
ws_x.cell(row=start_rt-1, column=1, value="Top 10 most delay-prone routes (500+ flights)").font = Font(name=FONT, bold=True, color=NAVY)
write_table(ws_x, start_rt, ["Route","Flights","Avg Arr Delay (min)","% Delayed 15m+"],
    rt.values.tolist(), pct_cols=(4,), num_cols=(2,))
ws_x.column_dimensions["A"].width = 26
for c in "BCD": ws_x.column_dimensions[c].width = 16
chw = BarChart(); chw.type="col"; chw.title="Delay rate: Adverse vs Normal weather"
dataw = Reference(ws_x, min_col=4, min_row=1, max_row=last_wx)
catsw = Reference(ws_x, min_col=1, min_row=2, max_row=last_wx)
chw.add_data(dataw, titles_from_data=True); chw.set_categories(catsw)
chw.height=7; chw.width=12; chw.legend=None
ws_x.add_chart(chw, "F1")

# ============================= NOTES =============================
nt = wb.create_sheet("Notes")
nt.sheet_view.showGridLines = False
nt.column_dimensions["A"].width = 100
notes = [
    ("Airline On-Time Performance Dashboard — Notes", True),
    ("", False),
    ("Data source: US DOT / BTS–style flight operations data (nycflights13):", False),
    ("all 336,776 flights departing the three major NYC airports (JFK, LGA, EWR) in 2013,", False),
    ("joined with carrier, airport and hourly weather reference tables.", False),
    ("", False),
    ("Definitions:", True),
    ("• 'Delayed' = arrived 15 or more minutes late (US DOT standard).", False),
    ("• Cancel rate = cancelled flights / total flights.", False),
    ("• Adverse weather = precipitation > 0, OR wind >= 20 mph, OR visibility < 5 miles (at origin).", False),
    ("", False),
    ("How this workbook is built:", True),
    ("• The summary tables (By Carrier, By Hour, etc.) are aggregated from the full 336,776-row dataset.", False),
    ("• The Dashboard KPI cards are LIVE FORMULAS: SUMPRODUCT weighted roll-ups and INDEX/MATCH lookups", False),
    ("  over the summary tables, so they recalculate if the underlying tables change.", False),
    ("• Charts are native Excel charts linked to the summary tables.", False),
    ("", False),
    ("To add PivotTables on the raw data: open data/fact_flights.csv from the project repo,", False),
    ("Insert > PivotTable, and follow docs/POWERBI_BUILD_GUIDE.md (Excel companion section).", False),
    ("", False),
    ("Built by Jenoah Gonsalves — github.com/Jenzzzz7", False),
]
for i, (text, bold) in enumerate(notes, 1):
    c = nt.cell(row=i, column=1, value=text)
    c.font = Font(name=FONT, bold=bold, size=12 if (bold and i==1) else 10,
                  color=NAVY if bold else "000000")

out = "airline_otp.xlsx"
wb.save(out)
print("saved", out)
