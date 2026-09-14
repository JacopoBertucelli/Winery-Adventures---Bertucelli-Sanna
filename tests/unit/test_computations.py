import math

import polars as pl
from numba import _dispatcher

from winery_adventures.computations import WineryHPCComputations, pairwise_stress_function


def test_pairwise_stress_small():
    pH = [3.4, 3.6]
    temp = [25.0, 26.0]
    cap = [500.0, 500.0]

    val = pairwise_stress_function(pl.Series(pH).to_numpy(), pl.Series(temp).to_numpy(), pl.Series(cap).to_numpy())
    assert math.isclose(val, 2.2, abs_tol=1e-7)


def test_is_function_numba():
    assert isinstance(pairwise_stress_function, _dispatcher.Dispatcher), "Numba JIT compilation failed"


def test_hpc_computations_class():
    df_input = pl.DataFrame({"tank_id": [1, 1], "pH": [3.4, 3.6], "temp": [25, 26], "quantity_liters": [500, 500]})
    hpc = WineryHPCComputations()
    df_out = hpc.analyze_data(df_input)
    assert "stress_score" in df_out.columns
    assert df_out["stress_score"][0] == 2.2
    assert df_out["stress_score"][1] == 2.2
