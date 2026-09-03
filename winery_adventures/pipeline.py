"""Pipeline di elaborazione dei dati della cantina."""

import logging
from collections.abc import Iterable

import polars as pl

from winery_adventures.base import BaseWineryAnalyzer
from winery_adventures.reporting import WandbReporter

LOGGER = logging.getLogger(__name__)


class WineryPipeline:
    """Esegue in sequenza trasformazioni e analisi della cantina."""

    def __init__(
        self,
        analyzers: Iterable[BaseWineryAnalyzer],
        project_name: str = "Winery-Adventures",
    ) -> None:
        self.analyzers = list(analyzers)
        self.project_name = project_name

    def run(self, df: pl.DataFrame, log_to_wandb: bool = False) -> pl.DataFrame:
        """Esegue gli analizzatori e, se richiesto, registra le metriche."""
        for analyzer in self.analyzers:
            LOGGER.info("Esecuzione %s", analyzer.__class__.__name__)
            df = analyzer.analyze_data(df)
        if log_to_wandb:
            self.log_to_wandb(df)
        return df

    def log_to_wandb(self, df: pl.DataFrame) -> None:
        """Registra i risultati su Weights & Biases."""
        WandbReporter(self.project_name).log(df)
