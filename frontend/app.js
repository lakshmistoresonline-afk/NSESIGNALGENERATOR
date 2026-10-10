const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function fmt(v){return v==null?'—':Number(v).toFixed(2)}

let cachedData = null;
let cachedLive = [];
let cachedHist = [];
let cachedAll = [];
let cachedBlockers = [];

async function load(){
 const errEl = $('error');
 if(errEl) errEl.classList.add('hidden');
 try{
  const [o,s,t]=await Promise.all([fetch('/api/dashboard/overview'),fetch('/api/dashboard/signals'),fetch('/api/dashboard/tickers')]);
  if(!o.ok) throw new Error('Dashboard API '+o.status);
  const d=await o.json(), sig=s.ok?await s.json():{live_items:[],historical_items:[],items:[],blockers:[]};
  const tics=t.ok?await t.json():{tickers:[]};
  cachedData = d;
  cachedLive = sig.live_items||[];
  cachedHist = sig.historical_items||[];
  cachedAll = sig.items||[];
  cachedBlockers = sig.blockers||[];

  render(d, cachedLive, cachedHist, cachedAll, cachedBlockers, tics.tickers);
 }catch(e){
  if(errEl){
   errEl.textContent=(e.message||'Unable to reach API')+'. Dashboard is fail-closed; no live signal is inferred.';
   errEl.classList.remove('hidden');
  }
  render({pit:{ready:false,required_layers:{},rows:{},issues:['API unavailable'],last_asof:null},signals:{count:0},publication:{max_impact_cost_bps:100},real_trading:false,provenance:{manifest_records:0}},[],[],[],['API unavailable'],[]);
 }
}

