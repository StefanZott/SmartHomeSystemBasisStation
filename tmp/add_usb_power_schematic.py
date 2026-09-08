"""Add USB-C 5V -> MP2359 buck 3.3V power section to BasisStation_Layout.kicad_sch."""
from __future__ import annotations

import re
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCH = ROOT / "pcb/BasisStation/BasisStation_Layout.kicad_sch"
POWER_SYM = ROOT / "pcb/Bauteile/Power/power.kicad_sym"

PROJECT_PATH = (
    "/498c7092-55c1-4229-9f4b-13c6a8e7da47/1af2eb5e-14cd-443f-ae96-dbfda52b298f"
)


def uid() -> str:
    return str(uuid.uuid4())


def wire(x1: float, y1: float, x2: float, y2: float) -> str:
    return f"""\t(wire
\t\t(pts
\t\t\t(xy {x1} {y1}) (xy {x2} {y2})
\t\t)
\t\t(stroke
\t\t\t(width 0)
\t\t\t(type default)
\t\t)
\t\t(uuid "{uid()}")
\t)"""


def junction(x: float, y: float) -> str:
    return f"""\t(junction
\t\t(at {x} {y})
\t\t(diameter 0)
\t\t(color 0 0 0 0)
\t\t(uuid "{uid()}")
\t)"""


def label_net(name: str, x: float, y: float, rot: int = 0) -> str:
    justify = "left bottom"
    if rot == 90:
        justify = "right bottom"
    return f"""\t(label "{name}"
\t\t(at {x} {y} {rot})
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1.27 1.27)
\t\t\t)
\t\t\t(justify {justify})
\t\t)
\t\t(uuid "{uid()}")
\t)"""


def sym(
    lib_id: str,
    x: float,
    y: float,
    rot: int,
    ref: str,
    value: str,
    footprint: str,
    pin_uuids: dict[str, str],
    fields_autoplaced: bool = False,
) -> str:
    pin_lines = "\n".join(
        f'\t\t(pin "{num}"\n\t\t\t(uuid "{puuid}")\n\t\t)'
        for num, puuid in pin_uuids.items()
    )
    fa = "\n\t\t(fields_autoplaced yes)" if fields_autoplaced else ""
    return f"""\t(symbol
\t\t(lib_id "{lib_id}")
\t\t(at {x} {y} {rot})
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no){fa}
\t\t(uuid "{uid()}")
\t\t(property "Reference" "{ref}"
\t\t\t(at {x} {y - 5.08} {rot})
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Value" "{value}"
\t\t\t(at {x} {y + 2.54} {rot})
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Footprint" "{footprint}"
\t\t\t(at {x} {y} {rot})
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(hide yes)
\t\t\t)
\t\t)
\t\t(property "Datasheet" "~"
\t\t\t(at {x} {y} {rot})
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(hide yes)
\t\t\t)
\t\t)
\t\t(property "Description" ""
\t\t\t(at {x} {y} {rot})
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(hide yes)
\t\t\t)
\t\t)
{pin_lines}
\t\t(instances
\t\t\t(project "BasisStation"
\t\t\t\t(path "{PROJECT_PATH}"
\t\t\t\t\t(reference "{ref}")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)"""


def pwr_gnd(x: float, y: float, rot: int, ref: str) -> str:
    return f"""\t(symbol
\t\t(lib_id "power:GND")
\t\t(at {x} {y} {rot})
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(fields_autoplaced yes)
\t\t(uuid "{uid()}")
\t\t(property "Reference" "{ref}"
\t\t\t(at {x} {y + 2.54} {rot})
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(hide yes)
\t\t\t)
\t\t)
\t\t(property "Value" "GND"
\t\t\t(at {x} {y - 2.54} {rot})
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Footprint" ""
\t\t\t(at {x} {y} {rot})
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(hide yes)
\t\t\t)
\t\t)
\t\t(property "Datasheet" ""
\t\t\t(at {x} {y} {rot})
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(hide yes)
\t\t\t)
\t\t)
\t\t(property "Description" "Power symbol creates a global label with name \\"GND\\" , ground"
\t\t\t(at {x} {y} {rot})
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(hide yes)
\t\t\t)
\t\t)
\t\t(pin "1"
\t\t\t(uuid "{uid()}")
\t\t)
\t\t(instances
\t\t\t(project "BasisStation"
\t\t\t\t(path "{PROJECT_PATH}"
\t\t\t\t\t(reference "{ref}")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)"""


