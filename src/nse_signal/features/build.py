import pandas as pd
from .indicators import add_all
from ..research.regime import add_regime_features
from .advanced import add_advanced_features

# Candidate feature matrix. Features are candidates, not claims of predictive power.
# Selection/parameter changes must be validated with purged walk-forward OOS testing.
FEATURES = [
    # Trend / overlap
    'sma_5','sma_10','sma_20','sma_50','sma_100','sma_200','ema_5','ema_10','ema_20','ema_50','ema_100','ema_200',
    'dema_20','tema_20','hma_20','kama_10','zlema_20','trima_20','t3_5','vwma_20','midpoint_14','midprice_14','wma_20','ht_trendline',
    'trend_strength','ema_stack_bull','price_sma_20_gap','price_sma_50_gap','price_sma_200_gap','price_ema_20_gap','price_ema_50_gap','price_ema_200_gap',
    'parabolic_sar','sar_gap','supertrend','supertrend_direction','supertrend_gap','pivot','pivot_r1','pivot_s1','pivot_r2','pivot_s2',
    'donchian_high','donchian_low','donchian_high_55','donchian_low_55','donchian_pos','donchian_pos_55','keltner_upper','keltner_lower','keltner_pos','aroon_up','aroon_down',
    # Volatility
    'tr','atr_5','atr_14','atr_20','natr_5','natr_14','natr_20','atr_pct','realized_vol_5','realized_vol_10','realized_vol_20','realized_vol_60',
    'bb_mid','bb_upper','bb_lower','bb_pos','bb_width','adr_14','chaikin_volatility_10','mass_index_9_25','stddev_20','variance_20','atr_z_60','range_z_20',
    # Momentum / direction
    'rsi_7','rsi_14','rsi_21','roc_5','roc_10','roc_20','macd','macd_signal','macd_hist','ppo','ppo_signal','ppo_hist','stoch_k','stoch_d','stochrsi_k','stochrsi_d',
    'adx','plus_di','minus_di','adxr','aroon_osc','cmou_14','ac_5_34','kdj_k','kdj_d','kdj_j','macdext','macdext_signal','macdext_hist','macdfix','macdfix_signal','macdfix_hist','fosc_14','fractal_up','fractal_down','cci_20','williams_r','mfi_14','tsi','awesome_osc','cmo_14','ultimate_osc','vortex_plus','vortex_minus','vortex_14','rvi_14','efficiency_ratio_10','vhf_28',
    'apo_12_26','dx_14','plus_dm_14','minus_dm_14','momentum_10','bop','qstick_14','elder_bull_power','elder_bear_power','trix_30','dpo_20','coppock','imi_14','stoch_fast_k','stoch_fast_d','rocp_20','rocr_20','rocr100_20',
    # Price transforms / structure
    'avg_price','median_price','typical_price','weighted_close','ha_open','ha_high','ha_low','ha_close','gap_pct','intraday_range_pct','body_pct','upper_wick_pct','lower_wick_pct',
    'high_20_breakout','low_20_breakdown','accbands_upper','accbands_lower','accbands_mid','linearreg_slope_20','linearreg_intercept_20','linearreg_angle_20','tsf_20','percentile_20','percent_rank_20',
    # Volume / flow
    'obv','obv_z','ad_line','ad_osc','pvt','vwap','vwap_gap','force_index_13','market_facilitation','pvi','nvi','pvo','pvo_signal','pvo_hist','rvol_20','volume_z','volume_ratio_20','volume_ratio_50','dollar_volume','turnover_z','cmf_20','squeeze_on','squeeze_momentum','anchored_vwap_20','avwap_gap_20',
    # Returns
    'return_1d','return_3d','return_5d','return_20d','return_60d','return_120d',
    # Other
    'wad','ibs','chop_14','parkinson_vol_20','garman_klass_vol_20','overnight_return_1d','intraday_return_1d','overnight_intraday_gap_20_z','amihud_20','dollar_volume_z20','range_per_volume_20','signed_volume_ratio_20','close_location_value','clv_volume_20','directional_efficiency_20','return_skew_20','return_kurtosis_20','vol_of_vol_20','range_compression_20','close_to_high_20','distance_from_20d_vwap','choptr_14','center_of_gravity_10','connors_rsi','smi','smi_signal','kst','kst_signal','kst_hist','kstext','kstext_signal','kstext_hist','kurtosis_20','median_20','emv_14','rvir_14',
    # Regime / uncertainty context derived causally from the same series
    'market_sma_200_gap','market_trend_slope_63','market_realized_vol_20','market_vol_percentile_252','regime_trend','regime_vol','regime_id',
    'close_fracdiff_0_2','close_fracdiff_0_4','log_return_fracdiff_0_2','log_return_fracdiff_0_4',
]

