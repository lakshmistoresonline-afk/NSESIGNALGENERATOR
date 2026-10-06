# V29 India-Wide Accuracy Research & Implementation Notes

## Official NSE data requirements

NSE's official report catalogue currently exposes CM-UDiFF final bhavcopy, security-master files, security-wise delivery, daily volatility, surveillance indicators, price-band/security lists, short-selling reports, impact-cost reports and India VIX/history. NSE also provides historical index data and F&O report families. Production ingestion must use the actual artifact plus its availability semantics rather than treating a public URL as proof of possession.

NSE states that the legacy CM common/bhavcopy formats were discontinued in July 2024 in favor of the CM-UDiFF Common Bhavcopy Final format. The V29 archive adapters therefore retain UDiFF-oriented contracts.

The NSE equity regular session is 09:15–15:30 IST in the current exchange timing material. The system uses explicit Asia/Kolkata session timestamps and does not infer holidays outside its covered official calendar.

## Financial-ML validation principles

The package retains purged/embargoed temporal validation, CPCV/CSCV-style diagnostics, multiple-testing accounting, deflated-performance diagnostics, calibration, drift controls and economic-cost testing. These are safeguards against overfitting rather than guarantees of predictive accuracy.

Backtest-overfitting research shows that selecting among many configurations can materially inflate apparent historical performance. The Deflated Sharpe Ratio literature explicitly addresses selection bias and non-normal returns. Time-series conformal research also cautions that classical exchangeability assumptions do not directly hold under serial dependence and regime drift; V29 therefore treats conformal output as an abstention/uncertainty control, not as a guarantee of trading accuracy.

## V29 implementation decisions

1. Broad NSE `EQ` is the default universe. NIFTY 200 is retained only for benchmark research.
2. Secondary data providers never silently become a production source.
3. Panel models use timestamp-grouped walk-forward evaluation.
4. Panel economic backtests process each security independently.
5. Production publication requires PIT provenance and a non-empty NSE checksum manifest.
6. Restriction, price-band, short-sale and impact-cost context is required before publication.
7. Corporate-event context is required; conservative event blackouts are generated from timestamped event data.
8. Production factor support is directional and causal; no fixed factor-score placeholder remains.
9. Unknown calendar years fail closed.
10. Synthetic results remain software diagnostics only.

## Sources reviewed

- NSE India — All Reports / official market-data report catalogue.
- NSE India — Market Timings & Holidays.
- NSE India — Historical Reports / Capital Market daily and monthly archives.
- NSE India — Corporate Filings / Corporate Actions.
- Bailey, Borwein, López de Prado & Zhu — Probability of Backtest Overfitting.
- Bailey & López de Prado — Deflated Sharpe Ratio.
- 2025–2026 time-series conformal forecasting research on dependence and distribution shift.

## Production-readiness boundary

The repository is intentionally not marked production-ready merely because the code and tests pass. Authoritative point-in-time historical datasets, their licensing/possession, exact availability timestamps, effective-dated security identity, corporate adjustments/events, realistic transaction costs and an untouched chronological test period are required before live publication decisions can be evaluated.
