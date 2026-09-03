# Winery Adventures

Pipeline Python per analizzare le rilevazioni delle cisterne di fermentazione.
È mantenuta intenzionalmente piccola, ma copre i requisiti del tutor: OOP,
Polars, Numba, Joblib, Weights & Biases, Pytest, CI, UML e performance report.

## Installazione riproducibile

Python 3.10+ e `uv` sono sufficienti. Il lockfile crea l'ambiente locale
`.venv/`, che è escluso da Git.

```bash
python3 -m pip install uv
uv sync --locked --extra dev
source .venv/bin/activate       # Linux/macOS
# .venv\Scripts\Activate.ps1    # Windows PowerShell
```

In alternativa, dopo aver creato `.venv` con `python -m venv .venv`, usare
`python -m pip install -e ".[dev]"`.

## Eseguire

```bash
winery-adventures data/sensors_sample.tsv output/results.csv \
  --tank-info data/tank_info_sample.tsv --no-wandb --n-jobs 1
winery-dashboard output/results.csv output/dashboard.html
```

Aprire `output/dashboard.html` nel browser. La dashboard è un singolo file
HTML senza framework: tabella pH medio, temperatura media e stress per
cisterna, anomalie dichiarate e un piccolo trend della temperatura.

Per registrare lo stress su Weights & Biases, omettere `--no-wandb` dopo
`wandb login`.

## Verifica e prestazioni

```bash
pytest
ruff check .
ruff format --check .
python data_generator.py --rows 100000 --tanks 100
python scripts/benchmark.py --rows 100000 --tanks 100
```

Il benchmark aggiorna [il report](docs/performance/performance_report.md).
I tre diagrammi richiesti sono in [docs/uml](docs/uml/): classi, sequenza e
casi d'uso. La CI esegue Ruff e Pytest su ogni push e pull request verso
`main`.

## Cosa calcola la pipeline

- pH medio e numero di rilevazioni per cisterna;
- conteggio delle rilevazioni per vitigno, se viene fornito `--tank-info`;
- deviazione dalla temperatura standard di 26 °C, scalata per volume;
- stress di fermentazione per cisterna con la formula `O(n²)` compilata da
  Numba;
- preparazione per cisterna con Joblib e salvataggio del CSV finale.

Il CSV risultante è l'unica sorgente della dashboard; W&B è solo una seconda
visualizzazione facoltativa delle metriche di stress.
