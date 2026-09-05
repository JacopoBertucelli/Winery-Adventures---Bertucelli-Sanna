"""Test di accettazione della pipeline."""

from pathlib import Path

import polars as pl

from winery_adventures.main import run_full_pipeline


def test_sample_pipeline(tmp_path: Path) -> None:
    """I dati sample producono il CSV analizzato con le colonne attese."""
    root = Path(__file__).parents[2]
    results = tmp_path / "results.csv"

    output = run_full_pipeline(
        root / "data/sensors_sample.tsv",
        root / "data/tank_info_sample.tsv",
        results,
        log_to_wandb=False,
        n_jobs=1,
    )

    assert {"avg_pH_per_tank", "stress_score"}.issubset(output.columns)
    assert pl.read_csv(results).height == output.height
