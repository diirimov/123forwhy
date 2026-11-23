const C=require('./core'), I=require('./ink'), Hn=require('./hand'); const fs=require('fs');
const c=C.createCanvas(1080,1920); const g=c.getContext('2d');
for (const mode of ['color','pencil']) {
I.ST.mode=mode; g.fillStyle=mode=='color'?'#3a4a66':'#f4efe3'; g.fillRect(0,0,1080,1920);
const cam=new C.Cam({pos:[0,0,190],look:[0,0,0],fov:40});
const poses=[{curl:.05,spread:.8,thumb:{curl:.1,out:.9}},{curl:[.1,.6,.7,.8],spread:.3},{curl:.9,thumb:{curl:.8,opp:1}},{curl:[.35,.4,.45,.5],spread:.2,thumb:{curl:.3,opp:.6}}];
const views=[ // fwd, nrm, th
 [[0,1,0],[0,0,1],[-1,0,0]],   // back of hand to camera, fingers up
 [[0,1,0],[0,0,-1],[1,0,0]],   // palm to camera
 [[0,1,0],[1,0,0],[0,0,1]],    // side
 [[0,-.5,-1],[0,1,-.4],[-1,0,0]], // reaching toward camera, back up
];
views.forEach((v,i)=>poses.forEach((ps,j)=>{
  const w=[-33+j*22, 30-i*23, 0];
  const h=Hn.buildHand({w,fwd:v[0],nrm:v[1],th:v[2],scale:.9,side:-1},ps);
  Hn.drawHand(g,cam,h,{sleeve:{col:'#1e1e26',r:3.6,len:12,cuff:'#f2efe8'}});
}));
fs.writeFileSync(`../t_hand_${mode}.png`,c.toBuffer('image/png'));}
