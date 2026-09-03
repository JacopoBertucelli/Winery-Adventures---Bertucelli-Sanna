"""Classi base utilizzate dagli analizzatori della cantina."""

from abc import ABC, abstractmethod

import polars as pl


class BaseWineryAnalyzer(ABC):
    """Interfaccia comune per gli elementi della pipeline."""

    @abstractmethod
    def analyze_data(self, df: pl.DataFrame) -> pl.DataFrame:
        """Elabora un DataFrame e restituisce il risultato.

        Args:
            df: DataFrame contenente i dati da elaborare.

        Returns:
            DataFrame ottenuto dopo l'elaborazione.
        """
        raise NotImplementedError
