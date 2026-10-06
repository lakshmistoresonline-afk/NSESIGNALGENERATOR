"""Auditable, dependency-light technical indicators for NSE research.

All calculations are causal at bar t: no value uses future bars.  Parameterized
indicators accept a registry dictionary; ``add_all`` loads the repository's
indicator registry when none is supplied.
"""
import numpy as np
import pandas as pd
from pathlib import Path
import yaml


def _sma(s, n): return s.rolling(int(n), min_periods=int(n)).mean()
def _ema(s, n):
    """TA-Lib-compatible EMA: SMA seed, then recursive alpha=2/(n+1)."""
    s=pd.Series(s,index=s.index,dtype=float); n=int(n)
    out=pd.Series(np.nan,index=s.index,dtype=float)
    valid=np.flatnonzero(s.notna().to_numpy())
    if len(valid)<n: return out
    i0=int(valid[0]); seed_i=i0+n-1; seed=float(s.iloc[i0:seed_i+1].mean())
    if not np.isfinite(seed): return out
    out.iloc[seed_i]=seed; a=2.0/(n+1.0)
    for i in range(seed_i+1,len(s)):
        x=s.iloc[i]
        out.iloc[i]=out.iloc[i-1] if not np.isfinite(x) else out.iloc[i-1]+a*(x-out.iloc[i-1])
    return out
def _wilder(s, n):
    """Wilder/RMA: SMA seed over n observations, then alpha=1/n."""
    s = pd.Series(s, index=s.index, dtype=float); n=int(n)
    out = pd.Series(np.nan, index=s.index, dtype=float)
    valid = np.flatnonzero(s.notna().to_numpy())
    if len(valid) < n: return out
    i0=int(valid[0]); seed_i=i0+n-1; seed=s.iloc[i0:seed_i+1].mean()
    if not np.isfinite(seed): return out
    out.iloc[seed_i]=seed; a=1.0/n
    for i in range(seed_i+1,len(s)):
        x=s.iloc[i]
        out.iloc[i]=out.iloc[i-1] if not np.isfinite(x) else out.iloc[i-1]+a*(x-out.iloc[i-1])
    return out

def _wma(s,n):
    n=int(n); w=np.arange(1,n+1,dtype=float); den=w.sum()
    return s.rolling(n,min_periods=n).apply(lambda z: np.dot(z,w)/den,raw=True)

def true_range(df):
    prev=df.close.shift(1)
    return pd.concat([df.high-df.low,(df.high-prev).abs(),(df.low-prev).abs()],axis=1).max(axis=1)
def atr(df,n=14): return _wilder(true_range(df),n)
def natr(df,n=14): return 100*atr(df,n)/df.close.replace(0,np.nan)

def rsi(c,n=14):
    d=c.diff(); g=d.clip(lower=0); loss=-d.clip(upper=0); ag,al=_wilder(g,n),_wilder(loss,n)
    rs=ag/al.replace(0,np.nan); out=100-100/(1+rs)
    return out.where(al.ne(0),100).where(~((ag.eq(0))&(al.eq(0))),50)
def roc(c,n): return c.pct_change(int(n))*100
def rocp(c,n): return c.pct_change(int(n))
def rocr(c,n): return c/c.shift(int(n))

def stochastic(df,n=14,slow_k=3,slow_d=3,slow_k_ma='sma',slow_d_ma='sma'):
    lo=df.low.rolling(n,min_periods=n).min(); hi=df.high.rolling(n,min_periods=n).max(); k=100*(df.close-lo)/(hi-lo).replace(0,np.nan)
    k=k.fillna(0).where((hi-lo).notna(),np.nan)
    sk=_ma(k,slow_k,slow_k_ma); sd=_ma(sk,slow_d,slow_d_ma)
    return sk,sd
def stochastic_fast(df,n=5,d=3,d_ma='sma'):
    lo=df.low.rolling(n,min_periods=n).min(); hi=df.high.rolling(n,min_periods=n).max(); fk=100*(df.close-lo)/(hi-lo).replace(0,np.nan); fk=fk.fillna(0).where((hi-lo).notna(),np.nan); fd=_ma(fk,d,d_ma); return fk,fd

def adx_components(df,n=14):
    tr=true_range(df); up=df.high.diff(); dn=-df.low.diff()
    plus=pd.Series(np.where((up>dn)&(up>0),up,0.),index=df.index); minus=pd.Series(np.where((dn>up)&(dn>0),dn,0.),index=df.index)
    atrs=_wilder(tr,n); pdm=_wilder(plus,n); mdm=_wilder(minus,n)
    pdi=100*pdm/atrs.replace(0,np.nan); mdi=100*mdm/atrs.replace(0,np.nan); dx=100*(pdi-mdi).abs()/(pdi+mdi).replace(0,np.nan)
    return tr,plus,minus,pdi,mdi,dx

def adx(df,n=14):
    _,_,_,pdi,mdi,dx=adx_components(df,n); return _wilder(dx,n),pdi,mdi
def dx(df,n=14): return adx_components(df,n)[-1]
def plus_dm(df,n=14): return _wilder(adx_components(df,n)[1],n)
def minus_dm(df,n=14): return _wilder(adx_components(df,n)[2],n)
def adxr(df,n=14):
    a,_,_=adx(df,n); return (a+a.shift(n-1))/2

def _ma(s,n,ma_type='sma'):
    t=str(ma_type).lower()
    if t=='sma': return _sma(s,n)
    if t=='ema': return _ema(s,n)
    if t=='wma': return _wma(s,n)
    if t=='dema': return dema(s,n)
    if t=='tema': return tema(s,n)
    if t=='trima': return trima(s,n)
    if t=='kama': return kama(s,n)
    if t=='t3': return t3(s,n,.7)
    if t=='hma': return hma(s,n)
    if t=='rma': return _wilder(s,n)
    if t=='zlema': return zlema(s,n)
    if t in {'mama','mavp','disabled','default'}:
        raise ValueError(f'MA type {ma_type!r} requires the exact TA-Lib reference backend or explicit implementation')
    raise ValueError(f'Unsupported MA type: {ma_type!r}')

def macd(c,fast=12,slow=26,signal=9,ma_type='ema'):
    line=_ma(c,fast,ma_type)-_ma(c,slow,ma_type); sig=_ma(line,signal,ma_type); return line,sig,line-sig
def apo(c,fast=12,slow=26,ma_type='ema'): return _ma(c,fast,ma_type)-_ma(c,slow,ma_type)
def ppo(c,fast=12,slow=26,signal=9,ma_type='ema'):
    se=_ma(c,slow,ma_type); line=100*(_ma(c,fast,ma_type)-se)/se.replace(0,np.nan); sig=_ma(line,signal,ma_type); return line,sig,line-sig
