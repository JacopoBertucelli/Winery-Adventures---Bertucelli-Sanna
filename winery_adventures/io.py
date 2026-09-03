"""Caricamento, preparazione e salvataggio dei dati."""

from pathlib import Path

import joblib
import polars as pl

SENSOR_COLUMNS = {"tank_id", "time", "pH", "temp", "quantity_liters"}
TANK_INFO_COLUMNS = {"tank_id", "grape_variety", "capacity_liters"}


def _check_file(path: str | Path, description: str) -> Path:
    """Restituisce un file esistente oppure solleva un errore descrittivo."""
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"File {description} non trovato: {file_path}")
    return file_path


def validate_columns(df: pl.DataFrame, required: set[str], description: str) -> None:
    """Verifica le colonne minime del DataFrame."""
    missing = required.difference(df.columns)
    if missing:
        columns = ", ".join(sorted(missing))
        raise ValueError(f"Colonne mancanti {description}: {columns}")


def load_sensor_data(path: str | Path) -> pl.DataFrame:
    """Carica e valida il TSV dei sensori usando Polars."""
    df = pl.read_csv(
        _check_file(path, "dei sensori"), separator="\t", try_parse_dates=True
    )
    validate_columns(df, SENSOR_COLUMNS, "nei dati dei sensori")
    if df.is_empty():
        raise ValueError("Il file dei sensori non contiene rilevazioni")
    if df.select(pl.col("tank_id", "time").is_null().any()).row(0) != (False, False):
        raise ValueError("tank_id e time non possono contenere valori nulli")
    return df


def load_tank_info(path: str | Path) -> pl.DataFrame:
    """Carica e valida il TSV delle cisterne."""
    df = pl.read_csv(_check_file(path, "delle informazioni cisterne"), separator="\t")
    validate_columns(df, TANK_INFO_COLUMNS, "nelle informazioni delle cisterne")
    if df.is_empty() or df["tank_id"].n_unique() != df.height:
        raise ValueError("Le informazioni delle cisterne non sono valide")
    return df


def process_tank(tank_df: pl.DataFrame) -> pl.DataFrame:
    """Normalizza e ordina le rilevazioni di una cisterna."""
    return tank_df.with_columns(
        pl.col("tank_id").cast(pl.Int64),
        pl.col("pH").cast(pl.Float64),
        pl.col("temp").cast(pl.Float64),
        pl.col("quantity_liters").cast(pl.Float64),
    ).sort("time")


def prepare_sensor_data(df: pl.DataFrame, n_jobs: int = -1) -> pl.DataFrame:
    """Normalizza in parallelo i gruppi per cisterna con Joblib."""
    groups = df.partition_by("tank_id", maintain_order=True)
    return pl.concat(
        joblib.Parallel(n_jobs=n_jobs)(
            joblib.delayed(process_tank)(group) for group in groups
        )
    )


def save_results(df: pl.DataFrame, path: str | Path) -> Path:
    """Salva il risultato CSV, creando la cartella di output se necessaria."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.write_csv(output_path)
    return output_path
