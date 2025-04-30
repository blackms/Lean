# QUANTCONNECT.COM - Democratizing Finance, Empowering Individuals.
# Lean Algorithmic Trading Engine v2.0. Copyright 2014 QuantConnect Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from AlgorithmImports import *
from datetime import timedelta
import numpy as np

class SPYTrendFollowingStrategy(QCAlgorithm):
    '''
    SPY Trend Following Strategy based on dual EMA crossover with ADX filter and confirmation indicators.
    
    Strategy Components:
    1. Primary Signal: 50-day EMA crosses above/below 200-day EMA
    2. Trend Strength Filter: ADX > 20 for confirmed trends
    3. Confirmation Indicators: MACD and RSI
    4. Risk Management: ATR-based stops, volatility filters, drawdown controls
    5. Position Sizing: Based on trend strength (ADX value)
    '''
    
    def Initialize(self):
        '''Initialize algorithm and set required parameters'''
        
        # Set start date, end date, and cash
        self.SetStartDate(2010, 1, 1)  # Set start date for backtest
        self.SetEndDate(2023, 12, 31)  # Set end date for backtest
        self.SetCash(100000)           # Set strategy cash
        
        # Set benchmark to SPY
        self.SetBenchmark("SPY")
        
        # Set brokerage model
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Margin)
        
        # Set warm-up period to ensure indicators are ready
        self.SetWarmUp(200)
        
        # Add SPY with daily resolution for primary signals
        self.spy = self.AddEquity("SPY", Resolution.Daily)
        self.spy_symbol = self.spy.Symbol
        
        # Add VIX for volatility filter
        self.vix = self.AddIndex("VIX", Resolution.Daily)
        self.vix_symbol = self.vix.Symbol
        
        # Initialize indicators
        # Primary trend indicators
        self.fast_ema = self.EMA(self.spy_symbol, 50, Resolution.Daily)
        self.slow_ema = self.EMA(self.spy_symbol, 200, Resolution.Daily)
        self.adx = self.ADX(self.spy_symbol, 14, Resolution.Daily)
        
        # Confirmation indicators
        self.macd = self.MACD(self.spy_symbol, 12, 26, 9, MovingAverageType.Exponential, Resolution.Daily)
        self.rsi = self.RSI(self.spy_symbol, 14, MovingAverageType.Simple, Resolution.Daily)
        
        # Risk management indicators
        self.atr = self.ATR(self.spy_symbol, 14, MovingAverageType.Simple, Resolution.Daily)
        self.atr_90 = RollingWindow[float](90)  # 90-day ATR window for volatility comparison
        
        # Price tracking
        self.high_since_entry = 0
        self.entry_price = 0
        self.days_since_entry = 0
        self.days_since_new_high = 0
        self.highest_price_20d = RollingWindow[float](20)  # Track 20-day highs for scaling
        
        # Strategy state variables
        self.is_invested = False
        self.position_size = 0
        self.initial_stop_price = 0
        self.trailing_stop_price = 0
        self.entry_time = None
        self.strategy_drawdown = 0
        self.peak_value = 0
        self.scaled_in = False
        
        # Schedule daily update for risk management and position monitoring
        self.Schedule.On(self.DateRules.EveryDay(self.spy_symbol), 
                         self.TimeRules.BeforeMarketClose(self.spy_symbol, 10), 
                         self.DailyUpdate)
        
        # Initialize charts
        self.InitializeCharts()
        
        # Log initialization
        self.Log(f"SPY Trend Following Strategy initialized with {self.Portfolio.Cash} starting capital")

    def InitializeCharts(self):
        '''Initialize charts for strategy visualization'''
        
        # Create indicator chart
        indicators = Chart("Indicators")
        indicators.AddSeries(Series("FastEMA", SeriesType.Line, 0))
        indicators.AddSeries(Series("SlowEMA", SeriesType.Line, 0))
        indicators.AddSeries(Series("ADX", SeriesType.Line, 1))
        indicators.AddSeries(Series("RSI", SeriesType.Line, 2))
        self.AddChart(indicators)
        
        # Create risk management chart
        risk = Chart("Risk Management")
        risk.AddSeries(Series("ATR", SeriesType.Line, 0))
        risk.AddSeries(Series("ATR_90_Avg", SeriesType.Line, 0))
        risk.AddSeries(Series("StopPrice", SeriesType.Line, 1))
        risk.AddSeries(Series("VIX", SeriesType.Line, 2))
        self.AddChart(risk)
        
        # Create strategy state chart
        state = Chart("Strategy State")
        state.AddSeries(Series("PositionSize", SeriesType.Line, 0))
        state.AddSeries(Series("DrawdownPct", SeriesType.Line, 1))
        self.AddChart(state)

    def OnData(self, data):
        '''Main event handler for market data updates'''
        
        # Skip processing during warm-up
        if self.IsWarmingUp:
            return
        
        # Check if we have data for SPY
        if not data.ContainsKey(self.spy_symbol) or not data.ContainsKey(self.vix_symbol):
            return
            
        # Update rolling windows
        if self.atr.IsReady:
            self.atr_90.Add(self.atr.Current.Value)
            
        # Update highest price tracking
        current_price = self.Securities[self.spy_symbol].Close
        self.highest_price_20d.Add(current_price)
        
        # Update strategy state charts
        self.Plot("Indicators", "FastEMA", self.fast_ema.Current.Value)
        self.Plot("Indicators", "SlowEMA", self.slow_ema.Current.Value)
        self.Plot("Indicators", "ADX", self.adx.Current.Value)
        self.Plot("Indicators", "RSI", self.rsi.Current.Value)
        
        self.Plot("Risk Management", "ATR", self.atr.Current.Value)
        self.Plot("Risk Management", "VIX", self.Securities[self.vix_symbol].Close)
        
        if self.atr_90.IsReady:
            atr_90_avg = np.mean([self.atr_90[i] for i in range(self.atr_90.Count)])
            self.Plot("Risk Management", "ATR_90_Avg", atr_90_avg)
        
        # Update drawdown tracking
        current_value = self.Portfolio.TotalPortfolioValue
        if current_value > self.peak_value:
            self.peak_value = current_value
        
        if self.peak_value > 0:
            self.strategy_drawdown = (self.peak_value - current_value) / self.peak_value
            self.Plot("Strategy State", "DrawdownPct", self.strategy_drawdown * 100)
        
        # Check if all indicators are ready
        if not self.fast_ema.IsReady or not self.slow_ema.IsReady or not self.adx.IsReady or not self.macd.IsReady or not self.rsi.IsReady or not self.atr.IsReady:
            return
            
        # Check for entry conditions if not invested
        if not self.is_invested:
            self.CheckEntrySignals(data)
        # Check for exit conditions if invested
        else:
            self.CheckExitSignals(data)
            self.UpdateStopLevels(data)
            self.CheckScalingOpportunity(data)

    def CheckEntrySignals(self, data):
        '''Check for entry signals based on strategy rules'''
        
        # Skip if we're in a significant drawdown
        if self.strategy_drawdown > 0.15:
            self.Log("Strategy in significant drawdown (>15%). Skipping new entries.")
            return
            
        # Get current indicator values
        fast_ema = self.fast_ema.Current.Value
        slow_ema = self.slow_ema.Current.Value
        adx_value = self.adx.Current.Value
        macd_value = self.macd.Current.Value
        macd_signal = self.macd.Signal.Current.Value
        rsi_value = self.rsi.Current.Value
        vix_value = self.Securities[self.vix_symbol].Close
        
        # Primary signal: EMA crossover
        ema_crossover = fast_ema > slow_ema and self.fast_ema.Current.Value > self.fast_ema.Previous.Value
        
        # Trend strength filter
        strong_trend = adx_value > 20
        
        # Confirmation signals
        macd_confirmation = macd_value > macd_signal
        rsi_confirmation = rsi_value > 50
        
        # Check for entry signal
        if ema_crossover and strong_trend:
            self.Log(f"Entry signal detected: EMA Crossover with ADX = {adx_value:.2f}")
            
            # Additional confirmation (optional)
            if macd_confirmation and rsi_confirmation:
                self.Log("Confirmation indicators are positive: MACD and RSI confirm trend")
            
            # Determine position size based on trend strength and volatility
            position_size = self.CalculatePositionSize(adx_value, vix_value)
            
            # Execute entry
            self.ExecuteEntry(position_size)

    def CheckExitSignals(self, data):
        '''Check for exit signals based on strategy rules'''
        
        # Get current indicator values
        fast_ema = self.fast_ema.Current.Value
        slow_ema = self.slow_ema.Current.Value
        current_price = self.Securities[self.spy_symbol].Close
        
        # Update tracking variables
        self.days_since_entry += 1
        
        # Check if price made a new high
        if current_price > self.high_since_entry:
            self.high_since_entry = current_price
            self.days_since_new_high = 0
        else:
            self.days_since_new_high += 1
        
        # Primary exit signal: EMA crossover (opposite of entry)
        ema_crossover_exit = fast_ema < slow_ema
        
        # Time-based exit conditions
        max_hold_period_exit = self.days_since_entry > 90
        no_new_high_exit = self.days_since_new_high > 30
        
        # Check for exit signals
        if ema_crossover_exit:
            self.Log("Exit signal: EMA crossover (fast below slow)")
            self.ExecuteExit()
        elif max_hold_period_exit:
            self.Log("Exit signal: Maximum hold period exceeded (90 days)")
            self.ExecuteExit()
        elif no_new_high_exit:
            self.Log("Warning: No new high in 30 days. Reevaluating position.")
            # Reduce position size by 25% if no new high in 30 days
            if self.position_size > 0:
                new_position = self.position_size * 0.75
                self.Log(f"Reducing position from {self.position_size:.2f} to {new_position:.2f} due to lack of momentum")
                self.SetHoldings(self.spy_symbol, new_position)
                self.position_size = new_position

    def UpdateStopLevels(self, data):
        '''Update stop loss levels based on ATR and price movement'''
        
        if not self.is_invested:
            return
            
        current_price = self.Securities[self.spy_symbol].Close
        atr_value = self.atr.Current.Value
        
        # Update trailing stop if price moves favorably
        if current_price > self.high_since_entry:
            self.high_since_entry = current_price
            new_stop = current_price - (3 * atr_value)
            
            # Only move stop up, never down
            if new_stop > self.trailing_stop_price:
                self.trailing_stop_price = new_stop
                self.Log(f"Trailing stop updated to {self.trailing_stop_price:.2f} (current price: {current_price:.2f})")
                self.Plot("Risk Management", "StopPrice", self.trailing_stop_price)
        
        # Check if stop is hit
        if current_price < self.trailing_stop_price:
            self.Log(f"Stop loss triggered at {current_price:.2f} (stop level: {self.trailing_stop_price:.2f})")
            self.ExecuteExit()

    def CheckScalingOpportunity(self, data):
        '''Check for scaling opportunity based on new 20-day highs'''
        
        if not self.is_invested or self.scaled_in or self.position_size >= 1.0:
            return
            
        current_price = self.Securities[self.spy_symbol].Close
        
        # Check if we have enough data
        if not self.highest_price_20d.IsReady:
            return
            
        # Calculate 20-day high
        high_20d = max([self.highest_price_20d[i] for i in range(self.highest_price_20d.Count)])
        
        # Scale in if price makes new 20-day high after entry
        if current_price > high_20d and self.days_since_entry > 5:
            additional_size = 0.1  # Add 10% to position
            new_position = min(1.0, self.position_size + additional_size)
            
            self.Log(f"Scaling in: Adding {additional_size:.2f} to position (new position size: {new_position:.2f})")
            self.SetHoldings(self.spy_symbol, new_position)
            self.position_size = new_position
            self.scaled_in = True

    def CalculatePositionSize(self, adx_value, vix_value):
        '''Calculate position size based on trend strength and volatility'''
        
        # Base position size based on ADX
        if adx_value > 25:
            base_position = 0.8  # 80% for strong trends
        else:
            base_position = 0.5  # 50% for moderate trends
            
        # Adjust for volatility (VIX)
        if vix_value > 30:
            base_position *= 0.5  # Reduce by 50% during high volatility
            self.Log(f"High volatility detected (VIX = {vix_value:.2f}). Reducing position size.")
            
        # Adjust for ATR volatility
        if self.atr_90.IsReady:
            atr_90_avg = np.mean([self.atr_90[i] for i in range(self.atr_90.Count)])
            current_atr = self.atr.Current.Value
            
            if current_atr > (2 * atr_90_avg):
                base_position *= 0.7  # Reduce by 30% if ATR is 2x the 90-day average
                self.Log(f"Elevated ATR detected (current: {current_atr:.2f}, 90d avg: {atr_90_avg:.2f}). Reducing position size.")
                
        # Adjust for strategy drawdown
        if self.strategy_drawdown > 0.1:
            base_position *= 0.5  # Reduce by 50% if drawdown exceeds 10%
            self.Log(f"Strategy in drawdown ({self.strategy_drawdown:.2%}). Reducing position size.")
            
        return base_position

    def ExecuteEntry(self, position_size):
        '''Execute entry with proper order type and position sizing'''
        
        if self.is_invested:
            return
            
        current_price = self.Securities[self.spy_symbol].Close
        atr_value = self.atr.Current.Value
        
        # Set initial and trailing stops
        self.initial_stop_price = current_price - (2 * atr_value)
        self.trailing_stop_price = self.initial_stop_price
        
        # Set entry tracking variables
        self.entry_price = current_price
        self.high_since_entry = current_price
        self.days_since_entry = 0
        self.days_since_new_high = 0
        self.entry_time = self.Time
        self.scaled_in = False
        
        # Execute the order
        self.SetHoldings(self.spy_symbol, position_size)
        self.position_size = position_size
        self.is_invested = True
        
        self.Log(f"Entered SPY position with size {position_size:.2f} at {current_price:.2f}")
        self.Log(f"Initial stop set at {self.initial_stop_price:.2f} ({(current_price - self.initial_stop_price) / current_price:.2%} below entry)")
        
        self.Plot("Risk Management", "StopPrice", self.initial_stop_price)
        self.Plot("Strategy State", "PositionSize", position_size * 100)

    def ExecuteExit(self):
        '''Execute exit with proper order type'''
        
        if not self.is_invested:
            return
            
        # Liquidate position
        self.Liquidate(self.spy_symbol)
        
        # Reset tracking variables
        self.is_invested = False
        self.position_size = 0
        self.initial_stop_price = 0
        self.trailing_stop_price = 0
        self.entry_time = None
        self.scaled_in = False
        
        self.Log(f"Exited SPY position at {self.Securities[self.spy_symbol].Close:.2f}")
        self.Plot("Strategy State", "PositionSize", 0)
        self.Plot("Risk Management", "StopPrice", 0)

    def DailyUpdate(self):
        '''Daily update for risk management and position monitoring'''
        
        if not self.is_invested:
            return
            
        # Log current position status
        days_held = (self.Time - self.entry_time).days if self.entry_time else 0
        current_price = self.Securities[self.spy_symbol].Close
        pnl_pct = (current_price / self.entry_price - 1) * 100 if self.entry_price > 0 else 0
        
        self.Log(f"Position update: Holding SPY for {days_held} days, P&L: {pnl_pct:.2f}%, Stop: {self.trailing_stop_price:.2f}")
        
        # Check for time-based reassessment
        if self.days_since_new_high >= 30:
            self.Log(f"Warning: No new high in {self.days_since_new_high} days")