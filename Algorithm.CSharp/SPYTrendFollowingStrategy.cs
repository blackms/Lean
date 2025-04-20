/*
 * QUANTCONNECT.COM - Democratizing Finance, Empowering Individuals.
 * Lean Algorithmic Trading Engine v2.0. Copyright 2014 QuantConnect Corporation.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
*/

using System;
using System.Collections.Generic;
using System.Linq;
using QuantConnect.Data;
using QuantConnect.Data.Market;
using QuantConnect.Indicators;
using QuantConnect.Orders;
using QuantConnect.Securities;
using QuantConnect.Algorithm;
using QuantConnect.Algorithm.Framework.Alphas;

namespace QuantConnect.Algorithm.CSharp
{
    /// <summary>
    /// SPY Trend Following Strategy based on dual EMA crossover with ADX filter and confirmation indicators.
    /// 
    /// Strategy Components:
    /// 1. Primary Signal: 50-day EMA crosses above/below 200-day EMA
    /// 2. Trend Strength Filter: ADX > 20 for confirmed trends
    /// 3. Confirmation Indicators: MACD and RSI
    /// 4. Risk Management: ATR-based stops, volatility filters, drawdown controls
    /// 5. Position Sizing: Based on trend strength (ADX value)
    /// </summary>
    public class SPYTrendFollowingStrategy : QCAlgorithm
    {
        private Symbol _spySymbol;
        private Symbol _vixSymbol;
        
        // Primary trend indicators
        private ExponentialMovingAverage _fastEma;
        private ExponentialMovingAverage _slowEma;
        private AverageDirectionalIndex _adx;
        
        // Confirmation indicators
        private MovingAverageConvergenceDivergence _macd;
        private RelativeStrengthIndex _rsi;
        
        // Risk management indicators
        private AverageTrueRange _atr;
        private RollingWindow<decimal> _atr90;
        
        // Price tracking
        private decimal _highSinceEntry;
        private decimal _entryPrice;
        private int _daysSinceEntry;
        private int _daysSinceNewHigh;
        private RollingWindow<decimal> _highestPrice20d;
        
        // Strategy state variables
        private bool _isInvested;
        private decimal _positionSize;
        private decimal _initialStopPrice;
        private decimal _trailingStopPrice;
        private DateTime _entryTime;
        private decimal _strategyDrawdown;
        private decimal _peakValue;
        private bool _scaledIn;
        
        /// <summary>
        /// Initialize algorithm and set required parameters
        /// </summary>
        public override void Initialize()
        {
            // Set start date, end date, and cash
            SetStartDate(2010, 1, 1);  // Set start date for backtest
            SetEndDate(2023, 12, 31);  // Set end date for backtest
            SetCash(100000);           // Set strategy cash
            
            // Set benchmark to SPY
            SetBenchmark("SPY");
            
            // Set brokerage model
            SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Margin);
            
            // Set warm-up period to ensure indicators are ready
            SetWarmUp(200);
            
            // Add SPY with daily resolution for primary signals
            var spy = AddEquity("SPY", Resolution.Daily);
            _spySymbol = spy.Symbol;
            
            // Add VIX for volatility filter
            var vix = AddIndex("VIX", Resolution.Daily);
            _vixSymbol = vix.Symbol;
            
            // Initialize indicators
            // Primary trend indicators
            _fastEma = EMA(_spySymbol, 50, Resolution.Daily);
            _slowEma = EMA(_spySymbol, 200, Resolution.Daily);
            _adx = ADX(_spySymbol, 14, Resolution.Daily);
            
            // Confirmation indicators
            _macd = MACD(_spySymbol, 12, 26, 9, MovingAverageType.Exponential, Resolution.Daily);
            _rsi = RSI(_spySymbol, 14, MovingAverageType.Simple, Resolution.Daily);
            
            // Risk management indicators
            _atr = ATR(_spySymbol, 14, MovingAverageType.Simple, Resolution.Daily);
            _atr90 = new RollingWindow<decimal>(90);  // 90-day ATR window for volatility comparison
            
            // Price tracking
            _highSinceEntry = 0;
            _entryPrice = 0;
            _daysSinceEntry = 0;
            _daysSinceNewHigh = 0;
            _highestPrice20d = new RollingWindow<decimal>(20);  // Track 20-day highs for scaling
            
            // Strategy state variables
            _isInvested = false;
            _positionSize = 0;
            _initialStopPrice = 0;
            _trailingStopPrice = 0;
            _entryTime = DateTime.MinValue;
            _strategyDrawdown = 0;
            _peakValue = 0;
            _scaledIn = false;
            
