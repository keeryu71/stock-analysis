# Algorithmic Trading & Backtesting Framework

A comprehensive Python framework for developing, backtesting, and analyzing algorithmic trading strategies with a focus on robust performance evaluation and risk management.

## 🚀 Features

- **Modular Strategy Framework**: Easy-to-extend base classes for implementing custom trading strategies
- **Comprehensive Backtesting Engine**: Realistic simulation with transaction costs, slippage, and execution modeling
- **Advanced Performance Analytics**: 30+ performance metrics including Sharpe ratio, Sortino ratio, maximum drawdown, VaR, and more
- **Multiple Strategy Types**: Pre-built moving average, momentum, and mean reversion strategies
- **Data Management**: Automated data fetching from Yahoo Finance with technical indicator calculation
- **Risk Management**: Built-in position sizing, stop-loss, and portfolio risk controls
- **Interactive Notebooks**: Jupyter notebooks for strategy development, analysis, and optimization
- **Visualization Tools**: Comprehensive plotting for performance analysis and trade visualization

## 📁 Project Structure

```
algorithmic-trading-project/
├── src/
│   ├── backtesting/
│   │   ├── engine.py              # Main backtesting engine
│   │   ├── strategy_base.py       # Abstract strategy base class
│   │   └── portfolio.py           # Portfolio management utilities
│   ├── strategies/
│   │   ├── moving_average.py      # Moving average strategies
│   │   ├── momentum.py            # Momentum-based strategies
│   │   └── mean_reversion.py      # Mean reversion strategies
│   ├── data/
│   │   └── data_loader.py         # Data fetching and processing
│   ├── utils/
│   │   ├── metrics.py             # Performance metrics
│   │   ├── risk.py                # Risk management tools
│   │   └── visualization.py       # Plotting utilities
│   └── config.py                  # Configuration management
├── notebooks/
│   ├── 01_strategy_development.ipynb    # Strategy development guide
│   ├── 02_backtesting_analysis.ipynb   # Backtesting analysis
│   └── 03_strategy_optimization.ipynb  # Parameter optimization
├── tests/                         # Unit tests
├── data/                          # Data storage
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download the project**:
   ```bash
   git clone <repository-url>
   cd algorithmic-trading-project
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (optional):
   Create a `.env` file in the project root:
   ```
   ALPHA_VANTAGE_API_KEY=your_api_key_here
   POLYGON_API_KEY=your_api_key_here
   ```

## 🚀 Quick Start

### 1. Basic Strategy Backtesting

```python
import sys
sys.path.append('src')

from data.data_loader import DataLoader
from backtesting.engine import BacktestEngine
from strategies.moving_average import MovingAverageCrossover

# Load data
loader = DataLoader()
data = loader.fetch_stock_data(['AAPL'], '2020-01-01', '2023-12-31')

# Create strategy
strategy = MovingAverageCrossover(short_window=20, long_window=50)

# Run backtest
engine = BacktestEngine()
results = engine.run_backtest(strategy, data['AAPL'])

print(f"Total Return: {results['total_return']:.2%}")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.3f}")
print(f"Max Drawdown: {results['max_drawdown']:.2%}")
```

### 2. Advanced Fibonacci MACD Strategy

```python
from strategies.fibonacci_macd_strategy import FibonacciMACDStrategy

# Create advanced multi-indicator strategy
strategy = FibonacciMACDStrategy(
    fibonacci_period=50,
    macd_fast=12, macd_slow=26, macd_signal=9,
    rsi_period=14, rsi_oversold=30, rsi_overbought=70,
    volume_threshold=1.2,  # 20% above average volume
    min_confidence=0.6     # 60% minimum confidence
)

# Run backtest
results = engine.run_backtest(strategy, data['AAPL'])
print(f"Total Return: {results['total_return']:.2%}")
print(f"Total Trades: {results['total_trades']}")
```

### 3. Multi-Strategy Comparison

```python
from strategies.moving_average import MovingAverageCrossover, ExponentialMovingAverageCrossover

# Create multiple strategies
strategies = [
    MovingAverageCrossover(short_window=20, long_window=50),
    ExponentialMovingAverageCrossover(short_span=12, long_span=26)
]

# Run comparison
results = engine.run_multiple_backtests(strategies, data['AAPL'])
summary = engine.get_results_summary()
print(summary)
```

