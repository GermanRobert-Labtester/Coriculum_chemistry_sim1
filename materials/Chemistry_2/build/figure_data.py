"""F06: one owner for the numeric rows behind every data plot.

The SVG figures and these tables both read `build/verified.json`.  Each table
row carries `data-point`, and the matching SVG marker carries the same value,
so `build/check_figure_data.py` can prove that every plotted point has a row
and that no row is unplotted.

Only the <tbody> rows are generated; captions, headers, notes and the
<details class="figure-data"> wrapper stay editable in the section sources.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
V = json.loads((ROOT / "verified.json").read_text(encoding="utf-8"))


def lv(value: float, dec: int = 1) -> str:
    return f"{value:.{dec}f}".replace(".", ",")


def signed(value: float, dec: int = 4) -> str:
    if abs(value) < 0.5 * 10 ** (-dec):
        return lv(0.0, dec)
    sign = "+" if value > 0 else "−"
    return sign + lv(abs(value), dec)


def row(key: str, cells: list[tuple[str, str, str]]) -> str:
    """cells: (header label, text, class) — first cell is the row header."""
    head_label, head_text, head_class = cells[0]
    out = [f'      <tr data-point="{html.escape(key, quote=True)}">']
    cls = f' class="{head_class}"' if head_class else ""
    out.append(f'        <th scope="row"{cls}>{head_text}</th>')
    for label, text, cell_class in cells[1:]:
        cls = f' class="{cell_class}"' if cell_class else ""
        out.append(
            f'        <td data-label="{html.escape(label, quote=True)}"{cls}>{text}</td>'
        )
    out.append("      </tr>")
    return "\n".join(out)


def calibration_rows() -> str:
    cal = V["calibration"]
    rows = []
    for s in cal["standards"]:
        rows.append(
            row(
                f'cal-std-{s["id"]}',
                [
                    ("Punkts", f'Standarts {s["id"]}', ""),
                    ("Tips", "standarts", ""),
                    ("ρ, mg/L", lv(s["rho"], 2), "num"),
                    ("A", lv(s["A"], 3), "num"),
                    ("Nolasījums, mg/L", "—", "num"),
                ],
            )
        )
    for s in cal["samples"]:
        kind = "paraugs, ekstrapolācija" if s["reading_kind"] == "ekstrapolācija" else "paraugs"
        rows.append(
            row(
                f'cal-smp-{s["name"]}',
                [
                    ("Punkts", html.escape(s["name"]), ""),
                    ("Tips", kind, ""),
                    ("ρ, mg/L", lv(s["c"], 2), "num"),
                    ("A", lv(s["A"], 3), "num"),
                    ("Nolasījums, mg/L", lv(s["c1"], 1), "num"),
                ],
            )
        )
    return "\n".join(rows)


def residual_rows() -> str:
    rows = []
    for s in V["calibration"]["standards"]:
        rows.append(
            row(
                f'res-std-{s["id"]}',
                [
                    ("Standarts", s["id"], ""),
                    ("ρ, mg/L", lv(s["rho"], 2), "num"),
                    ("Izmērītais A", lv(s["A"], 3), "num"),
                    ("Taisnes A", s["A_fit_lv"], "num"),
                    ("Atlikums ΔA", s["residual_A_lv"], "num"),
                    ("Atlikums, mg/L", s["residual_mgL_lv"], "num"),
                ],
            )
        )
    return "\n".join(rows)


def hg_rows() -> str:
    h = V["half_life"]
    th = float(h["hg_d"])
    t0 = float(h.get("hg_t0", 0.0))
    rows = []
    for k in range(4):
        t = t0 + k * th
        t_text = f"{t:.6f}".rstrip("0").rstrip(".").replace(".", ",")
        pct_text = f"{100 / (2**k):.3f}".rstrip("0").rstrip(".").replace(".", ",")
        rows.append(
            row(
                f"hg-model-{k}",
                [
                    ("Punkts", str(k), ""),
                    ("Veids", "modelis", ""),
                    ("Laiks, dienas", t_text, "num"),
                    ("Daļa, %", pct_text, "num"),
                ],
            )
        )
    for i, t in enumerate([50, 100, 145], start=1):
        pct = 100 * 2 ** (-(t - t0) / th)
        rows.append(
            row(
                f"hg-source-{t}",
                [
                    ("Punkts", f"Avots {i}", ""),
                    ("Veids", "avota nolasījums", ""),
                    ("Laiks, dienas", str(t), "num"),
                    ("Daļa, %", lv(pct, 1), "num"),
                ],
            )
        )
    return "\n".join(rows)


def hydrolysis_rows() -> str:
    h = V["half_life"]
    halvings = h["hyd_halvings"]
    concentrations = ["0,050", "0,025", "0,0125"]
    deltas = ["—", str(halvings[1] - halvings[0]), str(halvings[2] - halvings[1])]
    rows = []
    for i, (t, c, dt) in enumerate(zip(halvings, concentrations, deltas), start=1):
        rows.append(
            row(
                f"hyd-level-{i}",
                [
                    ("Līmenis", str(i), ""),
                    ("c(X), mol/L", c, "num"),
                    ("Laiks, s", str(t), "num"),
                    ("Starpība, s", dt, "num"),
                ],
            )
        )
    return "\n".join(rows)


def offset_rows() -> str:
    """F09: one dataset read twice — absolute time and elapsed time."""
    demo = V["half_life"]["offset_demo"]
    t0 = float(demo["t0_min"])
    times = [float(t) for t in demo["times_min"]]
    levels = [float(c) for c in demo["levels"]]
    deltas = [float(d) for d in demo["deltas_min"]]
    elapsed = [float(e) for e in demo["elapsed_min"]]
    rows = []
    for i, (t, c) in enumerate(zip(times, levels), start=1):
        rows.append(
            row(
                f"off-abs-{i}",
                [
                    ("Punkts", f"Līmenis {i}", ""),
                    ("Asis", "absolūtais t", ""),
                    ("c(X), mol/L", lv(c, 3), "num"),
                    ("Laiks, min", lv(t, 0), "num"),
                    ("Starpība, min", "—" if i == 1 else lv(deltas[i - 2], 0), "num"),
                ],
            )
        )
    for i, (e, c) in enumerate(zip(elapsed, levels), start=1):
        rows.append(
            row(
                f"off-elap-{i}",
                [
                    ("Punkts", f"Līmenis {i}", ""),
                    ("Asis", "pagājušais Δt", ""),
                    ("c(X), mol/L", lv(c, 3), "num"),
                    ("Laiks, min", lv(e, 0), "num"),
                    ("Starpība, min", "—" if i == 1 else lv(deltas[i - 2], 0), "num"),
                ],
            )
        )
    if abs(elapsed[0] - 0.0) > 1e-9 or abs(t0 - 40.0) > 1e-9:
        raise SystemExit("offset demo: elapsed series must start at 0 after subtracting t0")
    return "\n".join(rows)


def density_rows() -> str:
    d = V["density"]
    m = re.search(r"([0-9.]+)·w\s*\+\s*([0-9.]+)", d["line_equation"])
    if not m:
        raise SystemExit("density line equation not parseable")
    slope, intercept = float(m.group(1)), float(m.group(2))
    points = [
        ("den-line-0", "Krustpunkts (w = 0)", 0.0, intercept),
        ("den-table-4", "Tabulas vērtība (kvadrāts)", 4.0, d["table_4_293"]),
        ("den-measurement", "Mērījums (starpvērtība)", d["w_line"], d["rho"]),
        ("den-line-10", "Taisnes gals", 10.0, slope * 10 + intercept),
    ]
    rows = []
    for key, label, w, rho in points:
        rows.append(
            row(
                key,
                [
                    ("Punkts", label, ""),
                    ("w, %", lv(w, 2 if key == "den-measurement" else 0), "num"),
                    ("ρ, g/mL", lv(rho, 4), "num"),
                ],
            )
        )
    return "\n".join(rows)


def inject(article: str) -> str:
    specs = {
        "CALIBRATION": calibration_rows(),
        "RESIDUAL": residual_rows(),
        "HG": hg_rows(),
        "HYDROLYSIS": hydrolysis_rows(),
        "OFFSET": offset_rows(),
        "DENSITY": density_rows(),
    }
    for name, rows in specs.items():
        pattern = re.compile(
            rf"(<!-- FIGDATA_{name}_ROWS_START -->).*?(<!-- FIGDATA_{name}_ROWS_END -->)",
            re.S,
        )
        matches = pattern.findall(article)
        if len(matches) != 1:
            raise SystemExit(f"figure-data marker {name}: expected 1, found {len(matches)}")
        article = pattern.sub(lambda m: f"{m.group(1)}\n{rows}\n      {m.group(2)}", article)
    return article
