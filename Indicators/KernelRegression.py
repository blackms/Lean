# Indicators/KernelRegression.py

import numpy as np
from collections import deque
from QuantConnect.Indicators import PythonIndicator, IndicatorDataPoint

class KernelRegression(PythonIndicator):
    """
    Nadaraya-Watson Kernel Regression Indicator using a Gaussian Kernel.
    Calculates a weighted average of past prices, where weights are determined
    by a Gaussian kernel based on the time distance from the current point.
    """
    def __init__(self, name, period, bandwidth):
        """
        Initializes a new instance of the KernelRegression class.
        Args:
            name (str): The name of this indicator.
            period (int): The lookback period (L). Determines how many past data points are considered.
            bandwidth (float): The bandwidth (h) for the Gaussian kernel. Controls the smoothness.
                               Smaller bandwidth gives more weight to recent points (less smooth).
                               Larger bandwidth considers more points (smoother).
        """
        super().__init__(name)
        if period < 1:
            raise ValueError("KernelRegression: Period must be greater than 0.")
        if bandwidth <= 0:
            raise ValueError("KernelRegression: Bandwidth must be positive.")

        self.period = period
        self.bandwidth = bandwidth
        # Warm-up period is the lookback period L
        self.warm_up_period = period
        self.value = 0.0 # Store the current KR value for convenience

        # Use deques to efficiently store historical price data and corresponding indices (time steps)
        # We store the actual input values (prices)
        self._window = deque(maxlen=period)
        # We store a simple sequence of integers representing the time step index
        self._indices = deque(maxlen=period)
        self._current_index = 0 # Counter for the time step index

    @property
    def is_ready(self):
        """
        Gets a flag indicating when this indicator is ready and fully initialized.
        Requires 'period' data points.
        """
        return len(self._window) == self.period

    def update(self, input_data):
        """
        Updates the indicator with a new data point (typically price).
        Args:
            input_data (IndicatorDataPoint): The input data point containing price and time.
        Returns:
            bool: True if the indicator is ready after this update, False otherwise.
        """
        # Add new data point value and its corresponding time step index
        self._window.append(float(input_data.value))
        self._indices.append(self._current_index)
        self._current_index += 1 # Increment time step index

        # Wait until the window is full before calculating
        if not self.is_ready:
            # Assign time even during warm-up
            self.current.time = input_data.time
            return False

        # --- Kernel Regression Calculation ---
        # Get the index of the current point (the one we are calculating the regression for)
        current_index = self._indices[-1]
        # Convert deques to numpy arrays for vectorized calculations
        indices_array = np.array(self._indices)
        window_array = np.array(self._window) # These are the historical prices (y values)

        # Calculate weights using Gaussian kernel
        # K(u) = (1 / sqrt(2 * pi)) * exp(-0.5 * u^2)
        # u = (x_i - x) / h = (historical_index - current_index) / bandwidth
        # We calculate weights for each point in the window relative to the current point.
        u = (indices_array - current_index) / self.bandwidth
        # Gaussian kernel calculation. The constant factor (1/sqrt(2pi)) is often omitted
        # as it cancels out in the final weighted average calculation.
        weights = np.exp(-0.5 * u**2)

        # Calculate the Nadaraya-Watson estimator (weighted average)
        # KR_value = sum(weights * historical_prices) / sum(weights)
        sum_weights = np.sum(weights)

        # Avoid division by zero if all weights somehow become zero (highly unlikely with Gaussian kernel and positive bandwidth)
        if sum_weights > 1e-10: # Use a small threshold for floating point comparison
            self.value = np.sum(weights * window_array) / sum_weights
        else:
            # Fallback: Use the most recent price if weights sum is effectively zero
            self.value = window_array[-1]

        # Update the official IndicatorDataPoint value and time
        self.current.value = self.value
        self.current.time = input_data.time # Propagate time from input

        return True

    def reset(self):
        """
        Resets this indicator to its initial state.
        """
        self._window.clear()
        self._indices.clear()
        self._current_index = 0
        self.value = 0.0
        # Reset the base indicator properties
        super().reset()