"""Normalize NSE UDiFF/public reports into the platform's canonical schemas."""
from __future__ import annotations
from pathlib import Path
import gzip, io, zipfile
import pandas as pd
from .session_calendar import next_trading_day, session_close_utc, session_open_utc

ALIASES = {
    "symbol": ["TckrSymb", "SYMBOL", "Symbol"],
    "isin": ["ISIN", "ISINCode"],
    "series": ["SctySrs", "SERIES", "Series"],
    "date": ["TradDt", "BizDt", "Date", "DATE"],
    "open": ["OpnPric", "OPEN", "Open Price"],
    "high": ["HghPric", "HIGH", "High Price"],
    "low": ["LwPric", "LOW", "Low Price"],
    "close": ["ClsPric", "CLOSE", "Close Price"],
    "volume": ["TtlTradgVol", "TOTTRDQTY", "Total Traded Quantity"],
    "turnover": ["TtlTrfVal", "TOTTRDVAL", "Turnover"],
    "trades": ["TtlNbOfTxsExctd", "TOTALTRADES", "No. of Trades"],
    "oi": ["OpnIntrst", "OPEN_INT"],
    "oi_change": ["ChngInOpnIntrst", "CHG_IN_OI"],
    "underlying": ["UndrlygPric", "UNDERLYING_VALUE"],
    "expiry": ["XpryDt", "EXPIRY_DT"],
    "strike": ["StrkPric", "STRIKE_PR"],
    "option_type": ["OptnTp", "OPTION_TYP"],
    "iv": ["ImpliedVolatility", "Implied Volatility", "IV", "IMPL_VOL"],
    "trade_status": ["TradSts", "Trade Status", "TRAD_STS"],
}


def _read_any(path: str | Path) -> pd.DataFrame:
    p = Path(path)
    raw = p.read_bytes()
    if p.suffix == ".zip":
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            names = [n for n in z.namelist() if n.lower().endswith('.csv')]
            if not names: raise ValueError(f"No CSV in {p}")
            return pd.read_csv(z.open(names[0]))
    if p.suffix == ".gz": return pd.read_csv(gzip.open(p, "rb"))
    return pd.read_csv(p)


def _rename(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for target, candidates in ALIASES.items():
        for c in candidates:
            if c in out.columns:
                out = out.rename(columns={c: target}); break
    return out


def normalize_cash(path: str | Path) -> pd.DataFrame:
    df = _rename(_read_any(path))
    required = ["symbol", "date", "open", "high", "low", "close", "volume"]
    missing = [c for c in required if c not in df.columns]
    if missing: raise ValueError(f"Cash report missing required columns: {missing}")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for c in ["open","high","low","close","volume","turnover"]:
        if c in df: df[c] = pd.to_numeric(df[c], errors="coerce")
    if "series" in df: df = df[df["series"].isin(["EQ","BE","BZ"])].copy()
    # EOD cash data describes the completed trading session.  A daily signal using
    # this row is executable no earlier than the next NSE regular-session open.
    # We retain both market_time and signal_time to prevent accidental same-session use.
    df["market_time"] = df["date"].map(session_close_utc)
    df["signal_time"] = df["date"].map(session_open_utc)
    # signal_time is replaced with the next trading session open below.
    df["signal_time"] = df["date"].map(next_trading_day).map(session_open_utc)
    df["asof_time"] = df["signal_time"]
    return df.sort_values(["date","symbol"]).reset_index(drop=True)


def normalize_fo(path: str | Path) -> pd.DataFrame:
    df = _rename(_read_any(path))
    if "date" not in df: raise ValueError("F&O report has no trade date")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for c in ["open","high","low","close","volume","turnover","oi","oi_change","underlying","strike"]:
        if c in df: df[c] = pd.to_numeric(df[c], errors="coerce")
    df["market_time"] = df["date"].map(session_close_utc)
    df["signal_time"] = df["date"].map(next_trading_day).map(session_open_utc)
    df["asof_time"] = df["signal_time"]
    return df.reset_index(drop=True)


def normalize_security_master(path: str | Path) -> pd.DataFrame:
    df = _rename(_read_any(path))
    if "symbol" not in df: raise ValueError("Security master has no symbol column")
    df["asof_time"] = pd.Timestamp(Path(path).stem[:10], tz="Asia/Kolkata").tz_convert("UTC") + pd.Timedelta(hours=9)
    return df


def normalize_index(path: str | Path) -> pd.DataFrame:
    df=_rename(_read_any(path))
    if 'date' not in df: raise ValueError('index report has no date')
    if 'symbol' not in df:
        for c in ['Index Name','IndexName','INDEX_NAME','Index']:
            if c in df.columns: df=df.rename(columns={c:'symbol'}); break
    if 'symbol' not in df: raise ValueError('index report has no index identifier')
    df['date']=pd.to_datetime(df['date'],errors='coerce')
    for c in ['open','high','low','close','volume','turnover']:
        if c in df: df[c]=pd.to_numeric(df[c],errors='coerce')
    df['market_time']=df['date'].map(session_close_utc)
    df['signal_time']=df['date'].map(next_trading_day).map(session_open_utc)
    df['asof_time']=df['signal_time']
    return df.sort_values(['date','symbol']).reset_index(drop=True)