            // Schedule daily update for risk management and position monitoring
            Schedule.On(DateRules.EveryDay(_spySymbol), 
                        TimeRules.BeforeMarketClose(_spySymbol, 10), 
                        DailyUpdate);
            
            // Initialize charts
            InitializeCharts();
            
            // Log initialization
            Log($"SPY Trend Following Strategy initialized with {Portfolio.Cash} starting capital");
        }
        
        /// <summary>
        /// Initialize charts for strategy visualization
        /// </summary>
        private void InitializeCharts()
        {
            // Create indicator chart
            var indicators = new Chart("Indicators");
            indicators.AddSeries(new Series("FastEMA", SeriesType.Line, 0));
            indicators.AddSeries(new Series("SlowEMA", SeriesType.Line, 0));
            indicators.AddSeries(new Series("ADX", SeriesType.Line, 1));
            indicators.AddSeries(new Series("RSI", SeriesType.Line, 2));
            AddChart(indicators);
            
            // Create risk management chart
            var risk = new Chart("Risk Management");
            risk.AddSeries(new Series("ATR", SeriesType.Line, 0));
            risk.AddSeries(new Series("ATR_90_Avg", SeriesType.Line, 0));
            risk.AddSeries(new Series("StopPrice", SeriesType.Line, 1));
            risk.AddSeries(new Series("VIX", SeriesType.Line, 2));
            AddChart(risk);
            
            // Create strategy state chart
            var state = new Chart("Strategy State");
            state.AddSeries(new Series("PositionSize", SeriesType.Line, 0));
            state.AddSeries(new Series("DrawdownPct", SeriesType.Line, 1));
            AddChart(state);
        }
        
        /// <summary>
        /// Main event handler for market data updates
        /// </summary>
        public override void OnData(Slice data)
        {
            // Skip processing during warm-up
            if (IsWarmingUp)
            {
                return;
            }
            
            // Check if we have data for SPY and VIX
            if (!data.ContainsKey(_spySymbol) || !data.ContainsKey(_vixSymbol))
            {
                return;
            }
            
            // Update rolling windows
            if (_atr.IsReady)
            {
                _atr90.Add(_atr.Current.Value);
            }
            
            // Update highest price tracking
            decimal currentPrice = Securities[_spySymbol].Close;
            _highestPrice20d.Add(currentPrice);
            
            // Update strategy state charts
            Plot("Indicators", "FastEMA", _fastEma.Current.Value);
            Plot("Indicators", "SlowEMA", _slowEma.Current.Value);
            Plot("Indicators", "ADX", _adx.Current.Value);
            Plot("Indicators", "RSI", _rsi.Current.Value);
            
            Plot("Risk Management", "ATR", _atr.Current.Value);
            Plot("Risk Management", "VIX", Securities[_vixSymbol].Close);
            
            if (_atr90.IsReady)
            {
                decimal atr90Avg = _atr90.Sum() / _atr90.Count;
                Plot("Risk Management", "ATR_90_Avg", atr90Avg);
            }
            
            // Update drawdown tracking
            decimal currentValue = Portfolio.TotalPortfolioValue;
            if (currentValue > _peakValue)
            {
                _peakValue = currentValue;
            }
            
            if (_peakValue > 0)
            {
                _strategyDrawdown = (_peakValue - currentValue) / _peakValue;
                Plot("Strategy State", "DrawdownPct", _strategyDrawdown * 100);
            }
            
            // Check if all indicators are ready
            if (!_fastEma.IsReady || !_slowEma.IsReady || !_adx.IsReady || !_macd.IsReady || !_rsi.IsReady || !_atr.IsReady)
            {
                return;
            }
            
            // Check for entry conditions if not invested
            if (!_isInvested)
            {
                CheckEntrySignals(data);
            }
            // Check for exit conditions if invested
            else
            {
                CheckExitSignals(data);
                UpdateStopLevels(data);
                CheckScalingOpportunity(data);
            }
        }
        
