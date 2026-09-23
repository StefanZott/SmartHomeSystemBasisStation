#!/usr/bin/env python3
"""Generate the orderable bill of materials for the SmartHome base station.

Reads the KiCad schematic sheets directly rather than going through
`kicad-cli sch export bom`, because part numbers in this project live under
inconsistent field names depending on where a symbol came from (SnapEDA, the
Wuerth generator, hand-edited). The CLI exporter can only pull one fixed
field name and would silently return nothing for most parts.

Every position with a known part number is priced at Mouser and DigiKey side
by side; the cheapest offer that can deliver wins (see choose_source).
Responses are cached on disk so repeated runs neither hammer the APIs nor burn
the daily quota, and so a run stays reproducible without network.

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
import digikey  # noqa: E402
from sexp import children, parse  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCHEMATIC_GLOB = str(ROOT / "pcb" / "BasisStation" / "*.kicad_sch")
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
    # SMD contacts, but the four shell legs are through-hole.
    "shbs_power:USB_C_Receptacle_Amphenol_12401598E4-2A",
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

# Proposed parts for positions whose schematic carries only a value, or whose
# part is discontinued (house standard proposed 2026-09-23, SHBS-17, task
# 0041). Shown as "Vorschlag" until the operator confirms them and they move
# into the schematic fields - the schematic stays the source of truth.
_RES_0805 = "Dickschicht 0805, 1 %, 0,125 W (Hausstandard)"
_CAP_X7R = "X7R, 50 V, 0805 (Hausstandard)"
_PROPOSALS = [
    (("R17",), "RC0805FR-0749K9L", "YAGEO", _RES_0805),
    (("R18",), "RC0805FR-0716K2L", "YAGEO", _RES_0805),
    (("R19", "R20", "R21", "R22"), "RC0805FR-075K1L", "YAGEO", _RES_0805),
    (("R27",), "RC0805FR-0712K4L", "YAGEO", _RES_0805),
    (("R28", "R29", "R30", "R31", "R32"), "RC0805FR-0710KL", "YAGEO", _RES_0805),
    (("R33", "R34"), "RC0805FR-07220RL", "YAGEO", _RES_0805),
    (("R35",), "RC0805JR-070RL", "YAGEO", "Nullohm-Brücke 0805"),
    (("R36", "R37", "R39", "R40"), "RC0805FR-0749R9L", "YAGEO", _RES_0805),
    (("R38",), "RC0805FR-0710RL", "YAGEO", _RES_0805),
    (("R9",), "MFR-25FBF52-10K", "YAGEO", "Metallschicht 0207, 1 %, 0,25 W"),
    (
        ("R13", "R14", "R15", "R16"),
        "PR02000202200JR500",
        "Vishay BC Components",
        "Metallschicht 2 W, 5 %, passend zum Footprint DIN0617 (Raster 20,32 mm); "
        "elektrisch genügt 0,25 W — siehe Offene Punkte zur Mischbestückung",
    ),
    (
        ("R23", "R24", "R25", "R26"),
        "PR02000204701JR500",
        "Vishay BC Components",
        "Metallschicht 2 W, 5 %, passend zum Footprint DIN0617 (Raster 20,32 mm); "
        "elektrisch genügt 0,25 W — siehe Offene Punkte zur Mischbestückung",
    ),
    (("C13", "C27"), "CL21B106KOQNNNE", "Samsung", "X7R, 16 V, 0805"),
    (("C14",), "CL21A226MOQNNNE", "Samsung", "X5R, 16 V, 0805 — Kapazität sinkt unter DC-Vorspannung"),
    (("C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22"), "CC0805KRX7R9BB104", "YAGEO", _CAP_X7R),
    (("C23",), "CL21A475KAQNNNE", "Samsung", "X5R, 25 V, 0805"),
    (("C24", "C31"), "CC0805KRX7R9BB103", "YAGEO", _CAP_X7R),
    (
        ("C25", "C26"),
        "CC0805JRNPO9BN270",
        "YAGEO",
        "C0G, 50 V, 5 %. Wert geprüft: Quarz Y1 hat 18 pF Last, "
        "2 × (18 pF − ~4,5 pF Streukapazität) ≈ 27 pF",
    ),
    (("C28",), "C1206C102KGRACTU", "KEMET", "X7R, 2 kV, 1206 — Schirmabschluss Ethernet"),
    (("C29", "C30"), "CC0805KRX7R9BB682", "YAGEO", _CAP_X7R),
    (("C32",), "CL21B223KBANNNC", "Samsung", _CAP_X7R),
    (("D8",), "151033BS03000", "Würth Elektronik", "WL-TMRW 3 mm blau, passend zum Footprint"),
    (("D9",), "151033RS03000", "Würth Elektronik", "WL-TMRW 3 mm rot, passend zum Footprint"),
    (("D10",), "151031VS06000", "Würth Elektronik", "WL-TMRC 3 mm grün, passend zum Footprint"),
    (("Q1", "Q2", "Q3", "Q4"), "BC33740TA", "onsemi", "BC337-40 (höchste Verstärkungsgruppe), TO-92"),
    (
        ("F1",),
        "MF-NSMF110-2",
        "Bourns",
        "Polyfuse 1206, Haltestrom 1,1 A, 6 V, gemäß power_supply.md; "
        "Last ~400 mA am 5-V-Eingang (~36 %)",
    ),
    (("FB1",), "BLM21PG601SN1D", "Murata", "600 Ω @ 100 MHz, 0805"),
]
PROPOSED_PARTS = {ref: entry[1:] for entry in _PROPOSALS for ref in entry[0]}

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
            mouser_part = pick(properties, MOUSER_FIELDS)
            manufacturer = pick(properties, MANUFACTURER_FIELDS) or manufacturer
            proposal, replaced = "", ""
            if reference in PROPOSED_PARTS:
                proposed_part, proposed_maker, proposal = PROPOSED_PARTS[reference]
                # A schematic part number here is a discontinued one being
                # replaced; its Mouser number would resolve the old part.
                replaced = resolved_part
                resolved_part, manufacturer, mouser_part = proposed_part, proposed_maker, ""
                derived = False
            instances.append(
                {
                    "reference": reference,
                    "value": properties.get("Value", "").strip(),
                    "footprint": properties.get("Footprint", "").strip(),
                    "lib_id": str(lib_id),
                    "sheet": pathlib.Path(path).name,
                    "mouser_part": mouser_part,
                    "manufacturer_part": resolved_part,
                    "manufacturer": manufacturer,
                    "datasheet": "" if proposal else pick(properties, DATASHEET_FIELDS),
                    "derived": derived,
                    "proposal": proposal,
                    "replaced": replaced,
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
                "proposal": "",
                "replaced": "",
            },
        )
        group["references"].append(item["reference"])
        if item["lib_id"] and item["lib_id"] not in group["lib_ids"]:
            group["lib_ids"].append(item["lib_id"])
        for field in ("mouser_part", "manufacturer_part", "manufacturer", "datasheet", "proposal", "replaced"):
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


def mouser_offer(api_key: str, cache: dict, group: dict) -> dict | None:
    """Mouser result in the distributor-neutral offer shape."""
    part, how = lookup(api_key, cache, group["mouser_part"], group["manufacturer_part"])
    if not part:
        return None
    price, price_break = price_for_quantity(part, group["quantity"])
    lifecycle = part.get("LifecycleStatus") or ""
    return {
        "part": (part.get("MouserPartNumber") or "").strip(),
        "price": price,
        "price_break": price_break,
        "stock": stock_of(part),
        "url": part.get("ProductDetailUrl") or "",
        "lifecycle": lifecycle,
        "end_of_life": is_end_of_life(lifecycle),
        "manufacturer": part.get("Manufacturer") or "",
        "manufacturer_part": part.get("ManufacturerPartNumber") or "",
        "datasheet": part.get("DataSheetUrl") or "",
        "how": how,
    }


# --------------------------------------------------------------------------
# DigiKey


def digikey_offer(client, group: dict) -> dict | None:
    """Resolve one position at DigiKey via the manufacturer part number.

    Same two-step route as Mouser: exact number first, then a keyword search
    that accepts packaging suffixes ('D3V3XA4B10LP' -> '...-7') and generic
    types made by several vendors ('SS34').
    """
    wanted = group["manufacturer_part"]
    if not wanted:
        return None
    product = client.details(wanted)
    if product:
        result = digikey.offer(product, group["quantity"], "hersteller-nr")
        result["end_of_life"] = result["end_of_life"] or is_end_of_life(result["lifecycle"])
        return result

    target = normalise(wanted)
    candidates = []
    for product in client.keyword(wanted):
        number = normalise(product.get("ManufacturerProductNumber"))
        if not number.startswith(target):
            continue
        candidate = digikey.offer(product, group["quantity"], "stichwortsuche")
        candidate["end_of_life"] = candidate["end_of_life"] or is_end_of_life(candidate["lifecycle"])
        candidates.append((candidate, len(number) - len(target)))
    if not candidates:
        return None
    # Orderable and stocked first, then the closest number, then the price.
    candidates.sort(
        key=lambda c: (
            c[0]["price"] is None,
            c[0]["end_of_life"],
            c[0]["stock"] < group["quantity"],
            c[1],
            c[0]["price"] or 0,
        )
    )
    return candidates[0][0]


# --------------------------------------------------------------------------
# Distributor choice

# The cheapest distributor that can deliver wins (operator decision
# 2026-09-23, SHBS-17). PREFERENCE only breaks ties and orders the fallback;
# DigiKey first because it is the house distributor.
PREFERENCE = ("DigiKey", "Mouser")

END_OF_LIFE_MARKERS = (
    "obsolet",
    "end of life",
    "nicht für neukonstruktionen",
    "not recommended",
    "nrnd",
    "abgekündigt",
    "discontinued",
    "letzte",
    "last time",
)


def is_end_of_life(lifecycle: str) -> bool:
    text = (lifecycle or "").lower()
    return any(marker in text for marker in END_OF_LIFE_MARKERS)


def deliverable(offer: dict | None, quantity: int) -> bool:
    return bool(offer) and offer["price"] is not None and offer["stock"] >= quantity


def choose_source(group: dict) -> tuple:
    """Return (distributor, deliverable) for one position."""
    offers = group["offers"]
    candidates = [n for n in PREFERENCE if deliverable(offers.get(n), group["quantity"])]
    if candidates:
        # min() keeps the first of equal prices, i.e. the preferred one.
        return min(candidates, key=lambda n: offers[n]["price"]), True
    # Nobody has it on the shelf: still name a quote so the sum stays
    # meaningful, taking whoever has the larger (possibly zero) stock.
    priced = [n for n in PREFERENCE if offers.get(n) and offers[n]["price"] is not None]
    if priced:
        return max(priced, key=lambda n: offers[n]["stock"]), False
    return "", False


def enrich(groups: list, use_network: bool, refresh: bool) -> None:
    cache = {} if refresh else load_cache()
    api_key = ""
    if use_network:
        if not KEY_PATH.exists():
            print("! secrets/mouser_api_key fehlt - Mouser nur aus dem Cache", file=sys.stderr)
        else:
            api_key = KEY_PATH.read_text(encoding="utf-8").strip()
    client = digikey.DigiKey(offline=not use_network, refresh=refresh)
    if use_network and client.offline:
        print("! secrets/digikey_api.json fehlt - DigiKey nur aus dem Cache", file=sys.stderr)

    for group in groups:
        group["schematic_mouser_part"] = group["mouser_part"]
        group["mismatch"] = False
        group["offers"] = {}
        if group["mouser_part"] or group["manufacturer_part"]:
            group["offers"]["Mouser"] = mouser_offer(api_key, cache, group)
            group["offers"]["DigiKey"] = digikey_offer(client, group)

        mouser = group["offers"].get("Mouser")
        if mouser:
            if group["schematic_mouser_part"] and normalise(mouser["part"]) != normalise(
                group["schematic_mouser_part"]
            ):
                # The schematic field is stale - report it rather than quietly
                # replacing it, so the mismatch reaches the schematic as a fix.
                group["mismatch"] = True
            group["mouser_part"] = mouser["part"]

        source, available = choose_source(group)
        chosen = group["offers"].get(source) or {}
        group["source"] = source
        group["available"] = available
        group["price"] = chosen.get("price")
        group["stock"] = chosen.get("stock", "")

        # Fill gaps from the offer actually ordered first: for a generic type
        # such as SS34 the two distributors may well list different makers.
        others = [o for n, o in group["offers"].items() if o and n != source]
        for offer in ([chosen] if chosen else []) + others:
            if not group["manufacturer"]:
                group["manufacturer"] = offer["manufacturer"]
            if not group["manufacturer_part"]:
                group["manufacturer_part"] = offer["manufacturer_part"]
            if not group["datasheet"]:
                group["datasheet"] = offer["datasheet"]

    save_cache(cache)
    client.save_cache()


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
    offers = group.get("offers") or {}
    source = group.get("source", "")
    if group.get("mismatch"):
        notes.append(
            f"Mouser-Nr. im Schaltplan ({group['schematic_mouser_part']}) stimmt nicht — "
            f"gültig ist {group['mouser_part']}. Schaltplanfeld korrigieren."
        )
    end_of_life = [
        f"{name}: {offer['lifecycle']}" for name, offer in offers.items() if offer and offer["end_of_life"]
    ]
    if end_of_life:
        notes.append(f"Abgekündigt ({'; '.join(end_of_life)}) — Ersatztyp wählen.")
    if source and not group.get("available"):
        notes.append(
            f"Bei keinem Distributor ab Lager lieferbar (Lager {source}: {group['stock']}) — "
            "Lieferzeit anfragen oder Ersatz wählen."
        )
    elif source:
        other = next(n for n in PREFERENCE if n != source)
        alternative = offers.get(other)
        if not alternative:
            notes.append(f"Bei {other} nicht geführt — nur über {source}.")
        elif alternative["price"] is None:
            notes.append(f"Bei {other} nur in Großverpackung gelistet — nur über {source}.")
        elif not deliverable(alternative, group["quantity"]):
            notes.append(f"Bei {other} nicht ausreichend ab Lager ({alternative['stock']}) — nur über {source}.")
    if group["proposal"]:
        lead = group["proposal"] + "."
        if group["replaced"]:
            lead = f"Ersatz für {group['replaced']} (abgekündigt). " + lead
        notes.insert(0, lead)
        if group["price"] is None:
            notes.append("Bei keinem Distributor bepreist — Alternative wählen.")
        notes.append("Nach Freigabe als Feld in den Schaltplan übernehmen.")
        return ("Vorschlag", " ".join(notes))
    if group["derived"]:
        notes.append("Teilenummer aus Wert/Bibliothek abgeleitet — am Datenblatt bestätigen.")
        return ("abgeleitet", " ".join(notes))
    if end_of_life:
        return ("Ersatz nötig", " ".join(notes))
    if group["price"] is not None:
        status = "eindeutig" if group.get("available") and not group.get("mismatch") else "prüfen"
        return (status, " ".join(notes))
    if group["mouser_part"] or group["manufacturer_part"]:
        if any(offers.values()):
            notes.append("Gelistet, aber ohne Preis für diese Menge — Preis und Lieferzeit anfragen.")
        else:
            notes.append(
                "Teilenummer bekannt, aber weder bei Mouser noch bei DigiKey ein Treffer — "
                "Alternative oder weiteren Distributor suchen."
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