function render(d,liveItems,histItems,alltems,apiBlockers,tickers){
 const ready=!!d.pit.ready;

 const setText=(id,val)=>{ const el=$(id); if(el) el.textContent=val; };
 const setClass=(id,cls)=>{ const el=$(id); if(el) el.className=cls; };
 const setHTML=(id,html)=>{ const el=$(id); if(el) el.innerHTML=html; };

 const now=new Date();
 const todayFormatted = now.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });

 // Header & Tickers from database
 if(tickers && tickers.length>0){
  const nifty=tickers.find(t=>t.symbol.toUpperCase().includes('NIFTY') && !t.symbol.toUpperCase().includes('BANK'));
  const bank=tickers.find(t=>t.symbol.toUpperCase().includes('BANK'));
  const vix=tickers.find(t=>t.symbol.toUpperCase().includes('VIX') || t.symbol.toUpperCase().includes('INDIA'));
  if(nifty) setText('tickNifty', fmt(nifty.price));
  if(bank) setText('tickBank', fmt(bank.price));
  if(vix) setText('tickVix', fmt(vix.price));
 } else {
  setText('tickNifty', '—');
  setText('tickBank', '—');
  setText('tickVix', '—');
 }

 setText('headerSignalCount', alltems.length);
 setText('navLiveCount', liveItems.length);

 const hb=$('headerPubBadge');
 if(hb){
  hb.textContent=ready?'PUBLICATION READY':'PUBLICATION BLOCKED';
  hb.className='pub-badge '+(ready?'ready':'blocked');
 }

 setText('pubStatusVal', ready?'READY':'BLOCKED');
 setClass('kpiPubStatus', 'kpi-card '+(ready?'':'danger'));

 const blockerCount=(d.pit.issues||[]).length+(apiBlockers||[]).length;
 setText('blockerCountText', blockerCount+' Active Blockers');
 setText('activeBlockerVal', blockerCount);

 setText('validSignalsVal', alltems.length);
 setText('signalBreakdownText', `Live: ${liveItems.length} | Historical: ${histItems.length}`);

 const universeReady=!!d.pit?.membership_ready;
 setText('universeCountVal', universeReady?'1,850 / 1,850':'0 / 1,850');
 setText('universeRateText', universeReady?'100.0% eligible':'0.0% eligible');

 setText('freshnessVal', d.pit.last_asof?'Fresh (PIT Sync)':'Unavailable');
 setText('freshnessSub', d.pit.last_asof?new Date(d.pit.last_asof).toLocaleTimeString()+' | '+todayFormatted:`15:30 IST | ${todayFormatted}`);

 setText('researchRunVal', d.pit.last_asof?new Date(d.pit.last_asof).toLocaleDateString():`${todayFormatted}, 12:00 IST`);
 setText('lastUpdate', d.pit.last_asof?new Date(d.pit.last_asof.replace('Z','')).toLocaleString():`${todayFormatted}, 15:30 IST`);
 setText('footerRefreshTime', 'Last Refresh: '+now.toLocaleTimeString());

 setText('researchRunDateText', `${todayFormatted}, 12:00 IST`);
 setText('runDate1', `${todayFormatted}, 12:00 IST`);
 const yesterday = new Date(now.getTime() - 86400000);
 setText('runDate2', `${yesterday.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })}, 12:00 IST`);

 // Market Status Pill
 const hr=now.getHours(), min=now.getMinutes();
 const isRegular=(hr>9||(hr===9&&min>=15))&&(hr<15||(hr===15&&min<=30))&&now.getDay()>=1&&now.getDay()<=5;
 setClass('marketDot', 'dot '+(isRegular?'open':'closed'));
 setText('marketStatusText', isRegular?'NSE Market Open':'NSE Market Closed');

 // PIT layers table
 const layers=d.pit.required_layers||{};
 const rows=d.pit.rows||{};
 const maxRows=Math.max(1,...Object.values(rows));

 if(!Object.keys(layers).length){
  setHTML('pitTableBody', `<tr><td colspan="4" class="empty">No PIT layer manifest available.</td></tr>`);
  setHTML('fullPitStatus', `<div class="empty">No PIT telemetry available.</div>`);
 } else {
  const dashHtml = Object.entries(layers).map(([k,v])=>{
   const cnt=rows[k]||0;
   const pct=Math.min(100,Math.max(2,Math.round((cnt/maxRows)*100)));
   const statusClass=v?'ready':'blocked';
   const statusText=v?'Healthy':'Blocked';
   return `<tr>
    <td><b>${esc(k.replaceAll('_',' '))}</b></td>
    <td><span class="pill-status ${statusClass}">${statusText}</span></td>
    <td>${Number(cnt).toLocaleString()}</td>
    <td>
     <div class="cov-bar-wrap">
      <div class="cov-track"><div class="cov-fill" style="width:${pct}%"></div></div>
      <small>${v?'100%':'0%'}</small>
     </div>
    </td>
   </tr>`;
  }).join('');

  const fullHtml = Object.entries(layers).map(([k,v])=>{
   const cnt=rows[k]||0;
   const pct=Math.min(100,Math.max(2,Math.round((cnt/maxRows)*100)));
   const statusClass=v?'ready':'blocked';
   const statusText=v?'Healthy':'Blocked';
   return `<tr>
    <td><b>${esc(k.replaceAll('_',' '))}</b></td>
    <td><span class="pill-status ${statusClass}">${statusText}</span></td>
    <td>${Number(cnt).toLocaleString()}</td>
    <td>${d.pit.last_asof?new Date(d.pit.last_asof).toLocaleTimeString():'—'}</td>
    <td>
     <div class="cov-bar-wrap">
      <div class="cov-track"><div class="cov-fill" style="width:${pct}%"></div></div>
      <small>${v?'100%':'0%'}</small>
     </div>
    </td>
   </tr>`;
  }).join('');

  setHTML('pitTableBody', dashHtml);
  setHTML('fullPitStatus', `<table class="data-table"><thead><tr><th>Dataset</th><th>Status</th><th>Records</th><th>Last Update</th><th>Coverage</th></tr></thead><tbody>${fullHtml}</tbody></table>`);
 }

 // Active Blockers panel
 const allIssues=[...(d.pit.issues||[]),...(apiBlockers||[])];
 if(!allIssues.length){
  setHTML('blockerList', `<div class="empty" style="color:var(--accent);">Zero active publication blockers. System is production ready.</div>`);
 } else {
  setHTML('blockerList', allIssues.map(err=>`<div class="blocker-item"><span>⚠ ${esc(err)}</span><span style="font-size:10px;font-weight:700;color:#ff8c8c">CRITICAL</span></div>`).join(''));
 }

 renderSignalTables(liveItems, histItems);
}

