# Authoritative Historical PIT Data Gap Register — 2026-10-03

## Executive finding
The V21 package contains the acquisition/validation machinery but **does not contain, and the user has not supplied evidence of licenses for, the historical PIT datasets needed for a production-grade survivorship-free NSE signal research system**.

A URL is not a dataset and a public report page is not proof of historical completeness or commercial redistribution rights.

## Datasets not supplied/licensed

| Layer | Required for | Status | Authority / acquisition basis |
|---|---|---|---|
| Historical CM EOD | primary OHLCV/security history | **NOT SUPPLIED/LICENSED** | NSE Data & Analytics historical EOD product |
| Historical F&O EOD | derivatives features | **NOT SUPPLIED/LICENSED** | NSE Data & Analytics historical EOD product |
| Historical securities/contracts master | PIT identity/symbol lifecycle | **NOT SUPPLIED/LICENSED** | NSE historical master offering |
| Historical order & trade | true intraday/microstructure features | **NOT SUPPLIED/LICENSED** | NSE Historical Order & Trade product |
| Historical Nifty 200 constituents | survivorship-free universe | **NOT SUPPLIED/LICENSED** | NSE Indices historical constituent subscription |
| PIT corporate data | fundamentals/revisions/events | **NOT SUPPLIED/LICENSED** | NSE Corporate Data / EOD Corporate Announcement products |
| Historical index constituent weights | cross-sectional/index features | **NOT BUNDLED** | NSE Indices historical constituent data |
| Historical index OHLC/valuation | benchmark/regime features | **NOT BUNDLED** | NSE Indices historical reports |
| Timestamped historical news | news features | **NOT SUPPLIED/LICENSED** | Separate licensed provider required |
| Vintage/revision-aware fundamentals | true PIT fundamental features | **NOT SUPPLIED/LICENSED** | NSE Corporate Data or suitable licensed vendor |

NSE's official historical-data page identifies paid EOD and historical trade products, and its Historical Order & Trade offering covers CM/F&O order and trade history. citeturn0search0turn1search0

NSE's official policy states that subscribers must enter the relevant agreement and that usage, handling and redistribution are governed by those terms. citeturn0search2turn1search4

NSE's corporate-data page separately lists historical/company disclosure products, including fundamentals, announcements and shareholding data. citeturn1search1

NSE Indices explicitly offers ongoing and historical index constituent data by subscription. citeturn1search2

## Important distinction

The following official daily reports may be obtainable from NSE report pages, but they are still **not considered supplied merely because the website exposes a report**:

- delivery
- impact cost
- daily volatility
- surveillance
- price bands
- short selling
- participant OI
- FII derivatives statistics
- India VIX
- breadth

The repository requires actual downloaded files, SHA-256 provenance, coverage validation, availability timestamps and applicable usage rights before these become production PIT layers. NSE's current report catalog confirms the availability of many of these CM and F&O reports. citeturn0search4turn0search5

## Historical Nifty 200

The current Nifty 200 CSV is **not historical PIT membership**. NSE's current Nifty 200 page publishes the current constituent list, while NSE Indices separately offers historical constituent data. citeturn0search9turn1search2

Therefore the repository must not reconstruct historical Nifty 200 membership by applying today's list backward.

## Required acquisition order

1. Historical CM EOD + security master.
2. Historical Nifty 200 constituent snapshots/effective intervals.
3. Corporate actions and timestamped corporate announcements.
4. Historical F&O EOD.
5. Delivery/impact-cost/restriction/volatility layers.
6. Historical index data.
7. Historical order/trade data only if microstructure features are enabled.
8. Timestamped news only if the news feature family is enabled.
9. Vintage/revision-aware fundamentals before enabling fundamental features.

Until these dependencies are populated and validated, the publication gate must remain closed.
