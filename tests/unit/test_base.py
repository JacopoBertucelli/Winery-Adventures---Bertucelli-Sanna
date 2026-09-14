import polars as pl
import pytest

from winery_adventures.base import BaseWineryAnalyzer
from winery_adventures.computations import WineryHPCComputations
from winery_adventures.transformations import WineryTransformer


def test_base_class_is_abstract():
    with pytest.raises(TypeError):
        BaseWineryAnalyzer()


def test_base_class_abstract_method(sensors_df):
    class WrongConcreteAnalyzer(BaseWineryAnalyzer):
        def another_analyze_data_method(self, df: pl.DataFrame) -> pl.DataFrame:
            return df

    with pytest.raises(TypeError):
        WrongConcreteAnalyzer()

    class CorrectConcreteAnalyzer(BaseWineryAnalyzer):
        def analyze_data(self, df: pl.DataFrame) -> pl.DataFrame:
            return df

    analyzer = CorrectConcreteAnalyzer()
    assert analyzer.analyze_data(sensors_df) is sensors_df


def test_subclasses():
    assert issubclass(WineryTransformer, BaseWineryAnalyzer)
    assert issubclass(WineryHPCComputations, BaseWineryAnalyzer)
