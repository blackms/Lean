# Implementation Examples

## Overview

This section provides practical examples of implementing trading strategies using QuantConnect Lean. These examples demonstrate how to use the various components of the platform to create effective trading algorithms.

## Basic Strategies

Basic strategies demonstrate fundamental concepts and simple implementations. They are ideal for beginners to understand how Lean works and how to implement basic trading ideas.

### 1. Moving Average Crossover

The Moving Average Crossover strategy is a classic trend-following strategy that generates buy signals when a short-term moving average crosses above a long-term moving average, and sell signals when it crosses below.

```csharp
public class MovingAverageCrossoverAlgorithm : QCAlgorithm
{
    private Symbol _symbol;
    private SimpleMovingAverage _fast;
    private SimpleMovingAverage _slow;

    public override void Initialize()
    {
        SetStartDate(2018, 1, 1);
        SetEndDate(2018, 12, 31);
        SetCash(100000);
        
        _symbol = AddEquity("SPY", Resolution.Daily).Symbol;
        
        _fast = SMA(_symbol, 50, Resolution.Daily);
        _slow = SMA(_symbol, 200, Resolution.Daily);
    }

    public override void OnData(Slice data)
    {
        if (!_slow.IsReady)
            return;
        
        if (!Portfolio.Invested)
        {
            if (_fast > _slow)
            {
                SetHoldings(_symbol, 1.0);
                Debug("Bought SPY at " + Time.ToShortDateString());
            }
        }
        else
        {
            if (_fast < _slow)
            {
                Liquidate(_symbol);
                Debug("Sold SPY at " + Time.ToShortDateString());
            }
        }
    }
}
```

[Learn more about Basic Strategies](./basic-strategies.md)

### 2. RSI Mean Reversion

The RSI Mean Reversion strategy is a counter-trend strategy that buys when the RSI indicator is oversold and sells when it's overbought.

```csharp
public class RsiMeanReversionAlgorithm : QCAlgorithm
{
    private Symbol _symbol;
    private RelativeStrengthIndex _rsi;
    
    public override void Initialize()
    {
        SetStartDate(2018, 1, 1);
        SetEndDate(2018, 12, 31);
        SetCash(100000);
        
        _symbol = AddEquity("SPY", Resolution.Daily).Symbol;
        
        _rsi = RSI(_symbol, 14, MovingAverageType.Simple, Resolution.Daily);
    }
    
    public override void OnData(Slice data)
    {
        if (!_rsi.IsReady)
            return;
        
        if (!Portfolio.Invested)
        {
            if (_rsi < 30)
            {
                SetHoldings(_symbol, 1.0);
                Debug("Bought SPY at " + Time.ToShortDateString() + " with RSI " + _rsi.Current.Value);
            }
        }
        else
        {
            if (_rsi > 70)
            {
                Liquidate(_symbol);
                Debug("Sold SPY at " + Time.ToShortDateString() + " with RSI " + _rsi.Current.Value);
            }
        }
    }
}
```

### 3. Pairs Trading

The Pairs Trading strategy identifies pairs of securities that are historically correlated and trades when their relationship deviates from the norm.

