#!/usr/bin/env python3
"""Generate the orderable bill of materials for the SmartHome base station.

Reads the KiCad schematic sheets directly rather than going through
`kicad-cli sch export bom`, because part numbers in this project live under
inconsistent field names depending on where a symbol came from (SnapEDA, the
Wuerth generator, hand-edited). The CLI exporter can only pull one fixed
field name and would silently return nothing for most parts.

Mouser responses are cached on disk so repeated runs neither hammer the API
nor burn the daily quota, and so a run stays reproducible without network.

Usage:
    python3 tmp/bom/generate_bom.py [--no-network] [--refresh]
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sexp import children, parse  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCHEMATIC_GLOB = str(ROOT / "PCB" / "BasisStation" / "*.kicad_sch")
CACHE_PATH = ROOT / "tmp" / "bom" / "mouser_cache.json"
KEY_PATH = ROOT / "secrets" / "mouser_api_key"
OUTPUT_PATH = ROOT / "tmp" / "report" / "2026-09-22_stueckliste-basisstation.xlsx"

MOUSER_ENDPOINT = "https://api.mouser.com/api/v2/search/{mode}"

# Field-name aliases. Order matters: the first populated field wins.
MOUSER_FIELDS = ["Mouser Part Number", "MOUSER_PART_NUMBER"]
MPN_FIELDS = ["Manufacturer_Part_Number", "MANUFACTURER_PART_NUMBER", "MP", "Part Number", "MPN"]
MANUFACTURER_FIELDS = [
    "Manufacturer",
    "MANUFACTURER",
    "MF",
    "Manufacturer_Name",
    "MANUFACTURER_NAME",
]
DATASHEET_FIELDS = ["Datasheet", "DATASHEET"]

# Mounting technology per footprint. Explicit rather than guessed from the
# name: a wrong THT/SMD call silently changes the assembly cost estimate.
THROUGH_HOLE_FOOTPRINTS = {
    "Package_TO_SOT_THT:TO-92_Inline",
    "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal",
    "Resistor_THT:R_Axial_DIN0617_L17.0mm_D6.0mm_P20.32mm_Horizontal",
    "WL-TMRC_3MM:WL-TMRC_3MM",
    "WL-TMRW_3MM:WL-TMRW_3MM",
    "wuerth_6120XX21621:61200621621",
    "wuerth_rj45:T_Wurth_WE-RJ45LAN_7499011121A",
    "shbs_power:USB_C_Receptacle_Amphenol_12401548E4-2A",
    "1543-650-149:1543650149",
}

# Values that are already a orderable type designation even though no part
# number field is set. Flagged "abgeleitet" so nobody orders them unchecked.
DERIVED_PART_NUMBERS = {
    "D11": ("SS34", ""),
    "D12": ("SMAJ5.0A", ""),
    "U1": ("D3V3XA4B10LP", "Diodes Incorporated"),
    "L1": ("SRN6045TA-100M", "Bourns"),
    "J6": ("61200621621", "Würth Elektronik"),
}

GENERIC_PREFIXES = ("R", "C", "L", "FB")


def pick(properties: dict, keys: list) -> str:
    """Return the first non-empty value among `keys`."""
    for key in keys:
        value = properties.get(key, "")
        if value and value.strip():
            return value.strip()
    return ""


def reference_sort_key(reference: str):
    match = re.match(r"([A-Za-z_]+)(\d*)", reference)
    prefix = match.group(1) if match else reference
    number = int(match.group(2)) if match and match.group(2) else 0
    return (prefix, number)


def read_instances() -> list:
    """Collect every placed symbol across all schematic sheets."""
    instances = []
    for path in sorted(glob.glob(SCHEMATIC_GLOB)):
        document = parse(pathlib.Path(path).read_text(encoding="utf-8"))
        for node in children(document, "symbol"):
            properties = {p[1]: p[2] for p in children(node, "property")}
            reference = properties.get("Reference", "").strip()
            # Power flags and net ties carry a '#' reference and never ship.
            if not reference or reference.startswith("#"):
                continue
            in_bom = next((c[1] for c in children(node, "in_bom")), "yes")
            if str(in_bom) == "no":
                continue
            lib_id = next((c[1] for c in children(node, "lib_id")), "")
            manufacturer_part, manufacturer = DERIVED_PART_NUMBERS.get(reference, ("", ""))
            resolved_part = pick(properties, MPN_FIELDS)
            derived = False
            if not resolved_part and manufacturer_part:
                resolved_part, derived = manufacturer_part, True
            instances.append(
                {
                    "reference": reference,
                    "value": properties.get("Value", "").strip(),
                    "footprint": properties.get("Footprint", "").strip(),
                    "lib_id": str(lib_id),
                    "sheet": pathlib.Path(path).name,
                    "mouser_part": pick(properties, MOUSER_FIELDS),
                    "manufacturer_part": resolved_part,
                    "manufacturer": pick(properties, MANUFACTURER_FIELDS) or manufacturer,
                    "datasheet": pick(properties, DATASHEET_FIELDS),
                    "derived": derived,
                }
            )
    return instances


def group_instances(instances: list) -> list:
    """Collapse identical parts into orderable positions."""
    groups = OrderedDict()
    for item in instances:
        # Keyed on what is ordered, not on which symbol was drawn: J1 and
        # J_PWR1 are the same Amphenol receptacle behind two different
        # symbols, and a buyer wants one line of quantity two.
        key = (item["value"], item["footprint"])
        group = groups.setdefault(
            key,
            {
                "value": item["value"],
                "footprint": item["footprint"],
                "lib_ids": [],
                "references": [],
                "mouser_part": "",
                "manufacturer_part": "",
                "manufacturer": "",
                "datasheet": "",
                "derived": False,
            },
        )
        group["references"].append(item["reference"])
        if item["lib_id"] and item["lib_id"] not in group["lib_ids"]:
            group["lib_ids"].append(item["lib_id"])
        for field in ("mouser_part", "manufacturer_part", "manufacturer", "datasheet"):
            if not group[field] and item[field]:
                group[field] = item[field]
        group["derived"] = group["derived"] or item["derived"]

    result = list(groups.values())
    for group in result:
        group["references"].sort(key=reference_sort_key)
        group["quantity"] = len(group["references"])
        group["lib_id"] = ", ".join(group["lib_ids"])
    result.sort(key=lambda g: reference_sort_key(g["references"][0]))
    return result


# --------------------------------------------------------------------------
# Mouser


def load_cache() -> dict:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {}


def save_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")


def mouser_query(api_key: str, mode: str, payload: dict) -> dict:
    """Call one Mouser search endpoint and return the decoded response."""
    request = urllib.request.Request(
        MOUSER_ENDPOINT.format(mode=mode) + f"?apiKey={api_key}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def normalise(text: str) -> str:
    """Strip the separators Mouser and KiCad disagree about ('12401548E4#2A')."""
    return re.sub(r"[^A-Z0-9]", "", (text or "").upper())


def stock_of(part: dict) -> int:
    try:
        return int(part.get("AvailabilityInStock") or 0)
    except (TypeError, ValueError):
        return 0


def orderable(part: dict) -> bool:
    """Mouser returns 'N/A' as the part number for items it does not carry."""
    number = (part.get("MouserPartNumber") or "").strip()
    return bool(number) and number.upper() != "N/A"


def _call(api_key: str, cache: dict, cache_key: str, mode: str, payload: dict) -> list:
    """Cached Mouser call returning the raw parts list."""
    if cache_key in cache:
        return cache[cache_key] or []
    if not api_key:
        return []  # offline run: cache only, never guess
    try:
        response = mouser_query(api_key, mode, payload)
    except (urllib.error.URLError, TimeoutError) as error:
        print(f"  ! Abfrage fehlgeschlagen fuer {cache_key}: {error}", file=sys.stderr)
        return []
    time.sleep(1.0)  # stay well inside the free-tier rate limit
    if response.get("Errors"):
        print(f"  ! API-Fehler fuer {cache_key}: {response['Errors']}", file=sys.stderr)
        cache[cache_key] = []
        return []
    parts = (response.get("SearchResults") or {}).get("Parts") or []
    cache[cache_key] = parts
    return parts


def lookup(api_key: str, cache: dict, mouser_part: str, manufacturer_part: str):
    """Resolve one position against Mouser.

    Tries the stored Mouser part number first, then falls back to a keyword
    search on the manufacturer part number. The fallback matters: several
    numbers in this schematic are stale, and an exact lookup on them returns
    nothing at all. Returns (part, how) where `how` records which route hit.
    """
    if mouser_part:
        parts = _call(
            api_key,
            cache,
            f"mouser:{mouser_part}",
            "partnumber",
            {"SearchByPartRequest": {"mouserPartNumber": mouser_part,
                                     "partSearchOptions": "Exact"}},
        )
        exact = [p for p in parts if normalise(p.get("MouserPartNumber")) == normalise(mouser_part)]
        if exact and orderable(exact[0]):
            return exact[0], "mouser-nr"

    if not manufacturer_part:
        return None, ""

    parts = _call(
        api_key,
        cache,
        f"mpn:{manufacturer_part}",
        "keyword",
        {"SearchByKeywordRequest": {"keyword": manufacturer_part, "records": 10}},
    )
    wanted = normalise(manufacturer_part)
    # Accept a suffixed variant (packaging codes such as '-7' for tape & reel),
    # but never a shorter or unrelated number.
    candidates = [
        p
        for p in parts
        if normalise(p.get("ManufacturerPartNumber")).startswith(wanted) and orderable(p)
    ]
    if not candidates:
        return None, ""
    # Prefer something actually on the shelf, then the closest number.
    candidates.sort(
        key=lambda p: (
            stock_of(p) == 0,
            len(normalise(p.get("ManufacturerPartNumber"))) - len(wanted),
        )
    )
    return candidates[0], "mpn-suche"


PRICE_PATTERN = re.compile(r"([\d.,]+)")


def parse_price(raw: str) -> float | None:
    """Turn Mouser's localised '1,17 €' into a float."""
    if not raw:
        return None
    match = PRICE_PATTERN.search(raw)
    if not match:
        return None
    text = match.group(1)
    # German formatting: dot groups thousands, comma is the decimal separator.
    if "," in text:
        text = text.replace(".", "").replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


