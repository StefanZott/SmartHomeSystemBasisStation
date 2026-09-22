#!/usr/bin/env python3
"""Workbook rendering for the base-station bill of materials.

Kept separate from the data gathering so the sheet layout can change without
touching the schematic parsing or the Mouser client.
"""

from __future__ import annotations

import datetime
import re

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

TITLE_FONT = Font(bold=True, size=14)
HEAD_FONT = Font(bold=True, color="FFFFFF")
HEAD_FILL = PatternFill("solid", fgColor="44546A")
MANUAL_FILL = PatternFill("solid", fgColor="FFF2CC")  # still to be filled by hand
API_FILL = PatternFill("solid", fgColor="E2EFDA")  # came from the Mouser API
WARN_FILL = PatternFill("solid", fgColor="FCE4D6")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
EURO = '#,##0.00\\ "€"'

COLUMNS = [
    ("Pos", 5),
    ("Menge", 7),
    ("Referenzen", 26),
    ("Wert (Schaltplan)", 20),
    ("Technik", 8),
    ("Symbol (lib_id)", 30),
    ("Footprint", 38),
    ("Hersteller", 18),
    ("Hersteller-Teilenr.", 24),
    ("Mouser-Teilenr.", 22),
    ("Einzelpreis EUR", 14),
    ("Gesamtpreis EUR", 15),
    ("Staffel ab", 10),
    ("Lager", 9),
    ("Preisquelle", 13),
    ("Mouser-Link", 13),
    ("Datenblatt", 12),
    ("Status", 15),
    ("Hinweis", 60),
]


def _header(worksheet, title: str, subtitle: str, note: str, columns: list) -> int:
    worksheet["A1"] = title
    worksheet["A1"].font = TITLE_FONT
    worksheet["A2"] = subtitle
    worksheet["A3"] = note
    worksheet["A3"].font = Font(italic=True, size=9)
    row = 5
    for index, (label, width) in enumerate(columns, start=1):
        cell = worksheet.cell(row=row, column=index, value=label)
        cell.font = HEAD_FONT
        cell.fill = HEAD_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER
        worksheet.column_dimensions[get_column_letter(index)].width = width
    worksheet.freeze_panes = worksheet.cell(row=row + 1, column=1)
    return row + 1


def _bom_sheet(workbook, groups, technology, status_of, stamp) -> None:
    worksheet = workbook.create_sheet("Stückliste")
    priced = sum(1 for g in groups if g["price"] is not None)
    row = _header(
        worksheet,
        "Stückliste SmartHome-Basisstation",
        f"Quelle: PCB/BasisStation/*.kicad_sch · Stand {stamp} · "
        f"{len(groups)} Positionen · {sum(g['quantity'] for g in groups)} Bauteile",
        "Grün = Preis aus der Mouser-API (Tagespreis, unverbindlich). "
        "Gelb = von Hand zu füllen. Gesamtpreis und Summe rechnen sich aus Menge × Einzelpreis.",
        COLUMNS,
    )

    first_data_row = row
    for position, group in enumerate(groups, start=1):
        status, note = status_of(group)
        values = [
            position,
            group["quantity"],
            ", ".join(group["references"]),
            group["value"],
            technology(group["footprint"]),
            group["lib_id"],
            group["footprint"],
            group["manufacturer"],
            group["manufacturer_part"],
            group["mouser_part"],
            group["price"],
            None,  # formula below
            group["price_break"],
            group["stock"],
            group["source"],
            None,  # link below
            None,  # datasheet below
            status,
            note,
        ]
        for index, value in enumerate(values, start=1):
            cell = worksheet.cell(row=row, column=index, value=value)
            cell.border = BORDER
            cell.alignment = Alignment(vertical="top", wrap_text=index in (3, 19))

        worksheet.cell(row=row, column=12).value = (
            f'=IF(OR(K{row}="",B{row}=""),"",B{row}*K{row})'
        )
        for column in (11, 12):
            worksheet.cell(row=row, column=column).number_format = EURO

        price_cell = worksheet.cell(row=row, column=11)
        price_cell.fill = API_FILL if group["price"] is not None else MANUAL_FILL
        if not group["mouser_part"]:
            worksheet.cell(row=row, column=10).fill = MANUAL_FILL

        if group["url"]:
            link = worksheet.cell(row=row, column=16, value="Mouser")
            link.hyperlink = group["url"]
            link.font = Font(color="0563C1", underline="single")
        if group["datasheet"]:
            sheet_link = worksheet.cell(row=row, column=17, value="PDF")
            sheet_link.hyperlink = group["datasheet"]
            sheet_link.font = Font(color="0563C1", underline="single")

        if status in ("prüfen", "unvollständig"):
            worksheet.cell(row=row, column=18).fill = WARN_FILL
        row += 1

    last_data_row = row - 1
    worksheet.cell(row=row + 1, column=10, value="Summe erfasster Positionen").font = Font(bold=True)
    total = worksheet.cell(
        row=row + 1, column=12, value=f"=SUM(L{first_data_row}:L{last_data_row})"
    )
    total.font = Font(bold=True)
    total.number_format = EURO
    total.border = BORDER

    worksheet.cell(
        row=row + 3,
        column=1,
        value=(
            f"Von {len(groups)} Positionen tragen {priced} einen Preis aus der Mouser-API. "
            "Die Summe ist deshalb eine Teilsumme, kein Gesamtpreis der Baugruppe."
        ),
    ).font = Font(italic=True, size=9)
    worksheet.auto_filter.ref = f"A{first_data_row - 1}:S{last_data_row}"


