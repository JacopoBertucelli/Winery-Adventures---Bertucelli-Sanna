import polars as pl
import pytest

from winery_adventures.main import run_full_pipeline


@pytest.mark.slow
def test_winery_pipeline_end_to_end(tmp_path, monkey_joblib, monkey_wandb_run, sensors_df, tank_info_df):
    """
    1) Create a CSV with columns [tank_id, time, pH, temp, quantity_liters].
    2) Create an optional 'tank_info' CSV to test the join.
    3) Run the full pipeline.
    4) Check final CSV and wandb logs.
    """
    sensor_csv = tmp_path / "sensors.csv"
    sensor_csv.write_text(sensors_df.write_csv(separator="\t"))

    # Suppose we have an extra CSV with grape_variety, just to demonstrate the join
    info_csv = tmp_path / "tank_info.csv"
    info_csv.write_text(tank_info_df.write_csv(separator="\t"))

    output_csv = tmp_path / "results.csv"

    run_full_pipeline(
        input_csv=str(sensor_csv),
        tank_info_csv=str(info_csv),
        output_csv=str(output_csv),
        project_name="AcceptanceTest",
    )

    # 3) Check wandb logs
    assert any("stress_score" in d for d in monkey_wandb_run.logs), "No stress_score logged to wandb"

    # 4) Read final CSV
    df_result = pl.read_csv(output_csv)
    # Should have columns from transformations + HPC
    for col in ["avg_pH_per_tank", "stress_score"]:
        assert col in df_result.columns, f"Missing {col} in final output"
    # We won't do an exact numeric check, but you could if you wanted to.
    assert df_result.shape[0] == 9

    parallel_mock, delayed_mock = monkey_joblib

    parallel_mock.assert_called()
    delayed_mock.assert_called()
