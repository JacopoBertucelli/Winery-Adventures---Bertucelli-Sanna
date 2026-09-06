"""Dashboard HTML statica costruita dal CSV della pipeline."""

import argparse
import html
import math
import statistics
from pathlib import Path

import polars as pl

REQUIRED_COLUMNS = {"tank_id", "time", "pH", "temp", "stress_score"}
COLORS = [
    "#0f766e",
    "#2563eb",
    "#dc2626",
    "#9333ea",
    "#c2410c",
    "#0891b2",
    "#4d7c0f",
    "#be185d",
    "#475569",
]


def _anomalies(
    mean_ph: float, mean_temp: float, stress: float, stress_limit: float
) -> str:
    """Restituisce le anomalie semplici e dichiarate nella dashboard."""
    messages = []
    if not 3.0 <= mean_ph <= 4.0:
        messages.append("pH fuori intervallo 3.0–4.0")
    if not 22.0 <= mean_temp <= 28.0:
        messages.append("temperatura fuori intervallo 22–28 °C")
    if stress > stress_limit:
        messages.append("stress sopra media + deviazione standard")
    return "; ".join(messages) if messages else "nessuna"


def _temperature_chart(df: pl.DataFrame) -> str:
    """Crea piccoli grafici separati, con la stessa scala per ogni cisterna."""
    readings = (
        df.filter(pl.col("temp").is_not_null()).sort("time").with_row_index("_index")
    )
    if readings.is_empty():
        return ""

    temperatures = readings["temp"].to_list()
    low = math.floor(min(22.0, min(temperatures)))
    high = math.ceil(max(28.0, max(temperatures)))
    width, height = 320, 190
    left, right, top, bottom = 42, 14, 20, 42
    chart_width, chart_height = width - left - right, height - top - bottom
    first_time = str(readings["time"][0]).replace("T", " ")[5:16]
    last_time = str(readings["time"][-1]).replace("T", " ")[5:16]

    def x_position(index: int) -> float:
        return left + index * chart_width / max(readings.height - 1, 1)

    def y_position(temperature: float) -> float:
        return top + (high - temperature) * chart_height / max(high - low, 1)

    cards = []
    for index, tank in enumerate(readings.partition_by("tank_id", maintain_order=True)):
        color = COLORS[index % len(COLORS)]
        grid, labels, points, markers = [], [], [], []
        for tick in range(low, high + 1):
            y = y_position(tick)
            grid.append(
                f'<line class="grid" x1="{left}" y1="{y:.1f}" '
                f'x2="{width - right}" y2="{y:.1f}"/>'
            )
            labels.append(
                f'<text class="axis-label" x="{left - 6}" y="{y + 3:.1f}" '
                f'text-anchor="end">{tick}</text>'
            )
        for row in tank.iter_rows(named=True):
            x, y = x_position(row["_index"]), y_position(row["temp"])
            points.append(f"{x:.1f},{y:.1f}")
            markers.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.8" fill="{color}"/>'
            )
        tank_id = html.escape(str(tank["tank_id"][0]))
        cards.append(
            '<article class="chart-card">'
            f'<h3><i style="background:{color}"></i>Cisterna {tank_id}</h3>'
            f'<svg viewBox="0 0 {width} {height}" role="img" '
            f'aria-label="Trend temperatura cisterna {tank_id}">'
            f'<line class="axis" x1="{left}" y1="{top}" x2="{left}" '
            f'y2="{height - bottom}"/>'
            f'<line class="axis" x1="{left}" y1="{height - bottom}" '
            f'x2="{width - right}" y2="{height - bottom}"/>'
            f"{''.join(grid)}{''.join(labels)}"
            f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" '
            f'stroke-width="2.6" stroke-linecap="round" '
            f'stroke-linejoin="round"/>{"".join(markers)}'
            f'<text class="axis-label" x="{left}" y="{height - 12}">{html.escape(first_time)}</text>'
            f'<text class="axis-label" x="{width - right}" y="{height - 12}" '
            f'text-anchor="end">{html.escape(last_time)}</text></svg></article>'
        )

    return (
        '<section class="chart"><h2>Trend temperatura per cisterna</h2>'
        "<p>Grafici separati: stessa scala verticale e stesso intervallo temporale, "
        'senza sovrapporre le linee.</p><div class="chart-grid">'
        f"{''.join(cards)}</div></section>"
    )


