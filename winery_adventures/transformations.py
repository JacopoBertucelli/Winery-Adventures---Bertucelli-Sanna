"""Trasformazioni richieste sui dati dei sensori."""

import polars as pl

from winery_adventures.base import BaseWineryAnalyzer


class WineryTransformer(BaseWineryAnalyzer):
    """Aggiunge gli indicatori descrittivi richiesti alla pipeline."""

    STANDARD_TEMPERATURE = 26.0

    def __init__(self, tank_info: pl.DataFrame | None = None) -> None:
        self.tank_info = tank_info

    def analyze_data(self, df: pl.DataFrame) -> pl.DataFrame:
        """Applica pH medio, conteggi, vitigni e deviazione termica."""
        required = {"tank_id", "pH", "temp"}
        missing = required.difference(df.columns)
        if missing:
            raise ValueError(f"Colonne mancanti: {', '.join(sorted(missing))}")
        result = self.add_avg_ph_per_tank(df)
        result = self.add_num_readings_per_tank(result)
        if self.tank_info is not None:
            result = self.add_num_readings_per_grape_variety(result)
        return self.add_temperature_deviation(result)

    def add_avg_ph_per_tank(self, df: pl.DataFrame) -> pl.DataFrame:
        """Aggiunge il pH medio della cisterna a ogni rilevazione."""
        return df.with_columns(
            pl.col("pH").mean().over("tank_id").alias("avg_pH_per_tank")
        )

    def add_num_readings_per_tank(self, df: pl.DataFrame) -> pl.DataFrame:
        """Aggiunge il numero di rilevazioni della cisterna."""
        return df.with_columns(pl.len().over("tank_id").alias("tank_num_readings"))

    def add_num_readings_per_grape_variety(self, df: pl.DataFrame) -> pl.DataFrame:
        """Unisce i vitigni e conta le rilevazioni per ciascun vitigno."""
        if self.tank_info is None:
            raise ValueError("Le informazioni sulle cisterne non sono disponibili")
        required = {"tank_id", "grape_variety"}
        missing = required.difference(self.tank_info.columns)
        if missing or self.tank_info["tank_id"].n_unique() != self.tank_info.height:
            raise ValueError("Informazioni sulle cisterne non valide")
        info = self.tank_info
        if info.schema["grape_variety"] == pl.String:
            info = info.with_columns(pl.col("grape_variety").str.split(","))
        return (
            df.join(info.select("tank_id", "grape_variety"), on="tank_id", how="left")
            .explode("grape_variety", empty_as_null=True)
            .with_columns(
                pl.len().over("grape_variety").alias("grape_variety_num_readings")
            )
        )

    def add_temperature_deviation(self, df: pl.DataFrame) -> pl.DataFrame:
        """Aggiunge la deviazione da 26 °C, scalata su 1000 litri se disponibile."""
        deviation = (pl.col("temp") - self.STANDARD_TEMPERATURE).abs()
        if "quantity_liters" not in df.columns:
            return df.with_columns(deviation.alias("temperature_deviation"))
        return df.with_columns(
            pl.when(pl.col("quantity_liters") > 0)
            .then(deviation * 1000 / pl.col("quantity_liters"))
            .otherwise(None)
            .alias("temperature_deviation_scaled")
        )