def price_for_quantity(part: dict, quantity: int):
    """Pick the price break that actually applies to the ordered quantity."""
    breaks = []
    for entry in part.get("PriceBreaks") or []:
        price = parse_price(entry.get("Price", ""))
        if price is not None:
            breaks.append((int(entry.get("Quantity", 1)), price))
    if not breaks:
        return None, None
    breaks.sort()
    applicable = [b for b in breaks if b[0] <= max(quantity, 1)]
    chosen = applicable[-1] if applicable else breaks[0]
    return chosen[1], chosen[0]


def enrich(groups: list, use_network: bool, refresh: bool) -> None:
    cache = {} if refresh else load_cache()
    api_key = ""
    if use_network:
        if not KEY_PATH.exists():
            print("! secrets/mouser_api_key fehlt - laufe ohne Netzabfrage", file=sys.stderr)
            use_network = False
        else:
            api_key = KEY_PATH.read_text(encoding="utf-8").strip()

    for group in groups:
        group["price"] = None
        group["price_break"] = None
        group["stock"] = ""
        group["url"] = ""
        group["source"] = ""
        group["schematic_mouser_part"] = group["mouser_part"]
        group["mismatch"] = False
        if not (group["mouser_part"] or group["manufacturer_part"]):
            continue
        if not use_network and not cache:
            continue  # nothing to resolve against
        part, how = lookup(api_key, cache, group["mouser_part"], group["manufacturer_part"])
        if not part:
            continue

        resolved_part = (part.get("MouserPartNumber") or "").strip()
        if group["schematic_mouser_part"] and normalise(resolved_part) != normalise(
            group["schematic_mouser_part"]
        ):
            # The schematic field is stale - report it rather than quietly
            # replacing it, so the mismatch reaches the schematic as a fix.
            group["mismatch"] = True
        group["mouser_part"] = resolved_part

        price, price_break = price_for_quantity(part, group["quantity"])
        group["price"] = price
        group["price_break"] = price_break
        group["stock"] = stock_of(part)
        group["url"] = part.get("ProductDetailUrl") or ""
        group["source"] = f"Mouser-API ({how})"
        if not group["manufacturer"]:
            group["manufacturer"] = part.get("Manufacturer") or ""
        if not group["manufacturer_part"]:
            group["manufacturer_part"] = part.get("ManufacturerPartNumber") or ""
        if not group["datasheet"]:
            group["datasheet"] = part.get("DataSheetUrl") or ""

    save_cache(cache)