def _interactive_comparison(df: pl.DataFrame) -> str:
    """Crea un confronto in cui le singole cisterne possono essere nascoste."""
    readings = (
        df.filter(pl.col("temp").is_not_null()).sort("time").with_row_index("_index")
    )
    if readings.is_empty():
        return ""

    temperatures = readings["temp"].to_list()
    low = math.floor(min(22.0, min(temperatures)))
    high = math.ceil(max(28.0, max(temperatures)))
    width, height = 960, 390
    left, right, top, bottom = 56, 24, 20, 60
    chart_width, chart_height = width - left - right, height - top - bottom

    def x_position(index: int) -> float:
        return left + index * chart_width / max(readings.height - 1, 1)

    def y_position(temperature: float) -> float:
        return top + (high - temperature) * chart_height / max(high - low, 1)

    grid, labels = [], []
    for tick in range(low, high + 1):
        y = y_position(tick)
        grid.append(
            f'<line class="grid" x1="{left}" y1="{y:.1f}" '
            f'x2="{width - right}" y2="{y:.1f}"/>'
        )
        labels.append(
            f'<text class="axis-label" x="{left - 8}" y="{y + 4:.1f}" '
            f'text-anchor="end">{tick} °C</text>'
        )

    x_ticks = sorted({0, (readings.height - 1) // 2, readings.height - 1})
    for tick in x_ticks:
        value = str(readings["time"][tick]).replace("T", " ")[:16]
        x = x_position(tick)
        labels.append(
            f'<text class="axis-label" x="{x:.1f}" y="{height - bottom + 24}" '
            f'text-anchor="middle">{html.escape(value)}</text>'
        )

    series, controls = [], []
    for index, tank in enumerate(readings.partition_by("tank_id", maintain_order=True)):
        color = COLORS[index % len(COLORS)]
        tank_id = html.escape(str(tank["tank_id"][0]))
        points = " ".join(
            f"{x_position(row['_index']):.1f},{y_position(row['temp']):.1f}"
            for row in tank.iter_rows(named=True)
        )
        series.append(
            f'<g class="series" data-tank="{tank_id}"><polyline points="{points}" '
            f'fill="none" stroke="{color}" stroke-width="2.8" '
            'stroke-linecap="round" stroke-linejoin="round"/></g>'
        )
        controls.append(
            '<label class="tank-toggle">'
            f'<input type="checkbox" data-tank-toggle="{tank_id}" checked>'
            f'<i style="background:{color}"></i>Cisterna {tank_id}</label>'
        )

    return (
        '<section class="chart interactive"><h2>Confronto selezionabile</h2>'
        "<p>Disattiva le cisterne che non vuoi confrontare; il grafico si aggiorna "
        'subito nel browser.</p><div class="chart-controls">'
        '<button type="button" data-select="all">Tutte</button>'
        '<button type="button" data-select="none">Nessuna</button>'
        f"{''.join(controls)}</div>"
        f'<svg viewBox="0 0 {width} {height}" role="img" '
        'aria-label="Confronto interattivo delle temperature">'
        f'<line class="axis" x1="{left}" y1="{top}" x2="{left}" '
        f'y2="{height - bottom}"/>'
        f'<line class="axis" x1="{left}" y1="{height - bottom}" '
        f'x2="{width - right}" y2="{height - bottom}"/>'
        f"{''.join(grid)}{''.join(labels)}{''.join(series)}</svg></section>"
    )


def create_dashboard(csv_path: str | Path, output_path: str | Path) -> Path:
    """Legge il CSV della pipeline e salva un report HTML autosufficiente."""
    df = pl.read_csv(csv_path)
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"CSV della pipeline incompleto: {', '.join(sorted(missing))}")
    unique_readings = df.unique(subset=["tank_id", "time"], maintain_order=True)
    summary = unique_readings.group_by("tank_id", maintain_order=True).agg(
        pl.col("pH").mean().alias("pH medio"),
        pl.col("temp").mean().alias("temperatura media"),
        pl.col("stress_score").first().alias("stress"),
    )
    stresses = summary["stress"].to_list()
    stress_limit = statistics.mean(stresses)
    if len(stresses) > 1:
        stress_limit += statistics.stdev(stresses)
    rows = []
    for row in summary.iter_rows(named=True):
        anomaly = _anomalies(
            row["pH medio"], row["temperatura media"], row["stress"], stress_limit
        )
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(row['tank_id']))}</td>"
            f"<td>{row['pH medio']:.2f}</td><td>{row['temperatura media']:.2f} °C</td>"
            f"<td>{row['stress']:.3f}</td><td>{html.escape(anomaly)}</td></tr>"
        )
    page = f"""<!doctype html>
<html lang="it"><head><meta charset="utf-8"><title>Winery Adventures</title>
<style>body{{font-family:system-ui;max-width:960px;margin:2rem auto;padding:0 1rem;color:#222}}table{{border-collapse:collapse;width:100%}}th,td{{border-bottom:1px solid #ddd;padding:.55rem;text-align:left}}th{{background:#f5e9dc}}.chart{{margin-top:2rem}}.chart p{{color:#555}}.chart-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem}}.chart-card{{padding:.75rem;border:1px solid #eadfd4;border-radius:6px;background:#fffdf9}}.chart-card h3{{display:flex;align-items:center;gap:.45rem;margin:0 0 .5rem;font-size:1rem}}.chart-card h3 i,.tank-toggle i{{width:22px;height:4px;border-radius:2px}}svg{{width:100%;display:block}}.interactive svg{{background:#fffdf9;border:1px solid #eadfd4;border-radius:6px}}.chart-controls{{display:flex;flex-wrap:wrap;gap:.5rem 1rem;align-items:center;margin:.75rem 0}}button{{padding:.3rem .6rem;border:1px solid #9a7360;border-radius:4px;background:#fff;cursor:pointer}}.tank-toggle{{display:flex;align-items:center;gap:.35rem;cursor:pointer;font-size:.9rem}}.grid{{stroke:#ddd;stroke-dasharray:4 4}}.axis{{stroke:#555;stroke-width:1.2}}.axis-label{{font-size:9px;fill:#444}}.series[hidden]{{display:none}}</style>
</head><body><h1>Stato fermentazione</h1><p>Dal CSV prodotto dalla pipeline. Anomalie: pH 3.0–4.0, temperatura 22–28 °C, stress sopra media + deviazione standard.</p>
<table><thead><tr><th>Cisterna</th><th>pH medio</th><th>Temperatura</th><th>Stress</th><th>Anomalie</th></tr></thead><tbody>{"".join(rows)}</tbody></table>{_interactive_comparison(unique_readings)}{_temperature_chart(unique_readings)}
<script>document.querySelectorAll("[data-tank-toggle]").forEach(toggle => toggle.addEventListener("change", () => {{const series = document.querySelector(`[data-tank="${{toggle.dataset.tankToggle}}"]`);if (series) series.style.display = toggle.checked ? "" : "none";}}));document.querySelectorAll("[data-select]").forEach(button => button.addEventListener("click", () => {{const checked = button.dataset.select === "all";document.querySelectorAll("[data-tank-toggle]").forEach(toggle => {{toggle.checked = checked;toggle.dispatchEvent(new Event("change"));}});}}));</script>
</body></html>"""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(page, encoding="utf-8")
    return destination


def main() -> None:
    """Crea la dashboard dal CSV indicato in riga di comando."""
    parser = argparse.ArgumentParser(
        description="Crea la dashboard HTML della cantina."
    )
    parser.add_argument("results_csv", type=Path, help="CSV prodotto dalla pipeline")
    parser.add_argument("output_html", type=Path, help="Dashboard HTML da creare")
    args = parser.parse_args()
    print(create_dashboard(args.results_csv, args.output_html))
