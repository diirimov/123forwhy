const C=require('./core'), I=require('./ink'), Hd=require('./head'); const fs=require('fs');
const c=C.createCanvas(1080,1920); const g=c.getContext('2d');
for (const mode of ['color','pencil']) {
I.ST.mode=mode; g.fillStyle=mode=='color'?'#8296b4':'#f4efe3'; g.fillRect(0,0,1080,1920);
const cam=new C.Cam({pos:[0,0,300],look:[0,0,0],fov:44});
const whos=[['morten','80s'],['magne','80s'],['pal','80s'],['morten','late'],['magne','late'],['pal','late']];
const yaws=[0,.6,1.3,-.7];
whos.forEach(([w,e],i)=>yaws.forEach((yw,j)=>{
  const x=-30+j*20, y=60-i*24; const fr=C.frame([x,y,0],yw,0,0);
  Hd.drawHead(g,cam,[x,y,0],fr,w,e,{blink:0,gaze:[0,0],mouth:{smile:j==1?.8:0,open:j==3?.6:0},brow:{raise:j==3?.6:0}});
}));
fs.writeFileSync(`../t_head_${mode}.png`,c.toBuffer('image/png'));}
