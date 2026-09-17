/* Scan angles are already mounting-corrected by the web backend. */
const renderBase = render;
render = function(s) { renderBase(s); renderDualLidar(s); };
function drawScanTopView(id, scan, fresh, color) {
  const c = document.getElementById(id), x = c.getContext('2d');
  const w = c.width, h = c.height, radius = w * .43;
  x.clearRect(0, 0, w, h);
  x.strokeStyle = '#315d43';
  [.25, .5, .75, 1].forEach(k => {
    x.beginPath(); x.arc(w/2, h/2, radius*k, 0, 2*Math.PI); x.stroke();
  });
  x.fillStyle = '#b9cdbf'; x.font = '12px sans-serif';
  x.textAlign = 'center'; x.fillText('FRENTE', w/2, 15);
  x.fillText('IZQ', 20, h/2); x.fillText('DER', w-20, h/2);
  if (fresh) {
    x.fillStyle = color;
    (scan.points || []).forEach(([a, d]) => {
      if (!Number.isFinite(a) || !Number.isFinite(d) || d > 5 || d <= 0) return;
      const r = d / 5 * radius;
      x.fillRect(w/2 - Math.sin(a)*r-1, h/2 - Math.cos(a)*r-1, 3, 3);
    });
  } else {
    x.fillStyle = '#ffd77e'; x.fillText('SIN DATOS RECIENTES', w/2, h/2 + 35);
  }
  x.fillStyle = '#b8e35a'; x.beginPath(); x.moveTo(w/2, h/2-10);
  x.lineTo(w/2-6,h/2+7); x.lineTo(w/2+6,h/2+7); x.closePath(); x.fill();
}

function renderDualLidar(s) {
  const lower = s.scan_lower || {}, ages = s.ages || {};
  const fresh = Number.isFinite(ages.scan_lower) && ages.scan_lower < 1;
  const upperFresh = Number.isFinite(ages.scan) && ages.scan < 1;
  const set = (id, value) => document.getElementById(id).textContent = value;
  const metres = v => fresh && Number.isFinite(v) ? `${v.toFixed(2)} m` : '--';
  set('lowerStatus', fresh ? 'ONLINE' : 'SIN DATOS RECIENTES');
  set('lowerHz', fresh ? `${Number(lower.hz || 0).toFixed(1)} Hz` : '--');
  set('lowerPoints', fresh ? lower.valid_count : '--');
  set('lowerFront', metres(lower.front_min)); set('lowerMin', metres(lower.min));
  drawScanTopView('lidarLower', lower, fresh, '#66cfff');
  drawScanTopView('lidar', s.scan || {}, upperFresh, '#5ae17b');
  ['operationServices', 'testServices'].forEach(id => {
    const root = document.getElementById(id);
    const row = document.createElement('div'); row.className = 'service';
    const label = document.createElement('span');
    const dot = document.createElement('i'); dot.className = 'dot' + (fresh ? ' ok' : '');
    label.append(dot, document.createTextNode('LiDAR inferior'));
    const value = document.createElement('b');
    value.textContent = fresh ? `${lower.valid_count} pts · ${Number(lower.hz).toFixed(1)} Hz` : 'SIN DATOS';
    row.append(label, value); root.append(row);
  });
}