def _single_sheet(workbook, instances, technology, stamp) -> None:
    worksheet = workbook.create_sheet("Einzelpositionen")
    columns = [
        ("Referenz", 12),
        ("Wert", 20),
        ("Technik", 8),
        ("Blatt", 30),
        ("Symbol (lib_id)", 30),
        ("Footprint", 40),
        ("Hersteller", 18),
        ("Hersteller-Teilenr.", 24),
        ("Mouser-Teilenr.", 22),
    ]
    row = _header(
        worksheet,
        "Einzelpositionen",
        f"Alle {len(instances)} bestückten Referenzen einzeln · Stand {stamp}",
        "Dient dem Abgleich gegen den Schaltplan — jede Referenz erscheint genau einmal.",
        columns,
    )
    for item in instances:
        values = [
            item["reference"],
            item["value"],
            technology(item["footprint"]),
            item["sheet"],
            item["lib_id"],
            item["footprint"],
            item["manufacturer"],
            item["manufacturer_part"],
            item["mouser_part"],
        ]
        for index, value in enumerate(values, start=1):
            cell = worksheet.cell(row=row, column=index, value=value)
            cell.border = BORDER
        row += 1
    worksheet.auto_filter.ref = f"A5:I{row - 1}"


def _plural(count: int, singular: str, plural: str) -> str:
    """German needs the singular for exactly one; '1 Positionen' reads as a bug."""
    return f"{count} {singular if count == 1 else plural}"


