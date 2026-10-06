"""Research controls distilled from the selected NSE research repositories."""
import numpy as np

def next_bar_entry_rule(signal_timestamp, entry_timestamp):
    return entry_timestamp > signal_timestamp

def permutation_pvalue(observed, null_values):
    null=np.asarray(null_values,dtype=float)
    return float((1 + np.sum(null >= observed))/(len(null)+1))

def deflated_sharpe_proxy(sharpe, trials, observations):
    # Conservative diagnostic proxy; not a substitute for a full DSR implementation.
    penalty=np.sqrt(max(0.0,np.log(max(1,trials))/max(1,observations)))
    return float(sharpe-penalty)

def pass_cost_gate(gross_return, round_trip_cost_bps, turnover):
    return float(gross_return - (round_trip_cost_bps/10000.0)*turnover)
