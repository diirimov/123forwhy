// contact sheet of many timestamps: node src/contact.js out/x.png 0.5,1.2,... [cols]
const C=require('./core');const R=require('./render');const fs=require('fs');
const [file,list,colsS]=process.argv.slice(2);const ts=list.split(',').map(Number);const cols=+(colsS||6);
const sw=216,sh=384,rows=Math.ceil(ts.length/cols);const cv=C.canvas(cols*sw,rows*(sh+28));const x=cv.getContext('2d');x.fillStyle='#111';x.fillRect(0,0,cv.width,cv.height);
ts.forEach((t,i)=>{const f=R.renderFrame(Math.round(t*60));x.drawImage(f,(i%cols)*sw,Math.floor(i/cols)*(sh+28),sw,sh);x.fillStyle='#fff';x.font='20px "Archivo Black"';x.fillText(t.toFixed(2)+'s',(i%cols)*sw+6,Math.floor(i/cols)*(sh+28)+sh+22);});
fs.writeFileSync(file,cv.toBuffer('image/png'));