```csharp
public class PairsTradingAlgorithm : QCAlgorithm
{
    private Symbol _symbolA;
    private Symbol _symbolB;
    private decimal _spread;
    private decimal _meanSpread;
    private decimal _stdSpread;
    private int _lookback = 60;
    private List<decimal> _spreadHistory = new List<decimal>();
    
    public override void Initialize()
    {
        SetStartDate(2018, 1, 1);
        SetEndDate(2018, 12, 31);
        SetCash(100000);
        
        _symbolA = AddEquity("SPY", Resolution.Daily).Symbol;
        _symbolB = AddEquity("IVV", Resolution.Daily).Symbol;
    }
    
    public override void OnData(Slice data)
    {
        if (!data.ContainsKey(_symbolA) || !data.ContainsKey(_symbolB))
            return;
        
        decimal priceA = data[_symbolA].Close;
        decimal priceB = data[_symbolB].Close;
        
        _spread = priceA / priceB;
        _spreadHistory.Add(_spread);
        
        if (_spreadHistory.Count > _lookback)
            _spreadHistory.RemoveAt(0);
        
        if (_spreadHistory.Count < _lookback)
            return;
        
        _meanSpread = _spreadHistory.Average();
        _stdSpread = StandardDeviation(_spreadHistory);
        
        decimal zScore = (_spread - _meanSpread) / _stdSpread;
        
        if (!Portfolio.Invested)
        {
            if (zScore > 2)
            {
                SetHoldings(_symbolA, -0.5);
                SetHoldings(_symbolB, 0.5);
                Debug("Sold SPY and Bought IVV at " + Time.ToShortDateString() + " with z-score " + zScore);
            }
            else if (zScore < -2)
            {
                SetHoldings(_symbolA, 0.5);
                SetHoldings(_symbolB, -0.5);
                Debug("Bought SPY and Sold IVV at " + Time.ToShortDateString() + " with z-score " + zScore);
            }
        }
        else
        {
            if (Math.Abs(zScore) < 0.5)
            {
                Liquidate();
                Debug("Closed positions at " + Time.ToShortDateString() + " with z-score " + zScore);
            }
        }
    }
    
    private decimal StandardDeviation(List<decimal> values)
    {
        decimal mean = values.Average();
        decimal sumOfSquares = values.Sum(x => (x - mean) * (x - mean));
        return (decimal)Math.Sqrt((double)(sumOfSquares / values.Count));
    }
}
```

## Advanced Strategies

Advanced strategies demonstrate more complex implementations and sophisticated trading ideas. They are suitable for experienced users who want to leverage the full power of Lean.

### 1. Multi-Factor Ranking

The Multi-Factor Ranking strategy ranks securities based on multiple factors and trades the top and bottom performers.

```csharp
public class MultiFactor : QCAlgorithm
{
    private Symbol[] _symbols;
    private Dictionary<Symbol, decimal> _momentumScores = new Dictionary<Symbol, decimal>();
    private Dictionary<Symbol, decimal> _valueScores = new Dictionary<Symbol, decimal>();
    private Dictionary<Symbol, decimal> _qualityScores = new Dictionary<Symbol, decimal>();
    private Dictionary<Symbol, decimal> _compositeScores = new Dictionary<Symbol, decimal>();
    
    public override void Initialize()
    {
        SetStartDate(2018, 1, 1);
        SetEndDate(2018, 12, 31);
        SetCash(100000);
        
        // Add a universe of stocks
        UniverseSettings.Resolution = Resolution.Daily;
        AddUniverse(CoarseSelectionFunction, FineSelectionFunction);
        
        // Schedule rebalancing
        Schedule.On(DateRules.MonthStart(), TimeRules.AfterMarketOpen(), Rebalance);
    }
    
    public IEnumerable<Symbol> CoarseSelectionFunction(IEnumerable<CoarseFundamental> coarse)
    {
        return coarse
            .Where(x => x.Price > 5 && x.DollarVolume > 5000000)
            .OrderByDescending(x => x.DollarVolume)
            .Take(100)
            .Select(x => x.Symbol);
    }
    
    public IEnumerable<Symbol> FineSelectionFunction(IEnumerable<FineFundamental> fine)
    {
        return fine
            .Where(x => x.MarketCap > 500000000)
            .Take(50)
            .Select(x => x.Symbol);
    }
    
    public void OnSecuritiesChanged(SecurityChanges changes)
    {
        _symbols = changes.AddedSecurities.Select(x => x.Symbol).ToArray();
        
        foreach (var symbol in _symbols)
        {
            _momentumScores[symbol] = 0;
            _valueScores[symbol] = 0;
            _qualityScores[symbol] = 0;
            _compositeScores[symbol] = 0;
        }
    }
    
    public void Rebalance()
    {
        if (_symbols == null || _symbols.Length == 0)
            return;
        
        // Calculate factor scores
        CalculateMomentumScores();
        CalculateValueScores();
        CalculateQualityScores();
        
        // Calculate composite scores
        foreach (var symbol in _symbols)
        {
            _compositeScores[symbol] = 
                0.4m * _momentumScores[symbol] + 
                0.3m * _valueScores[symbol] + 
                0.3m * _qualityScores[symbol];
        }
        
        // Rank securities by composite score
        var rankedSymbols = _compositeScores
            .OrderByDescending(x => x.Value)
            .Select(x => x.Key)
            .ToList();
        
        // Select top and bottom performers
        var topSymbols = rankedSymbols.Take(5).ToList();
        var bottomSymbols = rankedSymbols.Skip(rankedSymbols.Count - 5).Take(5).ToList();
        
        // Liquidate existing positions
        Liquidate();
        
        // Invest in top performers
        foreach (var symbol in topSymbols)
        {
            SetHoldings(symbol, 0.1m);
        }
        
        // Short bottom performers
        foreach (var symbol in bottomSymbols)
        {
            SetHoldings(symbol, -0.1m);
        }
    }
    
    private void CalculateMomentumScores()
    {
        // Calculate momentum scores (e.g., 12-month return)
        foreach (var symbol in _symbols)
        {
            var history = History(symbol, 252, Resolution.Daily);
            if (history.Count() < 252)
                continue;
            
            var prices = history.Select(x => x.Close).ToList();
            var momentum = prices.Last() / prices.First() - 1;
            
            _momentumScores[symbol] = momentum;
        }
        
        // Normalize scores
        NormalizeScores(_momentumScores);
    }
    
    private void CalculateValueScores()
    {
        // Calculate value scores (e.g., P/E ratio)
        foreach (var symbol in _symbols)
        {
            var security = Securities[symbol];
            var fundamental = security.Fundamentals;
            
            if (fundamental == null || fundamental.ValuationRatios.PERatio <= 0)
                continue;
            
            var value = 1 / fundamental.ValuationRatios.PERatio;
            
            _valueScores[symbol] = value;
        }
        
        // Normalize scores
        NormalizeScores(_valueScores);
    }
    
    private void CalculateQualityScores()
    {
        // Calculate quality scores (e.g., ROE)
        foreach (var symbol in _symbols)
        {
            var security = Securities[symbol];
            var fundamental = security.Fundamentals;
            
            if (fundamental == null || fundamental.OperationRatios.ROE <= 0)
                continue;
            
            var quality = fundamental.OperationRatios.ROE;
            
            _qualityScores[symbol] = quality;
        }
        
        // Normalize scores
        NormalizeScores(_qualityScores);
    }
    
    private void NormalizeScores(Dictionary<Symbol, decimal> scores)
    {
        var values = scores.Values.ToList();
        if (values.Count == 0)
            return;
        
        var min = values.Min();
        var max = values.Max();
        
        if (max == min)
            return;
        
        foreach (var symbol in scores.Keys.ToList())
        {
            scores[symbol] = (scores[symbol] - min) / (max - min);
        }
    }
}
```

