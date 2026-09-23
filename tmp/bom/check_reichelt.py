#!/usr/bin/env python3
"""Check whether Reichelt carries a given part.

Reichelt offers no public API, so this queries the ordinary shop search and
reads the hit count out of the page title ("Die Suche nach X hatte N Treffer").
That makes it a coverage check, not a price source: it answers "does Reichelt
have anything matching this", not "what does it cost".

Beware of false negatives. Reichelt's search does not understand manufacturer
part numbers for generic parts - "SMD-Widerstand 0805 10K" returns nothing
while "Widerstand SMD 0805" returns hundreds. Always confirm a zero with a
broader wording before concluding the part is unavailable.

Usage:
    python3 tmp/bom/check_reichelt.py "Widerstand SMD 0805" "BC337"
    python3 tmp/bom/check_reichelt.py --bom        # alle offenen BOM-Positionen
"""

from __future__ import annotations

import argparse
import re
import sys
import time
import urllib.parse
import urllib.request

SEARCH_URL = "https://www.reichelt.de/de/de/shop/suche/"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120 Safari/537.36"
)
TITLE = re.compile(r"<title>(.*?)</title>", re.S)
COUNT = re.compile(r"hatte\s+(\d+)\s+Treffer", re.I)
NAME = re.compile(r'<meta itemprop="name" content="([^"]+)"')
PRODUCT = re.compile(r"/shop/produkt/([a-z0-9_\-]+)")

# Positions that Mouser could not resolve, plus the generic passives.
DEFAULT_TERMS = [
    ("ANT2 Antenne", "Taoglas GW.20"),
    ("ANT2 Alternative", "WLAN Antenne RP-SMA 2,4"),
    ("ANT1 Pigtail", "U.FL RP-SMA Pigtail"),
    ("U6 Modul (1U noetig!)", "ESP32-S3-WROOM-1U"),
    ("U7 Ethernet-IC", "W5500"),
    ("PS1 Buck-Regler", "MP2359"),
    ("U1 ESD-Array", "D3V3XA4B10LP"),
    ("J1/J_PWR1 USB-C", "12401548E4"),
    ("J6 Stiftleiste", "61200621621"),
    ("C7/C10/C12 Wuerth", "890334023023"),
    ("C8 Wuerth", "870235673001"),
    ("D7 LED Wuerth", "151031YS05900"),
    ("T1 RJ45 Wuerth", "7499011121A"),
    ("Y1 Quarz Wuerth", "830059532"),
    ("Y1 Quarz generisch", "Quarz 25 MHz SMD"),
    ("D11 Schottky", "SS34"),
    ("D12 TVS", "SMAJ5.0A"),
    ("L1 Induktivitaet", "SMD Induktivitaet 10uH"),
    ("S2 Taster", "1543-650-149"),
    ("Q1-Q4 Transistor", "BC337"),
    ("Kondensator 0805", "X7R 0805 100n"),
    ("Widerstand 0805", "Widerstand SMD 0805"),
]


def search(term: str):
    """Return (hit count, first product names, first product slug)."""
    request = urllib.request.Request(
        SEARCH_URL + urllib.parse.quote(term), headers={"User-Agent": USER_AGENT}
    )
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            html = response.read().decode("utf-8", "replace")
    except Exception as error:  # network hiccup should not abort the whole run
        print(f"  ! {term}: {error}", file=sys.stderr)
        return None, [], ""

    title_match = TITLE.search(html)
    title = title_match.group(1).strip() if title_match else ""
    count_match = COUNT.search(title)
    count = int(count_match.group(1)) if count_match else 0
    names = [n.strip() for n in NAME.findall(html)[:3]]
    slugs = PRODUCT.findall(html)
    return count, names, slugs[0] if slugs else ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("terms", nargs="*", help="Suchbegriffe")
    parser.add_argument("--bom", action="store_true", help="Alle offenen BOM-Positionen prüfen")
    parser.add_argument("--delay", type=float, default=1.5, help="Pause zwischen Abfragen")
    args = parser.parse_args()

    if args.bom or not args.terms:
        entries = DEFAULT_TERMS
    else:
        entries = [(term, term) for term in args.terms]

    print(f"{'':3}{'Position':24}{'Suchbegriff':28}{'Treffer':>8}  Beispiel")
    print("-" * 104)
    for label, term in entries:
        count, names, _ = search(term)
        marker = "OK " if (count or 0) > 0 else "-- "
        example = names[0][:40] if names else ""
        print(f"{marker}{label:24}{term:28}{str(count):>8}  {example}")
        time.sleep(args.delay)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
