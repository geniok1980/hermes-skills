# Concrete Freqtrade Strategy: AIAgentStrategyV2

## Location
`/root/ai-agent-services/freqtrade-strategies/user_data/strategies/AIAgentStrategyV2.py`

## Performance
- **Trades:** 30 in 60 days (5m timeframe, BTC/ETH/SOL/BNB/USDT)
- **Win rate:** 66.7% (20 win, 0 draw, 10 loss)
- **Total profit:** -0.9% (slightly negative — needs further optimisation)
- **Drawdown:** 0.97% (low)
- **Win rate is strong but avg win < avg loss** → needs better exit logic or tighter stop

## Strategy Logic
- **Entry (all must be true):**
  1. EMA_short > EMA_long (uptrend)
  2. RSI(14) between 28 and 42
  3. MACD line > Signal line
  4. ADX(14) > 22
  5. Volume > 1.6x SMA(20)
  6. Price > BB lower band
- **Exit:**
  1. RSI > 71
  2. MACD line < Signal line

## Hyperopt Results (100 epochs, SharpeHyperOptLoss)
- buy_rsi: 28, buy_rsi_max: 42, buy_ema_short: 45, buy_ema_long: 213
- buy_adx: 22, buy_volume_factor: 1.6
- sell_rsi: 71
- minimal_roi: {"0": 0.164, "21": 0.093, "81": 0.037, "122": 0}
- stoploss: -0.05 (overridden from hyperopt's -0.339 for safety)

## Known Issues
- Strategy is slightly negative on 60d test period. Likely causes:
  - Market was sideways/down during test (Apr-Jun 2026)
  - Exit signals fire too late — losers exceed winners in size
  - ADX filter may be too strict, missing good trades
- Next iterations should try: SortinoHyperOptLoss, dynamic stoploss based on ATR, add Chandelier Exit

## How to run
```bash
cd /root/ai-agent-services/freqtrade-strategies
source .venv/bin/activate  # or use hermes venv at /usr/local/lib/hermes-agent/venv/bin/python
freqtrade backtesting --strategy AIAgentStrategyV2 --config config.json --timeframe 5m --timerange 20260404-20260603
```