# --------------------------------------------------------------------------
# Classification


def technology(footprint: str) -> str:
    if not footprint:
        return ""
    return "THT" if footprint in THROUGH_HOLE_FOOTPRINTS else "SMD"


def is_generic(group: dict) -> bool:
    """A plain passive whose value alone is not orderable."""
    if group["mouser_part"] or group["manufacturer_part"]:
        return False
    prefix = re.match(r"([A-Za-z_]+)", group["references"][0]).group(1)
    return prefix in GENERIC_PREFIXES


def status_of(group: dict) -> tuple:
    """Return (status, note) for one position."""
    notes = []
    if group.get("mismatch"):
        notes.append(
            f"Mouser-Nr. im Schaltplan ({group['schematic_mouser_part']}) stimmt nicht — "
            f"gültig ist {group['mouser_part']}. Schaltplanfeld korrigieren."
        )
    if group["price"] is not None and group.get("stock") == 0:
        notes.append("Bei Mouser gelistet, aber Lagerbestand 0 — Lieferzeit vor der Bestellung prüfen.")
    if group["derived"]:
        notes.append("Teilenummer aus Wert/Bibliothek abgeleitet — am Datenblatt bestätigen.")
        return ("abgeleitet", " ".join(notes))
    if group["price"] is not None:
        status = "prüfen" if (notes and group.get("mismatch")) else "eindeutig"
        return (status, " ".join(notes))
    if group["mouser_part"] or group["manufacturer_part"]:
        if group["source"]:
            # Resolved at Mouser, but the response carried no price break.
            notes.append(
                "Bei Mouser gelistet, aber ohne Preisangabe und ohne Lagerbestand — "
                "Preis und Lieferzeit anfragen."
            )
        else:
            notes.append(
                "Teilenummer bekannt, aber bei Mouser kein bestellbarer Treffer — "
                "Alternative oder anderen Distributor suchen."
            )
        return ("prüfen", " ".join(notes))
    if is_generic(group):
        return (
            "Auswahl nötig",
            "Generisches Passivteil — Toleranz, Spannung, Dielektrikum bzw. Belastbarkeit festlegen.",
        )
    if not group["value"]:
        return ("unvollständig", "Kein Wert im Schaltplan gesetzt.")
    return ("Auswahl nötig", "Keine Teilenummer hinterlegt.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-network", action="store_true", help="Nur den lokalen Cache nutzen")
    parser.add_argument("--refresh", action="store_true", help="Cache verwerfen und neu abfragen")
    args = parser.parse_args()

    instances = read_instances()
    groups = group_instances(instances)
    print(f"Instanzen: {len(instances)}   Positionen: {len(groups)}")

    assert sum(g["quantity"] for g in groups) == len(instances), "Mengensumme weicht ab"
    seen = [r for g in groups for r in g["references"]]
    assert len(seen) == len(set(seen)), "Referenz in mehr als einer Gruppe"

    enrich(groups, use_network=not args.no_network, refresh=args.refresh)

    priced = [g for g in groups if g["price"] is not None]
    print(f"Mit Preis aus der API: {len(priced)} von {len(groups)} Positionen")

    from write_xlsx import write_workbook  # local module, imported late

    write_workbook(OUTPUT_PATH, groups, instances, technology, status_of)
    print(f"Geschrieben: {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