[Learn more about Advanced Strategies](./advanced-strategies.md)

### 2. Machine Learning Strategy

The Machine Learning Strategy uses machine learning algorithms to predict future price movements.

```csharp
public class MachineLearningAlgorithm : QCAlgorithm
{
    private Symbol _symbol;
    private int _lookback = 30;
    private int _predictionHorizon = 5;
    private PyObject _model;
    private PyObject _scaler;
    
    public override void Initialize()
    {
        SetStartDate(2018, 1, 1);
        SetEndDate(2018, 12, 31);
        SetCash(100000);
        
        _symbol = AddEquity("SPY", Resolution.Daily).Symbol;
        
        // Import Python modules
        var sklearn = PyImport.ImportModule("sklearn.ensemble");
        var preprocessing = PyImport.ImportModule("sklearn.preprocessing");
        
        // Create model and scaler
        _model = sklearn.GetAttr("RandomForestRegressor").Invoke();
        _scaler = preprocessing.GetAttr("StandardScaler").Invoke();
        
        // Schedule training
        Schedule.On(DateRules.WeekStart(), TimeRules.AfterMarketOpen(), TrainModel);
    }
    
    public void TrainModel()
    {
        // Get historical data
        var history = History(_symbol, _lookback + _predictionHorizon, Resolution.Daily);
        if (history.Count() < _lookback + _predictionHorizon)
            return;
        
        // Prepare features and labels
        var features = new List<List<double>>();
        var labels = new List<double>();
        
        for (int i = 0; i < history.Count() - _lookback - _predictionHorizon; i++)
        {
            var window = history.Skip(i).Take(_lookback).ToList();
            var label = history.Skip(i + _lookback + _predictionHorizon - 1).First();
            
            var feature = new List<double>();
            for (int j = 0; j < window.Count; j++)
            {
                feature.Add((double)window[j].Close);
            }
            
            features.Add(feature);
            labels.Add((double)label.Close);
        }
        
        // Convert to numpy arrays
        var np = PyImport.ImportModule("numpy");
        var X = np.GetAttr("array").Invoke(features.ToArray());
        var y = np.GetAttr("array").Invoke(labels.ToArray());
        
        // Scale features
        X = _scaler.GetAttr("fit_transform").Invoke(X);
        
        // Train model
        _model.GetAttr("fit").Invoke(X, y);
    }
    
    public override void OnData(Slice data)
    {
        if (!data.ContainsKey(_symbol) || _model == null)
            return;
        
        // Get historical data
        var history = History(_symbol, _lookback, Resolution.Daily);
        if (history.Count() < _lookback)
            return;
        
        // Prepare features
        var features = new List<double>();
        foreach (var bar in history)
        {
            features.Add((double)bar.Close);
        }
        
        // Convert to numpy array
        var np = PyImport.ImportModule("numpy");
        var X = np.GetAttr("array").Invoke(new[] { features.ToArray() });
        
        // Scale features
        X = _scaler.GetAttr("transform").Invoke(X);
        
        // Make prediction
        var prediction = _model.GetAttr("predict").Invoke(X);
        var predictedPrice = (decimal)prediction.GetItem(0).As<double>();
        
        // Current price
        var currentPrice = data[_symbol].Close;
        
        // Trading logic
        if (predictedPrice > currentPrice * 1.02m)
        {
            if (!Portfolio.Invested)
            {
                SetHoldings(_symbol, 1.0);
                Debug("Bought SPY at " + Time.ToShortDateString() + " with predicted price " + predictedPrice);
            }
        }
        else if (predictedPrice < currentPrice * 0.98m)
        {
            if (Portfolio.Invested)
            {
                Liquidate(_symbol);
                Debug("Sold SPY at " + Time.ToShortDateString() + " with predicted price " + predictedPrice);
            }
        }
    }
}
```

