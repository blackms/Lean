# Visualizing Backtest Results in LEAN

This guide explains how to visualize and analyze backtest results from LEAN algorithmic trading strategies.

## Understanding Results Location

When you run a backtest in LEAN, the results are saved in two locations:

1. **Primary Results Folder**: `Launcher/bin/Debug/Results/`
   - This is configured in `config.json` with the setting `"results-destination-folder": "./Results"`
   - Contains raw result files for all strategies

2. **Reports Folder**: `Launcher/bin/Debug/Reports/`
   - Contains generated visualizations and HTML reports
   - Organized by strategy name

## Available Result Files

For each strategy (e.g., `SPYTrendFollowingStrategy`), the following files are generated:

- **Main Results**: `StrategyName.json` - Contains all trades, equity curve data
- **Order Events**: `StrategyName-order-events.json` - Detailed order execution data
- **Summary**: `StrategyName-summary.json` - Performance metrics and statistics
- **Log**: `StrategyName-log.txt` - Detailed algorithm execution log

## Visualizing Results

We've created several tools to help visualize and analyze your backtest results:

### 1. Using the Visualization Script

The `visualize_results.py` script automatically processes result files and generates visualizations:

```bash
cd Launcher/bin/Debug
python visualize_results.py --strategy SPYTrendFollowingStrategy --open-browser
```

Options:
- `--strategy`: Specify which strategy to analyze (omit to analyze all)
- `--open-browser`: Automatically open HTML reports in your browser
- `--results-path`: Custom path to results (default: `./`)
- `--reports-path`: Custom path for generated reports (default: `./Reports`)

### 2. Opening Existing Reports

If you've already generated reports, you can open them using:

```bash
cd Launcher/bin/Debug
python open_reports.py --strategy SPYTrendFollowingStrategy
```

### 3. Understanding Generated Visualizations

For each strategy, the following visualizations are generated:

- **Equity Curve**: Shows the growth of your portfolio over time
- **Drawdown Chart**: Visualizes periods of decline from peak equity
- **Monthly Returns**: Heatmap showing performance by month/year
- **Returns Distribution**: Histogram of daily returns

> **Note**: For short backtests (less than 2 months), the monthly returns heatmap will be replaced with a simple bar chart or skipped entirely. This is normal and not an error.

## Troubleshooting

### "Results folder not created" Issue

If you don't see the Results folder:

1. **Check the correct location**: The Results folder is created at `Launcher/bin/Debug/Results/` relative to where the backtest was run
2. **Verify config.json**: Ensure `"results-destination-folder"` is set correctly
3. **Check permissions**: Ensure the application has write permissions to create the folder

### Missing or Incomplete Visualizations

- **Short backtests**: Backtests shorter than 2 months will have limited visualizations
- **No trades executed**: If your strategy didn't make any trades, some visualizations may be empty
- **Data errors**: Check the log files for any data-related errors

## Customizing Visualizations

The visualization scripts can be modified to add custom charts or metrics:

1. Edit `enhanced_results_analyzer.py` to add new visualization types
2. Modify HTML templates in the script to change report formatting
3. Add custom metrics calculations in the analysis section

## Next Steps

- Compare multiple strategy results side-by-side
- Export results to CSV for further analysis in Excel
- Integrate with external visualization tools like Tableau or Power BI