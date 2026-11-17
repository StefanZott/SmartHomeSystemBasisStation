# Usage: see pairs.py (SHBS-55). Validated against Hammerstad-Jensen: 49.5 vs 50.3 Ohm
# for a 2.95 mm microstrip on 1.6 mm FR4 (er 4.6).
# 2D quasi-static field solver (finite volume on a non-uniform rectilinear grid)
# for the cross-section of microstrip / coplanar lines over a ground plane.
# Z = eta0 / sqrt(C * C_air) with capacitances normalised to eps0.
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

ETA0 = 376.730313


def axis(fixed, lo, hi, fine, fine_lo, fine_hi, coarse=0.25, growth=1.2):
    """Grid lines: uniform 'fine' inside [fine_lo, fine_hi], growing outside."""
    pts = list(np.arange(fine_lo, fine_hi + fine / 2, fine))
    x, d = fine_hi, fine
    while x < hi:
        d = min(d * growth, coarse); x = min(x + d, hi); pts.append(x)
    x, d = fine_lo, fine
    while x > lo:
        d = min(d * growth, coarse); x = max(x - d, lo); pts.insert(0, x)
    pts = np.unique(np.round(np.array(pts + list(fixed)), 6))
    return pts


def solve(rects_by_volt, eps_layers, xs, ys):
    """rects_by_volt: list of (x0, x1, y0, y1, volt, tag); eps_layers: list of
    (y0, y1, eps). Bottom boundary y=ys[0] is ground. Other boundaries ground."""
    nx, ny = len(xs), len(ys)
    dx, dy = np.diff(xs), np.diff(ys)
    # cell permittivity (cells between grid lines)
    ycen = (ys[:-1] + ys[1:]) / 2
    eps_cell_row = np.ones(ny - 1)
    for y0, y1, e in eps_layers:
        eps_cell_row[(ycen > y0) & (ycen < y1)] = e
    eps_cell = np.tile(eps_cell_row, (nx - 1, 1))          # [ix, iy]
    fixed = np.full((nx, ny), np.nan); tag = np.full((nx, ny), -1)
    fixed[:, 0] = 0; fixed[:, -1] = 0; fixed[0, :] = 0; fixed[-1, :] = 0
    for k, (x0, x1, y0, y1, v, t) in enumerate(rects_by_volt):
        mx = (xs >= x0 - 1e-9) & (xs <= x1 + 1e-9); my = (ys >= y0 - 1e-9) & (ys <= y1 + 1e-9)
        fixed[np.ix_(mx, my)] = v; tag[np.ix_(mx, my)] = t
        # conductors are not dielectric: set cell eps inside conductor to 1 (irrelevant)
    idx = -np.ones((nx, ny), dtype=np.int64)
    free = np.isnan(fixed)
    idx[free] = np.arange(free.sum())
    N = free.sum()
    rows, cols, vals = [], [], []
    rhs = np.zeros(N)

    def coupling(i, j, i2, j2):
        # conductance between node (i,j) and neighbour (i2,j2)
        if i2 != i:  # x-neighbour
            c = min(i, i2); d = dx[c]
            a_lo = dy[j - 1] / 2 if j > 0 else 0; a_hi = dy[j] / 2 if j < ny - 1 else 0
            e_lo = eps_cell[c, j - 1] if j > 0 else 0; e_hi = eps_cell[c, j] if j < ny - 1 else 0
            return (e_lo * a_lo + e_hi * a_hi) / d
        else:
            c = min(j, j2); d = dy[c]
            a_lo = dx[i - 1] / 2 if i > 0 else 0; a_hi = dx[i] / 2 if i < nx - 1 else 0
            e_lo = eps_cell[i - 1, c] if i > 0 else 0; e_hi = eps_cell[i, c] if i < nx - 1 else 0
            return (e_lo * a_lo + e_hi * a_hi) / d

    fi, fj = np.nonzero(free)
    for i, j in zip(fi, fj):
        p = idx[i, j]; diag = 0.0
        for i2, j2 in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)):
            g = coupling(i, j, i2, j2); diag += g
            if free[i2, j2]:
                rows.append(p); cols.append(idx[i2, j2]); vals.append(-g)
            else:
                rhs[p] += g * fixed[i2, j2]
        rows.append(p); cols.append(p); vals.append(diag)
    A = sp.csr_matrix((vals, (rows, cols)), shape=(N, N))
    phi_free = spla.spsolve(A, rhs)
    phi = fixed.copy(); phi[free] = phi_free
    # charge per tagged conductor: sum of fluxes from conductor nodes to free nodes
    q = {}
    ti, tj = np.nonzero(tag >= 0)
    for i, j in zip(ti, tj):
        for i2, j2 in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)):
            if 0 <= i2 < nx and 0 <= j2 < ny and tag[i2, j2] != tag[i, j]:
                g = coupling(i, j, i2, j2)
                q[tag[i, j]] = q.get(tag[i, j], 0.0) + g * (phi[i, j] - phi[i2, j2])
    return q


def line(w, s=None, g=None, h=1.51, t=0.0375, er=4.5, mode='odd', fine=0.0125, span=40.0, top=20.0):
    """Single (s=None) or edge-coupled pair; g = gap to coplanar ground (None = none).
    Returns impedance: single Z0, or Zdiff (odd) / Zcm (even)."""
    if s is None:
        sig = [(-w / 2, w / 2)]
    else:
        sig = [(-s / 2 - w, -s / 2), (s / 2, s / 2 + w)]
    xr = max(abs(sig[0][0]), abs(sig[-1][1]))
    edges = [e for a in sig for e in a]
    gnd = []
    if g is not None:
        gnd = [(-span / 2, -xr - g), (xr + g, span / 2)]
        edges += [-xr - g, xr + g]
    fixed_x = edges
    fx = xr + (g if g is not None else 0) + 1.0
    xs = axis(fixed_x, -span / 2, span / 2, fine, -fx, fx, coarse=1.0)
    ys = axis([0, h, h + t], 0, h + top, fine, h - 0.4, h + t + 0.4, coarse=1.0)

    def run(eps):
        rects = []
        if s is None:
            rects.append((sig[0][0], sig[0][1], h, h + t, 1.0, 0))
        else:
            v2 = -1.0 if mode == 'odd' else 1.0
            rects.append((sig[0][0], sig[0][1], h, h + t, 1.0, 0))
            rects.append((sig[1][0], sig[1][1], h, h + t, v2, 1))
        for k, (a, b) in enumerate(gnd):
            rects.append((a, b, h, h + t, 0.0, 10 + k))
        return solve(rects, [(0, h, eps)], xs, ys)[0]

    c, c0 = run(er), run(1.0)
    z = ETA0 / np.sqrt(c * c0)
    eeff = c / c0
    if s is None:
        return z, eeff
    return (2 * z if mode == 'odd' else z / 2), eeff


if __name__ == '__main__':
    import sys
    # validation: Hammerstad-Jensen gives ~50.3 Ohm, eeff ~3.46 for w=2.95 mm, h=1.6 mm, er=4.6
    for span, top in ((40, 20), (80, 40)):
        print('span %d top %d: microstrip w=2.95 h=1.6 er=4.6: Z0=%.1f eeff=%.2f' % ((span, top) + line(2.95, h=1.6, er=4.6, t=0.035, fine=0.025, span=span, top=top)))
    # narrow line, Hammerstad: w=0.2, h=1.51, er=4.5 -> ~137 Ohm (IPC-2141 approx.)
    print('microstrip w=0.2 h=1.51: Z0=%.1f eeff=%.2f' % line(0.2))
