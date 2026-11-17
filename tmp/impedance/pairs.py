"""Differential impedance of the board's USB and Ethernet pairs (SHBS-55).

Stack-up: 2 layers, 1.6 mm FR4 (1.51 mm dielectric), 35 um copper, solid GND
plane on B.Cu, GND pour on F.Cu at 0.5 mm clearance. Run with numpy/scipy:
    python3 tmp/impedance/pairs.py
"""
from zsolve import line

PAIRS = (('USB', 0.45, 0.15), ('ETH', 0.30, 0.15))

if __name__ == '__main__':
    print('pair  w     s     er   Zdiff no pour  Zdiff pour 0.5 mm')
    for name, w, s in PAIRS:
        for er in (4.2, 4.5, 4.7):
            print('%-4s  %.2f  %.2f  %.1f  %6.1f         %6.1f' % (
                name, w, s, er, line(w, s, None, er=er)[0], line(w, s, 0.5, er=er)[0]))