### 3. Options Strategy

The Options Strategy trades options based on volatility and price movements of the underlying asset.

```csharp
public class OptionsStrategy : QCAlgorithm
{
    private Symbol _underlying;
    private Symbol _optionSymbol;
    private decimal _strikePrice;
    private DateTime _expiry;
    
    public override void Initialize()
    {
        SetStartDate(2018, 1, 1);
        SetEndDate(2018, 12, 31);
        SetCash(100000);
        
        // Add underlying asset
        _underlying = AddEquity("SPY", Resolution.Minute).Symbol;
        
        // Add option chain
        var option = AddOption("SPY", Resolution.Minute);
        option.SetFilter(universe => universe.Strikes(-2, 2).Expiration(0, 30));
        
        // Set up indicators
        var volatility = new StandardDeviation(_underlying, 20, Resolution.Daily);
        
        // Schedule option selection
        Schedule.On(DateRules.EveryDay(), TimeRules.AfterMarketOpen(), SelectOption);
    }
    
    public void SelectOption()
    {
        // Get option chain
        var chain = OptionChainProvider.GetOptionContractList(_underlying, Time);
        if (chain.Count == 0)
            return;
        
        // Get ATM options expiring in about 30 days
        var atmOptions = chain
            .Where(x => x.ID.OptionRight == OptionRight.Call)
            .OrderBy(x => Math.Abs(Securities[_underlying].Price - x.ID.StrikePrice))
            .ThenBy(x => (x.ID.Date - Time).TotalDays)
            .Where(x => (x.ID.Date - Time).TotalDays > 25 && (x.ID.Date - Time).TotalDays < 35)
            .Take(1)
            .ToList();
        
        if (atmOptions.Count == 0)
            return;
        
        // Select option
        var option = atmOptions.First();
        _optionSymbol = option.Symbol;
        _strikePrice = option.ID.StrikePrice;
        _expiry = option.ID.Date;
        
        // Add option to portfolio
        AddOptionContract(_optionSymbol);
    }
    
    public override void OnData(Slice data)
    {
        if (_optionSymbol == null || !data.ContainsKey(_optionSymbol))
            return;
        
        // Get option data
        var option = data[_optionSymbol];
        
        // Trading logic
        if (!Portfolio.Invested)
        {
            // Buy call option when underlying is trending up
            var history = History(_underlying, 20, Resolution.Daily);
            if (history.Count() < 20)
                return;
            
            var prices = history.Select(x => x.Close).ToList();
            var sma5 = prices.TakeLast(5).Average();
            var sma20 = prices.Average();
            
            if (sma5 > sma20)
            {
                Buy(_optionSymbol, 1);
                Debug("Bought SPY call option at " + Time.ToShortDateString() + " with strike " + _strikePrice + " expiring on " + _expiry.ToShortDateString());
            }
        }
        else
        {
            // Sell option if it's profitable or close to expiry
            var position = Portfolio[_optionSymbol];
            var daysToExpiry = (_expiry - Time).TotalDays;
            
            if (position.UnrealizedProfitPercent > 0.2m || daysToExpiry < 5)
            {
                Liquidate(_optionSymbol);
                Debug("Sold SPY call option at " + Time.ToShortDateString() + " with profit " + position.UnrealizedProfitPercent);
            }
        }
    }
}
```

