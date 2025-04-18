# Esecuzione del Backtest per la Strategia SMA Crossover

Questa guida spiega come eseguire il backtest per la strategia SMA Crossover utilizzando QuantConnect Lean.

## Prerequisiti

Prima di iniziare, assicurati di avere:

1. QuantConnect Lean installato correttamente
2. Dati storici disponibili nella cartella `Data`
3. La strategia SMA Crossover (in Python o C#) salvata nella posizione corretta

## Metodo 1: Utilizzo di Lean CLI (Raccomandato)

Il modo più semplice per eseguire un backtest è utilizzare Lean CLI.

### Passo 1: Installare Lean CLI

Se non l'hai già fatto, installa Lean CLI:

```
pip install lean
```

### Passo 2: Inizializzare un Progetto Lean

Inizializza un nuovo progetto Lean o utilizza uno esistente:

```
lean project-create
```

### Passo 3: Copiare la Strategia

Copia il file della strategia nella cartella appropriata del progetto:

- Per Python: `<progetto>/Algorithm.Python/`
- Per C#: `<progetto>/Algorithm.CSharp/`

### Passo 4: Eseguire il Backtest

Esegui il backtest con il comando:

```
# Per la versione Python
lean backtest "SMA_CrossOver"

# Per la versione C#
lean backtest "SMACrossover"
```

## Metodo 2: Esecuzione Manuale

Se preferisci eseguire manualmente il backtest, segui questi passaggi:

### Passo 1: Configurare il file config.json

Modifica il file `Launcher/config.json` con i seguenti parametri:

Per la versione Python:

```json
{
  "environment": "backtesting",
  "algorithm-type-name": "SMA_CrossOver",
  "algorithm-language": "Python",
  "algorithm-location": "../../../Algorithm.Python/esempio_strategia_sma_crossover.py",
  "data-folder": "../../../Data/"
}
```

Per la versione C#:

```json
{
  "environment": "backtesting",
  "algorithm-type-name": "SMACrossover",
  "algorithm-language": "CSharp",
  "algorithm-location": "QuantConnect.Algorithm.CSharp.dll",
  "data-folder": "../../../Data/"
}
```

### Passo 2: Compilare la Soluzione (solo per C#)

Se stai utilizzando la versione C#, compila la soluzione:

```
dotnet build QuantConnect.Lean.sln
```

### Passo 3: Eseguire il Launcher

Esegui il launcher di Lean:

```
cd Launcher/bin/Debug
dotnet QuantConnect.Lean.Launcher.dll
```

## Visualizzazione dei Risultati

Dopo l'esecuzione del backtest, i risultati saranno disponibili nella cartella di output specificata (di default in `./backtests/`).

### Analisi dei Risultati

I risultati del backtest includono:

1. **Statistiche di Performance**:
   - Rendimento totale e annualizzato
   - Sharpe ratio
   - Drawdown massimo
   - Win rate
   - Profit factor

2. **Grafici**:
   - Equity curve
   - Drawdown
   - Indicatori (SMA Fast e SMA Slow)

3. **Log delle Operazioni**:
   - Dettagli di ogni operazione eseguita
   - Timestamp
   - Prezzo di entrata/uscita
   - Dimensione della posizione

### Documentazione dei Risultati

Dopo aver eseguito il backtest, documenta i risultati utilizzando il template `project_journal/backtest_results/backtest_template.md`.

## Ottimizzazione dei Parametri

Per ottimizzare i parametri della strategia (ad esempio, i periodi delle medie mobili), puoi:

1. **Utilizzare Lean CLI**:
   ```
   lean optimize "SMA_CrossOver" --target "Sharpe Ratio"
   ```

2. **Modificare Manualmente i Parametri**:
   - Modifica i periodi delle medie mobili (ad es. 20/50, 50/100, 100/200)
   - Esegui backtest separati per ogni combinazione
   - Confronta i risultati per trovare la combinazione ottimale

## Suggerimenti per il Backtest

1. **Periodo di Test**: Utilizza un periodo di test sufficientemente lungo che includa diversi cicli di mercato
2. **Commissioni e Slippage**: Assicurati che il modello includa commissioni e slippage realistici
3. **Robustezza**: Testa la strategia su diversi asset e timeframe per verificarne la robustezza
4. **Out-of-Sample**: Riserva un periodo per il test out-of-sample per evitare l'overfitting