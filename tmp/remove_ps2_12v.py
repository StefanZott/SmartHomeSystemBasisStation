"""Remove PS2 and +12V from KiCad schematic and PCB."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sch = ROOT / "pcb/BasisStation/BasisStation_Layout.kicad_sch"
pcb = ROOT / "pcb/BasisStation/BasisStation.kicad_pcb"

WIRE_UUIDS = [
    "11d60c9b-a857-4cec-a332-403c3eb59c0e",
    "6b7c0aff-4840-4952-98d4-9b2bf236d0d4",
    "2d9b4be0-8814-498f-a26a-6fdcc749e432",
    "b3f34c2b-7e95-40bc-9f93-d5fc4d7eafc9",
    "ba6710f7-6c17-4a59-9934-77c40d6db401",
    "fd1ccc11-e79e-493d-bafe-32eec5cd9d8d",
]

SYM_UUIDS = [
    "ccebca91-5479-42f4-bccc-aa6dcb0d32b7",  # #PWR023
    "e05808ad-8dd3-4cb7-92d6-e6fbb2fadadc",  # PS2
]

WIRE_RE = re.compile(
    r"\t\(wire\n(?:\t\t[^\n]*\n)*?\t\t\(uuid \"({})\"\)\n\t\)\n".format(
        "|".join(re.escape(u) for u in WIRE_UUIDS)
    )
)

SYM_RE = re.compile(
    r"\t\(symbol\n(?:\t\t[^\n]*\n)*?\t\t\(uuid \"({})\"\)\n(?:\t\t[^\n]*\n)*?\t\)\n".format(
        "|".join(re.escape(u) for u in SYM_UUIDS)
    )
)

text = sch.read_text(encoding="utf-8")
before = text
text = WIRE_RE.sub("", text)
text = SYM_RE.sub("", text)
sch.write_text(text, encoding="utf-8")
print(f"Schematic: removed {before.count(chr(10)) - text.count(chr(10))} lines")

ptext = pcb.read_text(encoding="utf-8")
pb = ptext
ptext = re.sub(
    r"\t\(footprint \"Footprints:CONV_TSR_1-2433E\"\n(?:\t\t[^\n]*\n)*?\t\)\n",
    "",
    ptext,
)
ptext = re.sub(r"\t\(net 3 \"\+12V\"\)\n", "", ptext)
pcb.write_text(ptext, encoding="utf-8")
print(f"PCB: removed {pb.count(chr(10)) - ptext.count(chr(10))} lines")
