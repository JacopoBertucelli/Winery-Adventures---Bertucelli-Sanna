"""Computazioni Numba per lo stress di fermentazione."""

import numba
import numpy as np
import polars as pl

from winery_adventures.base import BaseWineryAnalyzer


@numba.njit(cache=True)
def pairwise_stress_function(
    pH_vals: np.ndarray, temp_vals: np.ndarray, quantity_vals: np.ndarray
) -> float:
    """Calcola la formula O(n²) di stress indicata dal tutor."""
    n_readings = len(pH_vals)
    if n_readings == 0:
        return 0.0
    stress_sum = 0.0
    for first in range(n_readings):
        for second in range(n_readings):
            pH_deviation = abs(pH_vals[first] - pH_vals[second])
            temperature_deviation = abs(temp_vals[first] - temp_vals[second]) * 2.0
            quantity_factor = (
                500.0 / quantity_vals[first] + 500.0 / quantity_vals[second]
            )
            stress_sum += (pH_deviation + temperature_deviation) * quantity_factor
    return stress_sum / (n_readings * n_readings)


class WineryHPCComputations(BaseWineryAnalyzer):
    """Calcola e aggiunge lo stress di fermentazione per cisterna."""

    def analyze_data(self, df: pl.DataFrame) -> pl.DataFrame:
        """Applica la funzione Numba ai dati validi di ogni cisterna."""
        required = {"tank_id", "pH", "temp", "quantity_liters"}
        missing = required.difference(df.columns)
        if missing:
            raise ValueError(f"Colonne mancanti: {', '.join(sorted(missing))}")
        scores: list[dict[str, int | float]] = []
        for tank in df.partition_by("tank_id", maintain_order=True):
            valid = tank.filter(
                pl.col("pH").is_not_null()
                & pl.col("temp").is_not_null()
                & (pl.col("quantity_liters") > 0)
            )
            if "grape_variety" in valid.columns:
                valid = valid.unique(
                    subset=["time", "pH", "temp", "quantity_liters"],
                    maintain_order=True,
                )
            scores.append(
                {
                    "tank_id": tank["tank_id"][0],
                    "stress_score": pairwise_stress_function(
                        valid["pH"].cast(pl.Float64).to_numpy(),
                        valid["temp"].cast(pl.Float64).to_numpy(),
                        valid["quantity_liters"].cast(pl.Float64).to_numpy(),
                    ),
                }
            )
        score_df = pl.DataFrame(
            scores, schema={"tank_id": df.schema["tank_id"], "stress_score": pl.Float64}
        )
        return df.join(score_df, on="tank_id", how="left")
