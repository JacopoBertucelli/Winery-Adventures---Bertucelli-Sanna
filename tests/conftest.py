from unittest.mock import Mock

import joblib
import polars as pl
import pytest
import wandb


@pytest.fixture()
def sensors_df():
    yield pl.DataFrame(
        {
            "tank_id": [1, 1, 2],
            "time": ["2025-01-01 00:00", "2025-01-01 01:00", "2025-01-01 00:30"],
            "pH": [3.3, 3.5, 3.7],
            "temp": [25.0, 26.0, 24.5],
            "quantity_liters": [500, None, 1000],
        }
    )


@pytest.fixture()
def sensors_df_without_quantities():
    yield pl.DataFrame(
        {
            "tank_id": [1, 1, 2],
            "time": ["2025-01-01 00:00", "2025-01-01 01:00", "2025-01-01 00:30"],
            "pH": [3.3, 3.5, 3.7],
            "temp": [25.0, 26.0, 24.5],
        }
    )


@pytest.fixture()
def tank_info_df():
    yield pl.DataFrame(
        {
            "tank_id": [1, 2],
            "capacity_liters": [500, 1000],
            "grape_variety": [
                "CannonauVellutato,BovaleBarricato,CarignanoNobile",
                "VermentinoAromatico,CannonauVellutato,MonicaIntenso",
            ],
        }
    )


@pytest.fixture()
def tank_info_df_grape_variety_split():
    yield pl.DataFrame(
        {
            "tank_id": [1, 2],
            "capacity_liters": [500, 1000],
            "grape_variety": [
                "CannonauVellutato,BovaleBarricato,CarignanoNobile",
                "VermentinoAromatico,CannonauVellutato,MonicaIntenso",
            ],
        }
    ).with_columns(pl.col("grape_variety").str.split(","))


@pytest.fixture()
def monkey_joblib(monkeypatch):
    def execute_parallel(*args, **kwargs):
        return [
        func(*inner_args, **call_kwargs)
        for func, inner_args, call_kwargs in args[0]
    ]
    fake_parallel_mock = Mock(side_effect=execute_parallel)
    fake_delayed_mock = Mock(wraps=joblib.delayed)

    monkeypatch.setattr(joblib.Parallel, "__call__", fake_parallel_mock)
    monkeypatch.setattr(joblib, "delayed", fake_delayed_mock)

    yield fake_parallel_mock, fake_delayed_mock


# @pytest.fixture()
# def monkey_joblib_delayed(monkeypatch):
#     joblib_delayed = joblib.delayed

#     def fake_delayed(function):
#         fake_delayed.delayed_called = True
#         return joblib_delayed(function)

#     fake_delayed_mock = Mock()

#     monkeypatch.setattr(joblib.Parallel, "__call__", fake_parallel_mock)

#     yield fake_parallel_mock

#     monkeypatch.setattr(joblib, "delayed", fake_delayed)


@pytest.fixture()
def monkey_wandb_run(monkeypatch, monkey_joblib):
    class FakeRun:
        def __init__(self):
            self.logs = []

        def finish(self):
            pass

        def log(self, data, **kwargs):
            self.logs.append(data)

    run = FakeRun()

    def fake_log(data, **kwargs):
        wandb.run.log(data, **kwargs)

    def fake_finish():
        pass

    def fake_init(*args, **kwargs):
        monkeypatch.setattr(wandb, "run", run)
        return run

    monkeypatch.setattr(wandb, "init", fake_init)
    monkeypatch.setattr(wandb, "log", fake_log)
    monkeypatch.setattr(wandb, "finish", fake_finish)

    yield run
