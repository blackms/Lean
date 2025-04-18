# Esecuzione del Backtest della Strategia SMA Crossover su S&P 500 (SPX)

Questa guida spiega come eseguire il backtest della strategia SMA Crossover sull'indice S&P 500 (SPX) utilizzando QuantConnect Lean.

## Dati Utilizzati

Per questo backtest utilizziamo:
- **Indice S&P 500 (SPX)**: Dati giornalieri dell'indice, disponibili in `Data/index/usa/daily/spx.zip`
- **ETF S&P 500 (SPY)**: Come proxy per il trading, poiché non è possibile tradare direttamente l'indice

## Metodo 1: Utilizzo di Lean CLI (Raccomandato)

Il modo più semplice per eseguire un backtest è utilizzare Lean CLI.

### Passo 1: Copiare la Strategia

Copia il file della strategia nella cartella appropriata del progetto Lean CLI:

```
cp project_journal/strategies/esempio_strategia_sma_crossover_spx.py [percorso-progetto-lean-cli]/Algorithm.Python/
```

### Passo 2: Eseguire il Backtest

Esegui il backtest con il comando:

```
lean backtest "SMA_CrossOver_SPX"
```

## Metodo 2: Esecuzione Manuale

Se preferisci eseguire manualmente il backtest, segui questi passaggi:

### Passo 1: Copiare il File di Configurazione

Copia il file di configurazione nella cartella Launcher:

```
cp project_journal/config_backtest_spx.json Launcher/config.json
```

### Passo 2: Compilare la Soluzione

Compila la soluzione Lean:

```
dotnet build QuantConnect.Lean.sln
```

### Passo 3: Eseguire il Launcher

Esegui il launcher di Lean:

```
cd Launcher/bin/Debug
dotnet QuantConnect.Lean.Launcher.dll
```

## Interpretazione dei Risultati

Dopo l'esecuzione del backtest, i risultati includeranno:

1. **Performance dell'Indice vs. Strategia**: Confronto tra la performance dell'indice S&P 500 e la strategia
2. **Segnali di Trading**: Momenti in cui la media mobile veloce (50 giorni) incrocia la media mobile lenta (200 giorni)
3. **Metriche di Performance**: Sharpe ratio, drawdown, rendimento totale, ecc.

## Note Importanti

- **Proxy di Trading**: Poiché non è possibile tradare direttamente l'indice SPX, la strategia utilizza l'ETF SPY come proxy per il trading
- **Differenze di Performance**: Potrebbero esserci piccole differenze tra l'indice SPX e l'ETF SPY a causa di costi di gestione e tracking error
- **Commissioni**: La strategia include commissioni di trading per SPY, che influenzano la performance complessiva

## Documentazione dei Risultati

Dopo aver eseguito il backtest, documenta i risultati utilizzando il template `project_journal/backtest_results/backtest_template.md`. Assicurati di includere:

1. **Screenshot dei Grafici**: Equity curve, drawdown, e indicatori
2. **Metriche di Performance**: Tutte le metriche generate dal backtest
3. **Osservazioni**: Analisi dei risultati e possibili miglioramenti

## Ottimizzazione dei Parametri

Per ottimizzare i parametri della strategia (periodi delle medie mobili), puoi:

1. Modificare i parametri nel file di configurazione:
   ```json
   "parameters": {
     "sma-fast-period": 50,
     "sma-slow-period": 200
   }
   ```

2. Eseguire backtest con diverse combinazioni di parametri
3. Confrontare i risultati per trovare la combinazione ottimale