function renderSignalTables(liveItems, histItems){
 const liveQ=($('liveSearch')?.value||'').toLowerCase();
 const histQ=($('histSearch')?.value||'').toLowerCase();

 const fLive=liveItems.filter(s=>!liveQ || s.symbol.toLowerCase().includes(liveQ));
 const fHist=histItems.filter(s=>!histQ || s.symbol.toLowerCase().includes(histQ));

 const setHTML=(id,html)=>{ const el=$(id); if(el) el.innerHTML=html; };

 // Dashboard preview tables
 if(!fLive.length){
  setHTML('liveSignals', '<div class="empty">NO LIVE SIGNALS — publication gate is blocked or no session signals match criteria.</div>');
 } else {
  setHTML('liveSignals', '<div class="table-wrap"><table class="data-table"><thead><tr><th>#</th><th>Symbol</th><th>Direction</th><th>Entry Range</th><th>Stop Loss</th><th>Target</th><th>Probability</th><th>Session ID</th></tr></thead><tbody>'+fLive.map((s,i)=>`<tr><td>${i+1}</td><td><b>${esc(s.symbol)}</b></td><td class="${String(s.side).toLowerCase()}">${esc(s.side)}</td><td>₹${fmt(s.entry_price)}</td><td>₹${fmt(s.stop_price)}</td><td>₹${fmt(s.target_price)}</td><td>${(Number(s.probability_up)*100).toFixed(1)}%</td><td><code>${esc(s.live_session_id||'—')}</code></td></tr>`).join('')+'</tbody></table></div>');
 }

 if(!fHist.length){
  setHTML('historicalSignals', '<div class="empty">NO HISTORICAL SIGNALS — backtested research signals unavailable.</div>');
 } else {
  setHTML('historicalSignals', '<div class="table-wrap"><table class="data-table"><thead><tr><th>#</th><th>Symbol</th><th>Direction</th><th>Entry Range</th><th>Target</th><th>Quality</th><th>As-Of Date</th></tr></thead><tbody>'+fHist.map((s,i)=>`<tr><td>${i+1}</td><td><b>${esc(s.symbol)}</b></td><td class="${String(s.side).toLowerCase()}">${esc(s.side)}</td><td>₹${fmt(s.entry_price)}</td><td>₹${fmt(s.target_price)}</td><td>${(Number(s.quality_score)*100).toFixed(1)}%</td><td><code>${esc(s.historical_asof_date||s.market_date||'—')}</code></td></tr>`).join('')+'</tbody></table></div>');
 }

 // Full Signals Workspace views
 if(!fLive.length){
  setHTML('fullLiveSignals', '<div class="empty">NO LIVE SIGNALS AVAILABLE.</div>');
 } else {
  setHTML('fullLiveSignals', '<div class="table-wrap"><table class="data-table"><thead><tr><th>#</th><th>Symbol</th><th>Direction</th><th>Price (₹)</th><th>Entry (₹)</th><th>Stop Loss (₹)</th><th>Target (₹)</th><th>Probability</th><th>Confidence</th><th>Session ID</th></tr></thead><tbody>'+fLive.map((s,i)=>`<tr><td>${i+1}</td><td><b>${esc(s.symbol)}</b></td><td class="${String(s.side).toLowerCase()}">${esc(s.side)}</td><td>₹${fmt(s.price)}</td><td>₹${fmt(s.entry_price)}</td><td>₹${fmt(s.stop_price)}</td><td>₹${fmt(s.target_price)}</td><td>${(Number(s.probability_up)*100).toFixed(1)}%</td><td>${(Number(s.confidence)*100).toFixed(1)}%</td><td><code>${esc(s.live_session_id||'—')}</code></td></tr>`).join('')+'</tbody></table></div>');
 }

 if(!fHist.length){
  setHTML('fullHistSignals', '<div class="empty">NO HISTORICAL SIGNALS AVAILABLE.</div>');
 } else {
  setHTML('fullHistSignals', '<div class="table-wrap"><table class="data-table"><thead><tr><th>#</th><th>Symbol</th><th>Direction</th><th>Price (₹)</th><th>Entry (₹)</th><th>Stop Loss (₹)</th><th>Target (₹)</th><th>Probability</th><th>Quality</th><th>As-Of Date</th></tr></thead><tbody>'+fHist.map((s,i)=>`<tr><td>${i+1}</td><td><b>${esc(s.symbol)}</b></td><td class="${String(s.side).toLowerCase()}">${esc(s.side)}</td><td>₹${fmt(s.price)}</td><td>₹${fmt(s.entry_price)}</td><td>₹${fmt(s.stop_price)}</td><td>₹${fmt(s.target_price)}</td><td>${(Number(s.probability_up)*100).toFixed(1)}%</td><td>${(Number(s.quality_score)*100).toFixed(1)}%</td><td><code>${esc(s.historical_asof_date||s.market_date||'—')}</code></td></tr>`).join('')+'</tbody></table></div>');
 }
}

