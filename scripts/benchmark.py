"""Benchmark riproducibile della formula Numba e della pipeline."""

import argparse
from pathlib import Path
from time import perf_counter

import numpy as np
import polars as pl

from winery_adventures.computations import (
    WineryHPCComputations,
    pairwise_stress_function,
)
from winery_adventures.io import prepare_sensor_data
from winery_adventures.pipeline import WineryPipeline
from winery_adventures.transformations import WineryTransformer


def python_stress(pH: np.ndarray, temp: np.ndarray, quantity: np.ndarray) -> float:
    """Versione Python della formula, usata solo per il confronto."""
    total = 0.0
    for first in range(len(pH)):
        for second in range(len(pH)):
            deviation = abs(pH[first] - pH[second]) + 2 * abs(
                temp[first] - temp[second]
            )
            total += deviation * (500 / quantity[first] + 500 / quantity[second])
    return total / (len(pH) ** 2) if len(pH) else 0.0


def sample_data(rows: int, tanks: int, seed: int) -> pl.DataFrame:
    """Crea in memoria dati uniformi e deterministici."""
    rng = np.random.default_rng(seed)
    return pl.DataFrame(
        {
            "tank_id": np.arange(rows) % tanks + 1,
            "time": np.arange(rows),
            "pH": rng.uniform(3.0, 4.0, rows),
            "temp": rng.uniform(22.0, 28.0, rows),
            "quantity_liters": rng.integers(200, 1000, rows),
        }
    )


def run_benchmark(rows: int, tanks: int, formula_size: int, output: Path) -> str:
    """Misura Numba e pipeline, poi salva un breve report Markdown."""
    formula_data = sample_data(formula_size, 1, 42)
    pH, temp, quantity = (
        formula_data[column].to_numpy() for column in ["pH", "temp", "quantity_liters"]
    )
    started = perf_counter()
    python_value = python_stress(pH, temp, quantity)
    python_seconds = perf_counter() - started
    pairwise_stress_function(pH, temp, quantity)  # compilazione JIT
    started = perf_counter()
    numba_value = pairwise_stress_function(pH, temp, quantity)
    numba_seconds = perf_counter() - started
    if not np.isclose(python_value, numba_value):
        raise RuntimeError("La formula Python e Numba non coincidono")
    started = perf_counter()
    data = prepare_sensor_data(sample_data(rows, tanks, 42), n_jobs=1)
    WineryPipeline([WineryTransformer(), WineryHPCComputations()]).run(data)
    pipeline_seconds = perf_counter() - started
    report = f"""# Report delle prestazioni

Generato con `python scripts/benchmark.py --rows {rows} --tanks {tanks}`.

| Misura | Dimensione | Tempo (s) |
|---|---:|---:|
| Formula Python | {formula_size} rilevazioni | {python_seconds:.6f} |
| Formula Numba (JIT caldo) | {formula_size} rilevazioni | {numba_seconds:.6f} |
| Pipeline Polars + Joblib | {rows} righe, {tanks} cisterne | {pipeline_seconds:.6f} |

La formula di stress segue il requisito `O(n²)` per cisterna. Numba elimina il
costo dell'interprete nel doppio ciclo; Polars mantiene le trasformazioni
colonnari e Joblib prepara i gruppi per cisterna. Il benchmark usa un worker
per una misura ripetibile; la CLI usa tutti i processori per default.
"""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    return report


def main() -> None:
    """Legge gli argomenti e aggiorna il report di prestazioni."""
    parser = argparse.ArgumentParser(description="Benchmark Winery Adventures")
    parser.add_argument("--rows", type=int, default=100_000)
    parser.add_argument("--tanks", type=int, default=100)
    parser.add_argument("--formula-size", type=int, default=300)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/performance/performance_report.md"),
    )
    args = parser.parse_args()
    print(run_benchmark(args.rows, args.tanks, args.formula_size, args.output))


if __name__ == "__main__":
    main()
