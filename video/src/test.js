const C=require('./core');const D=require('./draw');const K=require('./chars');const F=require('./film');const S=require('./scenes');const E=require('./env');
const out=(n,cv)=>require('fs').writeFileSync('out/'+n+'.png',cv.toBuffer('image/png'));
let cv=C.canvas(),x=cv.getContext('2d');let t=0.5;
S.street(x,{x:540,y:-420,z:1},t,{fg:c=>{K.drawPerson(c,'extraB',K.P0(Object.assign({x:900,y:120,s:0.8,face:-1,t},K.walk(t*7))));D.contactShadow(c,500,180,130);K.drawPerson(c,'villager',K.P0(Object.assign({x:500,y:180,s:1,t,sick:0.9,lid:0.45,mouth:'frown',brows:'sad'},K.walk(t*5,0.6))));}});
F.post(x,t);F.drawSub(x,{t0:0,t1:2,text:'MEDIEVAL MEDICINE WAS INSANE.',em:['INSANE']},t+0.5);out('t_street',cv);
console.log(E.HOUSES.map(h=>h.i+':'+Math.round(h.x)).join(' '));
cv=C.canvas();x=cv.getContext('2d');
S.study(x,{x:300,y:-480,z:0.85},t,{fg:c=>{D.contactShadow(c,250,260,150);K.drawPerson(c,'doc1',K.P0({x:250,y:260,s:1.05,face:-1,t,brows:'angry',armR:[100,40]}));D.contactShadow(c,-150,280,130);K.drawPerson(c,'villager',K.P0({x:-150,y:280,s:1,t,sick:0.9,lid:0.4,mouth:'o',sweat:1}));}});
F.post(x,t);F.drawStamp(x,{t0:0,t1:3,kicker:'TREATMENT Nº1',title:'Bloodletting'},1);F.drawSub(x,{t0:0,t1:2,text:'YOU HAVE A FEVER.',em:['FEVER']},1);out('t_study',cv);