### 3. Using Jupyter Notebooks

Start Jupyter and open the example notebooks:

```bash
jupyter notebook notebooks/01_strategy_development.ipynb
```

## 📊 Available Strategies

### Moving Average Strategies

1. **Simple Moving Average Crossover**
   - Buy when short MA crosses above long MA
   - Sell when short MA crosses below long MA
   - Configurable windows and signal thresholds

2. **Exponential Moving Average Crossover**
   - Uses exponential moving averages for faster response
   - Better for trending markets
   - Configurable spans and sensitivity

3. **Triple Moving Average System**
   - Uses three MAs for more robust signals
   - Requires alignment of all three averages
   - Higher confidence, fewer false signals

### Advanced Multi-Indicator Strategies

1. **Fibonacci MACD Strategy** ⭐ **NEW**
   - **Fibonacci Retracement Levels**: Identifies optimal entry points at key support/resistance levels (23.6%, 38.2%, 50%, 61.8%)
   - **MACD Confirmation**: Bullish crossover signals with momentum confirmation
   - **RSI Analysis**: Prevents entries at overbought levels, favors oversold recovery
   - **Volume Confirmation**: Requires above-average volume (20%+) with positive trend
   - **Confidence Scoring**: Multi-factor confidence system (minimum 60% required)
   - **Risk Management**: Built-in stop-loss (8%) and take-profit (15%) levels
   - **Dynamic Position Sizing**: Position size scales with signal confidence

### Momentum Strategies

1. **Price Momentum**
   - Based on rate of change in prices
   - Configurable lookback periods
   - Momentum threshold filtering

2. **RSI Strategy**
   - Relative Strength Index based signals
   - Overbought/oversold levels
   - Mean reversion approach

### Mean Reversion Strategies

1. **Bollinger Bands**
   - Statistical mean reversion
   - Dynamic support/resistance levels
   - Volatility-adjusted signals

2. **Z-Score Reversion**
   - Statistical z-score based entries
   - Configurable lookback and thresholds
   - Risk-adjusted position sizing

## 📈 Performance Metrics

The framework calculates 30+ performance metrics:

### Return Metrics
- Total Return
- Annualized Return
- Compound Annual Growth Rate (CAGR)
- Average Daily/Monthly Returns

### Risk Metrics
- Sharpe Ratio
- Sortino Ratio
- Calmar Ratio
- Maximum Drawdown
- Value at Risk (VaR)
- Conditional VaR (CVaR)
- Beta vs Benchmark
- Alpha vs Benchmark

### Trade Metrics
- Win Rate
- Profit Factor
- Average Win/Loss
- Expectancy
- Maximum Consecutive Wins/Losses
- Average Holding Period

## ⚙️ Configuration

### Trading Parameters

Edit `src/config.py` to customize:

```python
@dataclass
class TradingConfig:
    initial_capital: float = 100000.0
    commission: float = 0.001          # 0.1%
    slippage: float = 0.0005           # 0.05%
    max_position_size: float = 0.1     # 10% max per position
    stop_loss_pct: float = 0.02        # 2% stop loss
    take_profit_pct: float = 0.06      # 6% take profit
```

### Strategy Parameters

Each strategy has configurable parameters:

```python
# Moving Average Strategy
strategy = MovingAverageCrossover(
    short_window=20,
    long_window=50,
    signal_threshold=0.01,
    position_size_pct=0.1
)
```

## 🔧 Creating Custom Strategies

Extend the `StrategyBase` class to create custom strategies:

```python
from backtesting.strategy_base import StrategyBase, Signal, SignalType

class MyCustomStrategy(StrategyBase):
    def __init__(self, param1=10, param2=0.02):
        super().__init__("MyCustomStrategy")
        self.param1 = param1
        self.param2 = param2
    
    def generate_signals(self, data):
        signals = []
        # Your signal generation logic here
        # Return list of Signal objects
        return signals
    
    def calculate_position_size(self, signal, available_cash):
        # Your position sizing logic here
        return position_size
```

