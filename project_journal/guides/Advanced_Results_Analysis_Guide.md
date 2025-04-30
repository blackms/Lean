# Advanced Results Analysis Guide

## Overview

This guide explains how to use the advanced results analyzer to visualize and analyze your trading strategy backtest results. The analyzer processes the JSON output files from LEAN backtests and generates comprehensive reports and visualizations.

## Running the Analyzer

To analyze your backtest results, follow these steps:

1. Run your strategy backtest using LEAN
2. Navigate to the Debug directory
3. Run the results analyzer script

```bash
source /home/alessio/NeuralTrading/Lean/venv/bin/activate
cd /home/alessio/NeuralTrading/Lean/Launcher/bin/Debug
python3 results_analyzer.py
```

## Viewing the Reports

To open the HTML reports in your default web browser, use the provided script:

```bash
source /home/alessio/NeuralTrading/Lean/venv/bin/activate
cd /home/alessio/NeuralTrading/Lean/Launcher/bin/Debug
python3 open_reports.py
```

To open a specific strategy's report:

```bash
python3 open_reports.py --strategy SPYTrendFollowingStrategy
```

## Generated Reports

The analyzer creates the following outputs in the `Reports` directory:

### HTML Reports

Located in `Reports/html/`, these provide a comprehensive overview of your strategy's performance with key metrics and embedded visualizations.

- `[StrategyName]_report.html`: Contains performance metrics, equity curve, drawdowns, and return statistics

### CSV Reports

Located in `Reports/csv/`, these provide detailed metrics in a tabular format for further analysis.

- `[StrategyName]_metrics.csv`: Contains key performance metrics like total return, CAGR, Sharpe ratio, etc.

### Visualizations

Located in `Reports/images/[StrategyName]/`, these provide graphical representations of your strategy's performance.

- `equity_curve.png`: Shows the growth of your portfolio over time
- `drawdown.png`: Visualizes the drawdowns experienced by your strategy
- `monthly_returns.png`: Displays a heatmap of monthly returns
- `returns_distribution.png`: Shows the distribution of daily returns

## Understanding the Visualizations

### Equity Curve

The equity curve shows how your portfolio value changes over time. A steadily increasing line indicates consistent positive returns, while a volatile line indicates higher risk.

### Drawdown Chart

The drawdown chart shows the percentage decline from peak equity. This helps you understand the risk and volatility of your strategy. Larger drawdowns indicate higher risk.

### Monthly Returns Heatmap

The monthly returns heatmap displays returns by month and year, using colors to indicate performance (green for positive, red for negative). This helps identify seasonal patterns in your strategy's performance.

### Returns Distribution

The returns distribution chart shows the frequency distribution of daily returns. A normal distribution centered slightly to the right of zero is ideal, indicating consistent positive returns with manageable risk.

## Interpreting Key Metrics

- **Total Return**: The overall percentage return of your strategy
- **CAGR (Compound Annual Growth Rate)**: The annualized rate of return
- **Volatility**: The standard deviation of returns, indicating risk
- **Sharpe Ratio**: Return per unit of risk (higher is better)
- **Maximum Drawdown**: The largest percentage drop from peak to trough

## Troubleshooting

If you encounter issues with the analyzer:

1. **Missing Data**: Ensure your backtest completed successfully and generated all required output files
2. **Config Files**: The analyzer automatically excludes config files from analysis
3. **Insufficient Data**: Some visualizations (like monthly returns heatmap) require sufficient data points to generate

## Customizing the Analysis

You can modify the `results_analyzer.py` script to customize the analysis:

- Add new visualizations
- Change color schemes
- Adjust calculation methods
- Add additional metrics

## Best Practices

1. **Compare Multiple Strategies**: Run the analyzer on different strategies to compare performance
2. **Benchmark Comparison**: Compare your strategy against market benchmarks
3. **Parameter Sensitivity**: Analyze how changes in strategy parameters affect performance
4. **Out-of-Sample Testing**: Validate your strategy on data not used during development