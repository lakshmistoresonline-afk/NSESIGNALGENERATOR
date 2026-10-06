"""Market-session-aware signal expiry; wall-clock expiry alone is insufficient."""
from __future__ import annotations
import pandas as pd
from nse_signal.data.nse.session_calendar import classify

def expired(signal_time, now, ttl_sessions=1):
    s=pd.Timestamp(signal_time); n=pd.Timestamp(now)
    if s.tzinfo is None: s=s.tz_localize('Asia/Kolkata')
    if n.tzinfo is None: n=n.tz_localize('Asia/Kolkata')
    if n <= s: return False
    # For daily signals, a one-session TTL means the signal is valid through the
    # first subsequent regular session and expires before a later session.
    session_dates=[]; d=s.tz_convert('Asia/Kolkata').date()
    cur=n.tz_convert('Asia/Kolkata').date()
    for x in pd.date_range(d,cur,freq='D'):
        if classify(pd.Timestamp(x).tz_localize('Asia/Kolkata')+pd.Timedelta(hours=10))=='REGULAR': session_dates.append(x.date())
    return max(0,len(session_dates)-1) > int(ttl_sessions)
