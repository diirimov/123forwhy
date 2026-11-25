const C=require('./core');const D=require('./draw');const K=require('./chars2');const PR=require('./props');
const cv=C.canvas(1080,1920),x=cv.getContext('2d');x.fillStyle=D.PAL.paper;x.fillRect(0,0,1080,1920);
const t=1.3;
const items=[
 ['villager',{x:180,y:700,eyes:'wide',mouth:'eek',brows:'shock',armL:[150,40],armR:[-150,40],handL:'spread',handR:'spread',lean:-10,squash:-0.1,sweat:1}],
 ['doc1',{x:540,y:700,mouth:'smirk',brows:'skeptic',armR:[100,40],handR:'point',armL:[-30,-110],handL:'fist',lidLow:0.3}],
 ['doc2',{x:880,y:700,mouth:'grin',brows:'raised',armR:[150,20],handR:'relaxed',propR:{fn:c=>PR.leechJar(c,0,0,0.5,t,{n:4}),rot:180},armL:[60,60],handL:'open',eyes:'happy'}],
 ['villager',{x:220,y:1300,sit:1,pale:1,lid:0.6,mouth:'wavy',brows:'sad',armR:[60,-20],handR:'fist'}],
 ['doc3',{x:560,y:1300,lid:0.5,brows:'calm',armR:[80,60],handR:'relaxed',propR:{fn:c=>PR.braceDrill(c,t*2,0),rot:90,s:0.8},armL:[30,90],handL:'open'}],
 ['villager',{x:880,y:1300,mouth:'smile',brows:'worried',armR:[160,20],handR:'thumb',bandage:1,lid:0.2}],
 ['villager',{x:620,y:1800,rot:-90,piv:'hip',eyes:'wide',mouth:'scream',open:1,brows:'shock',armL:[160,20],armR:[-150,30],handL:'spread',handR:'spread'}],
];
items.forEach(([w,o])=>{const P=Object.assign({t,s:0.9},o);if(!o.rot)D.contactShadow(x,P.x,P.y,110);K.drawPerson(x,w,P);});
require('fs').writeFileSync('out/sheet2.png',cv.toBuffer('image/png'));
