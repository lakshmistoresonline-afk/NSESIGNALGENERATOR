"""Explicit source contracts for secondary NSE/PIT data layers."""
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class SourceContract:
    name: str
    official_url: str
    mode: Literal['public_archive','web_report','licensed_required','user_supplied']
    required_timestamp: str
    status: str

CONTRACTS = {
 'delivery': SourceContract('Security-wise Delivery Positions','https://www.nseindia.com/all-reports','web_report','trade_date/eod_availability','ready_for_local_acquisition'),
 'impact_cost': SourceContract('Security Category Impact Cost','https://www.nseindia.com/all-reports','web_report','report_date/eod_availability','ready_for_local_acquisition'),
 'breadth': SourceContract('Advances/Declines','https://www.nseindia.com/resources/historical-reports-capital-market-daily-monthly-archives','web_report','trade_date/eod_availability','ready_for_local_acquisition'),
 'india_vix': SourceContract('Historical Data - India VIX','https://www.nseindia.com/resources/historical-reports-capital-market-daily-monthly-archives','web_report','trade_date/eod_availability','ready_for_local_acquisition'),
 'corporate_events': SourceContract('Corporate Filings / Corporate Actions','https://www.nseindia.com/companies-listing/corporate-filings-actions','web_report','true announcement/broadcast timestamp','ready_with_timestamp_required'),
 'fundamentals': SourceContract('Point-in-time fundamentals','https://www.nseindia.com/companies-listing/corporate-filings-actions','user_supplied','actual information availability timestamp','external_PIT_source_required'),
 'surveillance': SourceContract('Surveillance Indicator','https://www.nseindia.com/all-reports','web_report','trade_date/eod_availability','ready_for_local_acquisition'),
 'price_bands': SourceContract('Price Band / Security List','https://www.nseindia.com/all-reports','web_report','trade_date/eod_availability','ready_for_local_acquisition'),
 'short_selling': SourceContract('Short Selling','https://www.nseindia.com/all-reports','web_report','trade_date/eod_availability','ready_for_local_acquisition'),
 'participant_oi': SourceContract('Participant-wise Open Interest','https://www.nseindia.com/all-reports-derivatives','web_report','trade_date/eod_availability','ready_for_local_acquisition'),
 'fii_derivatives': SourceContract('FII Derivatives Statistics','https://www.nseindia.com/all-reports-derivatives','web_report','trade_date/eod_availability','ready_for_local_acquisition'),
 'daily_volatility': SourceContract('CM Daily Volatility','https://www.nseindia.com/all-reports','web_report','trade_date/eod_availability','ready_for_local_acquisition'),
 'derivatives': SourceContract('F&O historical reports','https://www.nseindia.com/all-reports-derivatives','public_archive','trade_date/eod_availability','integrated'),
}

def contract(name): return CONTRACTS[name]
