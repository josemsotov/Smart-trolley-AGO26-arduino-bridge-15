(() => {
 const el=id=>document.getElementById(id), player=el('swingPlayer');
 let library=[], marks={}, current='';
 const message=text=>el('trainingMessage').textContent=text;
 async function refresh(selected='') {
  const r=await fetch('/api/training/videos');if(!r.ok)throw Error('No se pudo leer la biblioteca');
  library=await r.json();el('videoLibrary').replaceChildren(new Option('Selecciona un video',''));
  for(const v of library)el('videoLibrary').add(new Option(v.file,v.url));
  if(selected){el('videoLibrary').value=selected;choose(selected)}
 }
 function choose(url){if(!url)return;current=url;marks={};el('swingMarks').textContent='Sin marcas';player.src=url;
  const item=library.find(v=>v.url===url);el('swingFps').value=item?.fps||30;
  message(item?.fps?`${item.width} × ${item.height} · ${item.fps.toFixed(2)} fps del archivo · ${item.duration.toFixed(2)} s`:'Video guardado. Ajusta FPS si necesitas avanzar por fotogramas.');}
 el('videoLibrary').onchange=e=>choose(e.target.value);
 player.onerror=()=>message('El navegador no reproduce este codec. Exporta el telefono como MP4 H.264 o descarga el original: '+current);
 el('swingRate').onchange=e=>player.playbackRate=Number(e.target.value);
 function step(d){player.pause();player.currentTime=Math.max(0,Math.min(player.duration||0,player.currentTime+d/Math.max(1,Number(el('swingFps').value)||30)))}
 el('prevFrame').onclick=()=>step(-1);el('nextFrame').onclick=()=>step(1);
 function mark(key){marks[key]=player.currentTime;el('swingMarks').textContent=JSON.stringify(marks)+' (segundos del archivo)'}
 el('markTop').onclick=()=>mark('cima');el('markImpact').onclick=()=>mark('impacto');
 el('exportMarks').onclick=()=>{const url=URL.createObjectURL(new Blob([JSON.stringify({video:current,marks,time_basis:'file_seconds'},null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='swing-marcas.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};
 el('uploadSwing').onclick=()=>{const file=el('swingFile').files[0];if(!file)return message('Selecciona un video');if(file.size>300*1024*1024)return message('El video supera 300 MB');
  const button=el('uploadSwing');button.disabled=true;const xhr=new XMLHttpRequest();xhr.open('POST','/api/training/upload');xhr.setRequestHeader('X-Filename',encodeURIComponent(file.name));xhr.timeout=200000;
  xhr.upload.onprogress=e=>{if(e.lengthComputable)message(`Cargando ${Math.round(e.loaded/e.total*100)}%`)};
  xhr.onload=async()=>{button.disabled=false;try{const data=JSON.parse(xhr.responseText);if(xhr.status>=400)throw Error(data.detail);await refresh(data.url)}catch(e){message(e.message)}};
  xhr.onerror=xhr.ontimeout=()=>{button.disabled=false;message('La carga fallo. Comprueba la conexion y reintenta.')};xhr.send(file);};
 async function record(action){try{message(action==='start'?'Iniciando Kinect...':'Guardando video...');const r=await fetch('/api/camera/video',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action})});const x=await r.json();if(!r.ok)throw Error(x.detail);if(action==='stop'){await refresh(x.url);if(x.fps)el('swingFps').value=x.fps;message(`Kinect guardado: ${x.frames} imagenes · ${x.fps} fps efectivos`)}else message('Grabando Kinect. Maximo 30 s; pulsa Guardar Kinect al terminar.')}catch(e){message(e.message)}}
 el('recordSwingVideo').onclick=()=>record('start');el('finishSwingVideo').onclick=()=>record('stop');
 refresh().catch(e=>message(e.message));
})();
