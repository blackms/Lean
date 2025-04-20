# Quantitative Analysis

## Overview

This section provides detailed documentation on the quantitative analysis aspects of QuantConnect Lean. It covers the mathematical models, statistical methods, and performance metrics used in the platform for developing and evaluating trading strategies.

## Mathematical Models

QuantConnect Lean incorporates various mathematical models for analyzing financial markets and developing trading strategies. These models provide the theoretical foundation for many of the platform's features.

### 1. Time Series Models

Time series models are used to analyze and forecast financial data that changes over time. Lean supports several time series models:

- **Autoregressive (AR) Models**: Model the current value as a function of past values
- **Moving Average (MA) Models**: Model the current value as a function of past errors
- **Autoregressive Moving Average (ARMA) Models**: Combine AR and MA models
- **Autoregressive Integrated Moving Average (ARIMA) Models**: Extend ARMA models to non-stationary data
- **Generalized Autoregressive Conditional Heteroskedasticity (GARCH) Models**: Model time-varying volatility

[Learn more about Mathematical Models](./mathematical-models.md)

### 2. Portfolio Optimization Models

Portfolio optimization models are used to determine the optimal allocation of assets in a portfolio. Lean supports several optimization models:

- **Mean-Variance Optimization**: Maximize expected return for a given level of risk
- **Black-Litterman Model**: Combine market equilibrium with investor views
- **Risk Parity**: Allocate assets based on risk contribution
- **Maximum Sharpe Ratio**: Maximize the Sharpe ratio of the portfolio
- **Minimum Variance**: Minimize the variance of the portfolio

### 3. Option Pricing Models

Option pricing models are used to calculate the theoretical value of options. Lean supports several option pricing models:

- **Black-Scholes-Merton Model**: Calculate the theoretical value of European options
- **Binomial Tree Model**: Calculate the value of American options
- **Monte Carlo Simulation**: Simulate price paths to value complex options

## Statistical Methods

QuantConnect Lean incorporates various statistical methods for analyzing financial data and developing trading strategies. These methods provide the tools for extracting insights from market data.

### 1. Descriptive Statistics

Descriptive statistics summarize and describe the main features of a dataset. Lean provides functions for calculating various descriptive statistics:

- **Mean, Median, Mode**: Measures of central tendency
- **Standard Deviation, Variance**: Measures of dispersion
- **Skewness, Kurtosis**: Measures of distribution shape
- **Correlation, Covariance**: Measures of relationship between variables

[Learn more about Statistical Methods](./statistical-methods.md)

### 2. Hypothesis Testing

Hypothesis testing is used to determine if a statement about a population parameter is supported by the data. Lean supports several hypothesis tests:

- **t-tests**: Test if the mean of a population is equal to a specified value
- **F-tests**: Test if two populations have the same variance
- **Chi-squared tests**: Test if two categorical variables are related
- **Jarque-Bera test**: Test if a dataset follows a normal distribution

### 3. Regression Analysis

Regression analysis is used to model the relationship between variables. Lean supports several regression models:

- **Linear Regression**: Model the relationship between a dependent variable and one or more independent variables
- **Logistic Regression**: Model the probability of a binary outcome
- **Polynomial Regression**: Model non-linear relationships
- **Multiple Regression**: Model the relationship between a dependent variable and multiple independent variables

### 4. Machine Learning

Machine learning is used to develop models that can learn from data and make predictions. Lean supports integration with various machine learning libraries:

- **Supervised Learning**: Train models on labeled data
- **Unsupervised Learning**: Find patterns in unlabeled data
- **Reinforcement Learning**: Train models through trial and error
- **Deep Learning**: Train neural networks on large datasets

## Performance Metrics

QuantConnect Lean provides various metrics for evaluating the performance of trading strategies. These metrics help assess the profitability, risk, and efficiency of strategies.

### 1. Return Metrics

Return metrics measure the profitability of a strategy:

- **Total Return**: The overall return of the strategy
- **Annualized Return**: The return of the strategy expressed on an annual basis
- **Daily/Monthly/Yearly Returns**: Returns over specific time periods
- **Compound Annual Growth Rate (CAGR)**: The geometric progression ratio that provides a constant rate of return over the time period

[Learn more about Performance Metrics](./performance-metrics.md)

### 2. Risk Metrics

Risk metrics measure the risk of a strategy:

- **Standard Deviation**: Measures the dispersion of returns
- **Downside Deviation**: Measures the dispersion of returns below a threshold
- **Maximum Drawdown**: The maximum loss from a peak to a trough
- **Value at Risk (VaR)**: The maximum loss expected over a specific time period at a given confidence level
- **Conditional Value at Risk (CVaR)**: The expected loss given that the loss exceeds the VaR

### 3. Risk-Adjusted Return Metrics

Risk-adjusted return metrics measure the return of a strategy relative to its risk:

- **Sharpe Ratio**: The excess return per unit of total risk
- **Sortino Ratio**: The excess return per unit of downside risk
- **Calmar Ratio**: The annualized return divided by the maximum drawdown
- **Omega Ratio**: The probability-weighted ratio of gains versus losses
- **Information Ratio**: The active return divided by the tracking error

### 4. Other Metrics

Other metrics provide additional insights into the performance of a strategy:

- **Win Rate**: The percentage of trades that are profitable
- **Profit Factor**: The gross profit divided by the gross loss
- **Payoff Ratio**: The average win divided by the average loss
- **Expectancy**: The expected profit or loss per trade
- **Equity Curve**: A graphical representation of the value of a trading account over time

## Implementation in Lean

QuantConnect Lean provides a comprehensive set of tools for implementing quantitative analysis in trading strategies:

### 1. Indicators

Lean provides a wide range of technical indicators for analyzing price and volume data:

- **Moving Averages**: Simple, Exponential, Weighted, etc.
- **Oscillators**: RSI, MACD, Stochastic, etc.
- **Volatility Indicators**: Bollinger Bands, ATR, etc.
- **Volume Indicators**: OBV, Volume Weighted Average Price, etc.
- **Custom Indicators**: Create custom indicators for specific analysis needs

### 2. Statistics

Lean provides functions for calculating various statistical measures:

- **Descriptive Statistics**: Mean, Median, Standard Deviation, etc.
- **Correlation and Covariance**: Measure relationships between securities
- **Regression Analysis**: Linear regression, polynomial regression, etc.
- **Hypothesis Testing**: t-tests, F-tests, etc.

### 3. Optimization

Lean provides tools for optimizing strategy parameters:

- **Grid Search**: Exhaustively search through a specified parameter grid
- **Genetic Algorithms**: Use evolutionary algorithms to find optimal parameters
- **Bayesian Optimization**: Use Bayesian methods to efficiently search the parameter space

### 4. Machine Learning Integration

Lean supports integration with various machine learning libraries:

- **Python Integration**: Use Python libraries like scikit-learn, TensorFlow, and PyTorch
- **Feature Engineering**: Create features from raw market data
- **Model Training and Evaluation**: Train and evaluate machine learning models
- **Model Deployment**: Deploy trained models in live trading

## Next Steps

For detailed information about each aspect of quantitative analysis in Lean, refer to the individual documentation:

- [Mathematical Models](./mathematical-models.md)
- [Statistical Methods](./statistical-methods.md)
- [Performance Metrics](./performance-metrics.md)