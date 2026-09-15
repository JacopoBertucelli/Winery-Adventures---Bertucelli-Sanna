# Report delle prestazioni

Generato con `python scripts/benchmark.py --rows 100000 --tanks 100`.

| Misura | Dimensione | Tempo (s) |
|---|---:|---:|
| Formula Python | 300 rilevazioni | 0.043907 |
| Formula Numba (JIT caldo) | 300 rilevazioni | 0.000068 |
| Pipeline Polars + Joblib | 100000 righe, 100 cisterne | 0.127866 |

Picco di memoria Python tracciato durante la pipeline: **3.87 MiB**.

La formula di stress segue il requisito `O(n²)` per cisterna. Numba elimina il
costo dell'interprete nel doppio ciclo; Polars mantiene le trasformazioni
colonnari e Joblib prepara i gruppi per cisterna. Il benchmark usa un worker
per una misura ripetibile; la CLI usa tutti i processori per default.

La memoria è misurata con `tracemalloc`: rappresenta le allocazioni Python
tracciabili durante la pipeline, non l'intero RSS dei componenti nativi.
