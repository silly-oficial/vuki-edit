const paths={close:'m6 6 12 12M6 18 18 6',back:'m14 6-6 6 6 6',export:'M12 16V3m-4 4 4-4 4 4M5 12v8h14v-8',media:'M4 5h16v14H4zM4 10h16M9 5v5m6-5v5',text:'M4 5h16M12 5v15m-4 0h8',audio:'M9 17V5l11-2v12M9 17c0 4-6 4-6 0s6-4 6 0m11-2c0 4-6 4-6 0s6-4 6 0',shape:'m12 3 9 9-9 9-9-9z',effects:'m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5z',play:'m9 5 11 7-11 7z',pause:'M8 5v14m8-14v14',undo:'M9 5 4 10l5 5M4 10h9a6 6 0 0 1 0 12',redo:'m15 5 5 5-5 5m5-5h-9a6 6 0 0 0 0 12',canvas:'M8 3H3v5m13-5h5v5M3 16v5h5m13-5v5h-5',adjust:'M5 3v18M12 3v18M19 3v18M2 8h6m1 8h6m1-9h6',expand:'M8 3H3v5m13-5h5v5M3 16v5h5m13-5v5h-5',down:'m6 9 6 6 6-6',plus:'M12 5v14M5 12h14'};
const icon=k=>`<svg viewBox="0 0 24 24" aria-hidden="true"><path d="${paths[k]||paths.effects}"/></svg>`;
const $ = selector => document.querySelector(selector);
const phone = $('.phone'), panel = $('#sheet'), body = $('#sheetBody');
const video = $('#previewVideo'), image = $('#previewImage'), audio = $('#audioTrack');
const mediaFile = $('#mediaFile'), audioFile = $('#audioFile');
const defaults = {text:'',font:'system',size:28,color:'#ffffff',align:'center',textY:76,bold:true,shape:'none',shapeColor:'#ffffff',shapeSize:25,shapeOpacity:80,filter:'none',brightness:100,contrast:100,saturation:100,volume:100,muted:false,audioVolume:70,speed:1,fit:'contain',ratio:'4 / 3'};
let state = {...defaults}, history = [], future = [], active = '', opener = null;
let mediaURL = '', audioURL = '', mediaKind = '', mediaName = '', audioName = '';
const filters = {none:'',mono:'grayscale(1)',warm:'sepia(.3)',cool:'sepia(.15) hue-rotate(155deg)',soft:'contrast(.88) saturate(.85)'};
const fonts = {system:'-apple-system, BlinkMacSystemFont, sans-serif',serif:'Georgia, serif',mono:'ui-monospace, monospace'};
let noticeTimer;
function notice(text) { clearTimeout(noticeTimer); $('#status').textContent = text; noticeTimer = setTimeout(() => { $('#status').textContent = ''; }, 5000); }
function setState(patch) {
  history.push({...state}); if (history.length > 50) history.shift(); future = [];
  Object.assign(state, patch); apply();
}
function apply() {
  const filter = `${filters[state.filter]} brightness(${state.brightness}%) contrast(${state.contrast}%) saturate(${state.saturation}%)`;
  for (const el of [video,image,$('#demoPoster')]) el.style.filter = filter;
  for (const el of [video,image]) el.style.objectFit = state.fit;
  $('.preview').style.aspectRatio = state.ratio;
  const [rw,rh] = state.ratio.split('/').map(Number);
  $('.preview').style.setProperty('--preview-ratio', rw/rh);
  const text = $('#textOverlay'); text.textContent = state.text; text.hidden = !state.text.trim();
  Object.assign(text.style,{fontFamily:fonts[state.font],fontSize:state.size+'px',color:state.color,textAlign:state.align,top:state.textY+'%',fontWeight:state.bold?'700':'400'});
  const shape = $('#shapeOverlay'); shape.hidden = state.shape === 'none'; shape.dataset.shape = state.shape;
  Object.assign(shape.style,{background:state.shapeColor,width:state.shapeSize+'%',opacity:state.shapeOpacity/100});
  video.volume = state.volume/100; video.muted = state.muted; video.playbackRate = state.speed;
  audio.volume = state.audioVolume/100; audio.playbackRate = state.speed;
  $('#undo').disabled = !history.length; $('#redo').disabled = !future.length;
}
function range(label,key,min,max,suffix='') {
  const row = document.createElement('label'); row.className = 'control-row';
  const heading = document.createElement('span'); heading.className = 'control-label';
  const output = document.createElement('output'); output.textContent = state[key]+suffix;
  heading.append(document.createTextNode(label),output);
  const input = document.createElement('input'); input.type='range'; input.min=min; input.max=max; input.value=state[key]; input.setAttribute('aria-label',label);
  input.oninput=()=>{setState({[key]:Number(input.value)});output.textContent=input.value+suffix};
  row.append(heading,input); body.append(row);
}
function choices(label,key,items) {
  const group = document.createElement('fieldset'); group.className='choice-group';
  const legend = document.createElement('legend');legend.textContent=label;group.append(legend);
  const row = document.createElement('div');row.className='choices';group.append(row);
  for(const [value,name] of items){
    const b=document.createElement('button');b.type='button';b.textContent=name;b.dataset.value=value;
    b.setAttribute('aria-pressed',String(state[key]===value));
    b.onclick=()=>{setState({[key]:value});row.querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed',String(x===b)))};
    row.append(b);
  }
  body.append(group);
}
function color(label,key) {
  const row=document.createElement('label');row.className='color-row';row.append(document.createTextNode(label));
  const input=document.createElement('input');input.type='color';input.value=state[key];input.setAttribute('aria-label',label);input.oninput=()=>setState({[key]:input.value});row.append(input);body.append(row);
}
function action(label,key,fn,description='') {
  const b=document.createElement('button');b.className='action-row';
  b.innerHTML=`${icon(key)}<span></span>`;b.querySelector('span').textContent=label;
  if(description){const small=document.createElement('small');small.textContent=description;b.querySelector('span').append(small)}
  b.onclick=fn;body.append(b);return b;
}
function note(text){const p=document.createElement('p');p.className='panel-note';p.textContent=text;body.append(p)}
const tabs = [
  ['media','Mídia','Escolha o vídeo ou a foto para esta prévia.',()=>{
    action('Importar vídeo','media',()=>{mediaFile.accept='video/*';mediaFile.click()},'Abrir um arquivo do aparelho');
    action('Importar foto','plus',()=>{mediaFile.accept='image/*';mediaFile.click()},'Usar uma imagem na prévia');
    if(mediaName)note('Arquivo atual: '+mediaName);
    else note('A arte de exemplo será substituída pela sua mídia.');
  }],
  ['text','Texto','Escreva e veja o resultado diretamente na imagem.',()=>{
    const label=document.createElement('label');label.className='text-field';label.textContent='Seu texto';
    const input=document.createElement('textarea');input.rows=2;input.maxLength=160;input.placeholder='Digite uma legenda…';input.value=state.text;
    input.oninput=()=>setState({text:input.value});label.append(input);body.append(label);
    choices('Fonte','font',[['system','Padrão'],['serif','Editorial'],['mono','Mono']]);
    range('Tamanho','size',14,64,'px');color('Cor do texto','color');
    choices('Alinhamento','align',[['left','Esquerda'],['center','Centro'],['right','Direita']]);
    range('Posição vertical','textY',10,90,'%');
    choices('Peso','bold',[[false,'Regular'],[true,'Negrito']]);
    action('Remover texto','close',()=>{setState({text:''});renderPanel()});
  }],
  ['audio','Áudio','Trilha e volume, separados dos ajustes da imagem.',()=>{
    action(audioName?'Trocar trilha':'Adicionar trilha','audio',()=>audioFile.click(),audioName||'Escolher áudio do aparelho');
    if(audioName){range('Volume da trilha','audioVolume',0,100,'%');action('Remover trilha','close',removeAudio)}
    if(mediaKind==='video'){
      range('Som original do vídeo','volume',0,100,'%');
      choices('Som original','muted',[[false,'Ligado'],[true,'Mudo']]);
    }
    if(!audioName && mediaKind!=='video')note('Importe um vídeo ou adicione uma trilha para ajustar o som.');
    else note('A trilha acompanha a reprodução da prévia.');
  }],
  ['shape','Formas','Adicione um elemento por cima da sua imagem.',()=>{
    choices('Forma','shape',[['none','Nenhuma'],['circle','Círculo'],['square','Quadrado'],['pill','Pílula']]);
    color('Cor da forma','shapeColor');range('Tamanho da forma','shapeSize',10,60,'%');range('Opacidade','shapeOpacity',10,100,'%');
  }],
  ['effects','Efeitos','Filtros e ajustes de cor da imagem.',()=>{
    choices('Filtro','filter',[['none','Original'],['mono','P&B'],['warm','Quente'],['cool','Frio'],['soft','Suave']]);
    range('Brilho','brightness',50,150,'%');range('Contraste','contrast',50,150,'%');range('Saturação','saturation',0,200,'%');
    action('Redefinir efeitos','undo',()=>{setState({filter:'none',brightness:100,contrast:100,saturation:100});renderPanel()});
  }],
  ['clip','Opções do vídeo','Enquadramento e reprodução da mídia.',()=>{
    choices('Proporção','ratio',[['4 / 3','4:3'],['16 / 9','16:9'],['1 / 1','1:1']]);
    choices('Enquadramento','fit',[['contain','Inteiro'],['cover','Preencher']]);
    if(mediaKind==='video')choices('Velocidade da prévia','speed',[[0.5,'0,5×'],[1,'1×'],[1.5,'1,5×'],[2,'2×']]);
    else note('Importe um vídeo em Mídia para controlar a reprodução.');
  }]
];
function renderPanel(){const tab=tabs.find(t=>t[0]===active);if(!tab)return;$('#sheetTitle').textContent=tab[1];$('#sheetHint').textContent=tab[2];body.replaceChildren();tab[3]();}
function openPanel(key,trigger){
  active=key;opener=trigger;renderPanel();panel.classList.remove('hidden');phone.classList.add('panel-open');
  document.querySelectorAll('.tool').forEach(b=>{const on=b.dataset.key===key;b.classList.toggle('active',on);b.setAttribute('aria-expanded',String(on))});
  // This is an inline region: the toolbar and preview remain available.
  $('#close').focus({preventScroll:true});
}
function closePanel(){active='';panel.classList.add('hidden');phone.classList.remove('panel-open');document.querySelectorAll('.tool').forEach(b=>{b.classList.remove('active');b.setAttribute('aria-expanded','false')});opener?.focus({preventScroll:true})}
for(const [key,label] of tabs.slice(0,5)){
  const b=document.createElement('button');b.className='tool';b.dataset.key=key;b.innerHTML=`<b>${icon(key)}</b><span>${label}</span>`;b.setAttribute('aria-controls','sheet');b.setAttribute('aria-expanded','false');
  b.onclick=()=>active===key?closePanel():openPanel(key,b);$('#toolbar').append(b);
}
for(const [selector,key] of [['#undo','undo'],['#redo','redo'],['#play','play'],['#clipSettings','adjust'],['#close','close'],['.plus','plus'],['.music','audio']])$(selector).innerHTML=icon(key);
$('#close').onclick=closePanel;
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&active)closePanel()});
$('#clipSettings').onclick=e=>openPanel('clip',e.currentTarget);
$('.video .clip').onclick=e=>openPanel('clip',e.currentTarget);
$('.plus').onclick=()=>{mediaFile.accept='video/*,image/*';mediaFile.click()};
$('.music').onclick=e=>openPanel('audio',e.currentTarget);
$('#undo').onclick=()=>{if(!history.length)return;future.push({...state});state=history.pop();apply();renderPanel()};
$('#redo').onclick=()=>{if(!future.length)return;history.push({...state});state=future.pop();apply();renderPanel()};
function showPlaying(on){$('#play').innerHTML=icon(on?'pause':'play');$('#play').setAttribute('aria-label',on?'Pausar prévia':'Reproduzir prévia')}
function stop(){video.pause();audio.pause();showPlaying(false)}
function position(){return mediaKind==='video'?video.currentTime:audioURL?audio.currentTime:0}
function duration(){const n=mediaKind==='video'?video.duration:audioURL?audio.duration:15;return Number.isFinite(n)&&n>0?n:15}
function clock(t){return String(Math.floor(t/60)).padStart(2,'0')+':'+String(Math.floor(t%60)).padStart(2,'0')}
function updateTime(){const t=position(),end=duration();$('#timeReadout').innerHTML=`<b>${clock(t)}</b> / ${clock(end)}`;$('.needle').style.left=(16+Math.min(1,t/end)*80)+'%';$('.ruler').querySelectorAll('span').forEach((s,i)=>s.textContent=clock(end*i/3))}
$('#play').onclick=async()=>{
  const driver=mediaKind==='video'?video:audioURL?audio:null;if(!driver)return;
  if(!driver.paused){stop();return}
  try{
    if(driver.ended)driver.currentTime=0;
    if(mediaKind==='video'&&audioURL){audio.currentTime=Math.min(video.currentTime,Number.isFinite(audio.duration)?audio.duration:video.currentTime);audio.playbackRate=state.speed;await Promise.all([video.play(),audio.play()])}
    else await driver.play();showPlaying(true);
  }catch{stop();notice('Não foi possível reproduzir este arquivo. Tente outro formato.')}
};
for(const el of [video,audio]){el.addEventListener('timeupdate',updateTime);el.addEventListener('loadedmetadata',updateTime);el.addEventListener('error',()=>{stop();notice('Não foi possível abrir este formato no navegador. Escolha outro arquivo.');$('#play').disabled=true})}
video.addEventListener('ended',stop);audio.addEventListener('ended',()=>{if(mediaKind!=='video')showPlaying(false)});
function resetMediaElement(el){el.removeAttribute('src');el.load()}
mediaFile.onchange=()=>{
  const file=mediaFile.files?.[0];if(!file)return;
  if(!/^(video|image)\//.test(file.type)){notice('Escolha um vídeo ou uma foto.');return}
  stop();resetMediaElement(video);image.removeAttribute('src');if(mediaURL)URL.revokeObjectURL(mediaURL);
  mediaURL=URL.createObjectURL(file);mediaKind=file.type.startsWith('video/')?'video':'image';mediaName=file.name;
  video.hidden=mediaKind!=='video';image.hidden=mediaKind!=='image';$('#demoPoster').hidden=true;
  if(mediaKind==='video')video.src=mediaURL;else image.src=mediaURL;
  $('#projectName').textContent=file.name;$('#play').disabled=mediaKind!=='video'&&!audioURL;
  mediaFile.value='';apply();updateTime();notice('Mídia carregada nesta prévia.');if(active==='media'||active==='clip'||active==='audio')renderPanel();
};
image.addEventListener('error',()=>notice('Não foi possível abrir essa foto. Tente JPG ou PNG.'));
function removeAudio(){stop();resetMediaElement(audio);if(audioURL)URL.revokeObjectURL(audioURL);audioURL='';audioName='';$('#audioName').textContent='Adicionar uma trilha';$('#play').disabled=mediaKind!=='video';updateTime();renderPanel()}
audioFile.onchange=()=>{
  const file=audioFile.files?.[0];if(!file)return;if(!file.type.startsWith('audio/')){notice('Escolha um arquivo de áudio.');return}
  removeAudio();audioURL=URL.createObjectURL(file);audioName=file.name;audio.src=audioURL;audioFile.value='';$('#audioName').textContent=file.name;$('#play').disabled=false;apply();updateTime();renderPanel();notice('Trilha carregada nesta prévia.');
};
window.addEventListener('pagehide',event=>{stop();if(!event.persisted){if(mediaURL)URL.revokeObjectURL(mediaURL);if(audioURL)URL.revokeObjectURL(audioURL)}});
apply();updateTime();
