# Unified implementation matrix

| Capability | Unified location | Source inspiration |
|---|---|---|
| Signal-only safety | `src/nse_signal/signals/engine.py`, `server/api.py` | TradeMindAI + intraday AI |
| Regime classification | `src/nse_signal/integrations/trademind_core.py` | TradeMindAI |
| ATR risk geometry | `src/nse_signal/integrations/trademind_core.py` | TradeMindAI |
| OOS / walk-forward | `src/nse_signal/models/` | BharatMarketAI + intraday AI |
| Factor ranking | `src/nse_signal/research/factors.py` | NSE factor backtest |
| Cost-aware research | `src/nse_signal/backtest/`, `integrations/research_controls.py` | NSE factor + Dhan lab + EdgeLab |
| Statistical diagnostics | `src/nse_signal/research/statistics.py` + research controls | intraday AI + NSE factor |
| Outcome lifecycle | `src/nse_signal/backtest/engine.py` | TradeMindAI |
| Android client | `android/` | New unified client |
| Python API | `server/api.py` | New unified service boundary |
