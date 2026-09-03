"""Logging facoltativo delle metriche su Weights & Biases."""

import logging

import polars as pl
import wandb

LOGGER = logging.getLogger(__name__)


class WandbReporter:
    """Registra lo stress di ciascuna cisterna su Weights & Biases."""

    def __init__(self, project_name: str = "Winery-Adventures") -> None:
        self.project_name = project_name

    def log(self, df: pl.DataFrame) -> None:
        """Registra uno stress per cisterna senza bloccare la pipeline."""
        if "stress_score" not in df.columns:
            raise ValueError("La colonna stress_score non è disponibile per il logging")
        run = None
        try:
            run = wandb.init(project=self.project_name)
            for row in (
                df.select("tank_id", "stress_score")
                .unique("tank_id")
                .iter_rows(named=True)
            ):
                run.log(row) if run is not None else wandb.log(row)
        except Exception as error:
            LOGGER.warning("Reporting W&B non disponibile: %s", error)
        finally:
            try:
                run.finish() if run is not None else wandb.finish()
            except Exception as error:
                LOGGER.warning("Chiusura del run W&B non riuscita: %s", error)
