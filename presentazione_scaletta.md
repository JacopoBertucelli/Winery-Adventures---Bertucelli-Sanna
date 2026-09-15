# Winery Adventures — scaletta, discorsi e piano della demo (16 settembre 2026)

Le celle di codice del notebook iniziano con un commento `# ▶ nome`: nella scaletta ci si riferisce a quello, mai ai numeri `In [n]`, che cambiano con l'ordine di esecuzione.

## Prima di iniziare (10 minuti prima)

1. Sul computer che condivide lo schermo: `git checkout main && git pull`, poi `uv sync --locked --extra dev` e, se mancano, `uv pip install ipykernel matplotlib jupyterlab`.
2. `uv run jupyter lab presentazione.ipynb` (oppure VS Code con kernel `.venv/bin/python`).
3. Kernel → **Restart Kernel and Run All Cells**. Ci vogliono 10–15 secondi. **Mai eseguire una cella da sola su un kernel appena avviato** (si riconosce da `In [1]`): tutte dipendono dalla cella `▶ ambiente`. Controllare: nessuna cella rossa, il grafico O(n²) visibile, la dashboard in fondo visibile. Se la dashboard non si vede: File → **Trust Notebook** e rieseguire la cella `▶ dashboard`.
4. Tornare in cima, nascondere la barra laterale (`Ctrl+B` / `Cmd+B`), zoom del browser al 110–125 %.
5. Da qui in poi **non serve la rete**: W&B lavora offline, Jira è uno screenshot, tutto il resto è locale.
6. Durante la presentazione si rieseguono dal vivo solo le celle indicate con **[esegui]**; le altre si scorrono con i risultati già pronti. Se una cella dal vivo fallisce, il risultato di prima è ancora sotto: si commenta quello e si va avanti.

## Scaletta

| Minuti | Chi | Blocco | Celle |
|---:|---|---|---|
| 0–5 | Jacopo | Apertura, README, flusso, repository e organizzazione | copertina, `▶ ambiente`, sezione "Apertura e organizzazione del lavoro" |
| 5–9 | Alex | Test, CI e qualità | sezione "Qualità automatica", `▶ test e CI dal vivo` |
| 9–18 | Jacopo | Architettura, UML, dati, validazione, pipeline, formula, W&B | sezione "Il sistema", da `▶ dati sample e cisterna 9` a `▶ W&B offline` |
| 18–26 | Alex | Prestazioni, Numba, Joblib, report e dashboard | sezione "Prestazioni e dashboard", da `▶ Python contro Numba` a `▶ dashboard` |
| 26–28 | Jacopo | Limiti e sviluppi futuri | tabella "Limiti noti e sviluppi possibili" |
| 28–30 | Alex | Conclusione e domande | "Conclusione" |

Punti di controllo: al minuto 9 deve iniziare "Il sistema", al 18 "Prestazioni", al 26 i limiti. Se si è in ritardo, le celle da saltare sono indicate in ogni blocco.

---

## 0–5 · Jacopo — Apertura e organizzazione

**Cosa mostrare.** La copertina (scheda e "In breve"), la figura del flusso, poi la sezione "Apertura e organizzazione del lavoro" con la board Jira e la tabella delle pull request. La cella `▶ ambiente` è già eseguita: non commentarla.

**Discorso.**

