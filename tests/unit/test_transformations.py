import polars as pl
import pytest

from winery_adventures.transformations import WineryTransformer


def test_transformer_analyze_data(sensors_df, tank_info_df_grape_variety_split):
    transformer = WineryTransformer(tank_info_df_grape_variety_split)
    out_df = transformer.analyze_data(sensors_df)

    assert (
        "avg_pH_per_tank" in out_df.columns
        and "tank_num_readings" in out_df.columns
        and "grape_variety_num_readings" in out_df.columns
        and "temperature_deviation_scaled" in out_df.columns
    )


def test_add_avg_ph_per_tank(sensors_df):
    transformer = WineryTransformer(None)
    out_df = transformer.add_avg_ph_per_tank(sensors_df)

    assert out_df["avg_pH_per_tank"][0] == 3.4
    assert out_df["avg_pH_per_tank"][1] == 3.4
    assert out_df["avg_pH_per_tank"][2] == 3.7


def test_add_num_readings_per_tank(sensors_df):
    transformer = WineryTransformer(None)
    out_df = transformer.add_num_readings_per_tank(sensors_df)

    assert out_df["tank_num_readings"][0] == 2
    assert out_df["tank_num_readings"][1] == 2
    assert out_df["tank_num_readings"][2] == 1


def test_add_num_readings_per_grape_variety(sensors_df, tank_info_df_grape_variety_split):
    transformer = WineryTransformer(tank_info_df_grape_variety_split)
    out_df = transformer.add_num_readings_per_grape_variety(sensors_df)

    assert out_df.filter(pl.col("grape_variety") == "CannonauVellutato")["grape_variety_num_readings"][0] == 3
    assert out_df.filter(pl.col("grape_variety") == "CannonauVellutato")["tank_id"].unique().len() == 2
    assert out_df.filter(pl.col("grape_variety") == "VermentinoAromatico")["grape_variety_num_readings"][0] == 1
    assert out_df.filter(pl.col("grape_variety") == "VermentinoAromatico")["tank_id"][0] == 2
    assert out_df.filter(pl.col("grape_variety") == "VermentinoAromatico")["tank_id"].len() == 1

    transformer = WineryTransformer(None)
    with pytest.raises(AttributeError):
        transformer.add_num_readings_per_grape_variety(sensors_df)


def test_standard_temperature():
    assert WineryTransformer.STANDARD_TEMPERATURE == 26.0


def test_add_temperature_deviation(sensors_df, sensors_df_without_quantities):
    transformer = WineryTransformer(None)
    out_df = transformer.add_temperature_deviation(sensors_df)

    assert out_df["temperature_deviation_scaled"][0] == 2.0
    assert out_df["temperature_deviation_scaled"][1] is None
    assert out_df["temperature_deviation_scaled"][2] == 1.5

    out_df = transformer.add_temperature_deviation(sensors_df_without_quantities)
    assert out_df["temperature_deviation"][0] == 1.0
    assert out_df["temperature_deviation"][1] == 0.0
    assert out_df["temperature_deviation"][2] == 1.5
    assert "temperature_deviation_scaled" not in out_df.columns
