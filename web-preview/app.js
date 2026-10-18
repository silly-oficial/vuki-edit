const main=[['▣','Mídia','media'],['♫','Áudio','audio'],['T','Texto','text'],['✦','Efeitos','effects'],['•••','Mais','more']];
const groups={media:['Importar','Biblioteca','Fotos','Vídeos'],audio:['Sons','Música','Voz','Efeitos de áudio'],text:['Adicionar texto','Fonte','Estilo','Animação'],effects:['Efeitos de vídeo','Efeitos corporais','Favoritos','Recentes'],more:['Filtros','Ajustes','Transições','Legendas','Falar','Voiceover','Canvas','Projeto']};
const icons=['▧','♫','T','✦','◈','☼','⇄','CC'];
const toolbar=document.querySelector('#toolbar'),sheet=document.querySelector('#sheet'),title=document.querySelector('#sheetTitle'),body=document.querySelector('#sheetBody');
main.forEach(([i,l,k])=>{const b=document.createElement('button');b.className='tool';b.innerHTML=`<b>${i}</b>${l}`;b.onclick=()=>open(k,l);toolbar.appendChild(b)});
function open(k,l){title.textContent=l;body.innerHTML='';groups[k].forEach((x,n)=>{const c=document.createElement('button');c.className='card';c.innerHTML=`<b>${icons[n%icons.length]}</b>${x}`;c.onclick=()=>c.classList.toggle('selected');body.appendChild(c)});sheet.classList.remove('hidden')}
document.querySelector('#close').onclick=()=>sheet.classList.add('hidden');
let playing=false;document.querySelector('#play').onclick=e=>{playing=!playing;e.currentTarget.textContent=playing?'Ⅱ':'▶'};