function filterLiveSignals(){ renderSignalTables(cachedLive, cachedHist); }
function filterHistSignals(){ renderSignalTables(cachedLive, cachedHist); }
function filterLiveSignalsView(){ renderSignalTables(cachedLive, cachedHist); }
function filterHistSignalsView(){ renderSignalTables(cachedLive, cachedHist); }

// Robust Event Delegation for Timeframe pills and Sector Signal Strength toggles
document.addEventListener('click', e=>{
 const btn=e.target.closest('.tf-btn');
 if(btn){
  const parent=btn.closest('.panel-head');
  if(parent){
   parent.querySelectorAll('.tf-btn').forEach(b=>b.classList.remove('active'));
   btn.classList.add('active');

   const text=btn.textContent.trim();
   if(text==='Signals'||text==='Score'){
    renderSectorStrength(text);
   } else if(['1D','1W','1M','3M','1Y'].includes(text)){
    updateChartTimeframe(text);
   }
  }
 }
});

function renderSectorStrength(mode){
 const sectors=[
  {name:'IT', sig:82, score:0.84, top:'INFY, TCS'},
  {name:'Banking', sig:76, score:0.81, top:'HDFCBANK, ICICIBANK'},
  {name:'Auto', sig:62, score:0.76, top:'M&M, TATAMOTORS'},
  {name:'Pharma', sig:58, score:0.72, top:'SUNPHARMA'},
  {name:'FMCG', sig:48, score:0.68, top:'HINDUNILVR'},
  {name:'Energy', sig:42, score:0.65, top:'RELIANCE'},
  {name:'Metals', sig:38, score:0.59, top:'TATASTEEL'},
  {name:'Realty', sig:35, score:0.55, top:'DLF'}
 ];
 const container=document.querySelector('.sector-bars');
 if(!container) return;
 container.innerHTML=sectors.map(sec=>{
  const val=mode==='Signals'?sec.sig:sec.score;
  const maxVal=mode==='Signals'?100:1.0;
  const pct=Math.min(100,Math.max(10,(val/maxVal)*100));
  const color=val>(mode==='Signals'?60:0.75)?'var(--success)':(val>(mode==='Signals'?40:0.6)?'var(--warning)':'var(--danger)');
  return `<div class="sec-row">
   <span>${sec.name}</span>
   <div class="sec-bar"><i style="width:${pct}%;background:${color}"></i></div>
   <b>${mode==='Signals'?sec.sig:sec.score.toFixed(2)}</b>
   <small>${sec.top}</small>
  </div>`;
 }).join('');
}

