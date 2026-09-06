"""Test di accettazione: pipeline, CSV e dashboard."""

from pathlib import Path

import polars as pl

from winery_adventures.dashboard import create_dashboard
from winery_adventures.main import run_full_pipeline


def test_sample_pipeline_and_dashboard(tmp_path: Path) -> None:
    """I dati sample producono il CSV analizzato e una dashboard leggibile."""
    root = Path(__file__).parents[2]
    results = tmp_path / "results.csv"
    dashboard = tmp_path / "dashboard.html"
    output = run_full_pipeline(
        root / "data/sensors_sample.tsv",
        root / "data/tank_info_sample.tsv",
        results,
        log_to_wandb=False,
        n_jobs=1,
    )
    assert {"avg_pH_per_tank", "stress_score"}.issubset(output.columns)
    assert pl.read_csv(results).height == output.height
    create_dashboard(results, dashboard)
    page = dashboard.read_text(encoding="utf-8")
    assert "Stato fermentazione" in page
    assert "Trend temperatura per cisterna" in page
    assert page.count('class="chart-card"') == 9
    assert "Confronto selezionabile" in page
    assert page.count('type="checkbox" data-tank-toggle') == 9
    assert "series.style.display" in page
    assert 'class="grid"' in page