def pwr_3v3(x: float, y: float, ref: str) -> str:
    return f"""\t(symbol
\t\t(lib_id "power:+3V3")
\t\t(at {x} {y} 0)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(fields_autoplaced yes)
\t\t(uuid "{uid()}")
\t\t(property "Reference" "{ref}"
\t\t\t(at {x} {y + 3.81} 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(hide yes)
\t\t\t)
\t\t)
\t\t(property "Value" "+3V3"
\t\t\t(at {x} {y - 3.556} 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Footprint" ""
\t\t\t(at {x} {y} 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(hide yes)
\t\t\t)
\t\t)
\t\t(property "Datasheet" ""
\t\t\t(at {x} {y} 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(hide yes)
\t\t\t)
\t\t)
\t\t(property "Description" "Power symbol creates a global label with name \\"+3V3\\""
\t\t\t(at {x} {y} 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(hide yes)
\t\t\t)
\t\t)
\t\t(pin "1"
\t\t\t(uuid "{uid()}")
\t\t)
\t\t(instances
\t\t\t(project "BasisStation"
\t\t\t\t(path "{PROJECT_PATH}"
\t\t\t\t\t(reference "{ref}")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)"""


def pwr_flag(x: float, y: float, ref: str) -> str:
    return f"""\t(symbol
\t\t(lib_id "power:PWR_FLAG")
\t\t(at {x} {y} 0)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "{uid()}")
\t\t(property "Reference" "{ref}"
\t\t\t(at {x} {y - 1.905} 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(hide yes)
\t\t\t)
\t\t)
\t\t(property "Value" "PWR_FLAG"
\t\t\t(at {x} {y - 5.08} 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Footprint" ""
\t\t\t(at {x} {y} 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(hide yes)
\t\t\t)
\t\t)
\t\t(property "Datasheet" "~"
\t\t\t(at {x} {y} 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(hide yes)
\t\t\t)
\t\t)
\t\t(property "Description" "Special symbol for telling ERC where power comes from"
\t\t\t(at {x} {y} 0)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t\t(hide yes)
\t\t\t)
\t\t)
\t\t(pin "1"
\t\t\t(uuid "{uid()}")
\t\t)
\t\t(instances
\t\t\t(project "BasisStation"
\t\t\t\t(path "{PROJECT_PATH}"
\t\t\t\t\t(reference "{ref}")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)"""


def load_embedded_power_symbols() -> str:
    raw = POWER_SYM.read_text(encoding="utf-8")
    blocks = []
    for name in ("MP2359DJ", "USB_C_Receptacle_Power"):
        m = re.search(rf'\(symbol "{name}"(.*?)\n\t\)', raw, re.DOTALL)
        if not m:
            raise RuntimeError(f"Symbol {name} not found in power.kicad_sym")
        body = m.group(1)
        blocks.append(f'\t\t(symbol "power:{name}"{body}\n\t\t\t(embedded_fonts no)\n\t\t)')
    return "\n".join(blocks)