> Buongiorno. Il nostro progetto si chiama Winery Adventures: una piccola pipeline Python per monitorare le cisterne di fermentazione di una cantina. I sensori registrano pH, temperatura e quantità di mosto; il programma legge quelle letture da un file, calcola per ogni cisterna alcuni indicatori — tra cui lo stress di fermentazione richiesto dalla traccia — e produce un CSV e una dashboard che segnala le cisterne da tenere d'occhio.
>
> *(figura del flusso)* Questo è il flusso, preso dal README: entrano i dati dei sensori e le informazioni sulle cisterne; Polars e Joblib preparano i dati, Polars calcola gli indicatori, Numba calcola lo stress; esce il CSV dei risultati e da quello nasce la dashboard. Weights & Biases è un'aggiunta facoltativa per registrare i risultati.
>
> Il notebook che vedete segue l'ordine della presentazione: le tabelle e le misure sono ricalcolate dalle celle, le immagini sono un supporto alla spiegazione. Un filo conduttore ci accompagna: la cisterna 9, la più piccola e la più "stressata", che ritroveremo fino alla dashboard.
>
> Come abbiamo lavorato. Il repository è nato il 1° settembre; il 3 settembre abbiamo messo la configurazione di base — il `pyproject` con le dipendenze, il lockfile che fissa le versioni esatte, licenza MIT e README — e la prima pull request con la pipeline di analisi. Ci siamo divisi per aree: io la pipeline, i diagrammi UML e il README; Alexandro i test, l'integrazione continua, il benchmark e la dashboard.
>
> *(board)* Le attività le abbiamo organizzate su una board Kanban in Jira: questa è la board, con le attività nelle colonne To Do, In Progress, In Review e Done.
>
> *(tabella PR)* Per le attività principali abbiamo usato branch tematici e pull request, così implementazione, controllo e integrazione restano separati: queste sono le nove pull request, in ordine, con data, contenuto e autore. Su ogni push e pull request verso `main` gira l'integrazione continua, che esegue Ruff e Pytest: ve la mostra adesso Alexandro.

**Se sei lungo.** Non leggere la tabella delle PR riga per riga: "nove pull request, dalla pipeline alla dashboard, fino alla misura della memoria".

---

## 5–9 · Alex — Test, CI e qualità

**Cosa mostrare.** La sezione "Qualità automatica: test e integrazione continua" (tabella dei test), poi **[esegui]** `▶ test e CI dal vivo`.

**Discorso.**

> Prima di entrare nel sistema, come facciamo a fidarci che funzioni. Abbiamo 22 test automatici: 17 forniti con la traccia e 5 scritti da noi. I test unitari controllano un pezzo alla volta con dati minimi: che la formula dia 2,2 sull'esempio del tutor, che la classe base imponga davvero il metodo comune, che le trasformazioni aggiungano le colonne giuste. I due test di accettazione fanno girare tutta la pipeline, dal file di ingresso al CSV e alla dashboard, per verificare i requisiti nel loro insieme. Weights & Biases non viene mai contattato durante i test: al suo posto c'è un finto run.
>
> *(tabella)* Qui vedete cosa verifica ogni gruppo di test. La suite del tutor è arrivata dopo i nostri test: l'abbiamo integrata con una pull request dedicata, adattando tre dettagli che sono documentati nei commit.
>
> L'integrazione continua: un workflow di GitHub Actions parte a ogni push e a ogni pull request verso `main`. Ricrea l'ambiente dal lockfile ed esegue Ruff — stile del codice ed errori comuni — e Pytest, su Ubuntu con Python 3.10. Se un passo fallisce la pull request mostra un check rosso; noi integriamo le modifiche solo dopo i controlli verdi, così in due nessuno rompe il lavoro dell'altro senza accorgersene.
>
> *(esegui la cella)* Questi sono gli stessi tre comandi della CI, eseguiti qui e ora: 22 test passati in meno di un secondo, Ruff senza segnalazioni, formattazione a posto.

**Se sei lungo.** Salta la frase sulla PR #7.

---

## 9–18 · Jacopo — Il sistema

**Cosa mostrare, in ordine.** "Architettura" (tabella dei moduli e i tre UML) → "I dati in ingresso" → **[esegui]** `▶ dati sample e cisterna 9` → `▶ input errati` (già eseguita, saltabile) → "La pipeline al lavoro" → **[esegui]** `▶ esecuzione della pipeline` → `▶ cisterna 9 dopo la pipeline` (già eseguita, saltabile) → "La formula di stress" → **[esegui]** `▶ formula: esempio del tutor` → "Weights & Biases è facoltativo" → **[esegui]** `▶ W&B offline`.

**Discorso.**

