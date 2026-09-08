#!/usr/bin/env python3
"""Build Espressif-style ESP32-S3-WROOM-1U-N16R8 symbol for pcb/Bauteile/."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ESPRESSIF = ROOT / "pcb/Symbol/Espressif.kicad_sym"
OUT = ROOT / "pcb/Bauteile/ESP32-S3-WROOM-1U-N16R8/ESP32-S3-WROOM-1U-N16R8.kicad_sym"

MOUSER_PROPS = """
		(property "Height" "3.35"
			(at 29.21 -394.92 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left top)
				(hide yes)
			)
		)
		(property "Mouser Part Number" "356-ESP32S3WM1UN16R8"
			(at 29.21 -494.92 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left top)
				(hide yes)
			)
		)
		(property "Mouser Price/Stock" "https://www.mouser.co.uk/ProductDetail/Espressif-Systems/ESP32-S3-WROOM-1U-N16R8?qs=Li%252BoUPsLEns6V0Pr5KRJtw%3D%3D"
			(at 29.21 -594.92 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left top)
				(hide yes)
			)
		)
		(property "Manufacturer_Name" "Espressif Systems"
			(at 29.21 -694.92 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left top)
				(hide yes)
			)
		)
		(property "Manufacturer_Part_Number" "ESP32-S3-WROOM-1U-N16R8"
			(at 29.21 -794.92 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(justify left top)
				(hide yes)
			)
		)"""


def extract_symbol_block(content: str, name: str) -> str:
    token = f'(symbol "{name}"'
    start = content.find(token)
    if start == -1:
        raise SystemExit(f"{name} not found")

    rest = content[start:]
    depth = 0
    for i, ch in enumerate(rest):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return rest[: i + 1]
    raise SystemExit(f"Unterminated symbol block for {name}")


def transform_symbol(sym: str) -> str:
    sym = sym.replace('(symbol "ESP32-S3-WROOM-1"', '(symbol "ESP32-S3-WROOM-1U-N16R8"', 1)
    sym = sym.replace('"ESP32-S3-WROOM-1"', '"ESP32-S3-WROOM-1U-N16R8"')
    sym = sym.replace("PCM_Espressif:ESP32-S3-WROOM-1", "Footprints:ESP32-S3-WROOM-1U")
    sym = sym.replace(
        "Onboard PCB antenna",
        "16 MB flash, 8 MB octal PSRAM, IPEX antenna connector",
    )
    sym = sym.replace('(symbol "ESP32-S3-WROOM-1_0_0"', '(symbol "ESP32-S3-WROOM-1U-N16R8_0_0"')
    sym = sym.replace('(symbol "ESP32-S3-WROOM-1_0_1"', '(symbol "ESP32-S3-WROOM-1U-N16R8_0_1"')

    sym = sym.replace(
        "(pin passive line\n\t\t\t\t(at 0 -40.64 90)\n\t\t\t\t(length 2.54) hide\n\t\t\t\t(name \"GND\"",
        "(pin power_in line\n\t\t\t\t(at 0 -40.64 90)\n\t\t\t\t(length 2.54) hide\n\t\t\t\t(name \"GND\"",
        1,
    )

    sym = sym.replace(
        "(pin passive line\n\t\t\t\t(at 0 -40.64 90)\n\t\t\t\t(length 2.54) hide\n\t\t\t\t(name \"GND\"",
        "(pin power_in line\n\t\t\t\t(at 0 -40.64 90)\n\t\t\t\t(length 2.54) hide\n\t\t\t\t(name \"EPAD\"",
        1,
    )

    marker = '\t\t(symbol "ESP32-S3-WROOM-1U-N16R8_0_0"'
    pos = sym.find(marker)
    if pos == -1:
        raise SystemExit("Sub-symbol _0_0 marker not found")
    sym = sym[:pos] + MOUSER_PROPS + "\n" + sym[pos:]
    return sym


def main() -> None:
    raw = ESPRESSIF.read_text(encoding="utf-8")
    symbol = transform_symbol(extract_symbol_block(raw, "ESP32-S3-WROOM-1"))

    output = (
        "(kicad_symbol_lib\n"
        '\t(version 20241209)\n'
        '\t(generator "BasisStation")\n'
        '\t(generator_version "9.0")\n'
        f"\t{symbol.lstrip()}\n"
        ")\n"
    )
    OUT.write_text(output, encoding="utf-8", newline="\n")

    pins = re.findall(r'\(number "(\d+)"', symbol)
    unique = sorted(set(pins), key=int)
    print(f"Written: {OUT}")
    print(f"Pins: {len(pins)} unique: {len(unique)}")
    for pin_no in ("1", "40", "41"):
        m = re.search(rf'\(name "([^"]+)"[\s\S]*?\(number "{pin_no}"', symbol)
        print(f"  Pin {pin_no}: {m.group(1) if m else '?'}")


if __name__ == "__main__":
    main()