## 📊 Data Sources

### Supported Data Sources
- **Yahoo Finance** (default, free)
- **Alpha Vantage** (API key required)
- **Polygon.io** (API key required)
- **Custom CSV files**

### Data Features
- Automatic technical indicator calculation
- Multiple timeframes (1m, 5m, 1h, 1d, 1w, 1M)
- Data validation and cleaning
- Missing data handling

## 🧪 Testing

Run the test suite:

```bash
python -m pytest tests/
```

Run specific test categories:

```bash
# Test strategies
python -m pytest tests/test_strategies.py

# Test backtesting engine
python -m pytest tests/test_engine.py

# Test performance metrics
python -m pytest tests/test_metrics.py
```

## 📚 Examples

### Example 1: Simple Buy and Hold vs MA Strategy

```python
# Compare buy-and-hold with moving average strategy
from strategies.buy_and_hold import BuyAndHold

strategies = [
    BuyAndHold(),
    MovingAverageCrossover(20, 50)
]

results = engine.run_multiple_backtests(strategies, data)
```

### Example 2: Portfolio of Strategies

```python
# Run multiple strategies on different assets
symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
data = loader.fetch_stock_data(symbols, '2020-01-01', '2023-12-31')

for symbol in symbols:
    strategy = MovingAverageCrossover(20, 50)
    result = engine.run_backtest(strategy, data[symbol])
    print(f"{symbol}: {result['total_return']:.2%}")
```

### Example 3: Parameter Optimization

```python
from itertools import product

# Test different parameter combinations
short_windows = [10, 15, 20, 25]
long_windows = [40, 50, 60, 70]

best_sharpe = -999
best_params = None

for short, long in product(short_windows, long_windows):
    if short >= long:
        continue
    
    strategy = MovingAverageCrossover(short, long)
    result = engine.run_backtest(strategy, data['AAPL'])
    
    if result['sharpe_ratio'] > best_sharpe:
        best_sharpe = result['sharpe_ratio']
        best_params = (short, long)

print(f"Best parameters: {best_params}, Sharpe: {best_sharpe:.3f}")
```

## 🚨 Risk Warnings

**Important**: This framework is for educational and research purposes only. 

- **Past performance does not guarantee future results**
- **Backtesting can overfit to historical data**
- **Real trading involves additional risks not captured in simulation**
- **Always paper trade strategies before using real money**
- **Consider transaction costs, slippage, and market impact**
- **Diversify your strategies and risk management**

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run pre-commit hooks
pre-commit install

# Run full test suite
python -m pytest tests/ --cov=src/
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Yahoo Finance** for providing free financial data
- **pandas** and **numpy** for data manipulation
- **matplotlib** and **seaborn** for visualization
- **Jupyter** for interactive development environment

## 📞 Support

For questions, issues, or contributions:

1. Check the [Issues](../../issues) page
2. Review the [Wiki](../../wiki) for detailed documentation
3. Join our [Discussions](../../discussions) for community support

## 🗺️ Roadmap

### Upcoming Features

- [ ] **Machine Learning Strategies**: Integration with scikit-learn and TensorFlow
- [ ] **Options Trading**: Support for options strategies and Greeks calculation
- [ ] **Cryptocurrency Support**: Integration with crypto exchanges
- [ ] **Real-time Trading**: Live trading capabilities with broker APIs
- [ ] **Web Dashboard**: Interactive web interface for strategy monitoring
- [ ] **Advanced Risk Models**: VaR models, stress testing, scenario analysis
- [ ] **Multi-asset Strategies**: Portfolio optimization and asset allocation
- [ ] **Alternative Data**: Integration with sentiment, news, and economic data

### Version History

- **v1.0.0**: Initial release with basic backtesting framework
- **v1.1.0**: Added performance metrics and risk analysis
- **v1.2.0**: Jupyter notebook integration and visualization tools
- **v1.3.0**: Strategy optimization and parameter tuning (planned)

---

**Happy Trading! 📈**

*Remember: The best strategy is the one you understand and can stick with through different market conditions.*