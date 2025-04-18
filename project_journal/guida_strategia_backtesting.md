# Guida alla Creazione e al Backtesting di Strategie con QuantConnect Lean

Questa guida fornisce istruzioni dettagliate su come creare una strategia di trading e testarla utilizzando il framework QuantConnect Lean.

## Indice

1. [Introduzione a QuantConnect Lean](#introduzione-a-quantconnect-lean)
2. [Struttura di una Strategia](#struttura-di-una-strategia)
3. [Creazione di una Strategia](#creazione-di-una-strategia)
4. [Esecuzione del Backtesting](#esecuzione-del-backtesting)
5. [Analisi dei Risultati](#analisi-dei-risultati)
6. [Ottimizzazione della Strategia](#ottimizzazione-della-strategia)
7. [Esempi di Strategie](#esempi-di-strategie)

## Introduzione a QuantConnect Lean

QuantConnect Lean è un framework open-source per il trading algoritmico che supporta lo sviluppo, il backtesting e l'esecuzione di strategie di trading. Può essere utilizzato con C# o Python e supporta vari tipi di asset, tra cui azioni, forex, futures, opzioni e criptovalute.

### Caratteristiche principali:

- **Multilingua**: Supporto per C# e Python
- **Multi-asset**: Supporto per azioni, forex, futures, opzioni e criptovalute
- **Dati storici**: Accesso a dati storici per il backtesting
- **Indicatori**: Ampia libreria di indicatori tecnici
- **Framework**: Struttura modulare per la creazione di strategie

## Struttura di una Strategia

Una strategia di trading in QuantConnect Lean è composta da diverse parti:

### 1. Inizializzazione (`Initialize`)

Questa è la parte in cui si configurano i parametri della strategia, come:
- Date di inizio e fine del backtest
- Capitale iniziale
- Asset da tradare
- Indicatori da utilizzare
- Impostazioni di warm-up

### 2. Elaborazione dei dati (`OnData`)

Questa è la parte in cui si elaborano i dati in arrivo e si prendono decisioni di trading basate su:
- Prezzi correnti
- Valori degli indicatori
- Condizioni di mercato
- Stato del portafoglio

### 3. Eventi aggiuntivi (opzionali)

- `OnOrderEvent`: Gestisce gli eventi relativi agli ordini
- `OnEndOfDay`: Eseguito alla fine di ogni giorno di trading
- `OnEndOfAlgorithm`: Eseguito alla fine del backtest

## Creazione di una Strategia

### Passo 1: Scegliere il linguaggio

Puoi sviluppare strategie in C# o Python. Entrambi i linguaggi hanno accesso alle stesse funzionalità, ma la sintassi è diversa.

#### Esempio in C#:

```csharp
public class MyStrategy : QCAlgorithm
{
    public override void Initialize()
    {
        // Configurazione
    }

    public override void OnData(Slice data)
    {
        // Logica di trading
    }
}
```

#### Esempio in Python:

```python
class MyStrategy(QCAlgorithm):
    def Initialize(self):
        # Configurazione
        pass

    def OnData(self, data):
        # Logica di trading
        pass
```

### Passo 2: Configurare la strategia

Nella funzione `Initialize`, configura i parametri della strategia:

```csharp
public override void Initialize()
{
    // Imposta le date di inizio e fine del backtest
    SetStartDate(2018, 1, 1);
    SetEndDate(2020, 1, 1);
    
    // Imposta il capitale iniziale
    SetCash(100000);
    
    // Aggiungi asset da tradare
    AddEquity("SPY", Resolution.Daily);
    
    // Inizializza gli indicatori
    _sma = SMA("SPY", 50);
    
    // Imposta il warm-up per gli indicatori
    SetWarmUp(50);
}
```

### Passo 3: Implementare la logica di trading

Nella funzione `OnData`, implementa la logica di trading:

```csharp
public override void OnData(Slice data)
{
    // Verifica se gli indicatori sono pronti
    if (!_sma.IsReady) return;
    
    // Ottieni i dati correnti
    var price = Securities["SPY"].Price;
    
    // Logica di trading
    if (price > _sma.Current.Value && !Portfolio.Invested)
    {
        // Compra quando il prezzo è sopra la media mobile
        SetHoldings("SPY", 1.0);
        Debug("SEGNALE DI ACQUISTO: Prezzo sopra SMA");
    }
    else if (price < _sma.Current.Value && Portfolio.Invested)
    {
        // Vendi quando il prezzo è sotto la media mobile
        Liquidate("SPY");
        Debug("SEGNALE DI VENDITA: Prezzo sotto SMA");
    }
}
```

### Passo 4: Salvare la strategia

Salva la strategia in un file con estensione `.cs` (per C#) o `.py` (per Python) nella cartella appropriata:
- Per C#: `Algorithm.CSharp/`
- Per Python: `Algorithm.Python/` o in una cartella personalizzata

## Esecuzione del Backtesting

### Passo 1: Creare un file di configurazione

Crea un file `config.json` con i parametri del backtest:

```json
{
  "environment": "backtesting",
  "algorithm-type-name": "MyStrategy",
  "algorithm-language": "CSharp",
  "algorithm-location": "QuantConnect.Algorithm.CSharp.dll",
  "data-folder": "../../../Data/",
  "debugging": true,
  "debugging-method": "LocalCmdline",
  "log-handler": "QuantConnect.Logging.CompositeLogHandler",
  "messaging-handler": "QuantConnect.Messaging.Messaging",
  "job-queue-handler": "QuantConnect.Queues.JobQueue",
  "api-handler": "QuantConnect.Api.Api",
  "map-file-provider": "QuantConnect.Data.Auxiliary.LocalDiskMapFileProvider",
  "factor-file-provider": "QuantConnect.Data.Auxiliary.LocalDiskFactorFileProvider",
  "data-provider": "QuantConnect.Lean.Engine.DataFeeds.DefaultDataProvider",
  "data-channel-provider": "DataChannelProvider",
  "object-store": "QuantConnect.Lean.Engine.Storage.LocalObjectStore",
  "data-aggregator": "QuantConnect.Lean.Engine.DataFeeds.AggregationManager",
  "show-missing-data-logs": true,
  "maximum-data-points-per-chart-series": 4000,
  "transaction-log": "transaction-log.txt",
  "parameters": {
    "sma-period": 50
  }
}
```

### Passo 2: Compilare la soluzione (per C#)

Se stai utilizzando C#, compila la soluzione:

```
dotnet build QuantConnect.Lean.sln
```

### Passo 3: Eseguire il backtest

Esegui il launcher di Lean:

```
cd Launcher/bin/Debug
./QuantConnect.Lean.Launcher.exe
```

## Analisi dei Risultati

Dopo l'esecuzione del backtest, i risultati vengono salvati in diversi file:

- `[AlgorithmName]-log.txt`: Log dettagliato dell'esecuzione
- `[AlgorithmName]-summary.json`: Riepilogo dei risultati del backtest
- `[AlgorithmName].json`: Risultati dettagliati del backtest

### Metriche chiave da analizzare:

- **Rendimento complessivo**: Quanto ha guadagnato/perso la strategia
- **Sharpe Ratio**: Misura del rendimento aggiustato per il rischio
- **Drawdown**: La massima perdita dal picco al minimo
- **Win Rate**: Percentuale di operazioni vincenti
- **Profit Factor**: Rapporto tra profitti e perdite

## Ottimizzazione della Strategia

Dopo aver analizzato i risultati, puoi ottimizzare la strategia:

1. **Parametri**: Modifica i parametri degli indicatori
2. **Logica**: Migliora la logica di entrata/uscita
3. **Gestione del rischio**: Implementa tecniche di gestione del rischio
4. **Diversificazione**: Aggiungi più asset alla strategia

## Esempi di Strategie

### 1. SMA Crossover

Una strategia che utilizza il crossover di due medie mobili semplici (SMA):

```csharp
public class SMACrossover : QCAlgorithm
{
    private SimpleMovingAverage _smaFast;
    private SimpleMovingAverage _smaSlow;
    
    public override void Initialize()
    {
        SetStartDate(2018, 1, 1);
        SetEndDate(2020, 1, 1);
        SetCash(100000);
        
        AddEquity("SPY", Resolution.Daily);
        
        _smaFast = SMA("SPY", 50);
        _smaSlow = SMA("SPY", 200);
        
        SetWarmUp(200);
    }
    
    public override void OnData(Slice data)
    {
        if (!_smaFast.IsReady || !_smaSlow.IsReady) return;
        
        var fastValue = _smaFast.Current.Value;
        var slowValue = _smaSlow.Current.Value;
        
        if (!Portfolio.Invested)
        {
            if (fastValue > slowValue)
            {
                SetHoldings("SPY", 1);
                Debug($"SEGNALE DI ACQUISTO: SMA Fast ({fastValue:F2}) sopra SMA Slow ({slowValue:F2})");
            }
        }
        else
        {
            if (fastValue < slowValue)
            {
                Liquidate("SPY");
                Debug($"SEGNALE DI VENDITA: SMA Fast ({fastValue:F2}) sotto SMA Slow ({slowValue:F2})");
            }
        }
    }
}
```

### 2. RSI Contrarian

Una strategia contrarian basata sull'indice di forza relativa (RSI):

```csharp
public class RSIContrarian : QCAlgorithm
{
    private RelativeStrengthIndex _rsi;
    
    public override void Initialize()
    {
        SetStartDate(2018, 1, 1);
        SetEndDate(2020, 1, 1);
        SetCash(100000);
        
        AddEquity("SPY", Resolution.Daily);
        
        _rsi = RSI("SPY", 14);
        
        SetWarmUp(14);
    }
    
    public override void OnData(Slice data)
    {
        if (!_rsi.IsReady) return;
        
        var rsiValue = _rsi.Current.Value;
        
        if (!Portfolio.Invested)
        {
            if (rsiValue < 30)
            {
                SetHoldings("SPY", 1);
                Debug($"SEGNALE DI ACQUISTO: RSI ({rsiValue:F2}) sotto 30");
            }
        }
        else
        {
            if (rsiValue > 70)
            {
                Liquidate("SPY");
                Debug($"SEGNALE DI VENDITA: RSI ({rsiValue:F2}) sopra 70");
            }
        }
    }
}
```

## Conclusione

Questa guida fornisce le basi per creare e testare strategie di trading con QuantConnect Lean. Ricorda che il backtesting è solo una simulazione e i risultati passati non garantiscono performance future. È importante validare le strategie con test out-of-sample e paper trading prima di utilizzarle con denaro reale.

Per ulteriori informazioni, consulta la [documentazione ufficiale di QuantConnect](https://www.quantconnect.com/docs/).