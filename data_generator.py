"""Generatore deterministico di dataset grandi per il benchmark."""

import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path

import polars as pl


def generate_data(
    rows: int, tanks: int, seed: int
) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Genera letture e informazioni cisterne riproducibili."""
    rng = random.Random(seed)
    start = datetime(2025, 1, 1)
    sensors = []
    for index in range(rows):
        sensors.append(
            {
                "tank_id": index % tanks + 1,
                "time": start + timedelta(minutes=index),
                "pH": round(rng.uniform(3.0, 4.0), 2),
                "temp": round(rng.uniform(22.0, 28.0), 2),
                "quantity_liters": rng.randint(200, 1000),
            }
        )
    tank_info = [
        {
            "tank_id": tank,
            "grape_variety": "Cannonau,Bovale,Vermentino",
            "capacity_liters": 1200,
        }
        for tank in range(1, tanks + 1)
    ]
    return pl.DataFrame(sensors), pl.DataFrame(tank_info)


def main() -> None:
    """Salva il dataset grande richiesto per il report di prestazioni."""
    parser = argparse.ArgumentParser(description="Genera dati Winery Adventures")
    parser.add_argument("--rows", type=int, default=100_000)
    parser.add_argument("--tanks", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=Path, default=Path("data"))
    args = parser.parse_args()
    if args.rows < 1 or args.tanks < 1:
        raise ValueError("rows e tanks devono essere positivi")
    sensors, tanks = generate_data(args.rows, args.tanks, args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    sensors.write_csv(args.output_dir / "full_sensors.tsv", separator="\t")
    tanks.write_csv(args.output_dir / "full_tank_info.tsv", separator="\t")


if __name__ == "__main__":
    main()
