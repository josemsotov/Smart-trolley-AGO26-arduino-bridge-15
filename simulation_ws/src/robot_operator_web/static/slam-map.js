(() => {
  const canvas = document.getElementById('slamMap');
  const status = document.getElementById('mapStatus');
  let busy = false;
  async function update() {
    if (busy || document.hidden) return;
    busy = true;
    try {
      const response = await fetch('/api/map', {cache: 'no-store', signal: AbortSignal.timeout(6000)});
      if (!response.ok) throw new Error('Mapa no disponible');
      const m = await response.json();
      const grid = document.createElement('canvas');
      grid.width = m.width; grid.height = m.height;
      const g = grid.getContext('2d'), img = g.createImageData(m.width, m.height);
      for (let y=0;y<m.height;y++) for(let x=0;x<m.width;x++) {
        const v=m.cells[y*m.width+x], i=((m.height-1-y)*m.width+x)*4;
        const c=v<0?110:Math.round(240-215*v/100);
        img.data.set([c,c,c,255],i);
      }
      g.putImageData(img,0,0);
      const ctx=canvas.getContext('2d'), scale=Math.min((canvas.width-32)/m.width,(canvas.height-32)/m.height);
      const ox=(canvas.width-m.width*scale)/2, oy=(canvas.height-m.height*scale)/2;
      ctx.clearRect(0,0,canvas.width,canvas.height);ctx.imageSmoothingEnabled=false;
      ctx.drawImage(grid,ox,oy,m.width*scale,m.height*scale);
      const fresh=m.source==='live' && m.age!==null && m.age<10;
      if (fresh && m.robot && m.frame==='map') {
        const a=m.origin[2], dx=m.robot.x-m.origin[0],dy=m.robot.y-m.origin[1];
        const x=(Math.cos(a)*dx+Math.sin(a)*dy)/m.resolution;
        const y=(-Math.sin(a)*dx+Math.cos(a)*dy)/m.resolution;
        ctx.save();ctx.translate(ox+x*scale,oy+(m.height-y)*scale);ctx.rotate(-(m.robot.yaw-a));
        ctx.beginPath();ctx.moveTo(13,0);ctx.lineTo(-9,-8);ctx.lineTo(-5,0);ctx.lineTo(-9,8);ctx.closePath();
        ctx.fillStyle='#70ef70';ctx.strokeStyle='#143d20';ctx.lineWidth=2;ctx.fill();ctx.stroke();ctx.restore();
      }
      status.textContent=`${m.source==='saved'?'Mapa guardado: '+m.name:fresh?'Mapa en vivo':'Mapa sin actualizar'} · ${(m.width*m.resolution).toFixed(1)} × ${(m.height*m.resolution).toFixed(1)} m · ${(m.resolution*100).toFixed(0)} cm/celda${fresh&&!m.robot?' · Posicion no disponible':''}`;
    } catch(e) {
      status.textContent='Sin conexion al mapa. Esperando datos...';
      canvas.getContext('2d').clearRect(0,0,canvas.width,canvas.height);
    } finally { busy=false; }
  }
  document.getElementById('mapRefresh').onclick=update;
  update();setInterval(update,2000);
})();
