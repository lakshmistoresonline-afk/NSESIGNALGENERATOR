const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function fmt(v){return v==null?'—':Number(v).toFixed(2)}
async function load(){
 $('refresh').textContent='↻'; $('error').classList.add('hidden');
 try{
  const [o,s]=await Promise.all([fetch('/api/dashboard/overview'),fetch('/api/dashboard/signals')]);
  if(!o.ok) throw new Error('Dashboard API '+o.status);
  const d=await o.json(), sig=s.ok?await s.json():{items:[]}; render(d,sig.items||[]);
 }catch(e){$('error').textContent=(e.message||'Unable to reach API')+'. Dashboard is fail-closed; no live signal is inferred.';$('error').classList.remove('hidden');render({pit:{ready:false,required_layers:{},rows:{},issues:['API unavailable'],last_asof:null},signals:{count:0},publication:{max_impact_cost_bps:100},real_trading:false,provenance:{manifest_records:0}},[])}
}
function render(d,items){
 const ready=!!d.pit.ready; $('pitValue').textContent=ready?'READY':'BLOCKED';$('signalValue').textContent=items.length;$('universeValue').textContent=d.pit?.membership_ready?'READY':'BLOCKED';$('provenanceValue').textContent=d.provenance?.manifest_present?'READY':'BLOCKED';$('impactValue').textContent=fmt(d.publication?.max_impact_cost_bps)+' bps';$('tradingValue').textContent=d.real_trading?'ENABLED':'DISABLED';
 const st=$('pitStatus');st.className='status '+(ready?'ready':'blocked');st.innerHTML='<span class="dot"></span><div><b>'+(ready?'PIT READY':'PIT BLOCKED')+'</b><small>'+(d.pit.last_asof?'Last as-of '+new Date(d.pit.last_asof).toLocaleString():'Required datasets not yet complete')+'</small></div>';
 const layers=d.pit.required_layers||{};$('layers').innerHTML=Object.keys(layers).length?Object.entries(layers).map(([k,v])=>`<div class="layer"><span>${esc(k.replaceAll('_',' '))}</span><span class="pill ${v?'good':'bad'}">${v?'READY':'MISSING'}</span></div>`).join(''):'<div class="empty">No PIT layer manifest available.</div>';
 const issues=d.pit.issues||[];$('issues').innerHTML=issues.map(x=>`<div>⚠ ${esc(x)}</div>`).join('');$('issues').classList.toggle('hidden',issues.length===0);
 const rows=d.pit.rows||{}, max=Math.max(1,...Object.values(rows));$('coverage').innerHTML=Object.keys(rows).length?Object.entries(rows).map(([k,v])=>`<div class="barrow"><span>${esc(k.replaceAll('_',' '))}</span><div class="bar"><i style="width:${Math.max(2,Math.round(Number(v)/max*100))}%"></i></div><b>${Number(v).toLocaleString()}</b></div>`).join(''):`<div class="empty">No processed PIT datasets found.</div>`;
 $('manifest').textContent='Manifest: '+Number(d.provenance?.manifest_records||0).toLocaleString()+' records';
 if(!items.length){$('signals').innerHTML='<div class="empty">NO SIGNAL — no validated paper signals are currently published.</div>';return}
 $('signals').innerHTML='<div class="table-wrap"><table><thead><tr><th>Symbol</th><th>Side</th><th>Probability</th><th>Confidence</th><th>Entry</th><th>Stop</th><th>Target</th><th>Quality</th></tr></thead><tbody>'+items.map(s=>`<tr><td><b>${esc(s.symbol)}</b></td><td class="${String(s.side).toLowerCase()}">${esc(s.side)}</td><td>${(Number(s.probability_up)*100).toFixed(1)}%</td><td>${(Number(s.confidence)*100).toFixed(1)}%</td><td>${fmt(s.entry_price)}</td><td>${fmt(s.stop_price)}</td><td>${fmt(s.target_price)}</td><td>${(Number(s.quality_score)*100).toFixed(1)}%</td></tr>`).join('')+'</tbody></table></div>';
}
$('refresh').addEventListener('click',load);load();setInterval(load,30000);
