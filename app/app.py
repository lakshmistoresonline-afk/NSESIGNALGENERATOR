import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import streamlit as st
import pandas as pd
from nse_signal.data.market import load_symbol
from nse_signal.features.build import make_features
from nse_signal.models.walk_forward import walk_forward
from nse_signal.backtest.engine import backtest_oos
from nse_signal.research.factors import factor_snapshot, cross_sectional_rank
from nse_signal.signals.engine import SignalEngine
from nse_signal.risk.filters import filter_signals
from nse_signal.utils.config import load_config

st.set_page_config(page_title="NSE Signal Research", layout="wide")
cfg = load_config()
st.title("NSE Signal Research Platform")
st.caption("Signal-only • OOS research • No broker execution • REAL_TRADING = FALSE")

symbols = st.multiselect("Universe", cfg["universe"]["symbols"], default=cfg["universe"]["symbols"][:5])
if st.button("Generate research signals"):
    rows=[]; oos_map={}
    progress=st.progress(0)
    for i, symbol in enumerate(symbols):
        try:
            raw=load_symbol(symbol, cfg["data"]["cache_dir"]); feat=make_features(raw)
            oos=walk_forward(feat, cfg["model"]["min_train_rows"], horizon=cfg["model"]["horizon_bars"])
            bt, stats=backtest_oos(oos.predictions, cfg["backtest"]["round_trip_cost_bps"], cfg["backtest"]["slippage_bps"], cfg["model"]["probability_threshold"], cfg["backtest"]["holding_bars"])
            fs=factor_snapshot(raw); latest=oos.predictions.iloc[-1]
            rows.append({"symbol":symbol, "p_up":latest.p_up, **fs, "backtest_sharpe":stats["sharpe_annualized"], "backtest_return":stats["total_return"]})
            oos_map[symbol]=oos.metrics
        except Exception as e:
            st.warning(f"{symbol}: {e}")
        progress.progress((i+1)/len(symbols))
    ranked=cross_sectional_rank(rows) if rows else pd.DataFrame()
    if not ranked.empty:
        ranked["confidence"]=(ranked.p_up-.5).abs()*2
        ranked["factor_score"] = ranked.factor_score.fillna(.5)
        signals=[]; engine=SignalEngine(False)
        for _,r in ranked.iterrows():
            s=engine.generate(r.symbol, float(r.p_up), float(r.factor_score), cfg["model"]["probability_threshold"])
            if s: signals.append(s)
        sf=filter_signals(SignalEngine.frame(signals), cfg["risk"]["min_confidence"], cfg["risk"]["max_signal_count"], cfg["risk"]["max_single_name_weight"])
        st.subheader("Current paper signals")
        st.dataframe(sf, use_container_width=True)
        st.subheader("Research ranking")
        st.dataframe(ranked.sort_values("factor_score", ascending=False), use_container_width=True)
        st.subheader("OOS model diagnostics")
        st.json(oos_map)
else:
    st.info("Download market data first with the CLI, or run the sample-data/backtest commands to verify the pipeline offline.")

st.divider()
st.warning("This software is for research/education. Signals are not guaranteed to be profitable. No real orders are placed by this application.")
