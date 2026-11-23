const L=require('./lib'); const {shots,renderFrame}=require('./shots'); const fs=require('fs');
const args=process.argv.slice(2); const fr=parseFloat(args[0]||'.5'); const out=args[1]||'../stills';
fs.mkdirSync(out,{recursive:true});
const c=L.createCanvas(1080,1920); const g=c.getContext('2d');
const sel = args[2]? args[2].split(',').map(Number) : shots.map((_,i)=>i);
for (const i of sel){ const s=shots[i]; const T=s.a+(s.b-s.a)*fr; const t0=Date.now(); renderFrame(g,T,Math.round(T*30));
  fs.writeFileSync(`${out}/${String(i).padStart(2,'0')}_${s.name}.jpg`, c.toBuffer('image/jpeg',85)); console.log(i,s.name,T.toFixed(2),Date.now()-t0+'ms'); }
