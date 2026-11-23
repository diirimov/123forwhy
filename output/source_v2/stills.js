const C=require('./core'); const {renderFrame}=require('./film'); const fs=require('fs');
const out=process.argv[2]; const ts=process.argv[3].split(',').map(Number); fs.mkdirSync(out,{recursive:true});
const c=C.createCanvas(1080,1920); const g=c.getContext('2d');
for(const t of ts){ const t0=Date.now(); const n=renderFrame(g,t,Math.round(t*30)); fs.writeFileSync(`${out}/${t.toFixed(2)}.jpg`,c.toBuffer('image/jpeg',88)); console.log(t,n,Date.now()-t0,'ms'); }
