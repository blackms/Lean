# Guida al Backtesting con QuantConnect Lean

Questa guida spiega come creare e testare strategie di trading algoritmico utilizzando QuantConnect Lean.

## Indice
1. [Creazione di una Strategia](#creazione-di-una-strategia)
2. [Configurazione del Backtesting](#configurazione-del-backtesting)
3. [Esecuzione del Backtesting](#esecuzione-del-backtesting)
4. [Analisi dei Risultati](#analisi-dei-risultati)
5. [Ottimizzazione della Strategia](#ottimizzazione-della-strategia)

## Creazione di una Strategia

### Struttura Base di un Algoritmo

Ogni algoritmo in QuantConnect Lean deve ereditare dalla classe `QCAlgorithm` e implementare almeno due metodi:

1. **Initialize()**: Configura i parametri iniziali dell'algoritmo
2. **OnData()**: Elabora i dati in arrivo e prende decisioni di trading

### Esempio di Strategia in Python

```python
from AlgorithmImports import *

class MiaStrategia(QCAlgorithm):
    
    def initialize(self):
        # Imposta le date di inizio e fine del backtest
        self.set_start_date(2020, 1, 1)
        self.set_end_date(2020, 12, 31)
        
        # Imposta il capitale iniziale
        self.set_cash(100000)
        
        # Aggiungi i titoli da monitorare
        self.symbol = self.add_equity("SPY", Resolution.DAILY)
        
        # Inizializza gli indicatori
        self.sma_fast = self.SMA(self.symbol, 20)
        self.sma_slow = self.SMA(self.symbol, 50)
        
        # Imposta il warm-up per gli indicatori
        self.set_warm_up(50)
    
    def on_data(self, data):
        # Verifica se gli indicatori sono pronti
        if not self.sma_fast.is_ready or not self.sma_slow.is_ready:
            return
        
        # Logica di trading
        if not self.portfolio.invested:
            if self.sma_fast.current.value > self.sma_slow.current.value:
                self.set_holdings(self.symbol, 1)
                self.debug("COMPRATO: SMA Fast sopra SMA Slow")
        elif self.sma_fast.current.value < self.sma_slow.current.value:
            self.liquidate(self.symbol)
            self.debug("VENDUTO: SMA Fast sotto SMA Slow")
```

### Esempio di Strategia in C#

```csharp
using System;
using System.Collections.Generic;
using QuantConnect.Data;
using QuantConnect.Indicators;

namespace QuantConnect.Algorithm.CSharp
{
    public class MiaStrategia : QCAlgorithm
    {
        private Symbol _symbol;
        private SimpleMovingAverage _smaFast;
        private SimpleMovingAverage _smaSlow;
        
        public override void Initialize()
        {
            // Imposta le date di inizio e fine del backtest
            SetStartDate(2020, 1, 1);
            SetEndDate(2020, 12, 31);
            
            // Imposta il capitale iniziale
            SetCash(100000);
            
            // Aggiungi i titoli da monitorare
            _symbol = AddEquity("SPY", Resolution.Daily).Symbol;
            
            // Inizializza gli indicatori
            _smaFast = SMA(_symbol, 20);
            _smaSlow = SMA(_symbol, 50);
            
            // Imposta il warm-up per gli indicatori
            SetWarmUp(50);
        }
        
        public override void OnData(Slice data)
        {
            // Verifica se gli indicatori sono pronti
            if (!_smaFast.IsReady || !_smaSlow.IsReady)
                return;
            
            // Logica di trading
            if (!Portfolio.Invested)
            {
                if (_smaFast.Current.Value > _smaSlow.Current.Value)
                {
                    SetHoldings(_symbol, 1);
                    Debug("COMPRATO: SMA Fast sopra SMA Slow");
                }
            }
            else if (_smaFast.Current.Value < _smaSlow.Current.Value)
            {
                Liquidate(_symbol);
                Debug("VENDUTO: SMA Fast sotto SMA Slow");
            }
        }
    }
}
```

## Configurazione del Backtesting

La configurazione del backtesting viene effettuata nel file `config.json` nella cartella `Launcher`. Ecco i principali parametri da configurare:

```json
{
  "environment": "backtesting",
  "algorithm-type-name": "MiaStrategia",
  "algorithm-language": "Python", // o "CSharp"
  "algorithm-location": "Algorithm.Python/MiaStrategia.py", // o "QuantConnect.Algorithm.CSharp.dll"
  "data-folder": "../../../Data/",
  "debugging": true
}
```

### Parametri Principali

- **environment**: Imposta l'ambiente di esecuzione (backtesting, live-paper, ecc.)
- **algorithm-type-name**: Nome della classe dell'algoritmo
- **algorithm-language**: Linguaggio dell'algoritmo (Python o CSharp)
- **algorithm-location**: Percorso del file dell'algoritmo
- **data-folder**: Percorso della cartella contenente i dati storici

## Esecuzione del Backtesting

### Utilizzo di Lean CLI (Raccomandato)

Il modo più semplice per eseguire un backtest è utilizzare Lean CLI:

1. Installare Lean CLI:
   ```
   pip install lean
   ```

2. Creare un nuovo progetto:
   ```
   lean project-create
   ```

3. Eseguire il backtest:
   ```
   lean backtest "MiaStrategia"
   ```

### Esecuzione Manuale

Per eseguire manualmente un backtest:

1. Compilare la soluzione:
   ```
   dotnet build QuantConnect.Lean.sln
   ```

2. Eseguire il launcher:
   ```
   cd Launcher/bin/Debug
   dotnet QuantConnect.Lean.Launcher.dll
   ```

## Analisi dei Risultati

Dopo l'esecuzione del backtest, i risultati vengono salvati nella cartella specificata. È possibile analizzare:

- **Statistiche di performance**: Rendimento, Sharpe ratio, drawdown, ecc.
- **Grafici**: Equity curve, drawdown, ecc.
- **Log delle operazioni**: Dettagli di ogni operazione eseguita

### Metriche Chiave da Analizzare

- **Rendimento Totale e Annualizzato**: Misura la performance complessiva
- **Sharpe Ratio**: Misura il rendimento aggiustato per il rischio
- **Drawdown Massimo**: Misura la perdita massima dal picco
- **Win Rate**: Percentuale di operazioni vincenti
- **Profit Factor**: Rapporto tra profitti lordi e perdite lorde

## Ottimizzazione della Strategia

Per ottimizzare una strategia:

1. Identificare i parametri da ottimizzare
2. Definire un intervallo di valori per ciascun parametro
3. Eseguire backtest con diverse combinazioni di parametri
4. Analizzare i risultati per trovare la combinazione ottimale

### Utilizzo dell'Ottimizzatore

Lean CLI offre un comando per l'ottimizzazione:

```
lean optimize "MiaStrategia" --target "Sharpe Ratio"
```

### Evitare l'Overfitting

- Utilizzare periodi di test out-of-sample
- Verificare la robustezza della strategia su diversi asset e timeframe
- Preferire strategie con meno parametri
- Verificare la stabilità dei risultati al variare dei parametri