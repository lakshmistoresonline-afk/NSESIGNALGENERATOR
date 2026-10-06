"""Optional exact TA-Lib reference backend.

The core project keeps a dependency-light implementation. This module exposes
all functions from the installed TA-Lib Python binding when available, so
researchers can regression-test core calculations against the upstream
battle-tested implementation without pretending that a proxy is exact.
"""
from __future__ import annotations
from typing import Any

CATEGORIES = {
    "math_operators": ["ADD","CUMSUM","DIV","MAX","MAXINDEX","MIN","MININDEX","MINMAX","MINMAXINDEX","MULT","SUB","SUM"],
    "math_transform": ["ACOS","ASIN","ATAN","CEIL","COS","COSH","EXP","FLOOR","LN","LOG10","SIN","SINH","SQRT","TAN","TANH"],
    "cycle": ["HT_DCPERIOD","HT_DCPHASE","HT_PHASOR","HT_SINE","HT_TRENDMODE"],
    "momentum": ["AC","ADX","ADXR","AO","APO","AROON","AROONOSC","ASI","BOP","CCI","CG","CHOP","CHOPTR","CMO","CMOU","COPPOCK","CRSI","CTI","DPO","DX","ER","ERI","FOSC","FRACTAL","IBS","IMI","KDJ","KST","KSTEXT","MACD","MACDEXT","MACDFIX","MFI","MINUS_DI","MINUS_DM","MOM","PLUS_DI","PLUS_DM","PPO","QSTICK","ROC","ROCP","ROCR","ROCR100","RSI","SI","SMI","STC","STOCH","STOCHF","STOCHRSI","TRIX","TSI","ULTOSC","VHF","VORTEX","WAD","WILLR"],
    "overlap": ["ACCBANDS","ALMA","BBANDS","CKSP","DEMA","DONCHIAN","EMA","FRAMA","HMA","HT_TRENDLINE","KAMA","KC","MA","MAMA","MAVP","MCGD","MIDPOINT","MIDPRICE","RMA","SAR","SAREXT","SMA","SUPERTREND","T3","TEMA","TRIMA","VIDYA","VWMA","WMA","ZLEMA"],
    "price_transform": ["AVGDEV","AVGPRICE","HA","MEDPRICE","TYPPRICE","WCLPRICE"],
    "statistics": ["BETA","CORREL","KURTOSIS","LINEARREG","LINEARREG_ANGLE","LINEARREG_INTERCEPT","LINEARREG_SLOPE","MEDIAN","PERCENTILE","PERCENTRANK","STDDEV","TSF","VAR"],
    "volatility": ["ADR","ATR","BBW","CVI","MASSI","NATR","PERCENTB","RVI","RVIR","TRANGE"],
    "volume": ["AD","ADOSC","CMF","EFI","EMV","MARKETFI","NVI","OBV","PVI","PVO","PVT","RVOL","VWAP"],
}

# Candlestick functions are deliberately exposed as a separate namespace: they
# have their own candle-setting/range rules and should not silently enter the ML
# feature matrix.
CANDLESTICK_FUNCTIONS = [
    "CDL2CROWS","CDL3BLACKCROWS","CDL3INSIDE","CDL3LINESTRIKE","CDL3OUTSIDE","CDL3STARSINSOUTH","CDL3WHITESOLDIERS","CDLABANDONEDBABY","CDLADVANCEBLOCK","CDLBELTHOLD","CDLBREAKAWAY","CDLCLOSINGMARUBOZU","CDLCONCEALBABYSWALL","CDLCOUNTERATTACK","CDLDARKCLOUDCOVER","CDLDOJI","CDLDOJISTAR","CDLDRAGONFLYDOJI","CDLENGULFING","CDLEVENINGDOJISTAR","CDLEVENINGSTAR","CDLGAPSIDESIDEWHITE","CDLGRAVESTONEDOJI","CDLHAMMER","CDLHANGINGMAN","CDLHARAMI","CDLHARAMICROSS","CDLHIGHWAVE","CDLHIKKAKE","CDLHIKKAKEMOD","CDLHOMINGPIGEON","CDLIDENTICAL3CROWS","CDLINNECK","CDLINVERTEDHAMMER","CDLKICKING","CDLKICKINGBYLENGTH","CDLLADDERBOTTOM","CDLLONGLEGGEDDOJI","CDLLONGLINE","CDLMARUBOZU","CDLMATCHINGLOW","CDLMATHOLD","CDLMORNINGDOJISTAR","CDLMORNINGSTAR","CDLONNECK","CDLPIERCING","CDLRICKSHAWMAN","CDLRISEFALL3METHODS","CDLSEPARATINGLINES","CDLSHOOTINGSTAR","CDLSHORTLINE","CDLSPINNINGTOP","CDLSTALLEDPATTERN","CDLSTICKSANDWICH","CDLTAKURI","CDLTASUKIGAP","CDLTHRUSTING","CDLTRISTAR","CDLUNIQUE3RIVER","CDLUPSIDEGAP2CROWS","CDLXSIDEGAP3METHODS"
]


def available() -> bool:
    try:
        import talib  # noqa: F401
        return True
    except ImportError:
        return False


def all_functions() -> list[str]:
    return [f for group in CATEGORIES.values() for f in group] + CANDLESTICK_FUNCTIONS


def metadata(name: str) -> dict[str, Any]:
    """Return exact parameter/input/output metadata from the installed TA-Lib wrapper.

    The wrapper exposes the same abstract metadata used by TA-Lib's generic
    interface; this avoids maintaining a second, potentially stale parameter
    catalogue in this project.
    """
    try:
        import talib
        from talib import abstract
    except ImportError as exc:
        raise RuntimeError("Exact TA-Lib metadata requires the optional TA-Lib package.") from exc
    fn = abstract.Function(name)
    info = fn.info
    return {
        "name": info.get("name"),
        "group": info.get("group"),
        "input_names": info.get("input_names"),
        "parameters": info.get("parameters"),
        "output_names": info.get("output_names"),
    }


def parameter_registry() -> dict[str, dict[str, Any]]:
    """Return exact parameter metadata for every function in the installed TA-Lib."""
    return {name: metadata(name) for name in all_functions()}


def call(name: str, *args: Any, **kwargs: Any):
    try:
        import talib
    except ImportError as exc:
        raise RuntimeError("Exact TA-Lib reference calculations require the optional TA-Lib package. Install from requirements-reference.txt") from exc
    fn=getattr(talib, name, None)
    if fn is None:
        raise AttributeError(f"TA-Lib function not available: {name}")
    return fn(*args, **kwargs)