> *(Architettura, ~2 min)* Il sistema è una catena di analizzatori: ogni analizzatore riceve una tabella, la arricchisce e la passa al successivo. Tutti rispettano lo stesso contratto — un metodo `analyze_data` definito da una classe astratta — e la pipeline si limita a chiamarli in ordine. Aggiungere un indicatore vuol dire scrivere una nuova classe e metterla in lista: il resto non cambia. Nella tabella ci sono gli otto moduli: la classe base, le trasformazioni con Polars, lo stress con Numba, la pipeline, il collegamento a W&B, la lettura e il controllo dei file con Joblib, il comando principale e la dashboard.
>
> *(UML)* I tre diagrammi richiesti sono scritti in Mermaid dentro il repository, insieme al codice. Casi d'uso: l'analista avvia l'analisi e consulta la dashboard, lo sviluppatore misura le prestazioni, W&B è un sistema esterno. Classi: le due classi concrete estendono la classe astratta, la pipeline le contiene senza conoscerne i dettagli, il reporter W&B è opzionale. Sequenza: dalla riga di comando alla lettura dei file, alle trasformazioni, alla formula, al CSV.
>
> *(Dati, ~2 min)* In ingresso ci sono due file TSV: le rilevazioni dei sensori — una riga per lettura — e le informazioni sulle cisterne, con capacità e vitigni. I dati di esempio hanno 100 rilevazioni di 9 cisterne, in ordine sparso, e tre vitigni per cisterna. Prima di calcolare qualunque cosa, i file vengono controllati: se il file manca, mancano colonne, non ci sono rilevazioni o le cisterne sono duplicate, la pipeline si ferma subito con un messaggio chiaro invece di produrre un risultato sbagliato.
>
> *(esegui `▶ dati sample e cisterna 9`)* Ecco i dati caricati: le prime righe dei sensori, le informazioni delle cisterne, e per ogni cisterna quante rilevazioni ha e quanto mosto in media. La cisterna 9 ha solo 8 rilevazioni e meno mosto di tutte: ecco le sue letture. *(`▶ input errati`, se c'è tempo)* Qui invece tre casi di input sbagliato: file inesistente, colonne mancanti, cisterne duplicate. In tutti e tre la pipeline si ferma con un errore esplicito.
>
> *(Pipeline, ~2 min)* Il comando `winery-adventures` legge i sensori, prepara le cisterne in parallelo con Joblib, aggiunge gli indicatori con Polars, calcola lo stress con Numba e scrive il CSV. *(esegui `▶ esecuzione della pipeline`)* Lo eseguiamo sui dati di esempio: le righe INFO sono il diario della pipeline; in un decimo di secondo abbiamo 300 righe e 11 colonne, rilette dal CSV appena scritto. Qui sotto gli indicatori per cisterna: pH medio, numero di rilevazioni e stress, una riga per cisterna.
>
> Perché 300 righe da 100 rilevazioni: ogni rilevazione viene abbinata a ciascuno dei tre vitigni della sua cisterna, ed è così che contiamo le rilevazioni per vitigno, come chiede la traccia. Gli indicatori per cisterna sono ripetuti su ogni riga della cisterna: si leggono una volta per cisterna, non si sommano. *(`▶ cisterna 9 dopo la pipeline`, se c'è tempo)* Per la cisterna 9: 8 rilevazioni per 3 vitigni, 24 righe, e la prima lettura ripetuta per ognuno dei suoi vitigni con gli stessi indicatori.
>
> *(Formula, ~2 min)* La formula dello stress confronta ogni rilevazione con tutte le altre della stessa cisterna: quanto cambiano pH e temperatura — la temperatura pesa il doppio — e quanto poco mosto c'è, con il fattore 500 diviso i litri. Più le letture sono diverse tra loro e più la cisterna è vuota, più lo stress cresce. Confrontare tutte le coppie vuol dire n² operazioni per cisterna: per questo la funzione è compilata da Numba in codice macchina — stessa formula, centinaia di volte più veloce, come vedremo tra poco. *(esegui `▶ formula: esempio del tutor`)* Sull'esempio del tutor, due rilevazioni a 500 litri, il risultato è 2,2, che è il valore atteso anche dal test; la cisterna 9 arriva a 11.
>
> *(W&B, ~1 min)* Weights & Biases è facoltativo: se il logging è attivo, la pipeline apre un run e registra lo stress di ogni cisterna. Se W&B non è raggiungibile, il reporter intercetta l'errore, scrive un avviso nel log e la pipeline va avanti: il CSV arriva comunque. *(esegui `▶ W&B offline`)* Qui il run è offline, salvato in locale senza account: mezzo secondo, e le 300 righe ci sono.

**Se sei lungo.** Salta `▶ input errati` e `▶ cisterna 9 dopo la pipeline` (basta la frase "8 per 3, 24 righe"). Se serve ancora tempo, W&B a voce senza eseguire la cella.

**Se chiedono cosa succede senza rete.** Aprire `winery_adventures/reporting.py`: il `try/except` intorno a `wandb.init` e `run.log` trasforma qualsiasi errore in un `WARNING`.

---

## 18–26 · Alex — Prestazioni e dashboard

**Cosa mostrare, in ordine.** "Python contro Numba" → **[esegui]** `▶ Python contro Numba` → "Come cresce il tempo" → `▶ grafico O(n²)` (già eseguita: mostrare il grafico, non rieseguire) → "Pipeline completa, Joblib e report" → `▶ pipeline su 100 000 righe, Joblib e report` (già eseguita) → "La dashboard" → `▶ soglia delle anomalie` (già eseguita) → **[esegui]** `▶ dashboard` e scorrere la pagina.

**Discorso.**

> *(Benchmark, ~2 min)* Lo script di benchmark misura tre cose: la formula scritta in Python puro, la stessa formula compilata da Numba, e la pipeline completa su 100 000 rilevazioni di 100 cisterne generate in memoria. Controlla che Python e Numba diano lo stesso risultato e salva un report nel repository. *(esegui `▶ Python contro Numba`)* Qui la ripetiamo dal vivo su 300 rilevazioni, cioè 90 000 coppie: Python puro circa 50 millisecondi, Numba circa un decimo di millisecondo, stesso risultato: quattrocento e più volte più veloce.
>
> *(Grafico, ~2 min)* La traccia chiede proprio il confronto di tutte le coppie, quindi la complessità resta quadratica: raddoppiando le rilevazioni il tempo quadruplica, per entrambe le versioni. Nel grafico, con assi logaritmici, le due linee hanno la stessa pendenza della linea tratteggiata, che è l'andamento n² di riferimento: Numba non cambia la forma della curva, la abbassa di centinaia di volte. Python lo fermiamo a 2 000 rilevazioni per non allungare la demo; Numba arriva a 8 000, cioè 64 milioni di coppie, in meno di un decimo di secondo.
>
> *(100 000 righe e Joblib, ~2 min)* La pipeline intera sui 100 000 record — 100 cisterne, un milione di coppie ciascuna — ci mette poco più di un decimo di secondo. A parte misuriamo la fase che Joblib parallelizza, la preparazione delle cisterne: Joblib lavora con processi separati, e avviarli ha un costo; il compito da distribuire qui è leggero, quindi su questi dati il parallelismo non conviene ancora. Per questo test e benchmark usano un solo worker, che dà una misura ripetibile, mentre il comando lascia tutti i processori per default. In fondo c'è il report archiviato nel repository: tempi e, dall'ultima versione, anche il picco di memoria misurato con tracemalloc.
>
> *(Dashboard, ~2 min)* Il comando `winery-dashboard` legge il CSV della pipeline — la sua unica sorgente — e scrive una pagina HTML autosufficiente, senza librerie esterne: si apre con un doppio clic. Le regole di anomalia sono scritte nella pagina: pH medio fuori da 3–4, temperatura media fuori da 22–28 gradi, stress sopra la media più una deviazione standard delle cisterne. *(`▶ soglia delle anomalie`)* Ricalcolando la soglia: 8,02 più 1,65 fa 9,67, e la superano le cisterne 8 e 9. La 9 è la più stressata perché ha poche rilevazioni, molto diverse tra loro, e poco mosto. *(esegui `▶ dashboard` e scorri)* Questa è la dashboard vera: la tabella con le anomalie, il confronto delle temperature dove ogni cisterna si accende e si spegne con una casella, e i nove grafici separati con la stessa scala, perché nove linee sovrapposte sarebbero illeggibili.

**Se sei lungo.** Non commentare la terza riga della tabella Joblib; nella dashboard mostra solo tabella e confronto, salta i nove grafici.

---

## 26–28 · Jacopo — Limiti e sviluppi futuri

**Cosa mostrare.** La tabella "Limiti noti e sviluppi possibili".

**Discorso.**

> Chiudiamo con quello che il sistema non fa, perché sono scelte, non dimenticanze. Le righe vengono triplicate dall'abbinamento ai vitigni: serve al conteggio per vitigno ed è ciò che il test del tutor si aspetta; un'alternativa è un conteggio in una tabella separata. La dashboard mostra una sola lettura per istante, e nei dati di esempio la cisterna 6 ne ha due nello stesso minuto. Joblib oggi parallelizza un compito leggero: la cosa da fare è spostarci sotto il calcolo dello stress, che è quello pesante. La formula Numba usa un solo core e Polars lavora in memoria: con dati molto più grandi si passerebbe al ciclo parallelo e alla modalità lazy. Infine non abbiamo usato le issue di GitHub, la documentazione Sphinx e la copertura dei test in CI: le docstring sono già pronte per Sphinx.

---

## 28–30 · Alex — Conclusione e domande

**Cosa mostrare.** I tre punti della "Conclusione".

**Discorso.**

> In sintesi. Dal sensore al CSV: le 8 rilevazioni della cisterna 9 sono diventate 24 righe con le misure originali conservate, e le tabelle sull'output sono rilette dal CSV della pipeline, che è anche l'unica sorgente della dashboard. I casi limite sono decisioni esplicite: input scorretti fermano l'elaborazione con un messaggio chiaro, le rilevazioni incomplete restano nel risultato ed escono solo dalla formula, W&B non blocca mai la pipeline. Le ottimizzazioni sono misurate e il comportamento è verificato: Python e Numba danno lo stesso valore con l'andamento quadratico richiesto, e i 22 test, Ruff e la CI eseguiti qui sono gli stessi che girano su ogni pull request. Tutto è nel repository ed è riproducibile con i comandi in appendice. Grazie, siamo a disposizione per le domande.

---

## Domande probabili, risposte brevi

| Domanda | Risposta |
|---|---|
| Perché una classe astratta? | Fissa il contratto `analyze_data(df) -> df`; la pipeline chiama solo quello e non conosce Polars o Numba. Un nuovo indicatore è una nuova sottoclasse in lista. |
| Cos'è `over("tank_id")`? | Una window function di Polars: calcola l'aggregato per cisterna e lo riporta su ogni riga della cisterna (a differenza di `group_by`, che ridurrebbe a una riga). |
| Perché 300 righe? | Join left con le informazioni delle cisterne + explode della lista dei vitigni: ogni rilevazione compare una volta per vitigno, così si contano le rilevazioni per vitigno. È anche ciò che il test di accettazione del tutor si aspetta. |
| Cosa fa `@njit(cache=True)`? | Alla prima chiamata Numba compila la funzione in codice macchina per i tipi ricevuti (array `float64`); `cache=True` salva il compilato in `__pycache__`, così un nuovo avvio non ricompila. Stessa formula, niente interprete nel doppio ciclo. |
| Perché la formula è O(n²)? | La traccia chiede il confronto di tutte le coppie. Non riduciamo la complessità: la rendiamo sostenibile con Numba (64 milioni di coppie in meno di 0,1 s). |
| Joblib come è usato? | `Parallel(n_jobs)(delayed(process_tank)(gruppo) ...)` sui gruppi per cisterna, backend `loky` a processi. Con dati piccoli l'avvio dei processi costa più del guadagno: test e benchmark usano `n_jobs=1`, la CLI `-1`. |
| E se W&B non è raggiungibile? | `reporting.py` ha un `try/except` intorno a `init`/`log`/`finish`: l'errore diventa un `WARNING` e la pipeline continua. Nei test `wandb.init` è sostituito con `monkeypatch`; in CI `WANDB_MODE=disabled`. |
| Quali controlli sull'input? | File inesistente, colonne mancanti, nessuna rilevazione, `tank_id` o `time` nulli, cisterne duplicate nelle informazioni. Errori espliciti, elaborazione interrotta. |
| Cosa fa la deviazione termica? | Distanza dai 26 °C standard, rapportata a 1 000 litri con `when/then/otherwise` (litri nulli o zero → `null`, non divisione per zero); senza la colonna dei litri si chiama `temperature_deviation` e non è rapportata. Nomi imposti dai test del tutor. |
| Come decide le anomalie la dashboard? | pH medio fuori da 3,0–4,0; temperatura media fuori da 22–28 °C; stress sopra media + deviazione standard tra le cisterne (soglia relativa). Legge solo il CSV. |
| Unitari vs accettazione? | Unitari: un componente alla volta con dati minimi ("stiamo costruendo il sistema nel modo giusto?"). Accettazione: tutto il flusso rispetto ai requisiti ("stiamo costruendo il sistema giusto?"). |
| Perché uv e il lockfile? | `uv sync --locked` ricrea lo stesso ambiente ovunque; se `uv.lock` non è coerente con `pyproject.toml` il comando fallisce, anche in CI. |
| Quanta memoria usa? | Il benchmark misura con `tracemalloc` il picco delle allocazioni Python durante la pipeline sui 100 000 record: circa 4 MiB. Non è l'RSS dei componenti nativi (Polars, Numba). |
| Perché la cisterna 9 è la più stressata? | Poche rilevazioni, molto diverse tra loro, e poco mosto: il fattore 500/litri pesa di più. |
| Perché la dashboard mostra 99 letture su 100? | Deduplica su (`tank_id`, `time`) per annullare la triplicazione; la cisterna 6 ha due letture nello stesso istante e ne mostra una. È nei limiti. |
| Cosa non c'è? | Issue di GitHub, Sphinx, copertura in CI, parallelismo nella formula, Polars lazy. Tutti nella tabella dei limiti con la relativa estensione. |

## Cose da non dire (non sono dimostrabili dal repository)

- Che GitHub *impedisce* il merge con la CI rossa (non c'è branch protection): dire "integriamo solo dopo i controlli verdi".
- Numeri esatti di esecuzioni di GitHub Actions o revisioni automatiche.
- Che la board Jira è stata usata fin dal primo giorno o che "nessuna modifica è entrata direttamente in `main`" (c'è almeno un commit diretto sul README).
- Che nella seconda misura Joblib "i worker sono già attivi": dipende dal backend, dire solo "misura successiva".
- Che "tutto è calcolato dal codice al momento": le immagini sono statiche, i grafici sono del notebook.

## Piano B

- **`NameError: name 'os' is not defined`** (o `repo_root`, `pl`, `display`…): il kernel è nuovo e manca la cella `▶ ambiente`. Eseguirla e rilanciare la cella, oppure Run → **Run All Above Selected Cell** (≈10 s).
- **Una cella fallisce dal vivo**: il risultato della prova generale è ancora sotto la cella (il notebook conserva gli output). Commentare quello, non rieseguire.
- **Il kernel muore**: non riavviare durante la presentazione; continuare a scorrere gli output salvati.
- **JupyterLab non parte**: aprire il notebook in VS Code con il kernel `.venv/bin/python`.
- **La dashboard nel notebook è vuota**: aprire `output/demo/dashboard.html` con un doppio clic (è la stessa pagina).
- **Tempi**: l'esecuzione completa dura 10–15 s; nessuna cella dal vivo supera i 4 s (`▶ test e CI dal vivo` ≈ 2 s, `▶ grafico O(n²)` ≈ 4 s, `▶ pipeline su 100 000 righe` ≈ 2 s).