def _open_points_sheet(workbook, groups, technology, stamp) -> None:
    worksheet = workbook.create_sheet("Offene Punkte")
    columns = [("Nr", 5), ("Betrifft", 34), ("Punkt", 52), ("Warum es zählt", 62), ("Wer entscheidet", 16)]
    generic = [g for g in groups if g["price"] is None and not g["mouser_part"]]
    through_hole = sorted(
        (r for g in groups if technology(g["footprint"]) == "THT" for r in g["references"]),
        key=lambda r: (re.match(r"([A-Za-z_]+)", r).group(1), int(re.sub(r"\D", "", r) or 0)),
    )
    row = _header(
        worksheet,
        "Offene Punkte vor der Bestellung",
        f"Stand {stamp} · Der Schaltplan ist elektrisch fertig (ERC 0 Fehler).",
        "Diese Punkte betreffen ausschließlich die Beschaffung, nicht die Funktion.",
        columns,
    )
    mismatched = [g for g in groups if g.get("mismatch")]
    unavailable = [
        g for g in groups if (g["mouser_part"] or g["manufacturer_part"]) and g["price"] is None
    ]
    no_stock = [g for g in groups if g["price"] is not None and g.get("stock") == 0]

    points = []
    if mismatched:
        points.append(
            (
                _plural(len(mismatched), "veraltete Mouser-Nummer im Schaltplan", "veraltete Mouser-Nummern im Schaltplan"),
                "; ".join(
                    f"{', '.join(g['references'])}: {g['schematic_mouser_part']} → {g['mouser_part']}"
                    for g in mismatched
                ),
                "Die im Symbol gepflegte Mouser-Nummer führt zu keinem Treffer mehr; die gültige "
                "Nummer stammt aus der Suche über die Herstellernummer. Solange das Schaltplanfeld "
                "nicht korrigiert ist, liefert jeder neue Export wieder die alte Nummer.",
                "Agent",
            )
        )
    if unavailable:
        points.append(
            (
                _plural(len(unavailable), "Position ohne Preis bei Mouser", "Positionen ohne Preis bei Mouser"),
                "; ".join(
                    f"{', '.join(g['references'])} ({g['value']})" for g in unavailable
                ),
                "Teil ist bekannt, aber Mouser liefert keine Preisstaffel — entweder nicht "
                "geführt oder nur auf Anfrage. Vor der Bestellung Alternative prüfen oder einen "
                "zweiten Distributor anfragen.",
                "Bediener",
            )
        )
    if no_stock:
        points.append(
            (
                _plural(len(no_stock), "Position mit Lagerbestand 0", "Positionen mit Lagerbestand 0"),
                "; ".join(
                    f"{', '.join(g['references'])} ({g['mouser_part']})" for g in no_stock
                ),
                "Gelistet und bepreist, aber nicht ab Lager verfügbar. Lieferzeit klären, bevor "
                "der Termin für den Prototypenaufbau steht.",
                "Bediener",
            )
        )

    points += [
        (
            _plural(len(generic), "Position ohne Teilenummer", "Positionen ohne Teilenummer"),
            "Überwiegend generische Passivteile, die nur einen Wert tragen.",
            "Für eine Bestellung fehlen Toleranz, Spannungsfestigkeit, Dielektrikum (X7R/C0G) "
            "und Belastbarkeit. Kritisch bei C25/C26 am 25-MHz-Quarz und den 1-%-Widerständen "
            "des Ethernet-Zweigs.",
            "Bediener",
        ),
        (
            "Abgeleitete Teilenummern",
            "Bei D11, D12, U1, L1 und J6 stammt die Nummer aus Wert oder Bibliotheksnamen, "
            "nicht aus einem gepflegten Feld.",
            "In Spalte R als \"abgeleitet\" markiert. Vor der Bestellung am Datenblatt "
            "bestätigen — Serienbezeichnungen wie SRN6045TA brauchen noch den Wert-Suffix.",
            "Bediener",
        ),
        (
            "F1 (Sicherung)",
            "Der Wert lautet schlicht \"Fuse\" — kein Strom- oder Auslösewert.",
            "Ohne Nennstrom ist die Sicherung nicht bestellbar und die Schutzfunktion nicht "
            "definiert. Hängt an der Stromaufnahme der Baugruppe (SHBS-4).",
            "Bediener",
        ),
        (
            "FB1 (Ferritperle)",
            "Nutzt das Symbol Device:R — also einen Widerstand.",
            "Elektrisch folgenlos (zweipoliges Passivteil), aber Symbol und Bauteil "
            "widersprechen sich. Wer den Schaltplan liest, sieht einen Widerstand.",
            "Agent",
        ),
        (
            "J6 (Stiftleiste)",
            "Wert ist der generische KiCad-Symbolname \"Conn_02x03_Odd_Even\".",
            "Der Footprint verweist auf Würth 61200621621. Der Wert sollte die "
            "Bestellbezeichnung tragen, sonst ist die Stückliste ohne Blick in den "
            "Footprint nicht lesbar.",
            "Agent",
        ),
        (
            "D8, D9, D10 (LEDs)",
            "Nutzen das generische Symbol Device:LED, während D7 das spezifische "
            "WL-TMRC_3MM-Symbol nutzt.",
            "Uneinheitlich. Zudem liegen D8/D9 auf der Serie WL-TMRW, D10 auf WL-TMRC — "
            "zwei verschiedene Würth-Serien in derselben Funktionsgruppe.",
            "Bediener",
        ),
        (
            f"Mischbestückung THT / SMD ({len(through_hole)} bedrahtete Teile)",
            "Bedrahtet: " + ", ".join(through_hole) + ".",
            "Bedrahtete Teile erzwingen einen zweiten Bestückungsdurchlauf und verteuern die "
            "Fertigung spürbar. R13–R16 und R23–R26 sitzen zudem im Footprint DIN0617 "
            "(17 mm, 2-W-Klasse) — für 220 Ω und 4,7 kΩ in einer Signalfunktion "
            "überdimensioniert. Bei den LEDs und Steckverbindern ist THT bewusst gewählt; "
            "zu prüfen ist vor allem, ob Q1–Q4 und die Widerstände SMD werden können.",
            "Bediener",
        ),
        (
            "Preise sind Tagespreise",
            "Die grün hinterlegten Einzelpreise stammen aus der Mouser-API zum Stand oben.",
            "Sie sind unverbindlich, staffelabhängig (Spalte M zeigt die zugrunde gelegte "
            "Staffelmenge) und ohne Zoll, Versand und Steuer. Für ein Angebot neu abfragen.",
            "Bediener",
        ),
    ]
    for number, (affects, point, why, who) in enumerate(points, start=1):
        for index, value in enumerate([number, affects, point, why, who], start=1):
            cell = worksheet.cell(row=row, column=index, value=value)
            cell.border = BORDER
            cell.alignment = Alignment(vertical="top", wrap_text=index in (2, 3, 4))
        row += 1


def write_workbook(path, groups, instances, technology, status_of) -> None:
    stamp = datetime.date.today().isoformat()
    workbook = Workbook()
    workbook.remove(workbook.active)
    _bom_sheet(workbook, groups, technology, status_of, stamp)
    _single_sheet(workbook, instances, technology, stamp)
    _open_points_sheet(workbook, groups, technology, stamp)
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(path)
