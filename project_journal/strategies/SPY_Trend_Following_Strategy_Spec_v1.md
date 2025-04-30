# SPY Trend Following Strategy Specification

## Strategy Overview

This document specifies a comprehensive trend following strategy for trading SPY (SPDR S&P 500 ETF Trust). The strategy uses multiple technical indicators to identify and follow market trends while incorporating robust risk management rules.

## 1. Strategy Objective

To capture medium to long-term trends in SPY while managing drawdowns through systematic entry and exit rules.

## 2. Universe Selection

- **Asset**: SPY (SPDR S&P 500 ETF Trust)
- **Market**: US Equity Market
- **Rationale**: SPY offers high liquidity, tight spreads, and tracks the broad US market, making it ideal for trend following strategies.

## 3. Data Requirements

- **Resolution**: Daily data for primary signals, hourly data for entry/exit refinement
- **History Required**: Minimum 1 year of historical data for indicator calculation and warmup
- **Adjustments**: Price data should be adjusted for dividends and splits

## 4. Alpha Model (Signal Generation)

### Primary Trend Indicators

1. **Dual Moving Average Crossover System**
   - Fast MA: 50-day Exponential Moving Average (EMA)
   - Slow MA: 200-day Exponential Moving Average (EMA)
   - Long Signal: Fast MA crosses above Slow MA
   - Short/Exit Signal: Fast MA crosses below Slow MA

2. **ADX (Average Directional Index) Filter**
   - Period: 14 days
   - Trend Strength Threshold: ADX > 20 indicates a strong trend
   - Only take signals when ADX confirms trend strength

### Confirmation Indicators

1. **MACD (Moving Average Convergence Divergence)**
   - Fast EMA: 12-day
   - Slow EMA: 26-day
   - Signal Line: 9-day EMA of MACD
   - Confirmation: MACD line crosses above Signal line for long, below for short

2. **RSI (Relative Strength Index) Trend Alignment**
   - Period: 14 days
   - Bullish Alignment: RSI > 50 for uptrends
   - Bearish Alignment: RSI < 50 for downtrends

### Signal Logic

1. **Entry Conditions (Long)**
   - Primary: 50-day EMA crosses above 200-day EMA
   - Confirmation: ADX > 20
   - Additional Confirmation (optional): MACD crosses above signal line AND RSI > 50

2. **Exit Conditions (Long)**
   - Primary: 50-day EMA crosses below 200-day EMA
   - OR Trailing stop hit (see Risk Management)
   - OR Time-based exit (see Risk Management)

3. **Signal Duration**
   - Base Duration: 30 calendar days
   - Extension: Reset duration when trend strengthens (ADX increases by 5 points)

## 5. Portfolio Construction

1. **Position Sizing**
   - Base Position: 80% of equity for confirmed strong trends (ADX > 25)
   - Reduced Position: 50% of equity for moderate trends (ADX between 20-25)
   - No Position: When no trend is confirmed or during high volatility periods

2. **Scaling Rules**
   - Scale in: Add 10% to position when price makes new 20-day high after entry
   - Maximum Position: 100% of equity

## 6. Risk Management

1. **Stop Loss Mechanisms**
   - Initial Stop: 2 ATR (Average True Range, 14-period) below entry price for long positions
   - Trailing Stop: 3 ATR below current price, updated only when price moves in favorable direction

2. **Volatility Filters**
   - VIX Threshold: Reduce position by 50% when VIX > 30
   - ATR Filter: Reduce position by 30% when current ATR > 2x 90-day average ATR

3. **Maximum Drawdown Controls**
   - Strategy Pause: Pause new entries if strategy drawdown exceeds 15%
   - Position Reduction: Reduce position by 50% if drawdown exceeds 10%

4. **Time-Based Risk Management**
   - Maximum Hold Period: 90 calendar days without new high
   - Reassessment Period: Reevaluate position if no new 20-day high after 30 days

## 7. Execution Model

1. **Entry Execution**
   - Order Type: Limit order at previous day's closing price + 0.1%
   - Entry Window: Order valid for one trading day
   - Alternative Entry: Market order at next open if limit not filled and signal remains valid

2. **Exit Execution**
   - Stop Loss: Market order when stop level breached
   - Trend Reversal Exit: Limit order at previous day's closing price - 0.1%
   - End of Day: All exit orders should be placed with "valid till cancel" instruction

## 8. Performance Expectations

1. **Expected Metrics**
   - Win Rate: 40-45%
   - Profit Factor: >1.5
   - Maximum Drawdown: <20%
   - Annual Return Target: 8-12% above risk-free rate
   - Sharpe Ratio Target: >0.8

2. **Benchmark**
   - Primary: SPY buy and hold
   - Secondary: SMA(200) trend following strategy

## 9. Implementation Notes for Quant Developer

1. **LEAN Framework Implementation**
   - Use the Algorithm Framework approach with custom Alpha Model
   - Implement as EmaCrossAlphaModel with customizations for ADX and confirmation indicators
   - Use StandardDeviationExecutionModel for entries and exits
   - Implement custom RiskManagementModel for the specified stop loss and volatility rules

2. **Indicator Initialization**
   ```csharp
   // Example indicator initialization
   _fastEma = EMA("SPY", 50, Resolution.Daily);
   _slowEma = EMA("SPY", 200, Resolution.Daily);
   _adx = ADX("SPY", 14, Resolution.Daily);
   _macd = MACD("SPY", 12, 26, 9, Resolution.Daily);
   _rsi = RSI("SPY", 14, Resolution.Daily);
   _atr = ATR("SPY", 14, Resolution.Daily);
   ```

3. **Warmup Period**
   - Set algorithm warmup period to 200 days to ensure all indicators are properly initialized
   - Validate indicator readiness before generating signals

4. **Custom Alpha Model Structure**
   ```csharp
   public class CustomTrendFollowingAlphaModel : AlphaModel
   {
       private readonly Dictionary<Symbol, SymbolData> _symbolData;
       
       // Initialize indicators and parameters
       
       public override IEnumerable<Insight> Update(QCAlgorithm algorithm, Slice data)
       {
           // Implement signal logic as specified
           // Generate insights with appropriate direction, magnitude and period
       }
       
       // Implement helper methods for trend detection, confirmation, etc.
   }
   ```

5. **Logging and Debugging**
   - Log all signal generations with relevant indicator values
   - Log position changes and risk management actions
   - Create custom charts for key indicators and signal points

## 10. Testing and Validation

1. **Backtest Periods**
   - Primary: 2010-2023 (full market cycle including bull and bear markets)
   - Stress Test: 2008-2009 (financial crisis)
   - Recent: 2020-2023 (COVID crash and recovery)

2. **Parameter Sensitivity**
   - Test MA periods: 40/160, 50/200, 60/240
   - Test ADX thresholds: 15, 20, 25
   - Test ATR multipliers: 2, 3, 4

3. **Walk-Forward Analysis**
   - Perform walk-forward optimization to verify robustness
   - Use 3-year training, 1-year testing windows

## 11. Future Enhancements (Phase 2)

1. **Market Regime Detection**
   - Implement market regime detection based on volatility and trend metrics
   - Adjust strategy parameters based on identified regime

2. **Adaptive Parameters**
   - Dynamically adjust MA periods based on recent volatility
   - Adapt position sizing based on trend strength and market conditions

3. **Multi-Timeframe Analysis**
   - Add weekly timeframe confirmation for stronger signals
   - Incorporate monthly trend for strategic positioning