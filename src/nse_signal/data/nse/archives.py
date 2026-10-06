"""Official NSE archive URLs and deterministic download/manifest helpers.

The downloader targets the published NSE archive files, not broker feeds.  It is
intentionally conservative: every downloaded artifact gets a SHA-256, source URL,
retrieval timestamp, and trading date in a manifest.  No data is silently adjusted.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import date, datetime, timezone
from hashlib import sha256
from pathlib import Path
import json, time, urllib.error, urllib.request, os

ARCHIVE_ROOT = "https://archives.nseindia.com"

@dataclass(frozen=True)
class Artifact:
    layer: str
    trading_date: str
    url: str
    path: str
    sha256: str
    retrieved_at: str
    bytes: int


def cm_bhavcopy_url(d: date) -> str:
    if d >= date(2024, 7, 8):
        return f"{ARCHIVE_ROOT}/content/cm/BhavCopy_NSE_CM_0_0_0_{d:%Y%m%d}_F_0000.csv.zip"
    else:
        month_str = d.strftime("%b").upper()
        date_str = d.strftime("%d%b%Y").upper()
        return f"{ARCHIVE_ROOT}/content/historical/EQUITIES/{d.year}/{month_str}/cm{date_str}bhav.csv.zip"


def fo_bhavcopy_url(d: date) -> str:
    return f"{ARCHIVE_ROOT}/content/fo/BhavCopy_NSE_FO_0_0_0_{d:%Y%m%d}_F_0000.csv.zip"


def index_close_url(d: date) -> str:
    return f"{ARCHIVE_ROOT}/content/indices/ind_close_all_{d:%d%m%Y}.csv"


def security_master_url(d: date) -> str:
    if d >= date(2024, 7, 8):
        return f"{ARCHIVE_ROOT}/content/cm/NSE_CM_security_{d:%d%m%Y}.csv.gz"
    else:
        return f"{ARCHIVE_ROOT}/content/equities/EQUITY_L.csv"


def _download(url: str, dest: Path, timeout: int = 45, retries: int = 3) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; NSE-Signal-Research/1.0)",
        "Accept": "*/*",
        "Referer": "https://www.nseindia.com/",
    })
    last = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r, dest.open("wb") as f:
                while True:
                    chunk = r.read(1024 * 1024)
                    if not chunk: break
                    f.write(chunk)
            return
        except Exception as exc:
            last = exc
            if attempt + 1 < retries: time.sleep(2 ** attempt)
    raise RuntimeError(f"NSE download failed: {url} :: {last}")


def download_artifact(layer: str, trading_date: date, root: str = "data/raw/nse", overwrite: bool = False) -> Artifact:
    builders = {"cm_bhavcopy": cm_bhavcopy_url, "fo_bhavcopy": fo_bhavcopy_url,
                "index_close": index_close_url, "security_master": security_master_url}
    if layer not in builders: raise ValueError(f"Unsupported NSE archive layer: {layer}")
    url = builders[layer](trading_date)
    suffix = '.csv.zip' if url.endswith('.csv.zip') else ('.csv.gz' if url.endswith('.csv.gz') else '.csv')
    path = Path(root) / layer / f"{trading_date:%Y-%m-%d}{suffix}"
    if path.exists():
        if overwrite:
            raise RuntimeError(f"Refusing to overwrite immutable raw artifact: {path}")
        digest = sha256(path.read_bytes()).hexdigest()
    else:
        _download(url, path)
        digest = sha256(path.read_bytes()).hexdigest()
    return Artifact(layer, trading_date.isoformat(), url, str(path), digest,
                    datetime.now(timezone.utc).isoformat(), path.stat().st_size)


def append_manifest(artifact: Artifact, manifest: str = "data/raw/nse/manifest.jsonl") -> None:
    p = Path(manifest); p.parent.mkdir(parents=True, exist_ok=True)
    rows=[]
    if p.exists():
        for line in p.read_text(encoding='utf-8').splitlines():
            if line.strip():
                try: rows.append(json.loads(line))
                except json.JSONDecodeError as exc: raise ValueError(f"Corrupt provenance manifest: {p}") from exc
    key=(artifact.layer,artifact.trading_date,artifact.url,artifact.sha256)
    if any((r.get('layer'),r.get('trading_date'),r.get('url'),r.get('sha256'))==key for r in rows): return
    rows.append(asdict(artifact))
    tmp=p.with_name(p.name+'.tmp')
    tmp.write_text(''.join(json.dumps(r,sort_keys=True)+"\n" for r in rows),encoding='utf-8')
    os.replace(tmp,p)
