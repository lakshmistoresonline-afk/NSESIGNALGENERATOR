"""Generates a comprehensive analysis report of the SQLite database tables, date ranges, symbols, and published signals."""
from __future__ import annotations
import sys
import json
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from nse_signal.data.db import get_connection, init_db

def analyze():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    report = {
        "database_path": "data/processed/nse_signal.db",
        "tables": {}
    }

    for tbl in tables:
        try:
            df = pd.read_sql_query(f"SELECT * FROM {tbl}", conn)
            row_count = len(df)
            symbols = sorted(df["symbol"].unique().tolist()) if "symbol" in df.columns else []
            min_date = str(df["date"].min()) if "date" in df.columns and not df.empty else "N/A"
            max_date = str(df["date"].max()) if "date" in df.columns and not df.empty else "N/A"
            report["tables"][tbl] = {
                "row_count": row_count,
                "unique_symbols_count": len(symbols),
                "sample_symbols": symbols[:15],
                "min_date": min_date,
                "max_date": max_date
            }
        except Exception as e:
            report["tables"][tbl] = {"error": str(e)}

    conn.close()

    # Inspect published signals
    sig_path = ROOT / "data" / "processed" / "published_signals.json"
    signals_data = {}
    if sig_path.exists():
        try:
            signals_data = json.loads(sig_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    report["published_signals"] = signals_data

    out_path = ROOT / "reports" / "database_analysis_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps(report, indent=2))
    print(f"\nReport written to {out_path}")

if __name__ == "__main__":
    analyze()
