#!/usr/bin/env bash
# Build one documentation PDF for the base station board (SHBS-30):
#   1. schematic (all sheets)
#   2. PCB layers (one page per layer, board outline on every page)
#   3. interactive 3D model (U3D annotation, rotatable in Acrobat Reader/Foxit)
#
# Requires KiCad 10 (pcb export 3dpdf), kicad-packages3d and qpdf - all part of
# the devcontainer. Usage: pcb/export_pdf.sh [output.pdf]
set -euo pipefail

KICAD_CLI="${KICAD_CLI:-kicad-cli}"
QPDF="${QPDF:-qpdf}"

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_dir="${script_dir}/BasisStation"
schematic="${project_dir}/BasisStation.kicad_sch"
board="${project_dir}/BasisStation.kicad_pcb"
output="${1:-${script_dir}/export/BasisStation.pdf}"

# Pages of the PCB section, in this order
pcb_layers="F.Cu,B.Cu,F.Silkscreen,B.Silkscreen,F.Fab,B.Fab"

kicad_major="$("${KICAD_CLI}" version | cut -d. -f1)"
if [[ "${kicad_major}" -lt 10 ]]; then
  echo "error: KiCad 10 required for the 3D PDF, found $("${KICAD_CLI}" version)" >&2
  exit 1
fi

work_dir="$(mktemp -d)"
trap 'rm -rf "${work_dir}"' EXIT

echo "==> Schematic"
"${KICAD_CLI}" sch export pdf -o "${work_dir}/schematic.pdf" "${schematic}"

echo "==> PCB layers"
"${KICAD_CLI}" pcb export pdf --mode-multipage --include-border-title \
  --layers "${pcb_layers}" --common-layers Edge.Cuts \
  -o "${work_dir}/pcb.pdf" "${board}"

echo "==> 3D model"
"${KICAD_CLI}" pcb export 3dpdf -f --no-dnp \
  -o "${work_dir}/3d.pdf" "${board}"

echo "==> Merging"
mkdir -p "$(dirname "${output}")"
# qpdf copies whole page objects including annotations, so the 3D annotation
# and its U3D stream survive the merge. KiCad 10.0.6 writes xref entries with
# offset 0 into the 3D PDF; qpdf repairs them and warns (exit code 3), which
# must not abort the script - the merged file is written with a clean xref.
"${QPDF}" --warning-exit-0 --empty --pages \
  "${work_dir}/schematic.pdf" "${work_dir}/pcb.pdf" "${work_dir}/3d.pdf" -- \
  "${output}"

echo "Written: ${output}"
