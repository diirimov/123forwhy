'use strict';
window.boot = async () => { for (const f of ['Luckiest', 'CinzelD', 'Cinzel', 'Fredoka', 'Fell']) await document.fonts.load(`40px ${f}`); buildTextures(); if (window.buildEnv) buildEnv(); return document.fonts.check('40px Luckiest'); };
window.renderAt = t => { if (window.drawFilm) drawFilm(t); };
window.modelSheet = () => {
  ctx.fillStyle = lg(ctx, 0, 0, 0, H, [[0, '#e8dcc4'], [1, '#c9b89a']]); ctx.fillRect(0, 0, W, H);
  const list = ['knocker', 'sleeper', 'king', 'groom', 'groomRich', 'guard', 'noble1', 'noble2', 'servant', 'sineater', 'mother', 'boy', 'elder'];
  const pos = [[180, 600], [540, 600], [900, 600], [180, 1180], [540, 1180], [900, 1180], [140, 1800], [360, 1800], [560, 1800], [760, 1800], [960, 1800]];
  const poses = [{ shR: .6, elR: .9, handR: 'wave', expr: { mouth: 'grin', open: .4 } }, { expr: { eye: .1, mouth: 'snore', open: .5 } }, { shR: 1.2, elR: .3, expr: { mouth: 'grin', open: .6 } },
    { shR: .3, elR: 1.4, expr: { mouth: 'smirk', lids: .4 } }, { expr: { mouth: 'smile', brow: 1 } }, { expr: { mouth: 'flat', browAng: .6 } }, { expr: { mouth: 'o', open: .5, brow: 1.5 } }, { expr: { mouth: 'smile' } },
    { expr: { mouth: 'shout', open: .8, brow: 1.4, eye: 1.2 } }, { turn: .5, expr: { mouth: 'flat', eye: .7, lookX: .9 } }, { expr: { mouth: 'frown' } }];
  const names = ['knocker', 'sleeper', 'king', 'groom', 'groomRich', 'guard', 'noble1', 'noble2', 'servant', 'sineater', 'mother'];
  names.forEach((n, i) => { const [x, y] = pos[i]; drawChar(ctx, CAST[n], Object.assign({ x, y, s: i >= 6 ? .62 : .8, tt: 0 }, poses[i]), 0); });
  return cv.toDataURL('image/jpeg', .9);
};
window.envSheet = () => {
  const out = mk(1620, 1920), o = out.x; o.fillStyle = '#000'; o.fillRect(0, 0, 1620, 1920);
  const tiles = [];
  const comp = (fn) => { const t = mk(W, H); fn(t.x); return t.c; };
  tiles.push(comp(x => { const s = SETS.town; x.drawImage(s.sky, 0, 0); x.drawImage(s.far, -200, 0); x.drawImage(s.mid, -300, 0); x.drawImage(s.street, -300, s.ground); }));
  tiles.push(comp(x => x.drawImage(SETS.bedroom.bg, 0, 0)));
  tiles.push(comp(x => x.drawImage(SETS.wallwin.bg, 0, 0)));
  tiles.push(comp(x => x.drawImage(SETS.facade.bg, 0, 0)));
  tiles.push(comp(x => x.drawImage(SETS.factory.bg, 0, 0)));
  tiles.push(comp(x => { x.drawImage(SETS.hall.bg, 0, 0); }));
  tiles.push(comp(x => x.drawImage(SETS.privy.bg, 0, 0)));
  tiles.push(comp(x => { const s = SETS.village; x.drawImage(s.sky, 0, 0); x.drawImage(s.far, -200, 0); x.drawImage(s.mid, -300, 0); x.drawImage(s.ground, -300, s.gy); }));
  tiles.push(comp(x => x.drawImage(SETS.cottageIn.bg, 0, 0)));
  tiles.push(comp(x => x.drawImage(SETS.moon.bg, 0, 0)));
  tiles.push(comp(x => { x.drawImage(SETS.stage.bg, 0, 0); x.drawImage(SETS.prosc, 0, 0); }));
  tiles.forEach((t, i) => o.drawImage(t, (i % 6) * 270, Math.floor(i / 6) * 480, 270, 480));
  return out.c.toDataURL('image/jpeg', .85);
};
