# Guida ai Dati di Mercato in QuantConnect Lean

Questa guida fornisce informazioni dettagliate su come accedere, utilizzare e gestire i dati di mercato all'interno del framework QuantConnect Lean.

## Indice

1. [Introduzione](#introduzione)
2. [Tipi di Dati](#tipi-di-dati)
3. [Risoluzioni Temporali](#risoluzioni-temporali)
4. [Accesso ai Dati](#accesso-ai-dati)
5. [Dati Storici](#dati-storici)
6. [Dati in Tempo Reale](#dati-in-tempo-reale)
7. [Dati Personalizzati](#dati-personalizzati)
8. [Gestione dei Dati Mancanti](#gestione-dei-dati-mancanti)
9. [Esempi Pratici](#esempi-pratici)
10. [Best Practices](#best-practices)

## Introduzione

I dati di mercato sono la materia prima per qualsiasi strategia di trading algoritmico. QuantConnect Lean offre un'infrastruttura robusta per accedere a diversi tipi di dati di mercato, con varie risoluzioni temporali e per diversi asset.

## Tipi di Dati

QuantConnect Lean supporta diversi tipi di dati di mercato:

### 1. TradeBars

I TradeBars rappresentano i dati OHLCV (Open, High, Low, Close, Volume) per un determinato periodo di tempo.

```csharp
// Accesso ai dati TradeBars
var open = data["SPY"].Open;
var high = data["SPY"].High;
var low = data["SPY"].Low;
var close = data["SPY"].Close;
var volume = data["SPY"].Volume;
```

### 2. QuoteBars

I QuoteBars contengono informazioni sui prezzi bid e ask.

```csharp
// Accesso ai dati QuoteBars
var bidOpen = data["EURUSD"].Bid.Open;
var bidClose = data["EURUSD"].Bid.Close;
var askOpen = data["EURUSD"].Ask.Open;
var askClose = data["EURUSD"].Ask.Close;
```

### 3. Ticks

I Ticks rappresentano i dati a livello di singola transazione o quotazione.

```csharp
// Accesso ai dati Tick
var tickPrice = tick.Price;
var tickQuantity = tick.Quantity;
```

### 4. Dati Fondamentali

I dati fondamentali includono informazioni finanziarie sulle aziende, come bilanci, rapporti finanziari, ecc.

```csharp
// Accesso ai dati fondamentali
var fundamentals = data.Get<FundamentalData>();
var pe = fundamentals.ValuationRatios.PERatio;
var eps = fundamentals.EarningReports.BasicEPS;
```

### 5. Dati di Opzioni

I dati di opzioni includono informazioni su contratti di opzioni, come strike price, scadenza, ecc.

```csharp
// Accesso ai dati di opzioni
var chain = data.OptionChains["SPY"];
var calls = chain.Calls;
var puts = chain.Puts;
```

### 6. Dati di Futures

I dati di futures includono informazioni su contratti futures, come scadenza, prezzo, ecc.

```csharp
// Accesso ai dati di futures
var chain = data.FutureChains["ES"];
var contracts = chain.Contracts;
```

## Risoluzioni Temporali

QuantConnect Lean supporta diverse risoluzioni temporali per i dati di mercato:

- **Tick**: Dati a livello di singola transazione o quotazione
- **Second**: Dati aggregati al secondo
- **Minute**: Dati aggregati al minuto
- **Hour**: Dati aggregati all'ora
- **Daily**: Dati aggregati al giorno

```csharp
// Aggiunta di asset con diverse risoluzioni
AddEquity("SPY", Resolution.Minute);
AddForex("EURUSD", Resolution.Second);
AddCrypto("BTCUSD", Resolution.Hour);
AddOption("SPY", Resolution.Daily);
```

## Accesso ai Dati

### 1. Slice

L'oggetto `Slice` è il contenitore principale per i dati di mercato in QuantConnect Lean. Viene passato al metodo `OnData` e contiene tutti i dati disponibili per il timestamp corrente.

```csharp
public override void OnData(Slice data)
{
    // Accesso ai dati TradeBars
    if (data.ContainsKey("SPY"))
    {
        var spy = data["SPY"];
        var price = spy.Close;
    }
    
    // Accesso ai dati QuoteBars
    if (data.QuoteBars.ContainsKey("EURUSD"))
    {
        var eurusd = data.QuoteBars["EURUSD"];
        var spread = eurusd.Ask.Close - eurusd.Bid.Close;
    }
    
    // Accesso ai dati Tick
    if (data.Ticks.ContainsKey("BTCUSD"))
    {
        var btcTicks = data.Ticks["BTCUSD"];
        foreach (var tick in btcTicks)
        {
            var price = tick.Price;
        }
    }
}
```

### 2. Securities

L'oggetto `Securities` contiene informazioni sugli asset aggiunti all'algoritmo, inclusi i dati di mercato correnti.

```csharp
// Accesso ai dati tramite Securities
var price = Securities["SPY"].Price;
var volume = Securities["SPY"].Volume;
var bidPrice = Securities["EURUSD"].BidPrice;
var askPrice = Securities["EURUSD"].AskPrice;
```

### 3. Consolidators

I `Consolidators` permettono di aggregare dati a risoluzioni temporali personalizzate.

```csharp
// Creazione di un consolidator per aggregare dati al minuto in dati a 5 minuti
var fiveMinuteConsolidator = new TradeBarConsolidator(TimeSpan.FromMinutes(5));
fiveMinuteConsolidator.DataConsolidated += OnFiveMinuteBar;
SubscriptionManager.AddConsolidator("SPY", fiveMinuteConsolidator);

// Handler per i dati consolidati
private void OnFiveMinuteBar(object sender, TradeBar bar)
{
    var symbol = bar.Symbol;
    var open = bar.Open;
    var high = bar.High;
    var low = bar.Low;
    var close = bar.Close;
    var volume = bar.Volume;
}
```

## Dati Storici

QuantConnect Lean permette di accedere a dati storici per analisi e backtesting.

### 1. History API

L'API `History` permette di richiedere dati storici per uno o più asset.

```csharp
// Richiesta di dati storici per SPY
var spyHistory = History("SPY", 10, Resolution.Daily);
foreach (var bar in spyHistory)
{
    var date = bar.Time;
    var price = bar.Close;
}

// Richiesta di dati storici per più asset
var symbols = new[] { "SPY", "QQQ", "IWM" };
var history = History(symbols, 10, Resolution.Daily);
foreach (var slice in history)
{
    foreach (var kvp in slice.Bars)
    {
        var symbol = kvp.Key;
        var bar = kvp.Value;
        var price = bar.Close;
    }
}
```

### 2. Warm-Up

Il metodo `SetWarmUp` permette di inizializzare gli indicatori con dati storici prima di iniziare il trading.

```csharp
// Warm-up di 50 barre per gli indicatori
SetWarmUp(50);

// Warm-up con una durata specifica
SetWarmUp(TimeSpan.FromDays(10));

// Warm-up con una risoluzione specifica
SetWarmUp(50, Resolution.Daily);
```

## Dati in Tempo Reale

QuantConnect Lean supporta anche dati in tempo reale per il trading live.

### 1. Configurazione

Per utilizzare dati in tempo reale, è necessario configurare l'algoritmo per il trading live.

```csharp
// Configurazione per il trading live
SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage);
```

### 2. Accesso ai Dati

L'accesso ai dati in tempo reale avviene attraverso gli stessi metodi utilizzati per i dati storici.

```csharp
public override void OnData(Slice data)
{
    // Accesso ai dati in tempo reale
    if (data.ContainsKey("SPY"))
    {
        var spy = data["SPY"];
        var price = spy.Close;
    }
}
```

## Dati Personalizzati

QuantConnect Lean permette di utilizzare dati personalizzati per strategie più avanzate.

### 1. Definizione di una Classe di Dati Personalizzati

```csharp
public class MyCustomData : BaseData
{
    public decimal Value { get; set; }
    
    public override SubscriptionDataSource GetSource(SubscriptionDataConfig config, DateTime date, bool isLiveMode)
    {
        var source = "path/to/data/file.csv";
        return new SubscriptionDataSource(source, SubscriptionTransportMedium.LocalFile);
    }
    
    public override BaseData Reader(SubscriptionDataConfig config, string line, DateTime date, bool isLiveMode)
    {
        var data = new MyCustomData();
        data.Symbol = config.Symbol;
        data.Time = date;
        
        try
        {
            var csv = line.Split(',');
            data.Value = decimal.Parse(csv[1]);
        }
        catch (Exception)
        {
            return null;
        }
        
        return data;
    }
}
```

### 2. Aggiunta di Dati Personalizzati

```csharp
// Aggiunta di dati personalizzati
AddData<MyCustomData>("CUSTOM", Resolution.Daily);

// Accesso ai dati personalizzati
public override void OnData(Slice data)
{
    if (data.ContainsKey("CUSTOM"))
    {
        var custom = data.Get<MyCustomData>("CUSTOM");
        var value = custom.Value;
    }
}
```

## Gestione dei Dati Mancanti

La gestione dei dati mancanti è un aspetto importante del trading algoritmico.

### 1. Fill Forward

Il metodo `SetFillForwardResolution` permette di specificare come gestire i dati mancanti.

```csharp
// Configurazione del fill forward
SetFillForwardResolution(Resolution.Minute);
```

### 2. Controllo dei Dati

È importante controllare la presenza di dati prima di utilizzarli.

```csharp
public override void OnData(Slice data)
{
    // Controllo della presenza di dati
    if (!data.ContainsKey("SPY"))
    {
        Debug("Dati mancanti per SPY");
        return;
    }
    
    var spy = data["SPY"];
    var price = spy.Close;
}
```

## Esempi Pratici

### Esempio 1: Utilizzo di Dati OHLCV

```csharp
public class OHLCVExample : QCAlgorithm
{
    private SimpleMovingAverage _sma;
    
    public override void Initialize()
    {
        SetStartDate(2018, 1, 1);
        SetEndDate(2020, 1, 1);
        SetCash(100000);
        
        AddEquity("SPY", Resolution.Daily);
        
        _sma = SMA("SPY", 50);
    }
    
    public override void OnData(Slice data)
    {
        if (!_sma.IsReady) return;
        
        if (data.ContainsKey("SPY"))
        {
            var spy = data["SPY"];
            var open = spy.Open;
            var high = spy.High;
            var low = spy.Low;
            var close = spy.Close;
            var volume = spy.Volume;
            
            if (close > _sma.Current.Value && !Portfolio.Invested)
            {
                SetHoldings("SPY", 1.0);
                Debug($"ACQUISTO: Prezzo ({close}) > SMA ({_sma.Current.Value})");
            }
            else if (close < _sma.Current.Value && Portfolio.Invested)
            {
                Liquidate("SPY");
                Debug($"VENDITA: Prezzo ({close}) < SMA ({_sma.Current.Value})");
            }
        }
    }
}
```

### Esempio 2: Utilizzo di Dati Tick

```csharp
public class TickDataExample : QCAlgorithm
{
    private decimal _lastPrice;
    private int _tickCount;
    
    public override void Initialize()
    {
        SetStartDate(2018, 1, 1);
        SetEndDate(2020, 1, 1);
        SetCash(100000);
        
        AddEquity("SPY", Resolution.Tick);
        
        _lastPrice = 0;
        _tickCount = 0;
    }
    
    public override void OnData(Slice data)
    {
        if (data.Ticks.ContainsKey("SPY"))
        {
            var ticks = data.Ticks["SPY"];
            foreach (var tick in ticks)
            {
                _tickCount++;
                
                if (_lastPrice == 0)
                {
                    _lastPrice = tick.Price;
                    continue;
                }
                
                var priceDelta = tick.Price - _lastPrice;
                _lastPrice = tick.Price;
                
                if (_tickCount > 100)
                {
                    if (priceDelta > 0 && !Portfolio.Invested)
                    {
                        SetHoldings("SPY", 1.0);
                        Debug($"ACQUISTO: Delta Positivo ({priceDelta})");
                    }
                    else if (priceDelta < 0 && Portfolio.Invested)
                    {
                        Liquidate("SPY");
                        Debug($"VENDITA: Delta Negativo ({priceDelta})");
                    }
                }
            }
        }
    }
}
```

### Esempio 3: Utilizzo di Dati di Opzioni

```csharp
public class OptionsDataExample : QCAlgorithm
{
    private Symbol _optionSymbol;
    
    public override void Initialize()
    {
        SetStartDate(2018, 1, 1);
        SetEndDate(2020, 1, 1);
        SetCash(100000);
        
        var equity = AddEquity("SPY", Resolution.Minute);
        var option = AddOption("SPY", Resolution.Minute);
        
        option.SetFilter(universe => universe.Strikes(-2, 2).Expiration(0, 30));
        
        _optionSymbol = equity.Symbol;
    }
    
    public override void OnData(Slice data)
    {
        if (!Portfolio.Invested && data.OptionChains.ContainsKey(_optionSymbol))
        {
            var chain = data.OptionChains[_optionSymbol];
            
            // Filtra le opzioni call at-the-money
            var atmCalls = chain
                .Where(x => x.Right == OptionRight.Call)
                .OrderBy(x => Math.Abs(x.Strike - Securities[_optionSymbol].Price))
                .Take(1);
            
            foreach (var call in atmCalls)
            {
                MarketOrder(call.Symbol, 1);
                Debug($"ACQUISTO CALL: Strike ({call.Strike}), Scadenza ({call.Expiry})");
            }
        }
    }
}
```

### Esempio 4: Utilizzo di Dati Personalizzati

```csharp
public class CustomDataExample : QCAlgorithm
{
    public override void Initialize()
    {
        SetStartDate(2018, 1, 1);
        SetEndDate(2020, 1, 1);
        SetCash(100000);
        
        AddEquity("SPY", Resolution.Daily);
        AddData<MyCustomData>("CUSTOM", Resolution.Daily);
    }
    
    public override void OnData(Slice data)
    {
        if (data.ContainsKey("CUSTOM") && data.ContainsKey("SPY"))
        {
            var custom = data.Get<MyCustomData>("CUSTOM");
            var spy = data["SPY"];
            
            if (custom.Value > 100 && !Portfolio.Invested)
            {
                SetHoldings("SPY", 1.0);
                Debug($"ACQUISTO: Valore Personalizzato ({custom.Value}) > 100");
            }
            else if (custom.Value < 100 && Portfolio.Invested)
            {
                Liquidate("SPY");
                Debug($"VENDITA: Valore Personalizzato ({custom.Value}) < 100");
            }
        }
    }
    
    public class MyCustomData : BaseData
    {
        public decimal Value { get; set; }
        
        public override SubscriptionDataSource GetSource(SubscriptionDataConfig config, DateTime date, bool isLiveMode)
        {
            var source = "path/to/data/file.csv";
            return new SubscriptionDataSource(source, SubscriptionTransportMedium.LocalFile);
        }
        
        public override BaseData Reader(SubscriptionDataConfig config, string line, DateTime date, bool isLiveMode)
        {
            var data = new MyCustomData();
            data.Symbol = config.Symbol;
            data.Time = date;
            
            try
            {
                var csv = line.Split(',');
                data.Value = decimal.Parse(csv[1]);
            }
            catch (Exception)
            {
                return null;
            }
            
            return data;
        }
    }
}
```

## Best Practices

### 1. Gestione della Memoria

- Utilizza la risoluzione appropriata per i tuoi dati
- Limita l'uso di dati ad alta frequenza (tick) se non necessario
- Utilizza il metodo `SetWarmUp` con parsimonia

### 2. Efficienza

- Utilizza `data.ContainsKey()` per verificare la presenza di dati
- Evita di richiedere dati storici all'interno di `OnData`
- Utilizza i consolidatori per aggregare dati ad alta frequenza

### 3. Robustezza

- Gestisci i dati mancanti con il fill forward
- Controlla sempre la presenza di dati prima di utilizzarli
- Implementa controlli di validità sui dati

### 4. Scalabilità

- Limita il numero di asset monitorati
- Utilizza universi dinamici per gestire grandi set di asset
- Implementa filtri per ridurre il numero di asset da processare

## Conclusione

I dati di mercato sono la base di qualsiasi strategia di trading algoritmico. QuantConnect Lean offre un'infrastruttura robusta per accedere, utilizzare e gestire diversi tipi di dati di mercato. Seguendo le best practices descritte in questa guida, è possibile sviluppare strategie più efficienti e robuste.

Per ulteriori informazioni, consulta la [documentazione ufficiale di QuantConnect](https://www.quantconnect.com/docs/).