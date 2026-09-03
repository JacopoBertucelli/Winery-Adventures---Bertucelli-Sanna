"""Punto di ingresso per l'esecuzione completa della pipeline."""

import argparse
import logging
from pathlib import Path

import polars as pl

from winery_adventures.computations import WineryHPCComputations
from winery_adventures.io import (
    load_sensor_data,
    load_tank_info,
    prepare_sensor_data,
    save_results,
)
from winery_adventures.pipeline import WineryPipeline
from winery_adventures.transformations import WineryTransformer


def run_full_pipeline(
    input_csv: str | Path,
    tank_info_csv: str | Path | None,
    output_csv: str | Path,
    project_name: str = "Winery-Adventures",
    log_to_wandb: bool = True,
    n_jobs: int = -1,
) -> pl.DataFrame:
    """Carica TSV, esegue la pipeline e salva il CSV finale."""
    sensors = prepare_sensor_data(load_sensor_data(input_csv), n_jobs)
    tank_info = load_tank_info(tank_info_csv) if tank_info_csv else None
    result = WineryPipeline(
        [WineryTransformer(tank_info), WineryHPCComputations()], project_name
    ).run(sensors, log_to_wandb)
    save_results(result, output_csv)
    return result


def build_parser() -> argparse.ArgumentParser:
    """Crea il parser degli argomenti della riga di comando."""
    parser = argparse.ArgumentParser(
        description="Analizza i dati dei sensori della cantina."
    )
    parser.add_argument("input_csv", type=Path, help="File TSV dei sensori")
    parser.add_argument("output_csv", type=Path, help="File CSV dei risultati")
    parser.add_argument("--tank-info", type=Path, help="File TSV delle cisterne")
    parser.add_argument(
        "--project-name", default="Winery-Adventures", help="Nome progetto W&B"
    )
    parser.add_argument(
        "--no-wandb", action="store_true", help="Disabilita il logging W&B"
    )
    parser.add_argument("--n-jobs", type=int, default=-1, help="Processi Joblib")
    return parser


def main() -> None:
    """Esegue la pipeline da riga di comando."""
    args = build_parser().parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    run_full_pipeline(
        args.input_csv,
        args.tank_info,
        args.output_csv,
        args.project_name,
        not args.no_wandb,
        args.n_jobs,
    )
