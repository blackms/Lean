# Core Components

## Overview

QuantConnect Lean is built around several core components that work together to provide a complete algorithmic trading platform. This section provides detailed documentation on each of these components, explaining their purpose, functionality, and how they interact with other components.

## Component Categories

### Algorithm Framework

The Algorithm Framework is a structured approach to building trading strategies, separating concerns into distinct components:

- **Alpha Models**: Generate trading signals (insights) based on market data
- **Portfolio Construction Models**: Determine position sizes based on insights
- **Execution Models**: Convert target portfolios into orders
- **Risk Management Models**: Apply risk controls to orders
- **Universe Selection Models**: Select assets to trade

[Learn more about the Algorithm Framework](./algorithm-framework.md)

### Data Management

The Data Management components handle the acquisition, processing, and delivery of market data:

- **SubscriptionManager**: Manages data subscriptions for different securities and data types
- **DataFeeds**: Provides data from various sources (historical databases, live feeds)
- **Consolidators**: Aggregates tick data into bars (OHLCV) of different resolutions
- **Slices**: Packages data points from multiple sources into time-synchronized slices

[Learn more about Data Management](./data-management.md)

### Securities

The Securities components manage the universe of tradable assets:

- **SecurityManager**: Maintains the collection of securities in the algorithm
- **Security Models**: Defines the behavior of different asset classes
- **Market Hours**: Manages trading hours and holidays for different markets
- **Pricing Models**: Calculates fair values for different security types

[Learn more about Securities](./securities.md)

### Portfolio Management

The Portfolio Management components handle the financial aspects of the algorithm:

- **Portfolio Manager**: Tracks positions, cash balances, and overall portfolio value
- **Cash Book**: Manages cash balances in different currencies
- **Holdings**: Tracks position sizes and values
- **Performance**: Calculates performance metrics

[Learn more about Portfolio Management](./portfolio-management.md)

### Order Management

The Order Management components handle the lifecycle of orders:

- **Transaction Manager**: Processes orders and executions
- **Order Processor**: Manages order state transitions
- **Order Tickets**: Tracks order status and modifications
- **Fill Models**: Simulates order fills in backtesting

[Learn more about Order Management](./order-management.md)

### Risk Management

The Risk Management components handle risk control:

- **Risk Models**: Applies risk controls to orders
- **Margin Models**: Calculates margin requirements
- **Fee Models**: Calculates transaction costs
- **Slippage Models**: Simulates price slippage

[Learn more about Risk Management](./risk-management.md)

## Component Interactions

The core components interact with each other in a well-defined manner:

1. **Algorithm Initialization**:
   - The algorithm initializes its components
   - Securities are added to the SecurityManager
   - Data subscriptions are added to the SubscriptionManager
   - Framework components (Alpha, Portfolio, Execution, Risk, Universe) are set up

2. **Data Processing**:
   - Data feeds provide market data to the algorithm
   - The algorithm processes the data and generates insights through alpha models
   - Portfolio construction models convert insights into target portfolios
   - Execution models place orders to achieve the target portfolio
   - Risk management models apply risk controls to the orders

3. **Order Processing**:
   - Orders are placed through the TransactionManager
   - The OrderProcessor manages order state transitions
   - Fill models simulate order fills in backtesting
   - The PortfolioManager updates positions and cash balances based on fills

4. **Performance Reporting**:
   - Performance metrics are calculated based on portfolio value
   - Results are logged and reported

## Component Extensibility

Lean is designed to be easily extended with custom components:

- Custom data sources can be created by inheriting from BaseData
- Custom alpha models can be created by implementing IAlphaModel
- Custom portfolio construction models can be created by implementing IPortfolioConstructionModel
- Custom execution models can be created by implementing IExecutionModel
- Custom risk management models can be created by implementing IRiskManagementModel
- Custom universe selection models can be created by implementing IUniverseSelectionModel

## Next Steps

For detailed information about each component category, refer to the individual component documentation:

- [Algorithm Framework](./algorithm-framework.md)
- [Data Management](./data-management.md)
- [Securities](./securities.md)
- [Portfolio Management](./portfolio-management.md)
- [Order Management](./order-management.md)
- [Risk Management](./risk-management.md)