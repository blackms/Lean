# Architecture Overview

## Introduction

QuantConnect Lean is designed with a modular, event-driven architecture that separates concerns into distinct components. This section provides a high-level overview of the system architecture, explaining how the various components interact to form a complete algorithmic trading platform.

## Key Architectural Principles

1. **Modularity**: Lean is built with a plugin architecture where components can be replaced or extended without affecting the rest of the system.

2. **Event-Driven**: The system processes market data and other events in an event-driven manner, with algorithms responding to these events.

3. **Separation of Concerns**: The system separates different responsibilities into distinct components, such as data management, algorithm execution, portfolio management, and order execution.

4. **Extensibility**: The architecture is designed to be easily extended with new data sources, asset classes, and trading strategies.

## Core Components

### Algorithm Manager

The `AlgorithmManager` is the central component that coordinates the execution of trading algorithms. It:

- Manages the lifecycle of algorithm instances
- Processes data events and routes them to the appropriate algorithm handlers
- Coordinates between data feeds, transaction handlers, and result handlers
- Monitors algorithm performance and enforces resource limits

### Data System

The data system is responsible for acquiring, processing, and delivering market data to algorithms:

- **SubscriptionManager**: Manages data subscriptions for different securities and data types
- **DataFeeds**: Provides data from various sources (historical databases, live feeds)
- **Consolidators**: Aggregates tick data into bars (OHLCV) of different resolutions
- **Slices**: Packages data points from multiple sources into time-synchronized slices

### Securities System

The securities system manages the universe of tradable assets:

- **SecurityManager**: Maintains the collection of securities in the algorithm
- **Security Models**: Defines the behavior of different asset classes
- **Market Hours**: Manages trading hours and holidays for different markets
- **Pricing Models**: Calculates fair values for different security types

### Portfolio and Order Management

These components handle the financial aspects of the algorithm:

- **Portfolio Manager**: Tracks positions, cash balances, and overall portfolio value
- **Transaction Manager**: Processes orders and executions
- **Brokerage Models**: Simulates or interfaces with real brokerages
- **Fee Models**: Calculates transaction costs and fees

### Algorithm Framework

The Algorithm Framework provides a structured approach to building trading strategies:

- **Alpha Models**: Generate trading signals (insights)
- **Portfolio Construction Models**: Determine position sizes based on insights
- **Execution Models**: Convert target portfolios into orders
- **Risk Management Models**: Apply risk controls to orders
- **Universe Selection Models**: Select assets to trade

## System Flow

1. The `AlgorithmManager` initializes the algorithm and its dependencies
2. Data feeds provide market data to the algorithm
3. The algorithm processes the data and generates insights through alpha models
4. Portfolio construction models convert insights into target portfolios
5. Execution models place orders to achieve the target portfolio
6. Risk management models apply risk controls to the orders
7. Transaction handlers execute the orders
8. Results are logged and reported

## Deployment Architecture

Lean can be deployed in different configurations:

1. **Local Backtesting**: Running historical simulations on a local machine
2. **Cloud Backtesting**: Running simulations in a cloud environment
3. **Live Trading**: Connecting to brokerages for real-time trading
4. **Research Environment**: Interactive analysis using Jupyter notebooks

## Next Steps

For more detailed information about the architecture, refer to:

- [System Design](./system-design.md): Detailed explanation of the system design patterns
- [Data Flow](./data-flow.md): How data flows through the system
- [Component Relationships](./component-relationships.md): How components interact with each other