        /// <summary>
        /// Check for entry signals based on strategy rules
        /// </summary>
        private void CheckEntrySignals(Slice data)
        {
            // Skip if we're in a significant drawdown
            if (_strategyDrawdown > 0.15m)
            {
                Log("Strategy in significant drawdown (>15%). Skipping new entries.");
                return;
            }
            
            // Get current indicator values
            decimal fastEma = _fastEma.Current.Value;
            decimal slowEma = _slowEma.Current.Value;
            decimal adxValue = _adx.Current.Value;
            decimal macdValue = _macd.Current.Value;
            decimal macdSignal = _macd.Signal.Current.Value;
            decimal rsiValue = _rsi.Current.Value;
            decimal vixValue = Securities[_vixSymbol].Close;
            
            // Primary signal: EMA crossover
            bool emaCrossover = fastEma > slowEma && _fastEma.Current.Value > _fastEma.Previous.Value;
            
            // Trend strength filter
            bool strongTrend = adxValue > 20;
            
            // Confirmation signals
            bool macdConfirmation = macdValue > macdSignal;
            bool rsiConfirmation = rsiValue > 50;
            
            // Check for entry signal
            if (emaCrossover && strongTrend)
            {
                Log($"Entry signal detected: EMA Crossover with ADX = {adxValue:F2}");
                
                // Additional confirmation (optional)
                if (macdConfirmation && rsiConfirmation)
                {
                    Log("Confirmation indicators are positive: MACD and RSI confirm trend");
                }
                
                // Determine position size based on trend strength and volatility
                decimal positionSize = CalculatePositionSize(adxValue, vixValue);
                
                // Execute entry
                ExecuteEntry(positionSize);
            }
        }
        
        /// <summary>
        /// Check for exit signals based on strategy rules
        /// </summary>
        private void CheckExitSignals(Slice data)
        {
            // Get current indicator values
            decimal fastEma = _fastEma.Current.Value;
            decimal slowEma = _slowEma.Current.Value;
            decimal currentPrice = Securities[_spySymbol].Close;
            
            // Update tracking variables
            _daysSinceEntry += 1;
            
            // Check if price made a new high
            if (currentPrice > _highSinceEntry)
            {
                _highSinceEntry = currentPrice;
                _daysSinceNewHigh = 0;
            }
            else
            {
                _daysSinceNewHigh += 1;
            }
            
            // Primary exit signal: EMA crossover (opposite of entry)
            bool emaCrossoverExit = fastEma < slowEma;
            
            // Time-based exit conditions
            bool maxHoldPeriodExit = _daysSinceEntry > 90;
            bool noNewHighExit = _daysSinceNewHigh > 30;
            
            // Check for exit signals
            if (emaCrossoverExit)
            {
                Log("Exit signal: EMA crossover (fast below slow)");
                ExecuteExit();
            }
            else if (maxHoldPeriodExit)
            {
                Log("Exit signal: Maximum hold period exceeded (90 days)");
                ExecuteExit();
            }
            else if (noNewHighExit)
            {
                Log("Warning: No new high in 30 days. Reevaluating position.");
                // Reduce position size by 25% if no new high in 30 days
                if (_positionSize > 0)
                {
                    decimal newPosition = _positionSize * 0.75m;
                    Log($"Reducing position from {_positionSize:F2} to {newPosition:F2} due to lack of momentum");
                    SetHoldings(_spySymbol, newPosition);
                    _positionSize = newPosition;
                }
            }
        }
        
        /// <summary>
        /// Update stop loss levels based on ATR and price movement
        /// </summary>
        private void UpdateStopLevels(Slice data)
        {
            if (!_isInvested)
            {
                return;
            }
            
            decimal currentPrice = Securities[_spySymbol].Close;
            decimal atrValue = _atr.Current.Value;
            
            // Update trailing stop if price moves favorably
            if (currentPrice > _highSinceEntry)
            {
                _highSinceEntry = currentPrice;
                decimal newStop = currentPrice - (3 * atrValue);
                
                // Only move stop up, never down
                if (newStop > _trailingStopPrice)
                {
                    _trailingStopPrice = newStop;
                    Log($"Trailing stop updated to {_trailingStopPrice:F2} (current price: {currentPrice:F2})");
                    Plot("Risk Management", "StopPrice", _trailingStopPrice);
                }
            }
            
            // Check if stop is hit
            if (currentPrice < _trailingStopPrice)
            {
                Log($"Stop loss triggered at {currentPrice:F2} (stop level: {_trailingStopPrice:F2})");
                ExecuteExit();
            }
        }
        
        /// <summary>
        /// Check for scaling opportunity based on new 20-day highs
        /// </summary>
        private void CheckScalingOpportunity(Slice data)
        {
            if (!_isInvested || _scaledIn || _positionSize >= 1.0m)
            {
                return;
            }
            
            decimal currentPrice = Securities[_spySymbol].Close;
            
            // Check if we have enough data
            if (!_highestPrice20d.IsReady)
            {
                return;
            }
            
            // Calculate 20-day high
            decimal high20d = _highestPrice20d.Max();
            
            // Scale in if price makes new 20-day high after entry
            if (currentPrice > high20d && _daysSinceEntry > 5)
            {
                decimal additionalSize = 0.1m;  // Add 10% to position
                decimal newPosition = Math.Min(1.0m, _positionSize + additionalSize);
                
                Log($"Scaling in: Adding {additionalSize:F2} to position (new position size: {newPosition:F2})");
                SetHoldings(_spySymbol, newPosition);
                _positionSize = newPosition;
                _scaledIn = true;
            }
        }
        
