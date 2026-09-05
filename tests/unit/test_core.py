"""Test unitari essenziali dei requisiti del tutor."""

import math

import numpy as np
import polars as pl
import pytest

from winery_adventures.base import BaseWineryAnalyzer
from winery_adventures.computations import (
    WineryHPCComputations,
    pairwise_stress_function,
)
from winery_adventures.reporting import WandbReporter
from winery_adventures.transformations import WineryTransformer


def test_analyzers_follow_the_required_base_class() -> None:
    """Le due fasi della pipeline implementano l'astrazione richiesta."""
    with pytest.raises(TypeError):
        BaseWineryAnalyzer()
    assert issubclass(WineryTransformer, BaseWineryAnalyzer)
    assert issubclass(WineryHPCComputations, BaseWineryAnalyzer)


def test_transformations_add_required_columns() -> None:
    """Polars calcola gli indicatori descrittivi per cisterna e vitigno."""
    sensors = pl.DataFrame(
        {
            "tank_id": [1, 1, 2],
            "time": ["2025-01-01 00:00", "2025-01-01 01:00", "2025-01-01 00:00"],
            "pH": [3.4, 3.6, 3.7],
            "temp": [25.0, 26.0, 24.5],
            "quantity_liters": [500, 500, 1000],
        }
    )
    tanks = pl.DataFrame(
        {"tank_id": [1, 2], "grape_variety": ["Cannonau", "Vermentino"]}
    )
    result = WineryTransformer(tanks).analyze_data(sensors)
    assert {
        "avg_pH_per_tank",
        "tank_num_readings",
        "grape_variety_num_readings",
        "temperature_deviation_scaled",
    }.issubset(result.columns)
    assert result.filter(pl.col("tank_id") == 1)["avg_pH_per_tank"][0] == 3.5


def test_numba_stress_formula_and_analyzer() -> None:
    """La formula richiesta e il suo risultato per cisterna coincidono."""
    pH = np.array([3.4, 3.6])
    temp = np.array([25.0, 26.0])
    quantity = np.array([500.0, 500.0])
    assert math.isclose(pairwise_stress_function(pH, temp, quantity), 2.2)
    result = WineryHPCComputations().analyze_data(
        pl.DataFrame(
            {"tank_id": [1, 1], "pH": pH, "temp": temp, "quantity_liters": quantity}
        )
    )
    assert result["stress_score"].to_list() == [2.2, 2.2]


def test_wandb_reporter_logs_one_metric_per_tank(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """W&B rimane integrato senza richiedere la rete durante il test."""
    logged: list[dict[str, float | int]] = []

    class Run:
        def log(self, row: dict[str, float | int]) -> None:
            logged.append(row)

        def finish(self) -> None:
            pass

    monkeypatch.setattr("winery_adventures.reporting.wandb.init", lambda **_: Run())
    WandbReporter("test").log(
        pl.DataFrame({"tank_id": [1, 1, 2], "stress_score": [0.1, 0.1, 0.2]})
    )
    assert len(logged) == 2
