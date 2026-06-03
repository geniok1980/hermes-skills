# Freqtrade Strategy AIAgentStrategyV2

## Model definition
`opencode/deepseek-v4-flash-free`

## Performance (60 days, 5m, spot)
- Trades: 30
- Win rate: 66.7% (20/10)
- Total profit: -0.9% (-9 USDT from 1000)
- Max drawdown: 0.97%
- Duration: 60 days (Apr-Jun 2026)
- Pairs: BTC/USDT, ETH/USDT, SOL/USDT, BNB/USDT

## Entry signals
1. EMA_short > EMA_long (uptrend)
2. RSI(14) between buy_rsi (28) and buy_rsi_max (42)
3. MACD line > Signal line
4. ADX(14) > 22 (trend strength)
5. Volume > 1.6x SMA(20)
6. Price > BB lower band

## Exit signals
1. RSI > 71
2. MACD line < Signal line

## Risk management
- Stoploss: -5%
- Trailing stop: enabled, 1.5% once 3% profit reached
- ROI: 10% immediately → 0% over 2h

## Hyperopt results (100 epochs, SharpeHyperOptLoss)
Best params found:
```python
buy_params = {
    "buy_adx": 22,
    "buy_ema_long": 213,
    "buy_ema_short": 45,
    "buy_rsi": 28,
    "buy_rsi_max": 42,
    "buy_volume_factor": 1.6,
}
sell_params = {"sell_rsi": 71}
minimal_roi = {"0": 0.164, "21": 0.093, "81": 0.037, "122": 0}
stoploss = -0.05  # 5% (hyperopt suggested 33.9% — too high, hardcoded 5%)
```

## File location
`/root/ai-agent-services/freqtrade-strategies/user_data/strategies/AIAgentStrategyV2.py`

## Config pitfalls
See `references/freqtrade-config-pitfalls.md` in this skill.
