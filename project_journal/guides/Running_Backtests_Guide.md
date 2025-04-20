# Guide: Running Backtests in QuantConnect LEAN

This guide explains how to run backtests for the SPY Trend Following Strategy using the QuantConnect LEAN framework.

## Prerequisites

- QuantConnect LEAN framework installed
- Strategy code implemented (SPYTrendFollowingStrategy.cs or SPYTrendFollowingStrategy.py)
- Market data for SPY available in the Data folder

## Running a Backtest for the C# Strategy

### Step 1: Configure the Backtest

Edit the `Launcher/bin/Debug/config.json` file to set up your backtest:

```json
{
  "environment": "backtesting",
  
  // Set the algorithm class name
  "algorithm-type-name": "SPYTrendFollowingStrategy",
  
  // Set the language to C#
  "algorithm-language": "CSharp",
  
  // Set the location of the compiled algorithm
  "algorithm-location": "QuantConnect.Algorithm.CSharp.dll",
  
  // Other settings remain unchanged
  "data-folder": "../../../Data/",
  
  // Optional: Adjust parameters if needed
  "parameters": {
    // You can add strategy-specific parameters here
  }
}
```

### Step 2: Build the Solution

Before running the backtest, make sure the solution is built with the latest changes:

```bash
cd /home/alessio/NeuralTrading/Lean
dotnet build QuantConnect.Lean.sln -p:WarningLevel=0
```

> **IMPORTANT**: You must recompile the solution every time you make changes to C# strategy files. Unlike Python strategies which are interpreted at runtime, C# strategies need to be compiled before they can be executed. Failing to recompile after making changes will result in running the previous version of your strategy.

### Step 3: Run the Backtest

Execute the LEAN engine to run the backtest:

```bash
cd Launcher/bin/Debug
dotnet QuantConnect.Lean.Launcher.dll
```

### Step 4: View Results

After the backtest completes, results will be available in the following locations:

- Console output: Basic performance metrics
- `Launcher/bin/Debug/Results`: Detailed backtest results including:
  - `backtesting.json`: Performance metrics in JSON format
  - `backtesting.html`: HTML report with charts and statistics
  - Log files with detailed execution information

## Running a Backtest for the Python Strategy

### Step 1: Configure the Backtest

Edit the `Launcher/bin/Debug/config.json` file:

```json
{
  "environment": "backtesting",
  
  // Set the algorithm class name
  "algorithm-type-name": "SPYTrendFollowingStrategy",
  
  // Set the language to Python
  "algorithm-language": "Python",
  
  // Set the location of the Python algorithm file
  "algorithm-location": "../../../Algorithm.Python/SPYTrendFollowingStrategy.py",
  
  // Other settings remain unchanged
  "data-folder": "../../../Data/",
  
  // Optional: Adjust parameters if needed
  "parameters": {
    // You can add strategy-specific parameters here
  }
}
```

### Step 2: Run the Backtest

Execute the LEAN engine to run the backtest:

```bash
cd Launcher/bin/Debug
dotnet QuantConnect.Lean.Launcher.dll
```

## Analyzing Backtest Results

The backtest results provide several key metrics to evaluate the strategy's performance:

1. **Total Return**: Overall percentage return of the strategy
2. **Annual Return**: Annualized return percentage
3. **Sharpe Ratio**: Risk-adjusted return metric
4. **Drawdown**: Maximum peak-to-trough decline
5. **Win Rate**: Percentage of profitable trades
6. **Profit Factor**: Ratio of gross profits to gross losses

## Modifying Backtest Parameters

To test different parameters or time periods:

1. Edit the strategy code directly to modify indicator parameters, risk management rules, etc.
2. Or use the `parameters` section in `config.json` to pass parameters to the algorithm:

```json
"parameters": {
  "fast-ema": 40,
  "slow-ema": 160,
  "adx-threshold": 15
}
```

Then access these parameters in your algorithm using:

```csharp
// In C#
var fastEma = GetParameter("fast-ema", 50);
var slowEma = GetParameter("slow-ema", 200);
var adxThreshold = GetParameter("adx-threshold", 20);
```

