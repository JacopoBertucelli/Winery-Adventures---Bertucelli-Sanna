"""Classi base utilizzate dagli analizzatori della cantina."""

from abc import ABC, abstractmethod

import polars as pl


class BaseWineryAnalyzer(ABC):
    """Definisce il contratto comune degli analizzatori della pipeline.

    Le sottoclassi ricevono un DataFrame Polars e restituiscono il DataFrame
    arricchito senza modificare l'interfaccia usata dalla pipeline.
    """

    @abstractmethod
    def analyze_data(self, df: pl.DataFrame) -> pl.DataFrame:
        """Elabora un DataFrame e restituisce il risultato.

        Args:
            df: DataFrame contenente i dati da elaborare.

        Returns:
            DataFrame ottenuto dopo l'elaborazione.
        """
        raise NotImplementedError