def bollinger(c,n=20,k_up=2,k_dn=None,ma_type='sma'):
    if k_dn is None: k_dn=k_up
    mid=_ma(c,n,ma_type); sd=c.rolling(n,min_periods=n).std(ddof=0); up,lo=mid+k_up*sd,mid-k_dn*sd
    return mid,up,lo,(c-mid)/(k_up*sd).replace(0,np.nan)
def donchian(df,n=20): return df.high.rolling(n,min_periods=n).max(),df.low.rolling(n,min_periods=n).min()
def obv(df): return (np.sign(df.close.diff()).fillna(0)*df.volume).cumsum()

def mfi(df,n=14):
    tp=(df.high+df.low+df.close)/3; flow=tp*df.volume; d=tp.diff(); pos=flow.where(d>0,0).rolling(n,min_periods=n).sum(); neg=(-flow.where(d<0,0)).rolling(n,min_periods=n).sum()
    out=100-100/(1+pos/neg.replace(0,np.nan)); return out.where(neg.ne(0),100).where(~((pos.eq(0))&(neg.eq(0))),50)
def cmf(df,n=20):
    mf=((2*df.close-df.low-df.high)/(df.high-df.low).replace(0,np.nan)).fillna(0)*df.volume
    return mf.rolling(n,min_periods=n).sum()/df.volume.rolling(n,min_periods=n).sum().replace(0,np.nan)
def ad_line(df):
    mfm=((df.close-df.low)-(df.high-df.close))/(df.high-df.low).replace(0,np.nan); return (mfm.fillna(0)*df.volume).cumsum()
def ad_osc(df,fast=3,slow=10):
    a=ad_line(df); return _ema(a,fast)-_ema(a,slow)
def vwap(df):
    tp=(df.high+df.low+df.close)/3; pv=tp*df.volume
    if 'session_id' in df.columns:
        return pv.groupby(df.session_id).cumsum()/df.volume.groupby(df.session_id).cumsum().replace(0,np.nan)
    return pv.cumsum()/df.volume.cumsum().replace(0,np.nan)
def vwma(df,n=20): return (df.close*df.volume).rolling(n,min_periods=n).sum()/df.volume.rolling(n,min_periods=n).sum().replace(0,np.nan)
def pvo(v,fast=12,slow=26,signal=9,ma_type='ema'):
    ef,es=_ma(v,fast,ma_type),_ma(v,slow,ma_type); line=100*(ef-es)/es.replace(0,np.nan); sig=_ma(line,signal,ma_type); return line,sig,line-sig
def rvol(v,n=20): return v/v.rolling(n,min_periods=n).mean().replace(0,np.nan)

def tsi(c,r=25,s=13):
    m=c.diff(); a=_ema(_ema(m,r),s); b=_ema(_ema(m.abs(),r),s); return 100*a/b.replace(0,np.nan)
def cci(df,n=20):
    tp=(df.high+df.low+df.close)/3; mean=_sma(tp,n); mad=tp.rolling(n,min_periods=n).apply(lambda z:np.mean(np.abs(z-np.mean(z))),raw=True); return (tp-mean)/(0.015*mad).replace(0,np.nan)
def williams_r(df,n=14):
    hi=df.high.rolling(n,min_periods=n).max(); lo=df.low.rolling(n,min_periods=n).min(); return -100*(hi-df.close)/(hi-lo).replace(0,np.nan)
def awesome_osc(df,fast=5,slow=34):
    med=(df.high+df.low)/2; return _sma(med,fast)-_sma(med,slow)
def keltner(df,ema_n=20,atr_n=10,mult=2):
    mid=_ema(df.close,ema_n); a=atr(df,atr_n); return mid+mult*a,mid-mult*a,(df.close-mid)/(mult*a).replace(0,np.nan)
def parabolic_sar(df,step=.02,max_af=.2):
    h,l=df.high.to_numpy(),df.low.to_numpy(); out=np.full(len(df),np.nan)
    if not len(df): return pd.Series(out,index=df.index)
    bull=True; af=step; ep=h[0]; out[0]=l[0]
    for i in range(1,len(df)):
        sar=out[i-1]+af*(ep-out[i-1])
        if bull:
            sar=min(sar,l[i-1],l[i-2] if i>1 else l[i-1])
            if l[i]<sar: bull=False; sar=ep; ep=l[i]; af=step
            elif h[i]>ep: ep=h[i]; af=min(max_af,af+step)
        else:
            sar=max(sar,h[i-1],h[i-2] if i>1 else h[i-1])
            if h[i]>sar: bull=True; sar=ep; ep=h[i]; af=step
            elif l[i]<ep: ep=l[i]; af=min(max_af,af+step)
        out[i]=sar
    return pd.Series(out,index=df.index)
def rolling_z(s,n): return (s-_sma(s,n))/s.rolling(n,min_periods=n).std(ddof=0).replace(0,np.nan)
def beta_vs_market(a,b,n=60):
    # Population-covariance / population-variance definition, so beta is not
    # biased by pandas' default sample-covariance denominator.
    def _cov(z):
        aa=np.asarray(z[:n],dtype=float); bb=np.asarray(z[n:],dtype=float)
        if len(aa)!=n or len(bb)!=n or not np.isfinite(aa).all() or not np.isfinite(bb).all(): return np.nan
        return float(np.mean((aa-aa.mean())*(bb-bb.mean())))
    # Build aligned pairs without relying on rolling.cov's ddof=1.
    out=pd.Series(np.nan,index=a.index,dtype=float)
    for i in range(n-1,len(a)):
        aa=a.iloc[i-n+1:i+1].to_numpy(dtype=float); bb=b.iloc[i-n+1:i+1].to_numpy(dtype=float)
        mask=np.isfinite(aa)&np.isfinite(bb)
        if mask.sum()<n: continue
        bv=float(np.mean((bb[mask]-bb[mask].mean())**2))
        if bv>0: out.iloc[i]=float(np.mean((aa[mask]-aa[mask].mean())*(bb[mask]-bb[mask].mean()))/bv)
    return out
def corr(a,b,n=60): return a.rolling(n).corr(b)

def aroon(df,n=25):
    n=int(n)
    def _u(z): return 100.0*(n-(len(z)-1-np.argmax(z)))/n
    def _d(z): return 100.0*(n-(len(z)-1-np.argmin(z)))/n
    up=df.high.rolling(n,min_periods=n).apply(_u,raw=True); dn=df.low.rolling(n,min_periods=n).apply(_d,raw=True); return up,dn,up-dn
