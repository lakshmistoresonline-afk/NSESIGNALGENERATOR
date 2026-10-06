"""Authoritative NSE/NSE Indices PIT data contracts and acquisition planning.

This module deliberately separates *source authority* from *local availability*.
It never synthesizes historical observations.  A layer is production-eligible only
when its official artifact has been downloaded, hashed, normalized and passed the
PIT contract checks.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import date
from pathlib import Path
import json

@dataclass(frozen=True)
class SourceSpec:
    layer: str
    authority: str
    landing_url: str
    url_template: str | None
    cadence: str
    pit_role: str
    availability_rule: str
    notes: str

SOURCES = (
    SourceSpec("cash_bhavcopy", "NSE India", "https://www.nseindia.com/all-reports", "https://archives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{YYYYMMDD}_F_0000.csv.zip", "daily", "primary", "EOD artifact; usable only after its verified availability timestamp", "Official CM-UDiFF final bhavcopy."),
    SourceSpec("fo_bhavcopy", "NSE India", "https://www.nseindia.com/all-reports-derivatives", "https://archives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_{YYYYMMDD}_F_0000.csv.zip", "daily", "primary", "EOD artifact; usable only after its verified availability timestamp", "Official F&O-UDiFF final bhavcopy."),
    SourceSpec("security_master", "NSE India", "https://www.nseindia.com/all-reports", "https://archives.nseindia.com/content/cm/NSE_CM_security_{DDMMYYYY}.csv.gz", "daily", "identity", "Master is effective only from its published/as-of timestamp", "Official NSE listed-security master."),
    SourceSpec("index_close", "NSE India", "https://www.nseindia.com/all-reports", "https://archives.nseindia.com/content/indices/ind_close_all_{DDMMYYYY}.csv", "daily", "benchmark", "EOD index report; verified availability required", "Official NSE index close report."),
    SourceSpec("delivery", "NSE India / NSE Clearing", "https://www.nseindia.com/static/products-services/equity-market-data-reports-download", None, "daily", "secondary", "Use true report publication/availability time; do not infer intraday availability", "Security-wise delivery data."),
    SourceSpec("impact_cost", "NSE India", "https://www.nseindia.com/all-reports", None, "daily/monthly", "secondary", "Use report's effective date and verified publication time", "Security-category impact-cost report."),
    SourceSpec("daily_volatility", "NSE India", "https://www.nseindia.com/all-reports", None, "daily", "secondary", "EOD publication", "Official CM daily volatility."),
    SourceSpec("participant_oi", "NSE India", "https://www.nseindia.com/all-reports-derivatives", None, "daily", "secondary", "Report publication time must be respected", "Participant-wise open interest."),
    SourceSpec("fii_derivatives", "NSE India", "https://www.nseindia.com/all-reports-derivatives", None, "daily", "secondary", "Report publication time must be respected", "FII derivatives statistics."),
    SourceSpec("surveillance", "NSE India", "https://www.nseindia.com/all-reports", None, "daily", "restriction", "Effective from report date/time", "Surveillance indicator."),
    SourceSpec("price_bands", "NSE India", "https://www.nseindia.com/all-reports", None, "daily", "restriction", "Use next-trade-date/effective-date semantics", "Price-band complete list and changes."),
    SourceSpec("short_selling", "NSE India", "https://www.nseindia.com/all-reports", None, "daily", "restriction", "Use actual report date/effective semantics", "Short-selling report."),
    SourceSpec("india_vix", "NSE India / NSE Indices", "https://www.nseindia.com/all-reports", None, "daily", "market_state", "EOD publication; no same-session use unless timestamped", "India VIX historical data."),
    SourceSpec("nifty200_membership", "NSE India / NSE Indices", "https://www.nseindia.com/static/products-services/indices-nifty200-index", "https://nsearchives.nseindia.com/content/indices/ind_nifty200list.csv", "review/event", "universe", "Current list is not historical PIT; historical constituent data requires dated official records or licensed historical constituent data", "Do not use today's constituent list for historical backtests."),
    SourceSpec("nifty_index_history", "NSE Indices", "https://www.niftyindices.com/reports", None, "daily", "benchmark", "Historical index observations are official when obtained from NSE Indices", "Historical index OHLC/returns/valuation reports."),
    SourceSpec("corporate_actions", "NSE India / NSE Clearing", "https://www.nseindia.com/static/products-services/equity-market-data-reports-download", None, "event", "adjustment", "Announcement/broadcast timestamp required for PIT; ex/record dates are separate event dates", "Corporate-action report contains record/book closure/ex-date fields."),
    SourceSpec("corporate_filings", "NSE India", "https://www.nseindia.com/companies-listing/corporate-filings-actions", None, "event", "fundamental_event", "Use the actual NSE broadcast/publication timestamp", "Event-level corporate filings/actions."),
)

def catalog() -> dict:
    return {"version": "2.0", "authority_policy": "official_nse_only_for_production", "sources": [asdict(x) for x in SOURCES]}

def write_catalog(path="data/reference/authoritative_pit_dataset_catalog.json"):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(catalog(),indent=2,sort_keys=True),encoding="utf-8"); return p

def required_layers() -> list[str]:
    return ["cash_bhavcopy","fo_bhavcopy","security_master","delivery","impact_cost","daily_volatility","surveillance","price_bands","short_selling","india_vix"]
