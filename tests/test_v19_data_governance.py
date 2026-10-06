import json
from pathlib import Path
import pytest
from nse_signal.data.market import load_symbol, download_symbol


def test_third_party_download_is_disabled():
    with pytest.raises(RuntimeError, match="No third-party market-data downloader"):
        download_symbol("RELIANCE.NS")


def test_missing_local_market_data_fails_closed(tmp_path):
    with pytest.raises(FileNotFoundError, match="Authoritative local market data not found"):
        load_symbol("RELIANCE.NS", cache_dir=tmp_path)


def test_authoritative_gap_register_has_unlicensed_required_layers():
    p = Path("data/reference/authoritative_pit_data_gap_register.json")
    obj = json.loads(p.read_text(encoding="utf-8"))
    layers = {x["layer"] for x in obj["gaps"]}
    for required in ["historical_cm_eod", "historical_security_contract_master", "historical_index_constituents_nifty200", "pit_corporate_data"]:
        assert required in layers
    assert all("status" in x for x in obj["gaps"])
