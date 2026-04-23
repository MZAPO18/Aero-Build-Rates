"""
Excel workbook writer for the Aero Build Rates tool.

Produces a multi-sheet .xlsx workbook with:
  1. Overview Dashboard
  2. Airbus
  3. Boeing
  4. GE Aerospace
  5. Pratt & Whitney
  6. Rolls Royce
  7. Production Rate Targets
  8. Sources & Notes
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any

import openpyxl
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.styles import (
    Alignment,
    Border,
    Font,
    PatternFill,
    Side,
)
from openpyxl.utils import get_column_letter

# ── Brand colours (hex without #) ───────────────────────────────────────────
C = {
    "airbus_dark":  "00205B",   # Airbus navy
    "airbus_mid":   "003F8A",
    "airbus_light": "D6E4F7",
    "boeing_dark":  "0033A0",   # Boeing blue
    "boeing_mid":   "1A5276",
    "boeing_light": "D6EAF8",
    "ge_dark":      "003865",   # GE Aerospace teal/navy
    "ge_mid":       "005B8E",
    "ge_light":     "D0EAF5",
    "pw_dark":      "8B0000",   # RTX / P&W red
    "pw_mid":       "C0392B",
    "pw_light":     "FADBD8",
    "rr_dark":      "004225",   # Rolls Royce green
    "rr_mid":       "1D7A4E",
    "rr_light":     "D5F5E3",
    "header_bg":    "1F3864",   # generic dark-blue section header
    "header_text":  "FFFFFF",
    "sub_bg":       "D6DCE4",
    "row_alt":      "EEF2F7",
    "total_bg":     "BDD7EE",
    "white":        "FFFFFF",
    "black":        "000000",
    "border":       "A0A0A0",
    "note_bg":      "FFF9C4",
}


def _fill(hex_color: str) -> PatternFill:
    return PatternFill("solid", fgColor=hex_color)


def _font(
    bold: bool = False,
    size: int = 11,
    color: str = "000000",
    italic: bool = False,
    name: str = "Calibri",
) -> Font:
    return Font(bold=bold, size=size, color=color, italic=italic, name=name)


def _border(style: str = "thin") -> Border:
    s = Side(style=style, color=C["border"])
    return Border(left=s, right=s, top=s, bottom=s)


def _align(h: str = "left", v: str = "center", wrap: bool = False) -> Alignment:
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)


def _header_style(ws, row: int, col: int, value: str, bg: str, fg: str = "FFFFFF",
                  size: int = 11, bold: bool = True) -> None:
    cell = ws.cell(row=row, column=col, value=value)
    cell.fill = _fill(bg)
    cell.font = _font(bold=bold, size=size, color=fg)
    cell.alignment = _align("center")
    cell.border = _border()


def _data_cell(ws, row: int, col: int, value: Any, bg: str = "FFFFFF",
               bold: bool = False, num_fmt: str | None = None,
               align: str = "center") -> openpyxl.cell.cell.Cell:
    cell = ws.cell(row=row, column=col, value=value)
    cell.fill = _fill(bg)
    cell.font = _font(bold=bold)
    cell.alignment = _align(align)
    cell.border = _border()
    if num_fmt:
        cell.number_format = num_fmt
    return cell


def _set_col_widths(ws, widths: list[int | float]) -> None:
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def _freeze(ws, cell: str = "B2") -> None:
    ws.freeze_panes = cell


def _section_title(ws, row: int, value: str, ncols: int,
                   bg: str = C["header_bg"]) -> None:
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=ncols)
    cell = ws.cell(row=row, column=1, value=value)
    cell.fill = _fill(bg)
    cell.font = _font(bold=True, size=12, color=C["header_text"])
    cell.alignment = _align("left", wrap=False)
    cell.border = _border()


def _write_table(ws, start_row: int, headers: list[str], rows: list[list],
                 header_bg: str = C["header_bg"],
                 alt_bg: str = C["row_alt"],
                 total_col_idx: int | None = None,
                 num_fmt: str = "#,##0",
                 year_col: bool = True) -> int:
    """
    Write a header row then data rows.  Returns the next empty row index.
    `total_col_idx` (1-based) gets bold + blue background if set.
    `year_col` means column 0 contains a year → left-aligned, no comma format.
    """
    # Header row
    for c, h in enumerate(headers, start=1):
        _header_style(ws, start_row, c, h, header_bg)

    for r_idx, row in enumerate(rows, start=start_row + 1):
        bg = alt_bg if (r_idx - start_row) % 2 == 0 else C["white"]
        for c_idx, val in enumerate(row, start=1):
            is_total = total_col_idx and c_idx == total_col_idx
            cell_bg = C["total_bg"] if is_total else bg
            fmt = num_fmt if isinstance(val, (int, float)) else None
            if year_col and c_idx == 1:
                fmt = "0"
            _data_cell(ws, r_idx, c_idx, val, bg=cell_bg,
                       bold=is_total, num_fmt=fmt)

    return start_row + 1 + len(rows)


def _add_bar_chart(ws, title: str, data_ref: Reference,
                   cats_ref: Reference, anchor: str,
                   width: float = 20, height: float = 12,
                   chart_type: str = "bar") -> None:
    if chart_type == "line":
        chart = LineChart()
        chart.grouping = "standard"
    else:
        chart = BarChart()
        chart.type = "col"
        chart.grouping = "clustered"

    chart.title = title
    chart.style = 10
    chart.shape = 4
    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(cats_ref)
    chart.width = width
    chart.height = height
    chart.legend.position = "b"
    ws.add_chart(chart, anchor)


# ── Individual sheet writers ─────────────────────────────────────────────────

def _write_overview(wb: Workbook, data: dict) -> None:
    ws = wb.create_sheet("Overview")
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.tabColor = C["header_bg"]

    # Title banner
    ws.merge_cells("A1:J1")
    c = ws["A1"]
    c.value = "AEROSPACE BUILD RATES TRACKER"
    c.fill = _fill(C["header_bg"])
    c.font = Font(bold=True, size=16, color="FFFFFF", name="Calibri")
    c.alignment = _align("center")
    ws.row_dimensions[1].height = 30

    ws.merge_cells("A2:J2")
    c = ws["A2"]
    c.value = f"Data through: {data.get('as_of', datetime.now().strftime('%B %Y'))}   |   Sources: Airbus, Boeing, GE Aerospace, RTX/P&W, Rolls Royce official publications"
    c.fill = _fill("2E4057")
    c.font = Font(bold=False, size=10, color="FFFFFF", name="Calibri", italic=True)
    c.alignment = _align("center")
    ws.row_dimensions[2].height = 18

    row = 4

    # Airframer totals
    _section_title(ws, row, "AIRFRAMER ANNUAL DELIVERIES (UNITS)", 7)
    row += 1
    af = data["overview"]["airframer_totals"]
    nxt = _write_table(ws, row, af["headers"], af["rows"],
                       total_col_idx=len(af["headers"]))
    row = nxt + 1

    # Engine OEM totals
    _section_title(ws, row, "AEROENGINE OEM ANNUAL DELIVERIES (UNITS)  ·  GE + P&W + Rolls Royce", 7)
    row += 1
    eng = data["overview"]["engine_totals"]
    nxt = _write_table(ws, row, eng["headers"], eng["rows"],
                       total_col_idx=len(eng["headers"]))
    row = nxt + 1

    # Implied monthly delivery rate callout
    _section_title(ws, row, "IMPLIED MONTHLY DELIVERY RATE  (Annual Total ÷ 12)", 7, bg=C["ge_dark"])
    row += 1
    implied_headers = ["Year", "Airbus /month", "Boeing /month", "Total Airframers /month"]
    implied_rows = []
    for r in af["rows"]:
        yr = r[0]
        airbus_mo = round(r[1] / 12, 1)
        boeing_mo = round(r[2] / 12, 1)
        total_mo = round(r[3] / 12, 1)
        implied_rows.append([yr, airbus_mo, boeing_mo, total_mo])
    nxt = _write_table(ws, row, implied_headers, implied_rows,
                       header_bg=C["ge_dark"], num_fmt="#,##0.0",
                       total_col_idx=4)
    row = nxt + 1

    # Scrape status
    _section_title(ws, row, "LIVE SCRAPE STATUS", 7, bg="555555")
    row += 1
    scrape = data.get("scrape_results", {})
    headers_s = ["Manufacturer", "Source URL", "Status", "Note", "Scraped At"]
    scrape_rows = []
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    for mfr, res in scrape.items():
        scrape_rows.append([
            mfr.replace("_", " ").title(),
            res.get("source", "")[:80],
            res.get("status", "").upper(),
            res.get("message", "")[:100],
            now_str,
        ])
    _header_style(ws, row, 1, headers_s[0], "555555")
    _header_style(ws, row, 2, headers_s[1], "555555")
    _header_style(ws, row, 3, headers_s[2], "555555")
    _header_style(ws, row, 4, headers_s[3], "555555")
    _header_style(ws, row, 5, headers_s[4], "555555")
    for r_idx, srow in enumerate(scrape_rows, start=row + 1):
        bg = "E8F8E8" if srow[2] == "OK" else "FFF3CD" if srow[2] == "PARTIAL" else "FDECEA"
        for c_idx, val in enumerate(srow, start=1):
            cell = ws.cell(row=r_idx, column=c_idx, value=val)
            cell.fill = _fill(bg)
            cell.font = _font(size=10)
            cell.alignment = _align("left")
            cell.border = _border()

    _set_col_widths(ws, [8, 18, 16, 16, 16, 16, 16])
    _freeze(ws, "B4")

    # Chart: airframer deliveries
    chart_row = 4
    data_r = Reference(ws,
                        min_col=2, max_col=3,
                        min_row=chart_row + 1,
                        max_row=chart_row + 1 + len(af["rows"]))
    cats_r = Reference(ws,
                        min_col=1,
                        min_row=chart_row + 2,
                        max_row=chart_row + 1 + len(af["rows"]))
    _add_bar_chart(ws, "Annual Aircraft Deliveries", data_r, cats_r,
                   "H4", width=22, height=14)


def _write_airbus_sheet(wb: Workbook, data: dict) -> None:
    ws = wb.create_sheet("Airbus")
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.tabColor = C["airbus_dark"]

    # Banner
    ws.merge_cells("A1:I1")
    c = ws["A1"]
    c.value = "AIRBUS — Annual Deliveries & Production Rates"
    c.fill = _fill(C["airbus_dark"])
    c.font = Font(bold=True, size=14, color="FFFFFF", name="Calibri")
    c.alignment = _align("center")
    ws.row_dimensions[1].height = 28

    row = 3
    airbus = data["airbus"]

    _section_title(ws, row, "ANNUAL AIRCRAFT DELIVERIES BY FAMILY (UNITS)", 9, C["airbus_dark"])
    row += 1
    ann = airbus["annual_deliveries"]
    nxt = _write_table(ws, row, ann["headers"], ann["rows"],
                       header_bg=C["airbus_dark"], total_col_idx=len(ann["headers"]))
    # Implied monthly rate row
    ws.cell(row=nxt, column=1, value="  Impl. monthly rate →").font = _font(italic=True, size=9)
    for col_i in range(2, len(ann["headers"]) + 1):
        vals = [r[col_i - 1] for r in ann["rows"] if isinstance(r[col_i - 1], (int, float))]
        if vals:
            avg = round(sum(vals) / len(vals) / 12, 1)
            cell = ws.cell(row=nxt, column=col_i, value=avg)
            cell.number_format = "#,##0.0"
            cell.font = _font(italic=True, size=9, color="555555")
            cell.alignment = _align("center")
    row = nxt + 2

    _section_title(ws, row, "PRODUCTION RATE TARGETS (AIRCRAFT / MONTH)", 9, C["airbus_mid"])
    row += 1
    pr = airbus["production_rates"]
    nxt = _write_table(ws, row, pr["headers"], pr["rows"],
                       header_bg=C["airbus_mid"], year_col=False)
    row = nxt + 2

    _section_title(ws, row, "YEAR-END ORDER BACKLOG (UNITS, APPROXIMATE)", 9, C["airbus_mid"])
    row += 1
    bl = airbus["backlog"]
    nxt = _write_table(ws, row, bl["headers"], bl["rows"],
                       header_bg=C["airbus_mid"], total_col_idx=len(bl["headers"]))
    row = nxt + 2

    # Notes
    _section_title(ws, row, "NOTES", 9, "777777")
    ws.cell(row=row + 1, column=1, value=ann["notes"]).font = _font(size=9, italic=True)
    ws.merge_cells(start_row=row + 1, start_column=1, end_row=row + 1, end_column=9)
    ws.cell(row=row + 1, column=1).fill = _fill(C["note_bg"])
    ws.cell(row=row + 1, column=1).alignment = _align("left", wrap=True)
    ws.row_dimensions[row + 1].height = 45

    _set_col_widths(ws, [9, 10, 16, 9, 9, 9, 14, 14, 14])
    _freeze(ws, "B4")

    # Chart
    chart_start = 4
    dr = Reference(ws, min_col=2, max_col=len(ann["headers"]) - 1,
                   min_row=chart_start, max_row=chart_start + len(ann["rows"]))
    cr = Reference(ws, min_col=1,
                   min_row=chart_start + 1,
                   max_row=chart_start + len(ann["rows"]))
    _add_bar_chart(ws, "Airbus Deliveries by Family", dr, cr, "K3",
                   width=24, height=15)


def _write_boeing_sheet(wb: Workbook, data: dict) -> None:
    ws = wb.create_sheet("Boeing")
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.tabColor = C["boeing_dark"]

    ws.merge_cells("A1:I1")
    c = ws["A1"]
    c.value = "BOEING — Annual Deliveries & Production Rates"
    c.fill = _fill(C["boeing_dark"])
    c.font = Font(bold=True, size=14, color="FFFFFF", name="Calibri")
    c.alignment = _align("center")
    ws.row_dimensions[1].height = 28

    row = 3
    boeing = data["boeing"]

    _section_title(ws, row, "ANNUAL AIRCRAFT DELIVERIES BY FAMILY (UNITS)", 8, C["boeing_dark"])
    row += 1
    ann = boeing["annual_deliveries"]
    nxt = _write_table(ws, row, ann["headers"], ann["rows"],
                       header_bg=C["boeing_dark"], total_col_idx=len(ann["headers"]))
    row = nxt + 2

    _section_title(ws, row, "PRODUCTION RATE TARGETS (AIRCRAFT / MONTH)", 8, C["boeing_mid"])
    row += 1
    pr = boeing["production_rates"]
    nxt = _write_table(ws, row, pr["headers"], pr["rows"],
                       header_bg=C["boeing_mid"], year_col=False)
    row = nxt + 2

    _section_title(ws, row, "YEAR-END ORDER BACKLOG (UNITS, APPROXIMATE)", 8, C["boeing_mid"])
    row += 1
    bl = boeing["backlog"]
    nxt = _write_table(ws, row, bl["headers"], bl["rows"],
                       header_bg=C["boeing_mid"], total_col_idx=len(bl["headers"]))
    row = nxt + 2

    _section_title(ws, row, "NOTES", 8, "777777")
    ws.cell(row=row + 1, column=1, value=ann["notes"]).font = _font(size=9, italic=True)
    ws.merge_cells(start_row=row + 1, start_column=1, end_row=row + 1, end_column=8)
    ws.cell(row=row + 1, column=1).fill = _fill(C["note_bg"])
    ws.cell(row=row + 1, column=1).alignment = _align("left", wrap=True)
    ws.row_dimensions[row + 1].height = 60

    _set_col_widths(ws, [9, 16, 16, 13, 9, 9, 14, 14])
    _freeze(ws, "B4")

    chart_start = 4
    dr = Reference(ws, min_col=2, max_col=len(ann["headers"]) - 1,
                   min_row=chart_start, max_row=chart_start + len(ann["rows"]))
    cr = Reference(ws, min_col=1,
                   min_row=chart_start + 1,
                   max_row=chart_start + len(ann["rows"]))
    _add_bar_chart(ws, "Boeing Deliveries by Family", dr, cr, "J3",
                   width=24, height=15)


def _write_engine_sheet(wb: Workbook, data: dict, key: str,
                        title: str, tab_color: str,
                        header_bg: str, mid_bg: str) -> None:
    ws = wb.create_sheet(title)
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.tabColor = tab_color

    ws.merge_cells("A1:J1")
    c = ws["A1"]
    c.value = f"{title.upper()} — Annual Engine Deliveries"
    c.fill = _fill(tab_color)
    c.font = Font(bold=True, size=14, color="FFFFFF", name="Calibri")
    c.alignment = _align("center")
    ws.row_dimensions[1].height = 28

    row = 3
    eng_data = data[key]

    _section_title(ws, row, "ANNUAL COMMERCIAL ENGINE DELIVERIES (UNITS)", 10, header_bg)
    row += 1
    ann = eng_data["annual_deliveries"]
    nxt = _write_table(ws, row, ann["headers"], ann["rows"],
                       header_bg=header_bg, total_col_idx=len(ann["headers"]))
    # Add implied monthly rate
    ws.cell(row=nxt, column=1, value="  Impl. monthly rate →").font = _font(italic=True, size=9)
    for col_i in range(2, len(ann["headers"]) + 1):
        vals = [r[col_i - 1] for r in ann["rows"] if isinstance(r[col_i - 1], (int, float))]
        if vals:
            avg_mo = round(sum(vals) / len(vals) / 12, 0)
            cell = ws.cell(row=nxt, column=col_i, value=avg_mo)
            cell.number_format = "#,##0"
            cell.font = _font(italic=True, size=9, color="555555")
            cell.alignment = _align("center")
    row = nxt + 2

    _section_title(ws, row, "ENGINE MODEL BREAKDOWN (ESTIMATED ANNUAL DELIVERIES)", 10, mid_bg)
    row += 1
    br = eng_data["by_engine_type"]
    nxt = _write_table(ws, row, br["headers"], br["rows"],
                       header_bg=mid_bg, year_col=False)
    row = nxt + 2

    _section_title(ws, row, "NOTES", 10, "777777")
    note_cell = ws.cell(row=row + 1, column=1, value=ann["notes"])
    note_cell.font = _font(size=9, italic=True)
    ws.merge_cells(start_row=row + 1, start_column=1, end_row=row + 1, end_column=10)
    note_cell.fill = _fill(C["note_bg"])
    note_cell.alignment = _align("left", wrap=True)
    ws.row_dimensions[row + 1].height = 60

    _set_col_widths(ws, [9, 22, 16, 16, 16, 14, 14, 14, 14, 14])
    _freeze(ws, "B4")

    # Line chart for total deliveries
    chart_start = 4
    total_col = len(ann["headers"])
    dr = Reference(ws, min_col=total_col, max_col=total_col,
                   min_row=chart_start, max_row=chart_start + len(ann["rows"]))
    cr = Reference(ws, min_col=1,
                   min_row=chart_start + 1,
                   max_row=chart_start + len(ann["rows"]))
    _add_bar_chart(ws, f"{title} – Total Engine Deliveries", dr, cr, "L3",
                   width=20, height=13, chart_type="line")


def _write_prod_rate_sheet(wb: Workbook, data: dict) -> None:
    ws = wb.create_sheet("Production Rates")
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.tabColor = "4F4F4F"

    ws.merge_cells("A1:L1")
    c = ws["A1"]
    c.value = "PUBLISHED PRODUCTION RATE TARGETS — AIRBUS & BOEING (Aircraft / Month)"
    c.fill = _fill("2C3E50")
    c.font = Font(bold=True, size=13, color="FFFFFF", name="Calibri")
    c.alignment = _align("center")
    ws.row_dimensions[1].height = 28

    row = 3

    _section_title(ws, row, "AIRBUS PRODUCTION RATES", 10, C["airbus_dark"])
    row += 1
    pr_a = data["airbus"]["production_rates"]
    nxt = _write_table(ws, row, pr_a["headers"], pr_a["rows"],
                       header_bg=C["airbus_dark"], year_col=False)
    row = nxt + 2

    _section_title(ws, row, "BOEING PRODUCTION RATES", 10, C["boeing_dark"])
    row += 1
    pr_b = data["boeing"]["production_rates"]
    nxt = _write_table(ws, row, pr_b["headers"], pr_b["rows"],
                       header_bg=C["boeing_dark"], year_col=False)
    row = nxt + 2

    _section_title(ws, row,
                   "CONTEXT: 2019 vs. COVID Trough vs. 2024 vs. Target  (aircraft/month)",
                   10, "4F4F4F")
    row += 1
    ctx_headers = ["Manufacturer", "Programme", "2019 Peak", "COVID Trough",
                   "2024 Actual", "2025-26 Target", "% Recovery vs. 2019"]
    ctx_rows = [
        ["Airbus",  "A320 Family",   60,  40,  58,  65,  "97%"],
        ["Airbus",  "A220",           4,   2,   6,   7,  "150%"],
        ["Airbus",  "A350",         9.5,   6,  10,  12,  "105%"],
        ["Airbus",  "A330",           4,   2, 3.5,   4,   "88%"],
        ["Boeing",  "737 MAX",       52, "Halt", "~24", 38, "~46%"],
        ["Boeing",  "787 Dreamliner",12,   7,   7,  10,   "58%"],
        ["Boeing",  "777 / 777X",     5,   3,   4,   5,   "80%"],
    ]
    _write_table(ws, row, ctx_headers, ctx_rows,
                 header_bg="4F4F4F", year_col=False)

    _set_col_widths(ws, [12, 18, 12, 14, 12, 16, 22])
    _freeze(ws, "B3")


def _write_sources_sheet(wb: Workbook, data: dict) -> None:
    ws = wb.create_sheet("Sources & Notes")
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.tabColor = "888888"

    ws.merge_cells("A1:F1")
    c = ws["A1"]
    c.value = "DATA SOURCES, METHODOLOGY & DISCLAIMER"
    c.fill = _fill("2C3E50")
    c.font = Font(bold=True, size=14, color="FFFFFF", name="Calibri")
    c.alignment = _align("center")
    ws.row_dimensions[1].height = 28

    sources = [
        ("Airbus Annual Deliveries",
         "Airbus SE Press Releases",
         "https://www.airbus.com/en/newsroom/press-releases",
         "Full-year delivery press release (Jan each year)"),
        ("Airbus Orders & Deliveries Dashboard",
         "Airbus SE",
         "https://www.airbus.com/en/products-services/commercial-aircraft/orders-and-deliveries",
         "Interactive orders/deliveries tool (JS; best accessed via browser)"),
        ("Boeing Annual Deliveries",
         "Boeing Company IR",
         "https://ir.boeing.com/news-releases",
         "Monthly & annual orders/deliveries press releases"),
        ("Boeing Orders & Deliveries",
         "Boeing Commercial Airplanes",
         "https://www.boeing.com/commercial/#/orders-deliveries",
         "Interactive delivery tracker (JS-rendered)"),
        ("GE Aerospace Quarterly Earnings",
         "GE Aerospace Investor Relations",
         "https://www.geaerospace.com/investor-relations",
         "Quarterly & annual earnings releases; CESB engine delivery counts"),
        ("GE Aerospace Press Releases",
         "GE Aerospace",
         "https://www.geaerospace.com/news/press-releases",
         "Annual results and engine programme announcements"),
        ("CFM International (LEAP) Data",
         "CFM International",
         "https://www.cfmaeroengines.com",
         "Annual LEAP delivery statistics; joint GE/Safran venture (50/50)"),
        ("Pratt & Whitney / RTX Earnings",
         "RTX Corporation IR",
         "https://investors.rtx.com",
         "Quarterly earnings; P&W segment – large commercial engine deliveries"),
        ("Pratt & Whitney Newsroom",
         "Pratt & Whitney",
         "https://www.prattwhitney.com/en/newsroom/news",
         "GTF orders, deliveries and programme announcements"),
        ("Rolls Royce Financial Results",
         "Rolls-Royce Holdings plc",
         "https://www.rolls-royce.com/investors/results-reports-and-presentations/financial-results.aspx",
         "Annual and half-year results; large civil engine delivery figures"),
        ("Rolls Royce Press Releases",
         "Rolls-Royce Holdings plc",
         "https://www.rolls-royce.com/media/press-releases.aspx",
         "Programme updates, trading statements and results"),
    ]

    headers = ["Data Category", "Publisher", "URL", "What to Look For"]
    row = 3
    _section_title(ws, row, "PRIMARY DATA SOURCES", 4)
    row += 1
    for c_i, h in enumerate(headers, start=1):
        _header_style(ws, row, c_i, h, C["header_bg"])
    row += 1
    for i, (cat, pub, url, notes_) in enumerate(sources, start=0):
        bg = C["row_alt"] if i % 2 == 0 else C["white"]
        for c_i, val in enumerate([cat, pub, url, notes_], start=1):
            cell = ws.cell(row=row, column=c_i, value=val)
            cell.fill = _fill(bg)
            cell.font = _font(size=10)
            cell.alignment = _align("left", wrap=True)
            cell.border = _border()
        ws.row_dimensions[row].height = 30
        row += 1

    row += 1
    _section_title(ws, row, "METHODOLOGY", 4, "4F4F4F")
    row += 1
    methodology = [
        "• DELIVERY RATE vs. BUILD RATE: Aircraft deliveries are used as a proxy for production/build rates. "
        "Deliveries typically lag production by 4–12 weeks but track closely over annual periods. "
        "During the 2019-2020 737 MAX grounding, Boeing built but could not deliver aircraft; "
        "stored inventory was drawn down from late 2020 onwards.",

        "• ENGINE COUNT CONVENTIONS: GE Aerospace LEAP deliveries are reported as gross CFM International "
        "units (GE holds 50% economic interest). Engine counts include new-production engines only "
        "(excluding spare/shop-visit units unless otherwise stated).",

        "• ESTIMATES: Per-model delivery breakdowns and engine-type splits marked as 'estimated' are "
        "derived from multiple public investor presentations, earnings calls and third-party analysis. "
        "Annual programme totals are sourced directly from official press releases where available.",

        "• PRODUCTION RATE TARGETS are formal published targets from company earnings calls and investor "
        "presentations; actual achieved rates may vary. Rates are stated as aircraft/engines per month.",

        "• SCRAPING: This tool attempts live scraping of the above URLs each time it is run. "
        "Many manufacturer pages are JavaScript-rendered and may not yield data via basic HTTP scraping. "
        "The 'Overview' tab shows the scrape status for the current run; historical embedded data is "
        "used as the baseline in all cases.",

        "• DATA CURRENCY: The embedded baseline covers 2005 – 2025 (20+ years). "
        "2025 rows are full-year estimates pending official January 2026 delivery announcements. "
        "Pre-2015 per-model breakdowns are estimated from programme rate disclosures.",

        "• MONTHLY DATA: The 'Monthly Tracker' sheet shows month-by-month Airbus and Boeing "
        "deliveries scraped from official monthly press releases when Playwright is installed. "
        "If live scraping fails, the sheet falls back to quarterly estimates derived from "
        "H1/H2 disclosures and historical delivery-cadence patterns.",
    ]
    for note_line in methodology:
        cell = ws.cell(row=row, column=1, value=note_line)
        cell.font = _font(size=10)
        cell.alignment = _align("left", wrap=True)
        cell.fill = _fill(C["note_bg"])
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=4)
        ws.row_dimensions[row].height = 52
        row += 1

    row += 1
    _section_title(ws, row, "DISCLAIMER", 4, C["pw_dark"])
    row += 1
    disc = ws.cell(row=row, column=1,
                   value=(
                       "This workbook is produced for informational and analytical purposes only. "
                       "All figures should be independently verified against official manufacturer "
                       "publications before use in investment decisions or financial models. "
                       "The tool's embedded data is based on publicly available press releases as of "
                       f"the date of generation ({datetime.now().strftime('%d %B %Y')}). "
                       "No warranty, express or implied, is made regarding accuracy or completeness."
                   ))
    disc.font = _font(size=10, italic=True)
    disc.fill = _fill("FDECEA")
    disc.alignment = _align("left", wrap=True)
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=4)
    ws.row_dimensions[row].height = 75

    _set_col_widths(ws, [28, 28, 58, 52])


# ── Monthly Tracker sheet ────────────────────────────────────────────────────

_MONTH_ABBR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _write_monthly_sheet(wb: Workbook, data: dict) -> None:
    """
    Write the Monthly Tracker sheet.

    Priority (per manufacturer):
      1. Scraped monthly dict {"YYYY-MM": count}  →  one column per month
      2. Quarterly embedded data                  →  Q1-Q4 columns with note
    """
    ws = wb.create_sheet("Monthly Tracker")
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.tabColor = "2E4057"

    # Banner
    ws.merge_cells("A1:N1")
    c = ws["A1"]
    c.value = "MONTHLY DELIVERY TRACKER — Airbus & Boeing"
    c.fill = _fill("2E4057")
    c.font = Font(bold=True, size=14, color="FFFFFF", name="Calibri")
    c.alignment = _align("center")
    ws.row_dimensions[1].height = 28

    ws.merge_cells("A2:N2")
    c = ws["A2"]
    c.value = (
        "Monthly figures from live scrape of official press releases.  "
        "Where monthly data is unavailable, quarterly estimates (Q1–Q4) are shown."
    )
    c.fill = _fill("3D5A80")
    c.font = Font(size=9, color="FFFFFF", italic=True, name="Calibri")
    c.alignment = _align("center")
    ws.row_dimensions[2].height = 16

    row = 4

    for mfr_key, mfr_label, header_bg in [
        ("airbus", "AIRBUS — Monthly Deliveries (All Families Combined)", C["airbus_dark"]),
        ("boeing", "BOEING — Monthly Deliveries (All Families Combined)", C["boeing_dark"]),
    ]:
        monthly_scraped: dict[str, int] = data.get(f"{mfr_key}_monthly", {})
        quarterly_data  = data[mfr_key]["quarterly"]

        _section_title(ws, row, mfr_label, 14, header_bg)
        row += 1

        if monthly_scraped:
            # ── Scraped monthly view ──────────────────────────────────────────
            # Pivot: rows = years, cols = months Jan-Dec
            year_month: dict[int, dict[int, int]] = {}
            for ym_key, cnt in monthly_scraped.items():
                try:
                    yr, mo = int(ym_key[:4]), int(ym_key[5:7])
                    year_month.setdefault(yr, {})[mo] = cnt
                except ValueError:
                    continue

            monthly_headers = ["Year"] + _MONTH_ABBR + ["Total"]
            for c_i, h in enumerate(monthly_headers, start=1):
                _header_style(ws, row, c_i, h, header_bg)
            row += 1

            for yr in sorted(year_month.keys(), reverse=True):
                mo_data = year_month[yr]
                total   = sum(mo_data.values())
                bg = C["row_alt"] if row % 2 == 0 else C["white"]
                ws.cell(row=row, column=1, value=yr).fill    = _fill(bg)
                ws.cell(row=row, column=1).border            = _border()
                ws.cell(row=row, column=1).alignment         = _align("center")
                ws.cell(row=row, column=1).font              = _font()
                for mo in range(1, 13):
                    val = mo_data.get(mo, None)
                    cell = ws.cell(row=row, column=mo + 1, value=val)
                    cell.fill      = _fill(bg)
                    cell.border    = _border()
                    cell.alignment = _align("center")
                    cell.font      = _font()
                    if val is not None:
                        cell.number_format = "#,##0"
                # Total column
                tot_cell = ws.cell(row=row, column=14, value=total)
                tot_cell.fill      = _fill(C["total_bg"])
                tot_cell.border    = _border()
                tot_cell.alignment = _align("center")
                tot_cell.font      = _font(bold=True)
                tot_cell.number_format = "#,##0"
                row += 1

        else:
            # ── Quarterly fallback ────────────────────────────────────────────
            q_note = ws.cell(
                row=row, column=1,
                value="  Live monthly data unavailable — showing quarterly estimates",
            )
            q_note.font      = _font(size=9, italic=True, color="888888")
            q_note.alignment = _align("left")
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=7)
            row += 1

            q_ann = quarterly_data
            nxt = _write_table(ws, row, q_ann["headers"], q_ann["rows"],
                               header_bg=header_bg, total_col_idx=len(q_ann["headers"]))
            row = nxt

        row += 2

    # ── Combined monthly view (if both scraped) ───────────────────────────────
    ab_monthly = data.get("airbus_monthly", {})
    bo_monthly = data.get("boeing_monthly", {})
    if ab_monthly and bo_monthly:
        all_keys = sorted(set(ab_monthly) | set(bo_monthly), reverse=True)
        _section_title(ws, row, "COMBINED MONTHLY — AIRBUS + BOEING", 14, "2C3E50")
        row += 1
        combo_hdrs = ["Year-Month", "Airbus", "Boeing", "Total Industry"]
        for c_i, h in enumerate(combo_hdrs, start=1):
            _header_style(ws, row, c_i, h, "2C3E50")
        row += 1
        for ym_key in all_keys[:36]:  # up to 3 years
            ab_cnt = ab_monthly.get(ym_key, 0) or 0
            bo_cnt = bo_monthly.get(ym_key, 0) or 0
            bg = C["row_alt"] if row % 2 == 0 else C["white"]
            for c_i, val in enumerate([ym_key, ab_cnt or "—", bo_cnt or "—",
                                        (ab_cnt + bo_cnt) if (ab_cnt or bo_cnt) else "—"],
                                       start=1):
                cell = ws.cell(row=row, column=c_i, value=val)
                cell.fill      = _fill(bg)
                cell.border    = _border()
                cell.alignment = _align("center")
                cell.font      = _font()
                if isinstance(val, int) and c_i > 1:
                    cell.number_format = "#,##0"
            row += 1
        row += 1

    # ── Scrape status note ────────────────────────────────────────────────────
    _section_title(ws, row, "MONTHLY SCRAPE STATUS", 14, "555555")
    row += 1
    for mfr_key, mfr_label in [("airbus_monthly", "Airbus"), ("boeing_monthly", "Boeing")]:
        res = data.get("scrape_results", {}).get(mfr_key, {})
        status  = res.get("status", "not run").upper()
        message = res.get("message", "")
        count   = len(res.get("data", {})) if isinstance(res.get("data"), dict) else 0
        bg = "E8F8E8" if status == "OK" else "FFF3CD" if status == "PARTIAL" else "FDECEA"
        for c_i, val in enumerate(
            [mfr_label, status, f"{count} months parsed", message[:120]], start=1
        ):
            cell = ws.cell(row=row, column=c_i, value=val)
            cell.fill      = _fill(bg)
            cell.border    = _border()
            cell.font      = _font(size=9)
            cell.alignment = _align("left")
        row += 1

    _set_col_widths(ws, [10, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 10, 22, 22])
    _freeze(ws, "B4")


# ── Main entry point ─────────────────────────────────────────────────────────

def build_workbook(merged_data: dict, output_path: str) -> str:
    """
    Build the full Excel workbook from `merged_data` and save to `output_path`.
    Returns the absolute path to the saved file.
    """
    wb = Workbook()
    # Remove the default empty sheet
    wb.remove(wb.active)

    _write_overview(wb, merged_data)
    _write_monthly_sheet(wb, merged_data)
    _write_airbus_sheet(wb, merged_data)
    _write_boeing_sheet(wb, merged_data)

    _write_engine_sheet(
        wb, merged_data, key="ge_aerospace",
        title="GE Aerospace",
        tab_color=C["ge_dark"],
        header_bg=C["ge_dark"],
        mid_bg=C["ge_mid"],
    )
    _write_engine_sheet(
        wb, merged_data, key="pratt_whitney",
        title="Pratt & Whitney",
        tab_color=C["pw_dark"],
        header_bg=C["pw_dark"],
        mid_bg=C["pw_mid"],
    )
    _write_engine_sheet(
        wb, merged_data, key="rolls_royce",
        title="Rolls Royce",
        tab_color=C["rr_dark"],
        header_bg=C["rr_dark"],
        mid_bg=C["rr_mid"],
    )

    _write_prod_rate_sheet(wb, merged_data)
    _write_sources_sheet(wb, merged_data)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    wb.save(output_path)
    return os.path.abspath(output_path)
