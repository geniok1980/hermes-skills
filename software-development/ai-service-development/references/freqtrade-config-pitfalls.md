# Freqtrade Config Pitfalls

## Required config blocks (or backtest crashes)

These three blocks MUST be present in the config:

```json
{
  "exchange": {
    "name": "binance",
    "pair_whitelist": ["BTC/USDT", "ETH/USDT", "SOL/USDT"],
    "ccxt_config": { "rateLimit": 200 }
  },
  "entry_pricing": {
    "price_side": "same",
    "use_order_book": false,
    "price_last_balance": 0.0
  },
  "exit_pricing": {
    "price_side": "ask",
    "use_order_book": false,
    "price_last_balance": 0.0
  }
}
```

## Common errors and fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `KeyError: 'exchange'` | No `exchange.name` in config | Add `exchange.name: "binance"` |
| `{'pairs': [...]} is not of type 'array'` | `pair_whitelist` wrapped in object | Flatten to array: `["BTC/USDT"]` |
| `KeyError: 'exit_pricing'` | Missing exit_pricing block | Add exit_pricing with price_side/use_order_book |
| `KeyError: 'entry_pricing'` | Missing entry_pricing block | Add entry_pricing with price_side/use_order_book |
| `No module named 'optuna'` | optuna not in freqtrade's venv | `uv pip install --python /path/to/venv/bin/python optuna scikit-learn` |

## Command cheatsheet

```bash
# Download data
freqtrade download-data --exchange binance --pairs BTC/USDT ETH/USDT --days 60 --timeframe 5m -c config.json

# Backtest
freqtrade backtesting --strategy AIAgentStrategyV2 --config config.json --timeframe 5m --timerange 20260404-20260603

# Hyperopt
freqtrade hyperopt --strategy AIAgentStrategyV2 --config config.json --timeframe 5m --timerange 20260404-20260603 --hyperopt-loss SharpeHyperOptLoss --epochs 100
```

## Strategy template structure

Minimal starter strategy with all required methods:

```python
from functools import reduce
import talib.abstract as ta
from pandas import DataFrame
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter

class MyStrategy(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = "5m"
    startup_candle_count = 200
    minimal_roi = {"0": 0.1, "30": 0.05, "120": 0}
    stoploss = -0.05
    trailing_stop = True

    def populate_indicators(self, dataframe, metadata):
        # Add EMA, RSI, MACD, Bollinger...
        return dataframe

    def populate_entry_trend(self, dataframe, metadata):
        conditions = [ ... ]
        dataframe.loc[reduce(lambda x, y: x & y, conditions), "enter_long"] = 1
        return dataframe

    def populate_exit_trend(self, dataframe, metadata):
        conditions = [ ... ]
        dataframe.loc[reduce(lambda x, y: x & y, conditions), "exit_long"] = 1
        return dataframe
```

## Sellable strategy requirement

A strategy is sellable when:
- Backtest shows positive profit over 30+ days
- Win rate >= 60%
- Max drawdown < 10% 
- At least 20+ trades in the period
- Includes hyperopt-optimised parameters
- Has clear documentation and config file