def cmo(c,n=14):
    d=c.diff(); up=d.clip(lower=0).rolling(n,min_periods=n).sum(); dn=(-d.clip(upper=0)).rolling(n,min_periods=n).sum(); den=up+dn; return 100*(up-dn)/den.replace(0,np.nan)
def ultimate_oscillator(df,s=7,m=14,l=28):
    prev=df.close.shift(); lo=pd.concat([df.low,prev],axis=1).min(axis=1); hi=pd.concat([df.high,prev],axis=1).max(axis=1); bp=df.close-lo; tr=hi-lo
    return 100*(4*bp.rolling(s,min_periods=s).sum()/tr.rolling(s,min_periods=s).sum()+2*bp.rolling(m,min_periods=m).sum()/tr.rolling(m,min_periods=m).sum()+bp.rolling(l,min_periods=l).sum()/tr.rolling(l,min_periods=l).sum())/7
def vortex(df,n=14):
    tr=true_range(df); vp=(df.high-df.low.shift()).abs(); vm=(df.low-df.high.shift()).abs(); ts=tr.rolling(n,min_periods=n).sum().replace(0,np.nan); return vp.rolling(n,min_periods=n).sum()/ts,vm.rolling(n,min_periods=n).sum()/ts
def efficiency_ratio(c,n=10): return c.diff(n).abs()/c.diff().abs().rolling(n,min_periods=n).sum().replace(0,np.nan)
def vhf(c,n=28): return (c.rolling(n,min_periods=n).max()-c.rolling(n,min_periods=n).min())/c.diff().abs().rolling(n,min_periods=n).sum().replace(0,np.nan)
def dema(c,n): e=_ema(c,n); return 2*e-_ema(e,n)
def tema(c,n): e1=_ema(c,n); e2=_ema(e1,n); e3=_ema(e2,n); return 3*e1-3*e2+e3
def hma(c,n): n2=max(1,int(n)//2); root=max(1,int(np.sqrt(n))); return _wma(2*_wma(c,n2)-_wma(c,n),root)
def kama(c,n=10,fast=2,slow=30):
    er=efficiency_ratio(c,n); sc=(er*(2/(fast+1)-2/(slow+1))+2/(slow+1))**2; vals=c.to_numpy(); out=np.full(len(c),np.nan)
    if len(c): out[0]=vals[0]
    for i in range(1,len(c)):
        if not np.isfinite(out[i-1]): out[i]=vals[i]
        elif np.isfinite(sc.iloc[i]): out[i]=out[i-1]+sc.iloc[i]*(vals[i]-out[i-1])
        else: out[i]=out[i-1]
    return pd.Series(out,index=c.index)
def pvi(df):
    r=df.close.pct_change().fillna(0); out=pd.Series(index=df.index,dtype=float); out.iloc[0]=1000
    for i in range(1,len(df)): out.iloc[i]=out.iloc[i-1]*(1+r.iloc[i]) if df.volume.iloc[i]>df.volume.iloc[i-1] else out.iloc[i-1]
    return out
def nvi(df):
    r=df.close.pct_change().fillna(0); out=pd.Series(index=df.index,dtype=float); out.iloc[0]=1000
    for i in range(1,len(df)): out.iloc[i]=out.iloc[i-1]*(1+r.iloc[i]) if df.volume.iloc[i]<df.volume.iloc[i-1] else out.iloc[i-1]
    return out
def pvt(df): return (df.close.pct_change().fillna(0)*df.volume).cumsum()
def force_index(df,n=13): return _ema(df.close.diff()*df.volume,n)
def market_facilitation(df): return (df.high-df.low)/df.volume.replace(0,np.nan)
def stoch_rsi(c,rsi_n=14,k_n=5,d_n=3,d_ma='sma'):
    r=rsi(c,rsi_n); lo=r.rolling(k_n,min_periods=k_n).min(); hi=r.rolling(k_n,min_periods=k_n).max(); k=100*(r-lo)/(hi-lo).replace(0,np.nan); k=k.fillna(0).where((hi-lo).notna(),np.nan); return k,_ma(k,d_n,d_ma)
def rvi(df,n=14,std_n=10):
    ret=df.close.diff(); sd=ret.rolling(std_n,min_periods=std_n).std(ddof=0); up=sd.where(ret>0,0.0); dn=sd.where(ret<0,0.0); su,sdw=_wilder(up,n),_wilder(dn,n); den=su+sdw; return (100*su/den.replace(0,np.nan)).where(den.ne(0),50)
def supertrend(df,n=10,mult=3.):
    a=atr(df,n); hl2=(df.high+df.low)/2; upper=hl2+mult*a; lower=hl2-mult*a; fu=pd.Series(np.nan,index=df.index); fl=pd.Series(np.nan,index=df.index); trend=pd.Series(np.nan,index=df.index)
    valid=np.flatnonzero(a.notna().to_numpy())
    if not len(valid): return pd.Series(np.nan,index=df.index),trend
    i0=int(valid[0]); fu.iloc[i0]=upper.iloc[i0]; fl.iloc[i0]=lower.iloc[i0]; trend.iloc[i0]=1
    for i in range(i0+1,len(df)):
        fu.iloc[i]=upper.iloc[i] if (upper.iloc[i]<fu.iloc[i-1] or df.close.iloc[i-1]>fu.iloc[i-1]) else fu.iloc[i-1]
        fl.iloc[i]=lower.iloc[i] if (lower.iloc[i]>fl.iloc[i-1] or df.close.iloc[i-1]<fl.iloc[i-1]) else fl.iloc[i-1]
        trend.iloc[i]=1 if df.close.iloc[i]>fu.iloc[i-1] else (-1 if df.close.iloc[i]<fl.iloc[i-1] else trend.iloc[i-1])
    return pd.Series(np.where(trend>0,fl,fu),index=df.index),trend
def pivot_points(df):
    ph,pl,pc=df.high.shift(1),df.low.shift(1),df.close.shift(1); p=(ph+pl+pc)/3; return p,2*p-pl,2*p-ph,p+(ph-pl),p-(ph-pl)

# Additional high-value TA/price/statistical functions.
def avgprice(df): return (df.open+df.high+df.low+df.close)/4
def medprice(df): return (df.high+df.low)/2
def typprice(df): return (df.high+df.low+df.close)/3
def wclprice(df): return (df.high+df.low+2*df.close)/4
def heikin_ashi(df):
    ha_close=(df.open+df.high+df.low+df.close)/4; ha_open=pd.Series(np.nan,index=df.index)
    if len(df): ha_open.iloc[0]=(df.open.iloc[0]+df.close.iloc[0])/2
    for i in range(1,len(df)): ha_open.iloc[i]=(ha_open.iloc[i-1]+ha_close.iloc[i-1])/2
    return ha_open,(df.high.combine(pd.Series(np.maximum(ha_open,ha_close),index=df.index),max)),(df.low.combine(pd.Series(np.minimum(ha_open,ha_close),index=df.index),min)),ha_close
def rolling_stats(c,n=20):
    x=pd.Series(np.arange(n,dtype=float),index=range(n)); xmean=x.mean(); den=((x-xmean)**2).sum()
    def slope(z):
        y=np.asarray(z); return float(np.sum((x-xmean)*(y-y.mean()))/den)
    sl=c.rolling(n,min_periods=n).apply(slope,raw=True); intercept=_sma(c,n)-sl*xmean; forecast=intercept+sl*(n-1); angle=np.degrees(np.arctan(sl)); std=c.rolling(n,min_periods=n).std(ddof=0); var=c.rolling(n,min_periods=n).var(ddof=0)
    return sl,intercept,forecast,angle,std,var
def percentile_rank(c,n=20):
    return c.rolling(n,min_periods=n).apply(lambda z:100*np.mean(z<=z[-1]),raw=True)
def percent_rank(c,n=20): return percentile_rank(c,n)/100
def adr(df,n=14): return (df.high-df.low).rolling(n,min_periods=n).mean()
def chaikin_volatility(df,n=10):
    r=df.high-df.low; e=_ema(r,n); return 100*(e/e.shift(n)-1)
def mass_index(df,ema_n=9,sum_n=25):
    r=df.high-df.low; e=_ema(r,ema_n); ratio=e/_ema(e,ema_n); return ratio.rolling(sum_n,min_periods=sum_n).sum()
def bop(df): return (df.close-df.open)/(df.high-df.low).replace(0,np.nan)
def momentum(c,n=10): return c-c.shift(n)
def qstick(df,n=14): return _sma(df.close-df.open,n)
def elder_ray(df,n=13):
    e=_ema(df.close,n); return df.high-e,df.low-e
def wad(df):
    prev=df.close.shift(); ad=pd.Series(0.,index=df.index); ad.iloc[0]=0
    for i in range(1,len(df)):
        if df.close.iloc[i]>prev.iloc[i]: ad.iloc[i]=df.close.iloc[i]-min(df.low.iloc[i],prev.iloc[i])
        elif df.close.iloc[i]<prev.iloc[i]: ad.iloc[i]=df.close.iloc[i]-max(df.high.iloc[i],prev.iloc[i])
    return ad.cumsum()
def trix(c,n=30): return _ema(_ema(_ema(c,n),n),n).pct_change()*100
def dpo(c,n=20): return c.shift(int(n)//2+1)-_sma(c,n)
def coppock(c,roc1=14,roc2=11,wma=10): return _wma(roc(c,roc1)+roc(c,roc2),wma)
def imi(df,n=14):
    up=(df.close-df.open).clip(lower=0); dn=(df.open-df.close).clip(lower=0); return 100*up.rolling(n,min_periods=n).sum()/(up.rolling(n,min_periods=n).sum()+dn.rolling(n,min_periods=n).sum()).replace(0,np.nan)
def acceleration_bands(df,n=20,mult=4):
    hl=(df.high-df.low); mid=(df.high+df.low)/2; fac=mult*hl/(df.high+df.low).replace(0,np.nan); upper=(df.high*(1+fac)).rolling(n,min_periods=n).mean(); lower=(df.low*(1-fac)).rolling(n,min_periods=n).mean(); return upper,lower,mid.rolling(n,min_periods=n).mean()
def midpoint(c,n=14): return (c.rolling(n,min_periods=n).max()+c.rolling(n,min_periods=n).min())/2
def midprice(df,n=14): return (df.high.rolling(n,min_periods=n).max()+df.low.rolling(n,min_periods=n).min())/2
def zlema(c,n=20):
    lag=(n-1)//2; adj=c+(c-c.shift(lag)); return _ema(adj,n)
def trima(c,n=20): return _sma(_sma(c,(n+1)//2),n//2+1)
def t3(c,n=5,v=0.7):
    e1=_ema(c,n); e2=_ema(e1,n); e3=_ema(e2,n); e4=_ema(e3,n); e5=_ema(e4,n); e6=_ema(e5,n); a=v; c1=-a**3; c2=3*a*a+3*a**3; c3=-6*a*a-3*a-3*a**3; c4=1+3*a+a**3+3*a*a; return c1*e6+c2*e5+c3*e4+c4*e3

def add_all(df: pd.DataFrame, params=None) -> pd.DataFrame:
    x = df.copy().sort_index()
    if params is None:
        path = Path(__file__).resolve().parents[3] / 'config' / 'indicator_parameters.yaml'
        with open(path, 'r', encoding='utf-8') as f:
            params = yaml.safe_load(f)
    t = params.get('trend', {})
    m = params.get('momentum', {})
    vol = params.get('volatility', {})
    q = params.get('volume', {})
    ps = params.get('price_structure', {})
    rel = params.get('relative', {})
    extra = params.get('additional', {})
    c, h, l, v = x.close, x.high, x.low, x.volume
    feat = {}

    for n in rel.get('returns', [1, 3, 5, 20, 60, 120]):
        feat[f'return_{n}d'] = c.pct_change(n)

    sma_p = t.get('sma', [5, 10, 20, 50, 100, 200])
    ema_p = t.get('ema', [5, 10, 20, 50, 100, 200])
    for n in sorted(set(sma_p + ema_p)):
        feat[f'sma_{n}'] = _sma(c, n)
        feat[f'ema_{n}'] = _ema(c, n)
        feat[f'price_sma_{n}_gap'] = c / feat[f'sma_{n}'] - 1
        feat[f'price_ema_{n}_gap'] = c / feat[f'ema_{n}'] - 1
    feat['dema_20'] = dema(c, t.get('dema', [20])[0])
    feat['tema_20'] = tema(c, t.get('tema', [20])[0])
    feat['hma_20'] = hma(c, t.get('hma', [20])[0])
    kp = t.get('kama', {})
    feat['kama_10'] = kama(c, kp.get('period', 10), kp.get('fast', 2), kp.get('slow', 30))
    feat['tr'] = true_range(x)
    for n in vol.get('atr', [5, 14, 20]):
        feat[f'atr_{n}'] = atr(x, n)
        feat[f'natr_{n}'] = natr(x, n)
    feat['atr_pct'] = feat['atr_14'] / c
    for n in vol.get('realized_vol', [5, 10, 20, 60]):
        feat[f'realized_vol_{n}'] = c.pct_change().rolling(n, min_periods=n).std(ddof=0) * np.sqrt(252)
    for n in m.get('rsi', [7, 14, 21]):
        feat[f'rsi_{n}'] = rsi(c, n)
    for n in m.get('roc', [5, 10, 20]):
        feat[f'roc_{n}'] = roc(c, n)
    feat['rocp_20'] = rocp(c, 20)
    feat['rocr_20'] = rocr(c, 20)
    feat['rocr100_20'] = rocr100(c, extra.get('momentum', {}).get('rocr_period', 20))
    mac = m.get('macd', {})
    m_val, ms_val, mh_val = macd(c, mac.get('fast', 12), mac.get('slow', 26), mac.get('signal', 9), mac.get('ma_type', 'ema'))
    feat['macd'], feat['macd_signal'], feat['macd_hist'] = m_val, ms_val, mh_val
    ap = extra.get('momentum', {}).get('apo', {'fast': 12, 'slow': 26, 'ma_type': 'ema'})
    feat['apo_12_26'] = apo(c, ap.get('fast', 12), ap.get('slow', 26), ap.get('ma_type', 'ema'))
    pp = m.get('ppo', {})
    ppo_v, ppos_v, ppoh_v = ppo(c, pp.get('fast', 12), pp.get('slow', 26), pp.get('signal', 9), pp.get('ma_type', 'ema'))
    feat['ppo'], feat['ppo_signal'], feat['ppo_hist'] = ppo_v, ppos_v, ppoh_v
    st = m.get('stochastic', {})
    st_k, st_d = stochastic(x, st.get('k_period', 14), st.get('slow_k_period', 3), st.get('slow_d_period', 3), st.get('slow_k_ma_type', 'sma'), st.get('slow_d_ma_type', 'sma'))
    feat['stoch_k'], feat['stoch_d'] = st_k, st_d
    sf = extra.get('momentum', {}).get('stochastic_fast', {})
    stf_k, stf_d = stochastic_fast(x, sf.get('k_period', 5), sf.get('d_period', 3), sf.get('d_ma_type', 'sma'))
    feat['stoch_fast_k'], feat['stoch_fast_d'] = stf_k, stf_d
    sr = m.get('stochastic_rsi', {})
    sr_k, sr_d = stoch_rsi(c, sr.get('rsi_period', 14), sr.get('k_period', 5), sr.get('d_period', 3), sr.get('d_ma_type', 'sma'))
    feat['stochrsi_k'], feat['stochrsi_d'] = sr_k, sr_d
    adx_v, plus_di_v, minus_di_v = adx(x, m.get('adx', {}).get('period', 14))
    feat['adx'], feat['plus_di'], feat['minus_di'] = adx_v, plus_di_v, minus_di_v
    dxp = extra.get('momentum', {}).get('dx_period', 14)
    feat['dx_14'] = dx(x, dxp)
    feat['plus_dm_14'] = plus_dm(x, dxp)
    feat['minus_dm_14'] = minus_dm(x, dxp)
    feat['adxr'] = adxr(x, m.get('adxr', {}).get('period', 14))
    feat['williams_r'] = williams_r(x, m.get('williams_r', {}).get('period', 14))
    feat['cci_20'] = cci(x, m.get('cci', {}).get('period', 20))
    feat['mfi_14'] = mfi(x, m.get('mfi', {}).get('period', 14))
    feat['cmf_20'] = cmf(x, q.get('cmf', {}).get('period', 20))
    ts = m.get('tsi', {})
    feat['tsi'] = tsi(c, ts.get('long', 25), ts.get('short', 13))
    ao = m.get('awesome_oscillator', {})
    feat['awesome_osc'] = awesome_osc(x, ao.get('fast', 5), ao.get('slow', 34))
    feat['cmo_14'] = cmo(c, m.get('cmo', {}).get('period', 14))
    uo = m.get('ultimate_oscillator', {})
    feat['ultimate_osc'] = ultimate_oscillator(x, uo.get('short', 7), uo.get('medium', 14), uo.get('long', 28))
    vx = m.get('vortex', {})
    v_plus, v_minus = vortex(x, vx.get('period', 14))
    feat['vortex_plus'], feat['vortex_minus'] = v_plus, v_minus
    feat['vortex_14'] = feat['vortex_plus'] - feat['vortex_minus']
    ar = m.get('aroon', t.get('aroon', {}))
    a_up, a_down, a_osc = aroon(x, ar.get('period', 25))
    feat['aroon_up'], feat['aroon_down'], feat['aroon_osc'] = a_up, a_down, a_osc
    rv = m.get('rvi', {})
    feat['rvi_14'] = rvi(x, rv.get('period', 14), rv.get('stddev_period', 10))
    feat['efficiency_ratio_10'] = efficiency_ratio(c, m.get('efficiency_ratio', {}).get('period', 10))
    feat['vhf_28'] = vhf(c, m.get('vhf', {}).get('period', 28))

    bb = vol.get('bollinger', {})
    mid, up, lo, bp = bollinger(c, bb.get('period', 20), bb.get('stddev_up', bb.get('stddev', 2.)), bb.get('stddev_dn', bb.get('stddev', 2.)), bb.get('ma_type', 'sma'))
    feat['bb_mid'], feat['bb_upper'], feat['bb_lower'], feat['bb_pos'] = mid, up, lo, bp
    feat['bb_width'] = (up - lo) / mid.replace(0, np.nan)

    for n in vol.get('donchian', t.get('donchian', [20, 55])):
        dh, dl = donchian(x, n)
        feat[f'donchian_high_{n}'] = dh
        feat[f'donchian_low_{n}'] = dl
        feat[f'donchian_pos_{n}'] = (c - dl) / (dh - dl).replace(0, np.nan)
    alias_n = int(vol.get('donchian', t.get('donchian', [20, 55]))[0])
    feat['donchian_high'] = feat[f'donchian_high_{alias_n}']
    feat['donchian_low'] = feat[f'donchian_low_{alias_n}']
    feat['donchian_pos'] = feat[f'donchian_pos_{alias_n}']

    kc = vol.get('keltner', t.get('keltner', {}))
    ku, kl, kpos = keltner(x, kc.get('ema_period', 20), kc.get('atr_period', 10), kc.get('multiplier', 2.))
    feat['keltner_upper'], feat['keltner_lower'], feat['keltner_pos'] = ku, kl, kpos

    sar = t.get('parabolic_sar', {})
    feat['parabolic_sar'] = parabolic_sar(x, sar.get('step', .02), sar.get('max_af', .2))
    feat['sar_gap'] = c / feat['parabolic_sar'].replace(0, np.nan) - 1
    su = t.get('supertrend', {})
    st_v, st_d = supertrend(x, su.get('atr_period', 10), su.get('multiplier', 3.))
    feat['supertrend'], feat['supertrend_direction'] = st_v, st_d
    feat['supertrend_gap'] = c / feat['supertrend'].replace(0, np.nan) - 1
    p_vals = pivot_points(x)
    feat['pivot'], feat['pivot_r1'], feat['pivot_s1'], feat['pivot_r2'], feat['pivot_s2'] = p_vals

    feat['gap_pct'] = x.open / x.close.shift(1) - 1
    feat['intraday_range_pct'] = (h - l) / c.replace(0, np.nan)
    feat['body_pct'] = (c - x.open) / x.open.replace(0, np.nan)
    feat['upper_wick_pct'] = (h - x[['open', 'close']].max(axis=1)) / x.open.replace(0, np.nan)
    feat['lower_wick_pct'] = (x[['open', 'close']].min(axis=1) - l) / x.open.replace(0, np.nan)

    feat['obv'] = obv(x)
    feat['obv_z'] = rolling_z(feat['obv'], 20)
    feat['ad_line'] = ad_line(x)
    adp = q.get('ad_oscillator', {})
    feat['ad_osc'] = ad_osc(x, adp.get('fast', 3), adp.get('slow', 10))
    feat['pvt'] = pvt(x)
    feat['vwap'] = vwap(x)
    feat['vwap_gap'] = c / feat['vwap'].replace(0, np.nan) - 1
    fi = q.get('force_index', {})
    feat['force_index_13'] = force_index(x, fi.get('period', 13))
    feat['market_facilitation'] = market_facilitation(x)
    feat['pvi'] = pvi(x)
    feat['nvi'] = nvi(x)
    feat['volume_z'] = rolling_z(v, q.get('volume_zscore', [20])[0])
    feat['volume_ratio_20'] = v / v.rolling(q.get('volume_ratio', [20, 50])[0], min_periods=q.get('volume_ratio', [20, 50])[0]).mean()
    feat['volume_ratio_50'] = v / v.rolling(q.get('volume_ratio', [20, 50])[1], min_periods=q.get('volume_ratio', [20, 50])[1]).mean()
    feat['dollar_volume'] = c * v
    feat['turnover_z'] = rolling_z(feat['dollar_volume'], 20)

    pvconf = q.get('pvo', extra.get('volume', {}).get('pvo', {'fast': 12, 'slow': 26, 'signal': 9, 'ma_type': 'ema'}))
    pv_v, pvs_v, pvh_v = pvo(v, pvconf.get('fast', 12), pvconf.get('slow', 26), pvconf.get('signal', 9), pvconf.get('ma_type', 'ema'))
    feat['pvo'], feat['pvo_signal'], feat['pvo_hist'] = pv_v, pvs_v, pvh_v
    rvol_n = extra.get('volume', {}).get('rvol_period', 20)
    feat['rvol_20'] = rvol(v, rvol_n)
    feat['vwma_20'] = vwma(x, extra.get('overlap', {}).get('vwma_period', 20))

    for n in rel.get('returns', [1, 3, 5, 20, 60, 120]):
        feat[f'return_{n}d'] = c.pct_change(n)

    breakout_n = int(vol.get('donchian', t.get('donchian', [20, 55]))[0])
    feat['trend_strength'] = (feat['ema_20'] - feat['ema_50']) / c
    feat['ema_stack_bull'] = ((feat['ema_10'] > feat['ema_20']) & (feat['ema_20'] > feat['ema_50']) & (feat['ema_50'] > feat['ema_200'])).astype(int)
    feat['high_20_breakout'] = (c >= feat[f'donchian_high_{breakout_n}'].shift(1)).astype(int)
    feat['low_20_breakdown'] = (c <= feat[f'donchian_low_{breakout_n}'].shift(1)).astype(int)
    feat['atr_z_60'] = rolling_z(feat['atr_14'], 60)
    feat['range_z_20'] = rolling_z(h - l, 20)

    feat['avg_price'] = avgprice(x)
    feat['median_price'] = medprice(x)
    feat['typical_price'] = typprice(x)
    feat['weighted_close'] = wclprice(x)
    ha_o, ha_h, ha_l, ha_c = heikin_ashi(x)
    feat['ha_open'], feat['ha_high'], feat['ha_low'], feat['ha_close'] = ha_o, ha_h, ha_l, ha_c
    feat['wma_20'] = wma(c, extra.get('overlap', {}).get('wma_period', 20))
    feat['ht_trendline'] = ht_trendline(c, extra.get('overlap', {}).get('ht_trendline_period', 20))

    stat = extra.get('statistics', {})
    stat_n = stat.get('linear_regression_window', 20)
    sl, ic, fc, ang, sd, var = rolling_stats(c, stat_n)
    feat['linearreg_slope_20'], feat['linearreg_intercept_20'], feat['tsf_20'], feat['linearreg_angle_20'], feat['stddev_20'], feat['variance_20'] = sl, ic, fc, ang, sd, var
    pct_n = stat.get('percentile_window', 20)
    feat['percentile_20'] = percentile_rank(c, pct_n)
    feat['percent_rank_20'] = percent_rank(c, stat.get('percent_rank_window', pct_n))

    feat['aroon_osc'] = aroonosc(x, t.get('aroon', {}).get('period', 25))
    feat['cmou_14'] = cmou(c, extra.get('momentum', {}).get('cmou', {}).get('period', 14))
    feat['ac_5_34'] = ac_osc(x, 5, 34)
    kj = extra.get('momentum', {}).get('kdj', {})
    k_k, k_d, k_j = kdj(x, kj.get('k_period', 9), kj.get('k_smooth', 3), kj.get('d_smooth', 3), kj.get('k_ma_type', 'rma'), kj.get('d_ma_type', 'rma'))
    feat['kdj_k'], feat['kdj_d'], feat['kdj_j'] = k_k, k_d, k_j
    me = extra.get('momentum', {}).get('macd_extended', {})
    me_m, me_s, me_h = macdext(c, me.get('fast', 12), me.get('slow', 26), me.get('signal', 9), me.get('fast_type', 'ema'), me.get('slow_type', 'ema'), me.get('signal_type', 'ema'))
    feat['macdext'], feat['macdext_signal'], feat['macdext_hist'] = me_m, me_s, me_h
    mf_m, mf_s, mf_h = macdfix(c, extra.get('momentum', {}).get('macdfix_signal', 9))
    feat['macdfix'], feat['macdfix_signal'], feat['macdfix_hist'] = mf_m, mf_s, mf_h
    feat['fosc_14'] = fosc(c, extra.get('momentum', {}).get('fosc_period', 14))
    f_up, f_dn = fractal_williams(x)
    feat['fractal_up'], feat['fractal_down'] = f_up, f_dn

    vp = extra.get('volatility', {})
    feat['adr_14'] = adr(x, vp.get('adr_period', 14))
    feat['chaikin_volatility_10'] = chaikin_volatility(x, vp.get('chaikin_volatility_period', 10))
    feat['mass_index_9_25'] = mass_index(x, vp.get('mass_index_ema', 9), vp.get('mass_index_sum', 25))
    feat['bop'] = bop(x)
    mp = extra.get('momentum', {})
    feat['momentum_10'] = momentum(c, mp.get('momentum_period', 10))
    feat['qstick_14'] = qstick(x, mp.get('qstick_period', 14))
    eb_p, eb_b = elder_ray(x, mp.get('elder_ray_period', 13))
    feat['elder_bull_power'], feat['elder_bear_power'] = eb_p, eb_b
    feat['wad'] = wad(x)
    feat['trix_30'] = trix(c, mp.get('trix_period', 30))
    feat['dpo_20'] = dpo(c, mp.get('dpo_period', 20))
    cp = mp.get('coppock', {})
    feat['coppock'] = coppock(c, cp.get('roc1', 14), cp.get('roc2', 11), cp.get('wma', 10))
    feat['imi_14'] = imi(x, mp.get('imi_period', 14))
    op = extra.get('overlap', {})
    ab = op.get('acceleration_bands', {})
    ab_u, ab_l, ab_m = acceleration_bands(x, ab.get('period', 20), ab.get('multiplier', 4))
    feat['accbands_upper'], feat['accbands_lower'], feat['accbands_mid'] = ab_u, ab_l, ab_m
    feat['midpoint_14'] = midpoint(c, op.get('midpoint_period', 14))
    feat['midprice_14'] = midprice(x, op.get('midprice_period', 14))
    feat['zlema_20'] = zlema(c, op.get('zlema_period', 20))
    feat['trima_20'] = trima(c, op.get('trima_period', 20))
    t3p = op.get('t3', {})
    feat['t3_5'] = t3(c, t3p.get('period', 5), t3p.get('volume_factor', .7))

    add = extra.get('momentum', {})
    feat['ibs'] = ibs(x)
    feat['chop_14'] = chop(x, add.get('chop_period', 14))
    feat['choptr_14'] = choptr(x, add.get('choptr_period', 14))
    feat['center_of_gravity_10'] = center_of_gravity(c, add.get('center_of_gravity_period', 10))
    cr = add.get('connors_rsi', {})
    feat['connors_rsi'] = connors_rsi(c, cr.get('rsi_period', 3), cr.get('streak_rsi_period', 2), cr.get('rank_period', 100))
    sm = add.get('smi', {})
    s_v, ss_v = stochastic_momentum_index(x, sm.get('period', 13), sm.get('fast', sm.get('smooth2', 2)), sm.get('slow', sm.get('smooth1', 25)), sm.get('signal_period', 9))
    feat['smi'], feat['smi_signal'] = s_v, ss_v
    ks = add.get('kst', {})
    kst_v, ksts_v, ksth_v = kst(c, tuple(ks.get('roc_periods', [10, 15, 20, 30])), tuple(ks.get('sma_periods', [10, 10, 10, 15])), tuple(ks.get('weights', [1, 2, 3, 4])), ks.get('signal_period', 9))
    feat['kst'], feat['kst_signal'], feat['kst_hist'] = kst_v, ksts_v, ksth_v
    ke = add.get('kstext', {})
    kste_v, kstes_v, ksteh_v = kstext(c, tuple(ke.get('roc_periods', [10, 15, 20, 30])), tuple(ke.get('sma_periods', [10, 10, 10, 15])), tuple(ke.get('weights', [1, 2, 3, 4])), ke.get('signal_period', 9), ke.get('ma_type', 'sma'))
    feat['kstext'], feat['kstext_signal'], feat['kstext_hist'] = kste_v, kstes_v, ksteh_v
    feat['kurtosis_20'] = rolling_kurtosis(c, extra.get('statistics', {}).get('kurtosis_window', 20))
    feat['median_20'] = rolling_median(c, extra.get('statistics', {}).get('median_window', 20))
    feat['emv_14'] = emv(x, extra.get('volume', {}).get('emv_period', 14))
    feat['rvir_14'] = rv_ir(x, extra.get('volatility', {}).get('rvir_period', 14))

    for col in ['india_vix', 'nifty_return', 'sector_return', 'fii_net', 'dii_net', 'pcr', 'oi_change', 'futures_basis', 'advance_decline_ratio', 'relative_strength', 'delivery_pct', 'bid_ask_spread_bps', 'order_book_imbalance', 'news_sentiment', 'earnings_days', 'corporate_action_flag']:
        if col in x:
            feat[f'{col}_z20'] = rolling_z(x[col], 20)
    if 'nifty_return' in x:
        r1d = feat.get('return_1d', c.pct_change())
        r20d = feat.get('return_20d', c.pct_change(20))
        feat['beta_60'] = beta_vs_market(r1d, x.nifty_return, 60)
        feat['corr_60'] = corr(r1d, x.nifty_return, 60)
        feat['relative_strength_nifty'] = r20d - ((1 + x.nifty_return).rolling(20, min_periods=20).apply(np.prod, raw=True) - 1)
    if 'sector_return' in x:
        r20d = feat.get('return_20d', c.pct_change(20))
        feat['relative_strength_sector'] = r20d - ((1 + x.sector_return).rolling(20, min_periods=20).apply(np.prod, raw=True) - 1)

    feat_df = pd.DataFrame(feat, index=x.index)
    x = pd.concat([x, feat_df], axis=1)
    return x.replace([np.inf, -np.inf], np.nan)

# Extended TA-Lib-family indicators whose formulas are unambiguous and useful for
# research.  These remain candidate features; they are not automatically trusted.
def rocr100(c,n=20): return 100*rocr(c,n)
def aroonosc(df,n=25):
    up,dn,_=aroon(df,n); return up-dn

def cmou(c,n=14):
    d=c.diff(); up=d.clip(lower=0).rolling(n,min_periods=n).sum(); dn=(-d.clip(upper=0)).rolling(n,min_periods=n).sum(); den=up+dn
    return 100*(up-dn)/den.replace(0,np.nan)

def ac_osc(df,fast=5,slow=34):
    med=(df.high+df.low)/2
    return _sma(med,fast)-_sma(med,slow)

def kdj(df,k_period=9,k_smooth=3,d_smooth=3,k_ma='rma',d_ma='rma'):
    raw,_=stochastic(df,k_period,1,1,'sma','sma')
    k=_ma(raw,k_smooth,k_ma); d=_ma(k,d_smooth,d_ma); j=3*k-2*d
    return k,d,j

def macdext(c,fast=12,slow=26,signal=9,fast_type='ema',slow_type='ema',signal_type='ema'):
    def ma(s,n,t):
        t=str(t).lower()
        if t=='sma': return _sma(s,n)
        if t=='wma': return _wma(s,n)
        if t=='dema': return dema(s,n)
        if t=='tema': return tema(s,n)
        if t=='trima': return trima(s,n)
        if t=='kama': return kama(s,n)
        if t=='t3': return t3(s,n,.7)
        if t=='hma': return hma(s,n)
        if t=='rma': return _wilder(s,n)
        if t=='zlema': return zlema(s,n)
        return _ema(s,n)
    line=ma(c,fast,fast_type)-ma(c,slow,slow_type); sig=ma(line,signal,signal_type)
    return line,sig,line-sig

def macdfix(c,signal=9): return macd(c,12,26,signal)

def tsf(c,n=20):
    sl,ic,fc,ang,sd,var=rolling_stats(c,n)
    return fc

def fosc(c,n=14):
    fc=tsf(c,n); return 100*(c-fc)/c.replace(0,np.nan)

def fractal_williams(df):
    # Five-bar Williams fractal: center high/low must exceed the two bars on
    # either side. It is emitted only after the right-hand confirmation bars.
    up=(df.high.shift(2)<df.high)&(df.high.shift(1)<df.high)&(df.high.shift(-1)<df.high)&(df.high.shift(-2)<df.high)
    dn=(df.low.shift(2)>df.low)&(df.low.shift(1)>df.low)&(df.low.shift(-1)>df.low)&(df.low.shift(-2)>df.low)
    # Shift confirmation to the bar on which the pattern becomes knowable.
    return up.shift(2).fillna(False).astype(int),dn.shift(2).fillna(False).astype(int)

def wma(c,n=20): return _wma(c,n)

def ht_trendline(c,n=20):
    # Stable causal proxy for Hilbert-style trendline: a centered Hilbert
    # transform would leak future values, so use a causal two-pole smoothing.
    e1=_ema(c,n); return _ema(e1,max(2,n//2))

# Additional reference-family indicators. These are executable, causal research
# candidates and are kept separate from the core model until OOS validation.
def ibs(df):
    return (df.close-df.low)/(df.high-df.low).replace(0,np.nan)

def chop(df,n=14):
    tr=true_range(df); rng=df.high.rolling(n,min_periods=n).max()-df.low.rolling(n,min_periods=n).min()
    return 100*np.log10(tr.rolling(n,min_periods=n).sum()/rng.replace(0,np.nan))/np.log10(n)

def choptr(df,n=14):
    # True-range-box variant: same Choppiness construction with a TR-derived
    # rolling box width, avoiding a high/low-only denominator.
    tr=true_range(df); box=tr.rolling(n,min_periods=n).sum()
    return 100*np.log10(box/box.rolling(n,min_periods=n).mean().replace(0,np.nan))/np.log10(n)

def center_of_gravity(c,n=10):
    n=int(n); w=np.arange(1,n+1,dtype=float)
    return c.rolling(n,min_periods=n).apply(lambda z: -float(np.dot(w,z))/float(np.sum(z)) if np.sum(z)!=0 else np.nan,raw=True)

def connors_rsi(c,rsi_period=3,streak_rsi_period=2,rank_period=100):
    r1=rsi(c,rsi_period)
    d=c.diff(); streak=np.zeros(len(c),dtype=float)
    for i in range(1,len(c)):
        if d.iloc[i]>0: streak[i]=streak[i-1]+1 if streak[i-1]>0 else 1
        elif d.iloc[i]<0: streak[i]=streak[i-1]-1 if streak[i-1]<0 else -1
        else: streak[i]=0
    rs=rsi(pd.Series(streak,index=c.index),streak_rsi_period)
    rank=c.pct_change().rolling(rank_period,min_periods=rank_period).apply(lambda z:100*np.mean(z<=z[-1]),raw=True)
    return (r1+rs+rank)/3

def stochastic_momentum_index(df,period=13,fast=2,slow=25,signal_period=9):
    hh=df.high.rolling(period,min_periods=period).max(); ll=df.low.rolling(period,min_periods=period).min(); mid=(hh+ll)/2
    rel=df.close-mid; rng=hh-ll
    num=_ema(_ema(rel,slow),fast); den=_ema(_ema(rng,slow),fast)
    smi=100*num/(0.5*den).replace(0,np.nan)
    smi=smi.where((den!=0),0.0)
    signal=_ema(smi,signal_period)
    return smi,signal

def kst(c,roc_periods=(10,15,20,30),sma_periods=(10,10,10,15),weights=(1,2,3,4),signal_period=9):
    comps=[]
    for r,s,w in zip(roc_periods,sma_periods,weights): comps.append(w*_sma(roc(c,r),s))
    line=sum(comps); sig=_sma(line,signal_period)
    return line,sig,line-sig

def kstext(c,roc_periods=(10,15,20,30),sma_periods=(10,10,10,15),weights=(1,2,3,4),signal_period=9,ma_type='sma'):
    def ma(s,n):
        return _ema(s,n) if str(ma_type).lower()=='ema' else _sma(s,n)
    line=sum(w*ma(roc(c,r),s) for r,s,w in zip(roc_periods,sma_periods,weights)); sig=ma(line,signal_period)
    return line,sig,line-sig

def rolling_kurtosis(c,n=20):
    return c.rolling(n,min_periods=n).kurt()

def rolling_median(c,n=20):
    return c.rolling(n,min_periods=n).median()

def emv(df,n=14):
    distance=((df.high+df.low)/2).diff(); box=(df.high-df.low).replace(0,np.nan); raw=distance*box/df.volume.replace(0,np.nan); return _sma(raw,n)

def rv_ir(df,n=14):
    # Refined RVI using high/low range volatility split, smoothed causally.
    rng=(df.high-df.low).abs(); direction=df.close.diff()
    up=rng.where(direction>0,0.0); dn=rng.where(direction<0,0.0)
    su,sd=_wilder(up,n),_wilder(dn,n); den=su+sd
    return (100*su/den.replace(0,np.nan)).where(den.ne(0),50)