def embedded_plus_3v3() -> str:
    return """
\t\t(symbol "power:+3V3"
\t\t\t(power)
\t\t\t(pin_numbers
\t\t\t\t(hide yes)
\t\t\t)
\t\t\t(pin_names
\t\t\t\t(offset 0)
\t\t\t\t(hide yes)
\t\t\t)
\t\t\t(exclude_from_sim no)
\t\t\t(in_bom yes)
\t\t\t(on_board yes)
\t\t\t(property "Reference" "#PWR"
\t\t\t\t(at 0 -3.81 0)
\t\t\t\t(effects
\t\t\t\t\t(font
\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t)
\t\t\t\t\t(hide yes)
\t\t\t\t)
\t\t\t)
\t\t\t(property "Value" "+3V3"
\t\t\t\t(at 0 3.556 0)
\t\t\t\t(effects
\t\t\t\t\t(font
\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t\t(property "Footprint" ""
\t\t\t\t(at 0 0 0)
\t\t\t\t(effects
\t\t\t\t\t(font
\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t)
\t\t\t\t\t(hide yes)
\t\t\t\t)
\t\t\t)
\t\t\t(property "Datasheet" ""
\t\t\t\t(at 0 0 0)
\t\t\t\t(effects
\t\t\t\t\t(font
\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t)
\t\t\t\t\t(hide yes)
\t\t\t\t)
\t\t\t)
\t\t\t(property "Description" "Power symbol creates a global label with name \\"+3V3\\""
\t\t\t\t(at 0 0 0)
\t\t\t\t(effects
\t\t\t\t\t(font
\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t)
\t\t\t\t\t(hide yes)
\t\t\t\t)
\t\t\t)
\t\t\t(property "ki_keywords" "global power"
\t\t\t\t(at 0 0 0)
\t\t\t\t(effects
\t\t\t\t\t(font
\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t)
\t\t\t\t\t(hide yes)
\t\t\t\t)
\t\t\t)
\t\t\t(symbol "+3V3_0_1"
\t\t\t\t(polyline
\t\t\t\t\t(pts
\t\t\t\t\t\t(xy -0.762 1.27) (xy 0 2.54)
\t\t\t\t\t)
\t\t\t\t\t(stroke
\t\t\t\t\t\t(width 0)
\t\t\t\t\t\t(type default)
\t\t\t\t\t)
\t\t\t\t\t(fill
\t\t\t\t\t\t(type none)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(polyline
\t\t\t\t\t(pts
\t\t\t\t\t\t(xy 0 2.54) (xy 0.762 1.27)
\t\t\t\t\t)
\t\t\t\t\t(stroke
\t\t\t\t\t\t(width 0)
\t\t\t\t\t\t(type default)
\t\t\t\t\t)
\t\t\t\t\t(fill
\t\t\t\t\t\t(type none)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(polyline
\t\t\t\t\t(pts
\t\t\t\t\t\t(xy 0 0) (xy 0 2.54)
\t\t\t\t\t)
\t\t\t\t\t(stroke
\t\t\t\t\t\t(width 0)
\t\t\t\t\t\t(type default)
\t\t\t\t\t)
\t\t\t\t\t(fill
\t\t\t\t\t\t(type none)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t\t(symbol "+3V3_1_1"
\t\t\t\t(pin power_out line
\t\t\t\t\t(at 0 0 90)
\t\t\t\t\t(length 0)
\t\t\t\t\t(name "~"
\t\t\t\t\t\t(effects
\t\t\t\t\t\t\t(font
\t\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t\t)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t\t(number "1"
\t\t\t\t\t\t(effects
\t\t\t\t\t\t\t(font
\t\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t\t)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t\t(embedded_fonts no)
\t\t)"""


