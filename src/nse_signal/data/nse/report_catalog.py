"""Official NSE report catalog used by the PIT ingestion planner.

URLs here are landing pages, not guessed download endpoints, except for deterministic
UDiFF archive families implemented in archives.py. This avoids hard-coding fragile
web-app endpoints for reports whose delivery mechanism can change.
"""
REPORTS = {
    "cash_bhavcopy": "https://www.nseindia.com/all-reports",
    "fo_bhavcopy": "https://www.nseindia.com/all-reports-derivatives",
    "historical_equity": "https://www.nseindia.com/resources/historical-reports-capital-market-daily-monthly-archives",
    "corporate_actions": "https://www.nseindia.com/companies-listing/corporate-filings-actions",
    "index_data": "https://www.nseindia.com/resources/historical-reports-capital-market-daily-monthly-archives",
    "nifty200": "https://www.nseindia.com/static/products-services/indices-nifty200-index",
    "option_chain": "https://www.nseindia.com/option-chain",
    "fo_historical": "https://www.nseindia.com/report-detail/fo_eq_security",
    "real_time_data": "https://www.nseindia.com/static/market-data/real-time-data-subscription",
}