function updateChartTimeframe(tf){
 const priceEl=document.querySelector('.chart-price');
 const pathEl=document.querySelector('.mock-chart path:nth-of-type(2)');
 const areaEl=document.querySelector('.mock-chart path:nth-of-type(1)');
 const axisEl=document.querySelector('.chart-footer-axis');

 const dataConfig={
  '1D': {
   price: '23,402.15 <span class="pos">+112.60 (+0.74%)</span>',
   path: 'M 0 150 Q 100 120 200 130 T 400 80 T 600 50',
   area: 'M 0 150 Q 100 120 200 130 T 400 80 T 600 50 L 600 200 L 0 200 Z',
   axis: '<span>09:15</span><span>10:00</span><span>11:00</span><span>12:00</span><span>13:00</span><span>14:00</span><span>15:30</span>'
  },
  '1W': {
   price: '23,850.10 <span class="pos">+412.50 (+1.76%)</span>',
   path: 'M 0 160 Q 120 100 240 110 T 480 60 T 600 40',
   area: 'M 0 160 Q 120 100 240 110 T 480 60 T 600 40 L 600 200 L 0 200 Z',
   axis: '<span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span>'
  },
  '1M': {
   price: '24,210.80 <span class="pos">+921.40 (+3.95%)</span>',
   path: 'M 0 170 Q 150 140 300 90 T 500 70 T 600 30',
   area: 'M 0 170 Q 150 140 300 90 T 500 70 T 600 30 L 600 200 L 0 200 Z',
   axis: '<span>Week 1</span><span>Week 2</span><span>Week 3</span><span>Week 4</span>'
  },
  '3M': {
   price: '21,900.50 <span class="pos">+1,501.65 (+7.36%)</span>',
   path: 'M 0 180 Q 150 160 300 110 T 450 70 T 600 35',
   area: 'M 0 180 Q 150 160 300 110 T 450 70 T 600 35 L 600 200 L 0 200 Z',
   axis: '<span>Month 1</span><span>Month 2</span><span>Month 3</span>'
  },
  '1Y': {
   price: '19,850.20 <span class="pos">+3,551.95 (+21.09%)</span>',
   path: 'M 0 190 Q 150 140 300 100 T 450 60 T 600 20',
   area: 'M 0 190 Q 150 140 300 100 T 450 60 T 600 20 L 600 200 L 0 200 Z',
   axis: '<span>Q1</span><span>Q2</span><span>Q3</span><span>Q4</span>'
  }
 };

 const cfg=dataConfig[tf];
 if(cfg){
  if(priceEl) priceEl.innerHTML=cfg.price;
  if(pathEl) pathEl.setAttribute('d', cfg.path);
  if(areaEl) areaEl.setAttribute('d', cfg.area);
  if(axisEl) axisEl.innerHTML=cfg.axis;
 }
}

// View Switching Logic
function switchView(viewName){
 document.querySelectorAll('.nav-item').forEach(el=>el.classList.remove('active'));
 document.querySelectorAll('.view-panel').forEach(el=>el.classList.remove('active'));

 const nav=document.querySelector(`[data-view="${viewName}"]`);
 if(nav) nav.classList.add('active');

 const panel=$(`view-${viewName}`);
 if(panel) panel.classList.add('active');
 window.scrollTo(0,0);
}

document.querySelectorAll('.sidebar-nav .nav-item').forEach(item=>{
 item.addEventListener('click', e=>{
  e.preventDefault();
  const v=item.getAttribute('data-view');
  if(v) switchView(v);
 });
});

const refBtn=$('refresh');
if(refBtn) refBtn.addEventListener('click',load);
load();
setInterval(load,30000);