def build_power_section() -> str:
    # Coordinates (mm)
    y_5v = 46.99
    y_gnd = 33.02
    y_out = 40.64

    parts: list[str] = []

    parts.append(
        """\t(text_box "USB-C power input (SHBS-4):\\n5 V VBUS -> F1 polyfuse -> D12 TVS -> PS1 MP2359 buck -> +3V3\\nCC1/CC2: 5.1 kΩ Rd to GND (UFP sink)"
\t\t(exclude_from_sim no)
\t\t(at 15.24 15.24 0)
\t\t(size 88.9 12.7)
\t\t(margins 0.9525 0.9525 0.9525 0.9525)
\t\t(stroke
\t\t\t(width 0)
\t\t\t(type default)
\t\t)
\t\t(fill
\t\t\t(type none)
\t\t)
\t\t(uuid "%s")
\t)"""
        % uid()
    )

    # --- USB-C J_PWR at (20.32, 43.18) ---
    parts.append(
        sym(
            "power:USB_C_Receptacle_Power",
            20.32,
            43.18,
            0,
            "J_PWR",
            "12401548E4-2A",
            "Footprints:USB_C_Receptacle_Amphenol_12401548E4-2A",
            {
                "A4": uid(),
                "A9": uid(),
                "A5": uid(),
                "B5": uid(),
                "A1": uid(),
                "B1": uid(),
                "S1": uid(),
            },
        )
    )

    # VBUS merge and rail
    parts += [
        wire(10.16, 48.26, 10.16, 45.72),
        junction(10.16, 46.99),
        wire(10.16, 46.99, 27.94, 46.99),
    ]

    # F1 polyfuse horizontal at (33.02, 46.99)
    parts.append(
        sym(
            "Device:Fuse",
            33.02,
            46.99,
            0,
            "F1",
            "1.1A",
            "Fuse:Fuse_1206_3216Metric",
            {"1": uid(), "2": uid()},
        )
    )
    parts += [wire(27.94, 46.99, 30.48, 46.99), wire(35.56, 46.99, 40.64, 46.99)]

    # D12 TVS SMAJ5.0A — cathode on +5V, anode to GND
    parts.append(
        sym(
            "Device:D",
            43.18,
            46.99,
            0,
            "D12",
            "SMAJ5.0A",
            "Diode_SMD:D_SMA",
            {"1": uid(), "2": uid()},
        )
    )
    parts += [
        wire(40.64, 46.99, 41.91, 46.99),
        wire(44.45, 46.99, 50.8, 46.99),
        wire(43.18, 48.26, 43.18, y_gnd),
        pwr_gnd(43.18, y_gnd, 0, "#PWR043"),
        wire(43.18, y_gnd, 43.18, 35.56),
    ]

    # Input cap C13
    parts.append(
        sym(
            "Device:C",
            55.88,
            46.99,
            0,
            "C13",
            "10uF",
            "Capacitor_SMD:C_0805_2012Metric",
            {"1": uid(), "2": uid()},
        )
    )
    parts += [
        wire(50.8, 46.99, 53.34, 46.99),
        junction(50.8, 46.99),
        wire(53.34, 46.99, 58.42, 46.99),
        wire(55.88, 48.26, 55.88, y_gnd),
        wire(55.88, y_gnd, 43.18, y_gnd),
        label_net("+5V", 48.26, 49.53),
    ]

    # PS1 MP2359 at (78.74, 40.64)
    parts.append(
        sym(
            "power:MP2359DJ",
            78.74,
            40.64,
            0,
            "PS1",
            "MP2359DJ-LF-Z",
            "Footprints:MP2359DJ",
            {
                "1": uid(),
                "2": uid(),
                "3": uid(),
                "4": uid(),
                "5": uid(),
                "6": uid(),
            },
        )
    )
    # PS1 MP2359 at (78.74, 40.64) — pin coords: BST 68.58/43.18, FB 68.58/40.64, EN 68.58/38.1,
    # GND 88.9/38.1, SW 88.9/40.64, VIN 88.9/43.18
    parts += [
        wire(50.8, 46.99, 88.9, 46.99),
        wire(88.9, 46.99, 88.9, 43.18),
        wire(68.58, 38.1, 68.58, 43.18),
        wire(68.58, 43.18, 88.9, 43.18),
        wire(88.9, 38.1, 88.9, 33.02),
        wire(88.9, 33.02, 43.18, 33.02),
        pwr_gnd(88.9, 33.02, 0, "#PWR044"),
    ]

    # BST bootstrap cap C15 between BST and SW
    parts.append(
        sym(
            "Device:C",
            78.74,
            43.18,
            0,
            "C15",
            "100nF",
            "Capacitor_SMD:C_0805_2012Metric",
            {"1": uid(), "2": uid()},
        )
    )
    parts += [
        wire(68.58, 43.18, 76.2, 43.18),
        wire(81.28, 43.18, 88.9, 43.18),
        wire(78.74, 44.45, 78.74, 40.64),
        wire(78.74, 40.64, 88.9, 40.64),
    ]

    # Schottky D11 — cathode to SW, anode to GND
    parts.append(
        sym(
            "Device:D",
            93.98,
            40.64,
            90,
            "D11",
            "SS34",
            "Diode_SMD:D_SMA",
            {"1": uid(), "2": uid()},
        )
    )
    parts += [
        wire(88.9, 40.64, 92.71, 40.64),
        wire(93.98, 38.1, 93.98, 33.02),
        wire(93.98, 33.02, 88.9, 33.02),
    ]

    # Inductor L1
    parts.append(
        sym(
            "Device:L",
            101.6,
            40.64,
            0,
            "L1",
            "10uH",
            "Inductor_SMD:L_6.3x6.3",
            {"1": uid(), "2": uid()},
        )
    )
    parts += [
        wire(88.9, 40.64, 99.06, 40.64),
        wire(104.14, 40.64, 109.22, 40.64),
        junction(109.22, 40.64),
    ]

    # Output cap C14
    parts.append(
        sym(
            "Device:C",
            114.3,
            40.64,
            0,
            "C14",
            "22uF",
            "Capacitor_SMD:C_0805_2012Metric",
            {"1": uid(), "2": uid()},
        )
    )
    parts += [
        wire(109.22, 40.64, 111.76, 40.64),
        wire(116.84, 40.64, 119.38, 40.64),
        wire(114.3, 42.54, 114.3, y_gnd),
        wire(114.3, y_gnd, 91.44, y_gnd),
    ]

    # FB divider: R17 (FB→+3V3), R18 (FB→GND)
    parts.append(
        sym(
            "Device:R",
            68.58,
            35.56,
            90,
            "R17",
            "100k",
            "Resistor_SMD:R_0805_2012Metric",
            {"1": uid(), "2": uid()},
        )
    )
    parts.append(
        sym(
            "Device:R",
            63.5,
            33.02,
            0,
            "R18",
            "32k",
            "Resistor_SMD:R_0805_2012Metric",
            {"1": uid(), "2": uid()},
        )
    )
    parts += [
        wire(68.58, 40.64, 68.58, 38.1),
        wire(68.58, 38.1, 68.58, 35.56),
        wire(68.58, 33.02, 68.58, 35.56),
        wire(63.5, 33.02, 68.58, 33.02),
        wire(63.5, 33.02, 43.18, 33.02),
        wire(68.58, 35.56, 109.22, 35.56),
        wire(109.22, 35.56, 109.22, 40.64),
    ]

    # +3V3 output
    parts += [
        pwr_3v3(124.46, 40.64, "#PWR045"),
        pwr_flag(124.46, 35.56, "#FLG05"),
        wire(119.38, 40.64, 124.46, 40.64),
        wire(124.46, 35.56, 124.46, 40.64),
    ]

    # CC Rd resistors
    parts.append(
        sym(
            "Device:R",
            10.16,
            38.1,
            0,
            "R19",
            "5.1k",
            "Resistor_SMD:R_0805_2012Metric",
            {"1": uid(), "2": uid()},
        )
    )
    parts.append(
        sym(
            "Device:R",
            10.16,
            33.02,
            0,
            "R20",
            "5.1k",
            "Resistor_SMD:R_0805_2012Metric",
            {"1": uid(), "2": uid()},
        )
    )
    parts += [
        wire(10.16, 43.18, 10.16, 40.64),
        wire(10.16, 40.64, 10.16, 38.1),
        wire(10.16, 38.1, 10.16, 35.56),
        wire(10.16, 35.56, 10.16, 33.02),
        wire(10.16, 33.02, 10.16, 30.48),
        pwr_gnd(10.16, 30.48, 0, "#PWR046"),
        wire(10.16, 30.48, 43.18, 30.48),
        wire(43.18, 30.48, 43.18, 33.02),
    ]

    # USB GND + shield
    parts += [
        wire(30.48, 48.26, 30.48, 46.99),
        wire(30.48, 45.72, 30.48, 46.99),
        wire(30.48, 43.18, 30.48, 46.99),
        wire(30.48, 46.99, 43.18, 46.99),
        pwr_gnd(30.48, 50.8, 0, "#PWR047"),
        wire(30.48, 48.26, 30.48, 50.8),
    ]

    return "\n".join(parts)


def main() -> None:
    text = SCH.read_text(encoding="utf-8")

    if "J_PWR" in text:
        print("Power section already present — skipping.")
        return

    # Remove misplaced +3V3 label on GND bus (y=22.86)
    text = re.sub(
        r'\t\(label "\+3V3"\n\t\t\(at 243\.84 22\.86 0\).*?\n\t\)\n',
        "",
        text,
        flags=re.DOTALL,
    )

    embedded = (
        load_embedded_power_symbols()
        + embedded_plus_3v3()
    )
    text = text.replace(
        "\t\t(embedded_fonts no)\n\t\t)\n\t)\n\t(text \"RESET BUTTON\"",
        f"\t\t(embedded_fonts no)\n\t\t)\n{embedded}\n\t)\n\t(text \"RESET BUTTON\"",
        1,
    )

    power_section = build_power_section()
    if not text.rstrip().endswith(")"):
        raise RuntimeError("Unexpected schematic file ending")
    text = text.rstrip()[:-1] + power_section + "\n)\n"

    SCH.write_text(text, encoding="utf-8")
    print(f"Updated {SCH}")


if __name__ == "__main__":
    main()