## Custom Data Integration

Custom data integration examples demonstrate how to incorporate external data sources into Lean algorithms.

### 1. CSV Data Integration

The CSV Data Integration example shows how to import and use data from CSV files.

```csharp
public class MyCustomData : BaseData
{
    public decimal Value { get; set; }
    
    public override DateTime EndTime => Time;
    
    public override SubscriptionDataSource GetSource(SubscriptionDataConfig config, DateTime date, bool isLiveMode)
    {
        return new SubscriptionDataSource(
            Path.Combine("CustomData", "MyCustomData", date.ToString("yyyyMMdd") + ".csv"),
            SubscriptionTransportMedium.LocalFile
        );
    }
    
    public override BaseData Reader(SubscriptionDataConfig config, string line, DateTime date, bool isLiveMode)
    {
        var csv = line.Split(',');
        return new MyCustomData
        {
            Symbol = config.Symbol,
            Time = DateTime.Parse(csv[0]),
            Value = decimal.Parse(csv[1])
        };
    }
}

public class CsvDataAlgorithm : QCAlgorithm
{
    private Symbol _customDataSymbol;
    private Symbol _equitySymbol;
    
    public override void Initialize()
    {
        SetStartDate(2018, 1, 1);
        SetEndDate(2018, 12, 31);
        SetCash(100000);
        
        _equitySymbol = AddEquity("SPY", Resolution.Daily).Symbol;
        _customDataSymbol = AddData<MyCustomData>("CUSTOM", Resolution.Daily).Symbol;
    }
    
    public override void OnData(Slice data)
    {
        if (!data.ContainsKey(_customDataSymbol) || !data.ContainsKey(_equitySymbol))
            return;
        
        var customData = data[_customDataSymbol];
        var equity = data[_equitySymbol];
        
        if (customData.Value > 0 && !Portfolio.Invested)
        {
            SetHoldings(_equitySymbol, 1.0);
            Debug("Bought SPY at " + Time.ToShortDateString() + " with custom data value " + customData.Value);
        }
        else if (customData.Value < 0 && Portfolio.Invested)
        {
            Liquidate(_equitySymbol);
            Debug("Sold SPY at " + Time.ToShortDateString() + " with custom data value " + customData.Value);
        }
    }
}
```

[Learn more about Custom Data Integration](./custom-data.md)

### 2. API Data Integration

The API Data Integration example shows how to import and use data from external APIs.

