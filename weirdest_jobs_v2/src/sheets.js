'use strict';
// model sheet: one character, 4 views + walk + dance + 6 expressions + hands
function modelSheet2(ch, label, opts = {}) {
  const S = mk(2160, 1920), c = S.x;
  c.fillStyle = lg(c, 0, 0, 0, 1920, [[0, '#f4ead6'], [1, '#e6d6b8']]); c.fillRect(0, 0, 2160, 1920);
  c.font = '64px Slab'; c.fillStyle = '#3a2416'; c.textAlign = 'left'; c.fillText(label, 40, 80);
  c.font = '26px Bree'; c.fillStyle = '#6a4a30';
  const g = 900, s = opts.s || 1.0;
  const views = [['f', 'FRONT'], ['q', '3/4'], ['p', 'PROFILE'], ['b', 'BACK']];
  views.forEach(([v, n], i) => { const x = 150 + i * 250; drawChar2(c, ch, { x, y: g, s, view: v, expr: X('neutral'), hold: opts.hold }, 0); c.fillText(n, x - 40, g + 50); });
  const w = walk2(.15, { amp: 1 }); drawChar2(c, ch, mergeP({ x: 1180, y: g, s, view: 'p' }, w, { expr: X('happy') }), 0); c.fillText('WALK', 1140, g + 50);
  drawChar2(c, ch, { x: 1430, y: g, s, view: 'q', shR: 2.7, elR: .4, shL: -.9, elL: -.6, hipR: .7, kneeR: .9, hipL: -.2, kneeL: .1, lean: -.12, handR: 'spread', handL: 'spread', expr: X('grin') }, 0); c.fillText('DANCE', 1390, g + 50);
  drawChar2(c, ch, { x: 1680, y: g, s, view: 'q', f: -1, shR: 1.6, elR: 1.9, shL: 2.4, elL: .2, hipR: -.3, kneeR: .5, hipL: .4, kneeL: .2, lean: .15, handR: 'point', handL: 'open', expr: X('shout') }, 0);
  drawChar2(c, ch, { x: 1930, y: g, s, view: 'p', shR: .3, elR: 1.6, shL: -.5, elL: .5, hipR: .1, kneeR: .5, hipL: .1, kneeL: .5, air: 10, lean: .3, handR: 'fist', expr: X('anger') }, 0);
  const ex = [['happy', 'HAPPY'], ['surprise', 'SURPRISE'], ['anger', 'ANGER'], ['fear', 'FEAR'], ['confused', 'CONFUSED'], ['smug', 'SMUG'], ['shout', 'SHOUT'], ['sad', 'SAD']];
  ex.forEach(([e, n], i) => { const x = 140 + i * 210, y = 1340; c.save(); c.translate(x, y); drawHead2(c, ch, i % 2 ? 'q' : 'p', X(e), 150, 4.2); c.restore(); c.fillText(n, x - 50, y + 60); });
  const hk = ['open', 'spread', 'fist', 'point', 'grip', 'relaxed'];
  hk.forEach((k, i) => { hand2(c, [200 + i * 300, 1560], .2, k, 120, ch.skin, 4.5); c.fillText(k.toUpperCase(), 160 + i * 300, 1840); });
  return S.c;
}
window.sheetFor = (key, label) => { const ch = CAST2[key] || eval(key); const s = modelSheet2(ch, label); ctx.drawImage(s, 0, 0, 2160, 1920, 0, 0, 1080, 960); return s.toDataURL('image/jpeg', .9); };
window.lineup = () => {
  const S = mk(2160, 1920), c = S.x;
  c.fillStyle = lg(c, 0, 0, 0, 1920, [[0, '#f4ead6'], [1, '#e2d0ae']]); c.fillRect(0, 0, 2160, 1920);
  const L = [['knocker', 'NED'], ['sleeper', 'ALF'], ['king', 'KING'], ['groom', 'THOMAS'], ['groomRich', 'THOMAS (RICH)'], ['sineater', 'SIN-EATER']];
  L.forEach(([k, n], i) => { const ch = CAST2[k], y = 880; drawChar2(c, ch, { x: 170 + i * 360, y, s: 1.05, view: 'q', expr: X('happy'), shR: .2, elR: .4 }, 0); c.font = '34px Slab'; c.fillStyle = '#3a2416'; c.textAlign = 'center'; c.fillText(n, 170 + i * 360, y + 60); });
  const M = [CAST2.guards[0], CAST2.guards[1], CAST2.noble, CAST2.lady, CAST2.servant, CAST2.widow, CAST2.boy, villager(5, 'ind'), villager(8, 'ind'), villager(12, 'vil')];
  M.forEach((ch, i) => { drawChar2(c, ch, { x: 110 + i * 205, y: 1800, s: .95, view: i % 2 ? 'p' : 'q', f: i % 3 ? 1 : -1, expr: X(['happy', 'surprise', 'smug', 'neutral', 'grin'][i % 5]) }, 0); });
  return S.c.toDataURL('image/jpeg', .9);
};
window.heads = (keys) => {
  const S = mk(2160, 1920), c = S.x; c.fillStyle = '#efe2c8'; c.fillRect(0, 0, 2160, 1920);
  keys.forEach((k, r) => { const ch = CAST2[k]; [['p', 'neutral'], ['q', 'happy'], ['f', 'surprise'], ['q', 'anger'], ['p', 'shout'], ['q', 'smug']].forEach(([v, e], i) => { c.save(); c.translate(180 + i * 350, 400 + r * 460); drawHead2(c, ch, v, X(e), 300, 5); c.restore(); }); });
  return S.c.toDataURL('image/jpeg', .9);
};
