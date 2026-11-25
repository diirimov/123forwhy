const C=require('./core');const D=require('./draw');const K=require('./chars');
const cv=C.canvas(1080,1920),x=cv.getContext('2d');x.fillStyle=D.PAL.paper;x.fillRect(0,0,1080,1920);
const rows=[
 ['villager',{mouth:'frown',sick:0.8,lid:0.45,brows:'sad'}],
 ['villager',{eyes:'wide',mouth:'scream',open:1,brows:'worried',sweat:1,armL:[160,30],armR:[-160,30]}],
 ['doc1',{mouth:'flat',brows:'angry',armR:[-100,-40]}],
 ['doc2',{mouth:'grin',eyes:'open',brows:'raised'}],
 ['doc3',{mouth:'flat',lid:0.45,brows:'calm',turn:-0.2}],
 ['villager',{pale:1,eyes:'spiral',mouth:'wavy',bandage:1}],
];
rows.forEach(([w,o],i)=>{const P=K.P0(Object.assign({x:200+(i%3)*340,y:850+Math.floor(i/3)*900,s:0.95,t:1.3},o));D.contactShadow(x,P.x,P.y,120);K.drawPerson(x,w,P);});
require('fs').writeFileSync('out/sheet.png',cv.toBuffer('image/png'));
