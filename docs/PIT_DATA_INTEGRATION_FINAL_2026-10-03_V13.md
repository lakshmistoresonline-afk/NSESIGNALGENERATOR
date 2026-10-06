# PIT NSE Data Integration — V13

## Integrated layers
- CM UDiFF equity
- F&O UDiFF
- dated security master
- historical index data
- delivery
- impact cost
- advances/declines
- India VIX
- surveillance indicator
- price-band/security list
- short-selling context
- participant OI adapter
- FII derivatives adapter
- daily volatility adapter
- corporate-event PIT interface
- PIT fundamentals interface
- authoritative corporate-adjustment interface

## Derived derivatives context
When IV/OI/option rows are present:
- nearest-expiry DTE
- put/call OI ratio
- put/call volume ratio
- put/call OI-change ratio
- weighted IV
- put IV / call IV
- put-minus-call IV skew
- ATM-strike OI share
- nearest-expiry futures/spot basis can be added from futures rows

## Acquisition rule
Official files are acquired locally, hashed, normalized and stored with provenance. The package does not claim that external/licensed historical data is populated until the files are actually supplied/acquired.