```csharp
public class ApiData : BaseData
{
    public decimal Value { get; set; }
    
    public override DateTime EndTime => Time;
    
    public override SubscriptionDataSource GetSource(SubscriptionDataConfig config, DateTime date, bool isLiveMode)
    {
        if (isLiveMode)
        {
            return new SubscriptionDataSource(
                "https://api.example.com/data?date=" + date.ToString("yyyyMMdd"),
                SubscriptionTransportMedium.Rest
            );
        }
        else
        {
            return new SubscriptionDataSource(
                Path.Combine("CustomData", "ApiData", date.ToString("yyyyMMdd") + ".json"),
                SubscriptionTransportMedium.LocalFile
            );
        }
    }
    
    public override BaseData Reader(SubscriptionDataConfig config, string line, DateTime date, bool isLiveMode)
    {
        var jObject = JObject.Parse(line);
        return new ApiData
        {
            Symbol = config.Symbol,
            Time = DateTime.Parse(jObject["time"].ToString()),
            Value = decimal.Parse(jObject["value"].ToString())
        };
    }
}

public class ApiDataAlgorithm : QCAlgorithm
{
    private Symbol _apiDataSymbol;
    private Symbol _equitySymbol;
    
    public override void Initialize()
    {
        SetStartDate(2018, 1, 1);
        SetEndDate(2018, 12, 31);
        SetCash(100000);
        
        _equitySymbol = AddEquity("SPY", Resolution.Daily).Symbol;
        _apiDataSymbol = AddData<ApiData>("API", Resolution.Daily).Symbol;
    }
    
    public override void OnData(Slice data)
    {
        if (!data.ContainsKey(_apiDataSymbol) || !data.ContainsKey(_equitySymbol))
            return;
        
        var apiData = data[_apiDataSymbol];
        var equity = data[_equitySymbol];
        
        if (apiData.Value > 0 && !Portfolio.Invested)
        {
            SetHoldings(_equitySymbol, 1.0);
            Debug("Bought SPY at " + Time.ToShortDateString() + " with API data value " + apiData.Value);
        }
        else if (apiData.Value < 0 && Portfolio.Invested)
        {
            Liquidate(_equitySymbol);
            Debug("Sold SPY at " + Time.ToShortDateString() + " with API data value " + apiData.Value);
        }
    }
}
```

### 3. Alternative Data Integration

The Alternative Data Integration example shows how to incorporate alternative data sources such as news sentiment or social media data.

```csharp
public class SentimentData : BaseData
{
    public decimal Sentiment { get; set; }
    
    public override DateTime EndTime => Time;
    
    public override SubscriptionDataSource GetSource(SubscriptionDataConfig config, DateTime date, bool isLiveMode)
    {
        return new SubscriptionDataSource(
            Path.Combine("CustomData", "Sentiment", date.ToString("yyyyMMdd") + ".csv"),
            SubscriptionTransportMedium.LocalFile
        );
    }
    
    public override BaseData Reader(SubscriptionDataConfig config, string line, DateTime date, bool isLiveMode)
    {
        var csv = line.Split(',');
        return new SentimentData
        {
            Symbol = config.Symbol,
            Time = DateTime.Parse(csv[0]),
            Sentiment = decimal.Parse(csv[1])
        };
    }
}

public class SentimentAlgorithm : QCAlgorithm
{
    private Symbol _sentimentSymbol;
    private Symbol _equitySymbol;
    
    public override void Initialize()
    {
        SetStartDate(2018, 1, 1);
        SetEndDate(2018, 12, 31);
        SetCash(100000);
        
        _equitySymbol = AddEquity("SPY", Resolution.Daily).Symbol;
        _sentimentSymbol = AddData<SentimentData>("SENTIMENT", Resolution.Daily).Symbol;
    }
    
    public override void OnData(Slice data)
    {
        if (!data.ContainsKey(_sentimentSymbol) || !data.ContainsKey(_equitySymbol))
            return;
        
        var sentiment = data[_sentimentSymbol];
        var equity = data[_equitySymbol];
        
        if (sentiment.Sentiment > 0.5m && !Portfolio.Invested)
        {
            SetHoldings(_equitySymbol, 1.0);
            Debug("Bought SPY at " + Time.ToShortDateString() + " with sentiment " + sentiment.Sentiment);
        }
        else if (sentiment.Sentiment < -0.5m && Portfolio.Invested)
        {
            Liquidate(_equitySymbol);
            Debug("Sold SPY at " + Time.ToShortDateString() + " with sentiment " + sentiment.Sentiment);
        }
    }
}
```

## Next Steps

For detailed information about each type of implementation example, refer to the individual documentation:

- [Basic Strategies](./basic-strategies.md)
- [Advanced Strategies](./advanced-strategies.md)
- [Custom Data Integration](./custom-data.md)