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
  const [o,s]=await Promise.all([fetch('/api/dashboard/overview'),fetch('/api/dashboard/signals')]);
  if(!o.ok) throw new Error('Dashboard API '+o.status);
  const d=await o.json(), sig=s.ok?await s.json():{live_items:[],historical_items:[],items:[],blockers:[]};
  cachedData = d;
  cachedLive = sig.live_items||[];
  cachedHist = sig.historical_items||[];
  cachedAll = sig.items||[];
  cachedBlockers = sig.blockers||[];

  render(d, cachedLive, cachedHist, cachedAll, cachedBlockers);
 }catch(e){
  if(errEl){
   errEl.textContent=(e.message||'Unable to reach API')+'. Dashboard is fail-closed; no live signal is inferred.';
   errEl.classList.remove('hidden');
  }
  render({pit:{ready:false,required_layers:{},rows:{},issues:['API unavailable'],last_asof:null},signals:{count:0},publication:{max_impact_cost_bps:100},real_trading:false,provenance:{manifest_records:0}},[],[],[],['API unavailable']);
 }
}

function render(d,liveItems,histItems,alltems,apiBlockers){
 const ready=!!d.pit.ready;

 const setText=(id,val)=>{ const el=$(id); if(el) el.textContent=val; };
 const setClass=(id,cls)=>{ const el=$(id); if(el) el.className=cls; };
 const setHTML=(id,html)=>{ const el=$(id); if(el) el.innerHTML=html; };

 // Header & KPI updates
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
 setText('freshnessSub', d.pit.last_asof?new Date(d.pit.last_asof).toLocaleTimeString():'Awaiting feed');

 setText('lastUpdate', d.pit.last_asof?new Date(d.pit.last_asof.replace('Z','')).toLocaleString():'—');
 setText('footerRefreshTime', 'Last Refresh: '+new Date().toLocaleTimeString());

 // Market Status Pill
 const now=new Date();
 const hr=now.getHours(), min=now.getMinutes();
 const isRegular=(hr>9||(hr===9&&min>=15))&&(hr<15||(hr===15&&min<=30))&&now.getDay()>=1&&now.getDay()<=5;
 setClass('marketDot', 'dot '+(isRegular?'open':'closed'));
 setText('marketStatusText', isRegular?'NSE Market Open':'NSE Market Closed');

 // PIT layers table
 const layers=d.pit.required_layers||{};
 const rows=d.pit.rows||{};
 const maxRows=Math.max(1,...Object.values(rows));

 if(!Object.keys(layers).length){
  setHTML('pitTableBody', `<tr><td colspan="5" class="empty">No PIT layer manifest available.</td></tr>`);
  setHTML('fullPitStatus', `<div class="empty">No PIT telemetry available.</div>`);
 } else {
  const tableHtml = Object.entries(layers).map(([k,v])=>{
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
  setHTML('pitTableBody', tableHtml);
  setHTML('fullPitStatus', `<table class="data-table"><thead><tr><th>Dataset</th><th>Status</th><th>Records</th><th>Last Update</th><th>Coverage</th></tr></thead><tbody>${tableHtml}</tbody></table>`);
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