PANEL_FEATURES = ['cs_return_rank','cs_return_5d_rank','cs_return_20d_rank','cs_vol_rank','cs_liquidity_rank','cs_return_z','cs_return_5d_z','cs_return_20d_z','cs_vol_z','cs_liquidity_z','cs_market_residual_1d','cs_sector_residual_1d','cs_sector_return_rank']

OPTIONAL_FEATURES = [
    'beta_60','corr_60','relative_strength_nifty','relative_strength_sector','relative_strength','relative_strength_z20','sector_relative_strength_20','market_breadth_up_share','market_breadth_down_share','market_return_dispersion','market_high_vol_share',
    'india_vix','india_vix_z20','nifty_return','nifty_return_z20','sector_return','sector_return_z20',
    'fii_net','fii_net_z20','dii_net','dii_net_z20','pcr','pcr_z20','oi_change','oi_change_z20','futures_basis','futures_basis_z20',
    'advance_decline_ratio','advance_decline_ratio_z20','delivery_pct','delivery_pct_z20','impact_cost_bps','impact_cost_bps_z20','pcr_oi','pcr_volume','pcr_oi_change','weighted_iv','put_iv','call_iv','iv_skew_put_minus_call','atm_strike_oi_share','participant_oi','participant_oi_z20','fii_derivatives_net','fii_derivatives_net_z20','daily_volatility','daily_volatility_z20','bid_ask_spread_bps','bid_ask_spread_bps_z20','order_book_imbalance','order_book_imbalance_z20','news_sentiment','news_sentiment_z20','earnings_days','corporate_action_flag','restricted','near_price_band','short_sale_blocked',
]

def make_features(df, params=None):
    """Build causal features without allowing rolling windows to cross symbols.

    A multi-symbol frame is processed independently per symbol, then combined
    for same-timestamp cross-sectional features. A single-symbol frame keeps the
    original fast path.
    """
    if {'timestamp','symbol'}.issubset(df.columns):
        parts=[]
        x=df.copy()
        x['timestamp']=pd.to_datetime(x['timestamp'],utc=True,errors='coerce')
        if x['timestamp'].isna().any():
            raise ValueError('panel contains invalid timestamps')
        for symbol,g in x.groupby('symbol',sort=False):
            g=g.sort_values('timestamp').copy()
            g=add_all(g,params=params)
            g=add_advanced_features(g)
            from .advanced import add_fractional_features
            g=add_fractional_features(g)
            parts.append(g)
        out=pd.concat(parts,ignore_index=True).sort_values(['timestamp','symbol']).reset_index(drop=True)
        # Regime features are computed from the panel after symbol-safe features
        # exist, allowing a cross-sectional market proxy or explicit benchmark.
        out=add_regime_features(out)
        from ..research.panel import add_cross_sectional_panel_features, add_market_structure_features
        out=add_cross_sectional_panel_features(out)
        out=add_market_structure_features(out)
        return out
    out=add_all(df,params=params)
    out=add_advanced_features(out)
    out=add_regime_features(out)
    from .advanced import add_fractional_features
    return add_fractional_features(out)

def feature_columns(df):
    cols = [c for c in FEATURES if c in df.columns] + [c for c in OPTIONAL_FEATURES if c in df.columns]
    if {'timestamp','symbol'}.issubset(df.columns): cols += [c for c in PANEL_FEATURES if c in df.columns]
    return cols


def make_labels(df, horizon=5, threshold=0.0):
    """Create supervised labels without crossing securities.

    For a panel, every future value is taken from the same symbol.  The
    previous implementation used a frame-wide shift, which could make the
    final row of one security consume the first row of another security.
    """
    if int(horizon) < 1:
        raise ValueError('horizon must be >= 1')
    out=df.copy()
    if {'symbol','timestamp'}.issubset(out.columns):
        out=out.sort_values(['symbol','timestamp']).copy()
        future_close=out.groupby('symbol',sort=False)['close'].shift(-int(horizon))
        out['future_return']=future_close/out['close']-1.0
    else:
        out['future_return']=out.close.shift(-int(horizon))/out.close-1.0
    out['target']=((out.future_return>float(threshold)).astype('float')).where(out.future_return.notna())
    return out

def make_labeled_features(df, params=None, horizon=5, threshold=0.0):
    return make_labels(make_features(df, params=params), horizon=horizon, threshold=threshold)