        /// <summary>
        /// Calculate position size based on trend strength and volatility
        /// </summary>
        private decimal CalculatePositionSize(decimal adxValue, decimal vixValue)
        {
            // Base position size based on ADX
            decimal basePosition;
            if (adxValue > 25)
            {
                basePosition = 0.8m;  // 80% for strong trends
            }
            else
            {
                basePosition = 0.5m;  // 50% for moderate trends
            }
            
            // Adjust for volatility (VIX)
            if (vixValue > 30)
            {
                basePosition *= 0.5m;  // Reduce by 50% during high volatility
                Log($"High volatility detected (VIX = {vixValue:F2}). Reducing position size.");
            }
            
            // Adjust for ATR volatility
            if (_atr90.IsReady)
            {
                decimal atr90Avg = _atr90.Sum() / _atr90.Count;
                decimal currentAtr = _atr.Current.Value;
                
                if (currentAtr > (2 * atr90Avg))
                {
                    basePosition *= 0.7m;  // Reduce by 30% if ATR is 2x the 90-day average
                    Log($"Elevated ATR detected (current: {currentAtr:F2}, 90d avg: {atr90Avg:F2}). Reducing position size.");
                }
            }
            
            // Adjust for strategy drawdown
            if (_strategyDrawdown > 0.1m)
            {
                basePosition *= 0.5m;  // Reduce by 50% if drawdown exceeds 10%
                Log($"Strategy in drawdown ({_strategyDrawdown:P2}). Reducing position size.");
            }
            
            return basePosition;
        }
        
        /// <summary>
        /// Execute entry with proper order type and position sizing
        /// </summary>
        private void ExecuteEntry(decimal positionSize)
        {
            if (_isInvested)
            {
                return;
            }
            
            decimal currentPrice = Securities[_spySymbol].Close;
            decimal atrValue = _atr.Current.Value;
            
            // Set initial and trailing stops
            _initialStopPrice = currentPrice - (2 * atrValue);
            _trailingStopPrice = _initialStopPrice;
            
            // Set entry tracking variables
            _entryPrice = currentPrice;
            _highSinceEntry = currentPrice;
            _daysSinceEntry = 0;
            _daysSinceNewHigh = 0;
            _entryTime = Time;
            _scaledIn = false;
            
            // Execute the order
            SetHoldings(_spySymbol, positionSize);
            _positionSize = positionSize;
            _isInvested = true;
            
            Log($"Entered SPY position with size {positionSize:F2} at {currentPrice:F2}");
            Log($"Initial stop set at {_initialStopPrice:F2} ({(currentPrice - _initialStopPrice) / currentPrice:P2} below entry)");
            
            Plot("Risk Management", "StopPrice", _initialStopPrice);
            Plot("Strategy State", "PositionSize", positionSize * 100);
        }
        
        /// <summary>
        /// Execute exit with proper order type
        /// </summary>
        private void ExecuteExit()
        {
            if (!_isInvested)
            {
                return;
            }
            
            // Liquidate position
            Liquidate(_spySymbol);
            
            // Reset tracking variables
            _isInvested = false;
            _positionSize = 0;
            _initialStopPrice = 0;
            _trailingStopPrice = 0;
            _entryTime = DateTime.MinValue;
            _scaledIn = false;
            
            Log($"Exited SPY position at {Securities[_spySymbol].Close:F2}");
            Plot("Strategy State", "PositionSize", 0);
            Plot("Risk Management", "StopPrice", 0);
        }
        
        /// <summary>
        /// Daily update for risk management and position monitoring
        /// </summary>
        private void DailyUpdate()
        {
            if (!_isInvested)
            {
                return;
            }
            
            // Log current position status
            int daysHeld = _entryTime != DateTime.MinValue ? (Time - _entryTime).Days : 0;
            decimal currentPrice = Securities[_spySymbol].Close;
            decimal pnlPct = _entryPrice > 0 ? (currentPrice / _entryPrice - 1) * 100 : 0;
            
            Log($"Position update: Holding SPY for {daysHeld} days, P&L: {pnlPct:F2}%, Stop: {_trailingStopPrice:F2}");
            
            // Check for time-based reassessment
            if (_daysSinceNewHigh >= 30)
            {
                Log($"Warning: No new high in {_daysSinceNewHigh} days");
            }
        }
    }
}