```python
# In Python
self.fast_ema_period = self.GetParameter("fast-ema", 50)
self.slow_ema_period = self.GetParameter("slow-ema", 200)
self.adx_threshold = self.GetParameter("adx-threshold", 20)
```

## Troubleshooting

If you encounter issues running the backtest:

1. **Missing Data**: Ensure you have SPY data in the Data folder
2. **Compilation Errors**:
   - Check the build output for any errors
   - Make sure you've recompiled the solution after making changes to C# files
   - Try using the `-p:WarningLevel=0` flag to suppress warnings: `dotnet build QuantConnect.Lean.sln -p:WarningLevel=0`
   - If you get reference errors, ensure all required packages are installed
3. **Changes Not Reflected**:
   - For C# strategies, verify you've recompiled the solution after making changes
   - Check that the correct algorithm name is specified in the config.json file
4. **Runtime Errors**: Check the log files in the Results folder and the console output
5. **Performance Issues**: Consider reducing the backtest period or data resolution
6. **Data Availability Issues**:
   - If your strategy requires specific data (like VIX) that isn't available, modify your code to handle missing data gracefully
   - Check the log files for warnings about missing data

## Next Steps

After running the initial backtest:

1. Analyze the performance metrics and charts
2. Adjust strategy parameters to optimize performance
3. Test the strategy over different market conditions
4. Implement any Phase 2 enhancements from the strategy specification

## Handling Data Availability Issues

When developing strategies that rely on multiple data sources, it's important to handle cases where some data might be unavailable:

### Detecting Missing Data

Add checks in your algorithm to detect when required data is missing:

```csharp
// C# example
if (!data.ContainsKey(_spySymbol))
{
    Log($"ERROR: SPY data missing at {Time}. Cannot proceed without price data.");
    return;
}

// For optional data like VIX
bool hasVixData = data.ContainsKey(_vixSymbol);
if (!hasVixData)
{
    Log("VIX data is missing. Using default volatility assumptions.");
}
```

```python
# Python example
if self.spy not in data:
    self.Log(f"ERROR: SPY data missing at {self.Time}. Cannot proceed without price data.")
    return

# For optional data like VIX
has_vix_data = self.vix in data
if not has_vix_data:
    self.Log("VIX data is missing. Using default volatility assumptions.")
```

### Graceful Fallbacks

Implement fallback mechanisms for missing data:

1. **Default Values**: Use reasonable default values when specific data is unavailable
   ```csharp
   decimal vixValue = 20m; // Default moderate volatility value
   if (Securities.ContainsKey(_vixSymbol))
   {
       vixValue = Securities[_vixSymbol].Close;
   }
   ```

2. **Alternative Indicators**: Calculate alternative metrics when preferred ones are unavailable
   ```csharp
   // If VIX is unavailable, use ATR as a volatility proxy
   if (!hasVixData && _atr.IsReady)
   {
       decimal atrVolatility = _atr.Current.Value / Securities[_spySymbol].Close;
       // Use atrVolatility for risk management decisions
   }
   ```

3. **Conditional Logic**: Adjust strategy behavior based on available data
   ```csharp
   // Only apply volatility filter if VIX data is available
   if (hasVixData && vixValue > 30)
   {
       // Reduce position size during high volatility
       positionSize *= 0.5m;
   }
   ```

### Logging and Monitoring

Add comprehensive logging to track data availability issues:

```csharp
// Log data availability periodically (e.g., once a month)
if (Time.Day == 1)
{
    bool hasSpy = data.ContainsKey(_spySymbol);
    bool hasVix = data.ContainsKey(_vixSymbol);
    Log($"DEBUG [{Time}] - Data availability: SPY={hasSpy}, VIX={hasVix}");
    
    if (!hasSpy || !hasVix)
    {
        Log($"WARNING: Missing data - SPY={hasSpy}, VIX={hasVix}");
    }
}
```

By implementing these practices, your strategies will be more robust and can continue to operate effectively even when some data sources are unavailable.