// story captions: sentence case, warm white, subtle shadow, one restrained accent
const C = require('./core');
const WARM = '#fff2de', ACC = '#ffb45e', SIZE = 54, LH = 68, MAXW = 860;
// segments: [text, accent?]; zone 'top' baseline y of first line
const CAPS = [
  { a: 0.00, b: 5.10, y: 300, lines: [[['The first version of ‘Take On Me’']], [['sold about '], ['300 copies', 1], ['.']]] },
  { a: 21.00, b: 24.45, y: 300, lines: [[['Three musicians from Norway']], [['had brought the song to London.']]] },
  { a: 24.60, b: 29.75, y: 300, lines: [[['After the first release flopped,']], [['a-ha recorded it again.']]] },
  { a: 30.30, b: 33.62, y: 300, lines: [[['For the new video, artists']], [['traced live footage by hand.']]] },
  { a: 44.30, b: 47.40, y: 300, lines: [[['In 1985, ‘Take On Me’']], [['reached No. 1 in the US.']]] },
  { a: 47.55, b: 50.65, y: 300, lines: [[['Then ‘The Sun Always Shines']], [['on T.V.’ topped the UK chart.']]] },
  { a: 50.95, b: 53.85, y: 300, lines: [[['Oslo, 2010.']], [['Their farewell concert.']]] },
  { a: 54.25, b: 57.45, y: 300, lines: [[['Five years later,']], [['they were back.']]] },
];
const FADE = .22;
function draw(g, t) {
  for (const c of CAPS) {
    if (t < c.a || t > c.b) continue;
    const fin = Math.min(1, (t - c.a) / FADE), fout = Math.min(1, (c.b - t) / FADE); const a = Math.max(0, Math.min(fin, fout));
    const rise = (1 - C.eOut(fin)) * 10;
    g.save(); g.globalAlpha = a; g.font = `${SIZE}px CapBold`; g.textBaseline = 'alphabetic'; g.letterSpacing = '-0.5px';
    // soft legibility band behind the text (very subtle)
    const widths = c.lines.map(L => L.reduce((s, [txt]) => s + g.measureText(txt).width, 0));
    const W = Math.max(...widths); const top = c.y - SIZE - 30, h = LH * c.lines.length + 44;
    const band = g.createLinearGradient(0, top, 0, top + h); band.addColorStop(0, 'rgba(0,0,0,0)'); band.addColorStop(.5, 'rgba(0,0,0,.28)'); band.addColorStop(1, 'rgba(0,0,0,0)');
    let lum = .3; try { const id = g.getImageData(Math.max(0, C.W / 2 - W / 2), Math.max(0, top + 20), Math.min(C.W, W), Math.max(1, h - 40)).data; let s = 0, n = 0; for (let i = 0; i < id.length; i += 64) { s += (id[i] * .3 + id[i + 1] * .59 + id[i + 2] * .11) / 255; n++; } lum = s / n; } catch (e) { }
    const ba = .26 + Math.max(0, Math.min(.42, (lum - .4) * 1.2));
    const band2 = g.createLinearGradient(0, top, 0, top + h); band2.addColorStop(0, 'rgba(0,0,0,0)'); band2.addColorStop(.5, `rgba(12,8,6,${ba})`); band2.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = band2; g.fillRect(C.W / 2 - W / 2 - 80, top, W + 160, h);
    c.lines.forEach((L, i) => {
      let x = C.W / 2 - widths[i] / 2; const y = c.y + i * LH + rise;
      for (const [txt, acc] of L) {
        g.shadowColor = 'rgba(10,6,4,.6)'; g.shadowBlur = 16; g.shadowOffsetY = 3;
        g.fillStyle = acc ? ACC : WARM; g.fillText(txt, x, y); x += g.measureText(txt).width;
      }
    });
    g.restore();
  }
}
function check(g) { g.font = `${SIZE}px CapBold`; return CAPS.map(c => Math.max(...c.lines.map(L => L.reduce((s, [txt]) => s + g.measureText(txt).width, 0)))); }
module.exports = { draw, CAPS, check, MAXW };
