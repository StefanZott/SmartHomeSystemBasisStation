"""Restore schematic from last git commit and re-apply PS2/+12V removal only."""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCH = ROOT / "pcb/BasisStation/BasisStation_Layout.kicad_sch"

raw = subprocess.check_output(
    ["git", "show", "HEAD:pcb/BasisStation/BasisStation_Layout.kicad_sch"],
    cwd=ROOT,
    text=True,
    encoding="utf-8",
)

WIRE_UUIDS = [
    "11d60c9b-a857-4cec-a332-403c3eb59c0e",
    "6b7c0aff-4840-4952-98d4-9b2bf236d0d4",
    "2d9b4be0-8814-498f-a26a-6fdcc749e432",
    "b3f34c2b-7e95-40bc-9f93-d5fc4d7eafc9",
    "ba6710f7-6c17-4a59-9934-77c40d6db401",
    "fd1ccc11-e79e-493d-bafe-32eec5cd9d8d",
]
SYM_UUIDS = [
    "04746ab2-ab6e-4bc6-ac05-5a495d745587",  # #PWR022
    "c615e105-390c-491d-b3f5-2f5ad089bf06",  # #FLG04
    "ccebca91-5479-42f4-bccc-aa6dcb0d32b7",  # #PWR023
    "e05808ad-8dd3-4cb7-92d6-e6fbb2fadadc",  # PS2
    "619f9d23-7bf1-4da3-82d3-2dff064aae45",  # #PWR033
]

# Remove embedded lib symbols TSR and +12V from lib_symbols
raw = re.sub(
    r'\t\t\(symbol "TSR_1-2433E:TSR_1-2433E".*?\n\t\t\)\n',
    "",
    raw,
    flags=re.DOTALL,
)
raw = re.sub(
    r'\t\t\(symbol "power:\+12V".*?\n\t\t\)\n',
    "",
    raw,
    flags=re.DOTALL,
)

for uid in WIRE_UUIDS:
    raw = re.sub(
        rf'\t\(wire\n(?:\t\t[^\n]*\n)*?\t\t\(uuid "{re.escape(uid)}"\)\n\t\)\n',
        "",
        raw,
    )

for uid in SYM_UUIDS:
    raw = re.sub(
        rf'\t\(symbol\n(?:\t\t[^\n]*\n)*?\t\t\(uuid "{re.escape(uid)}"\)\n(?:\t\t[^\n]*\n)*?\t\)\n',
        "",
        raw,
    )

# Remove misplaced +3V3 label on GND bus if present
raw = re.sub(
    r'\t\(label "\+3V3"\n\t\t\(at 243\.84 22\.86 0\).*?\n\t\)\n',
    "",
    raw,
    flags=re.DOTALL,
)

SCH.write_text(raw, encoding="utf-8", newline="\n")
print(f"Restored {SCH} from HEAD + PS2/+12V removal")
