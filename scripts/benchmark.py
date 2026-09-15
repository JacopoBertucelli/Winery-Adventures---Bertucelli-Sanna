"""Benchmark riproducibile della formula Numba e della pipeline."""

import argparse
import tracemalloc
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
    """Calcola in Python puro la formula di stress per il confronto.

    Args:
        pH: Valori di pH della cisterna.
        temp: Valori di temperatura della cisterna.
        quantity: Volumi corrispondenti alle rilevazioni.

    Returns:
        Lo stress medio calcolato con il doppio ciclo Python.
    """
    total = 0.0
    for first in range(len(pH)):
        for second in range(len(pH)):
            deviation = abs(pH[first] - pH[second]) + 2 * abs(
                temp[first] - temp[second]
            )
            total += deviation * (500 / quantity[first] + 500 / quantity[second])
    return total / (len(pH) ** 2) if len(pH) else 0.0


def sample_data(rows: int, tanks: int, seed: int) -> pl.DataFrame:
    """Crea dati sintetici uniformi e riproducibili in memoria.

    Args:
        rows: Numero totale di rilevazioni da generare.
        tanks: Numero di cisterne da distribuire nelle rilevazioni.
        seed: Seme del generatore casuale NumPy.

    Returns:
        DataFrame Polars con le colonne richieste dalla pipeline.
    """
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
    """Misura tempi e memoria Python della pipeline e salva il report.

    Args:
        rows: Numero di righe usate per la misura della pipeline.
        tanks: Numero di cisterne nel dataset sintetico della pipeline.
        formula_size: Numero di letture usate per confrontare Python e Numba.
        output: Percorso del report Markdown da aggiornare.

    Returns:
        Testo Markdown scritto nel report delle prestazioni.
    """
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
    tracemalloc.start()
    started = perf_counter()
    data = prepare_sensor_data(sample_data(rows, tanks, 42), n_jobs=1)
    WineryPipeline([WineryTransformer(), WineryHPCComputations()]).run(data)
    pipeline_seconds = perf_counter() - started
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    peak_memory_mib = peak_bytes / (1024 * 1024)
    report = f"""# Report delle prestazioni

Generato con `python scripts/benchmark.py --rows {rows} --tanks {tanks}`.

| Misura | Dimensione | Tempo (s) |
|---|---:|---:|
| Formula Python | {formula_size} rilevazioni | {python_seconds:.6f} |
| Formula Numba (JIT caldo) | {formula_size} rilevazioni | {numba_seconds:.6f} |
| Pipeline Polars + Joblib | {rows} righe, {tanks} cisterne | {pipeline_seconds:.6f} |

Picco di memoria Python tracciato durante la pipeline: **{peak_memory_mib:.2f} MiB**.

La formula di stress segue il requisito `O(n²)` per cisterna. Numba elimina il
costo dell'interprete nel doppio ciclo; Polars mantiene le trasformazioni
colonnari e Joblib prepara i gruppi per cisterna. Il benchmark usa un worker
per una misura ripetibile; la CLI usa tutti i processori per default.

La memoria è misurata con `tracemalloc`: rappresenta le allocazioni Python
tracciabili durante la pipeline, non l'intero RSS dei componenti nativi.
"""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    return report


def main() -> None:
    """Legge gli argomenti e aggiorna il report delle prestazioni.

    Returns:
        None. Il report è scritto nel percorso indicato da ``--output``.
    """
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
