const C=require('./core'), I=require('./ink'), B=require('./body'); const fs=require('fs');
const c=C.createCanvas(1080,1920); const g=c.getContext('2d');
for (const mode of ['color','pencil']) {
I.ST.mode=mode; g.fillStyle=mode=='color'?'#7d8fae':'#f4efe3'; g.fillRect(0,0,1080,1920);
const cam=new C.Cam({pos:[0,60,1150],look:[0,60,0],fov:33});
const rows=[['morten','80s'],['magne','80s'],['pal','80s']];
const yaws=[0,.7,1.57,3.0];
rows.forEach(([w,e],i)=>yaws.forEach((y,j)=>{
  const x=-150+j*100, py=165-i*190+95;
  const base={...B.stand([x,py,0],y), head:{yaw:j==1?.3:0,E:{mouth:{smile:j==0?.6:0},blink:0}}};
  if(j==0){ base.hr={p:C.fx(C.frame([x,py,0],y),-24,40,22)}; }
  B.person(g,cam,w,e,base);
}));
fs.writeFileSync(`../t_body_${mode}.png`,c.toBuffer('image/png'));}
