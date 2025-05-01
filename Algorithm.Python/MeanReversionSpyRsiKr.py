# Algorithm.Python/MeanReversionSpyRsiKr.py

from QuantConnect.Algorithm import QCAlgorithm
from QuantConnect.Data import SubscriptionDataSource, DataNormalizationMode # Added DataNormalizationMode
from QuantConnect.Data.Market import TradeBar
from QuantConnect.Indicators import RelativeStrengthIndex, AverageTrueRange, MovingAverageType # Added MovingAverageType
from QuantConnect.Orders import OrderStatus, StopMarketOrder, LimitOrder, OrderDirection, OrderType # Added OrderDirection, OrderType
from datetime import datetime, timedelta

# Import the custom Kernel Regression indicator
# Need to ensure the path is correct for LEAN to find it.
# Assuming LEAN automatically handles imports from the Indicators directory.
try:
    from Indicators.KernelRegression import KernelRegression
except ImportError:
    # Fallback for local testing if needed, adjust path as necessary
    # This might require adding the project root to sys.path in local environments
    from KernelRegression import KernelRegression # Assuming it's in the same dir or PYTHONPATH includes Indicators

class MeanReversionSpyRsiKr(QCAlgorithm):
    """
    Algorithm Description:
    Implements a daily mean-reversion strategy on SPY using RSI, ATR, and a custom Kernel Regression indicator.
    Entry Logic: Long when RSI < 30 and Close < KR; Short when RSI > 70 and Close > KR.
    Exit Logic: RSI crosses 50 OR ATR-based Stop Loss (1.5x) OR ATR-based Profit Target (3.0x).
    """

    def Initialize(self):
        """
        Initializes the algorithm, setting parameters, adding data, and indicators.
        """
        # --- Algorithm Settings ---
        self.SetStartDate(2020, 1, 1)  # Set Start Date
        self.SetEndDate(2024, 1, 1)    # Set End Date
        self.SetCash(100000)           # Set Strategy Cash

        # --- Data Subscription ---
        self.spy = self.AddEquity("SPY", Resolution.Daily)
        self.spy.SetDataNormalizationMode(DataNormalizationMode.Raw) # Or adjust as needed

        # --- Indicator Initialization ---
        # Standard Indicators
        self.rsi_period = 14
        self.atr_period = 14
        self.rsi = self.RSI("SPY", self.rsi_period, MovingAverageType.Simple, Resolution.Daily)
        self.atr = self.ATR("SPY", self.atr_period, MovingAverageType.Simple, Resolution.Daily)

        # Custom Kernel Regression Indicator
        self.kr_period = 80  # Lookback L
        self.kr_bandwidth = 15 # Bandwidth h
        self.kr = KernelRegression(f"KR({self.kr_period},{self.kr_bandwidth})", self.kr_period, self.kr_bandwidth)
        # Register the custom indicator to receive data from SPY
        self.RegisterIndicator("SPY", self.kr, Resolution.Daily, Field.Close) # Use Close price for KR

        # --- Warm-up Period ---
        # Set warm-up period to ensure all indicators are ready before trading.
        # The longest period is KR (80), plus potentially a small buffer.
        self.SetWarmUp(timedelta(days=self.kr_period + 5)) # Add a buffer

        # --- Strategy Parameters ---
        self.rsi_oversold = 30
        self.rsi_overbought = 70
        self.rsi_exit_level = 50
        self.atr_stop_multiplier = 1.5
        self.atr_profit_multiplier = 3.0
        self.portfolio_allocation = 0.95 # Allocate 95% to each trade

        # --- Tracking ---
        self.entry_price = 0.0
        self.stop_loss_order_ticket = None
        self.profit_target_order_ticket = None


    def OnData(self, data):
        """
        Main event handler for new data. Executes the trading logic.
        Args:
            data: Slice object containing the latest data for subscribed securities.
        """
        # Wait for the warm-up period to complete
        if self.IsWarmingUp:
            return

        # Check if SPY data is present
        if not data.ContainsKey("SPY") or data["SPY"] is None:
             return

        # Check if all indicators are ready
        if not self.rsi.IsReady or not self.atr.IsReady or not self.kr.IsReady:
            return

        # Get indicator values
        current_rsi = self.rsi.Current.Value
        current_atr = self.atr.Current.Value
        current_kr = self.kr.Current.Value # Access the calculated KR value
        current_price = data["SPY"].Close

        # --- Trading Logic ---

        # Check if we have an existing position
        position = self.Portfolio["SPY"]
        if not position.Invested:
            # --- Entry Logic ---
            # Check Long condition: RSI < 30 AND Close < KR
            if current_rsi < self.rsi_oversold and current_price < current_kr:
                self.Log(f"{self.Time} >> ENTRY SIGNAL: Long. RSI={current_rsi:.2f}, Close={current_price:.2f}, KR={current_kr:.2f}")
                # Calculate order size
                quantity = self.CalculateOrderQuantity("SPY", self.portfolio_allocation)
                if quantity != 0:
                    self.MarketOrder("SPY", quantity, asynchronous=True) # Place async market order
                    # SL/PT will be placed in OnOrderEvent upon fill confirmation

            # Check Short condition: RSI > 70 AND Close > KR
            elif current_rsi > self.rsi_overbought and current_price > current_kr:
                self.Log(f"{self.Time} >> ENTRY SIGNAL: Short. RSI={current_rsi:.2f}, Close={current_price:.2f}, KR={current_kr:.2f}")
                # Calculate order size (negative for short)
                quantity = self.CalculateOrderQuantity("SPY", -self.portfolio_allocation)
                if quantity != 0:
                    self.MarketOrder("SPY", quantity, asynchronous=True) # Place async market order
                    # SL/PT will be placed in OnOrderEvent upon fill confirmation

        else: # We are invested
            # --- Exit Logic ---
            # Check RSI exit condition first (overrides SL/PT if triggered)
            if position.IsLong and current_rsi > self.rsi_exit_level:
                self.Log(f"{self.Time} >> EXIT SIGNAL: RSI Exit Long. RSI={current_rsi:.2f}")
                self.Liquidate("SPY", "RSI Exit")
                self.CancelStopLossAndProfitTarget() # Ensure SL/PT are cancelled
            elif position.IsShort and current_rsi < self.rsi_exit_level:
                self.Log(f"{self.Time} >> EXIT SIGNAL: RSI Exit Short. RSI={current_rsi:.2f}")
                self.Liquidate("SPY", "RSI Exit")
                self.CancelStopLossAndProfitTarget() # Ensure SL/PT are cancelled

            # Note: The SL/PT orders placed via PlaceStopLossAndProfitTarget will be handled
            # automatically by the brokerage/QC engine. We don't need explicit checks here
            # unless we were manually managing stops with market orders based on price crossing levels.


    def OnOrderEvent(self, orderEvent):
        """
        Event handler for order status changes. Crucial for placing SL/PT after entry fill.
        Args:
            orderEvent: The order event object containing details about the order status change.
        """
        order = self.Transactions.GetOrderById(orderEvent.OrderId)

        # Log fills and place SL/PT for entry orders
        if orderEvent.Status == OrderStatus.Filled:
            # Check if it's an entry fill (market order for SPY, and we are not currently tracking SL/PT)
            if order.Symbol == self.spy.Symbol and order.Type == OrderType.Market and \
               self.stop_loss_order_ticket is None and self.profit_target_order_ticket is None:

                # Check if the fill actually resulted in a position matching the order direction
                # (Handles cases where fills might be partial or delayed)
                position = self.Portfolio["SPY"]
                if (order.Direction == OrderDirection.Buy and position.IsLong) or \
                   (order.Direction == OrderDirection.Sell and position.IsShort):

                    self.entry_price = orderEvent.FillPrice
                    fill_quantity = orderEvent.AbsoluteFillQuantity # Use actual filled quantity
                    self.Log(f"{self.Time} >> ENTRY FILL: {order.Direction} {fill_quantity} SPY @ {self.entry_price:.2f}")

                    # Place SL and PT orders now that we have the fill price and quantity
                    # Ensure ATR is ready before using its value
                    if self.atr.IsReady:
                        current_atr = self.atr.Current.Value
                        self.PlaceStopLossAndProfitTarget(order.Direction, fill_quantity, self.entry_price, current_atr)
                    else:
                        self.Log(f"{self.Time} >> WARNING: ATR not ready at time of fill. Cannot place SL/PT for OrderId {orderEvent.OrderId}.")
                        # Liquidate immediately if we can't set SL/PT? Or handle differently?
                        self.Liquidate("SPY", "ATR Not Ready on Fill") # Safer to liquidate if SL/PT cannot be set

            # Check if a SL or PT order was filled
            elif self.stop_loss_order_ticket is not None and orderEvent.OrderId == self.stop_loss_order_ticket.OrderId:
                self.Log(f"{self.Time} >> STOP LOSS FILLED: OrderId {orderEvent.OrderId} @ {orderEvent.FillPrice:.2f}")
                if self.profit_target_order_ticket is not None:
                    self.profit_target_order_ticket.Cancel("Stop Loss Hit")
                self.ResetTradeTracking() # Reset tracking variables

            elif self.profit_target_order_ticket is not None and orderEvent.OrderId == self.profit_target_order_ticket.OrderId:
                self.Log(f"{self.Time} >> PROFIT TARGET FILLED: OrderId {orderEvent.OrderId} @ {orderEvent.FillPrice:.2f}")
                if self.stop_loss_order_ticket is not None:
                    self.stop_loss_order_ticket.Cancel("Profit Target Hit")
                self.ResetTradeTracking() # Reset tracking variables

        # Handle cancellations (including those triggered by Liquidate or manually)
        elif orderEvent.Status == OrderStatus.Canceled:
             if self.stop_loss_order_ticket is not None and orderEvent.OrderId == self.stop_loss_order_ticket.OrderId:
                 self.Log(f"{self.Time} >> Stop Loss Order Canceled: {orderEvent.OrderId}")
                 self.stop_loss_order_ticket = None
             if self.profit_target_order_ticket is not None and orderEvent.OrderId == self.profit_target_order_ticket.OrderId:
                 self.Log(f"{self.Time} >> Profit Target Order Canceled: {orderEvent.OrderId}")
                 self.profit_target_order_ticket = None
             # If the cancellation means we are flat, reset tracking
             if not self.Portfolio["SPY"].Invested:
                 self.ResetTradeTracking()

        # Log other statuses like errors or invalid for debugging
        elif orderEvent.Status in [OrderStatus.Invalid, OrderStatus.CancelPending, OrderStatus.Error]:
            self.Log(f"{self.Time} >> ORDER EVENT {orderEvent.Status}: {orderEvent.ToString()}")
            # If an entry order fails, reset tracking if necessary
            if order.Type == OrderType.Market and not self.Portfolio["SPY"].Invested:
                 self.ResetTradeTracking()


    def PlaceStopLossAndProfitTarget(self, direction, quantity, entry_price, current_atr):
        """
        Places the ATR-based Stop Loss and Profit Target orders after an entry fill.
        Args:
            direction: The direction of the trade (OrderDirection.Buy or OrderDirection.Sell).
            quantity: The absolute quantity filled for the entry.
            entry_price: The average fill price of the entry order.
            current_atr: The current ATR value to calculate stops/targets.
        """
        if current_atr <= 0:
            self.Log(f"{self.Time} >> WARNING: ATR is zero or negative ({current_atr:.2f}), cannot place SL/PT.")
            # Consider liquidating if SL/PT cannot be set
            self.Liquidate("SPY", "Invalid ATR for SL/PT")
            return

        self.Log(f"{self.Time} >> Placing SL/PT: Entry={entry_price:.2f}, ATR={current_atr:.2f}, Direction={direction}, Qty={quantity}")

        # Determine the quantity for the closing orders (opposite sign of entry)
        close_quantity = -quantity if direction == OrderDirection.Buy else quantity

        if direction == OrderDirection.Buy: # Long position
            stop_price = entry_price - self.atr_stop_multiplier * current_atr
            target_price = entry_price + self.atr_profit_multiplier * current_atr
            # Place Stop Market order for SL
            self.stop_loss_order_ticket = self.StopMarketOrder("SPY", close_quantity, stop_price, "ATR SL")
            # Place Limit order for PT
            self.profit_target_order_ticket = self.LimitOrder("SPY", close_quantity, target_price, "ATR PT")
            self.Log(f"{self.Time} >> Long SL placed at {stop_price:.2f}, PT at {target_price:.2f}")

        elif direction == OrderDirection.Sell: # Short position
            stop_price = entry_price + self.atr_stop_multiplier * current_atr
            target_price = entry_price - self.atr_profit_multiplier * current_atr
            # Place Stop Market order for SL
            self.stop_loss_order_ticket = self.StopMarketOrder("SPY", close_quantity, stop_price, "ATR SL")
            # Place Limit order for PT
            self.profit_target_order_ticket = self.LimitOrder("SPY", close_quantity, target_price, "ATR PT")
            self.Log(f"{self.Time} >> Short SL placed at {stop_price:.2f}, PT at {target_price:.2f}")

        # Check if orders were created successfully (tickets are not None)
        if self.stop_loss_order_ticket is None or self.profit_target_order_ticket is None:
             self.Log(f"{self.Time} >> ERROR: Failed to create SL or PT order tickets. Liquidating position.")
             self.Liquidate("SPY", "SL/PT Creation Failed")
             self.ResetTradeTracking()


    def CancelStopLossAndProfitTarget(self):
        """ Cancels any existing SL or PT orders. """
        if self.stop_loss_order_ticket is not None and self.stop_loss_order_ticket.Status.IsActive():
            self.stop_loss_order_ticket.Cancel("Position Closed Manually")
            self.Log(f"{self.Time} >> Canceled Stop Loss order.")
        if self.profit_target_order_ticket is not None and self.profit_target_order_ticket.Status.IsActive():
            self.profit_target_order_ticket.Cancel("Position Closed Manually")
            self.Log(f"{self.Time} >> Canceled Profit Target order.")
        # Reset tracking immediately after cancellation attempt
        self.ResetTradeTracking()


    def ResetTradeTracking(self):
        """ Resets variables used for tracking a single trade's state (entry price, SL/PT orders). """
        self.entry_price = 0.0
        self.stop_loss_order_ticket = None
        self.profit_target_order_ticket = None
        # self.Log(f"{self.Time} >> Trade tracking variables reset.") # Optional: for debugging