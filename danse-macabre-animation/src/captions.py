"""Captions: narration word-reveal (reference style), gothic title reveal, short story captions."""
import math
from core import *

B = bar_t
FONT_CAP = 'Cinzel.ttf'
FONT_TITLE = 'Unifraktur.ttf'
FONT_DECO = 'CinzelDecorative-Black.ttf'

# narration: exact phrases, word onsets measured from the narration waveform
NARR = [
    [('IN', 0.09, None), ('MEDIEVAL', 0.20, GOLD), ('EUROPE,', 0.62, GOLD)],
    [('EVERYONE', 1.37, None), ('HAD', 1.95, None), ('ONE', 2.15, None)],
    [('FINAL', 2.50, '#e0484a'), ('DANCE...', 3.00, '#e0484a')],
]
NARR_END = 3.53
TITLE = [('The', 3.96), ('Dance', 4.15), ('of', 4.61), ('Death', 4.86)]
TITLE_END = 6.35

STORY = [
    ('NO CROWN COULD SAVE YOU.', B(8) + 0.05, B(10) - 0.12, ['CROWN']),
    ('NO SWORD COULD DEFEAT IT.', B(12), B(14) + 0.9, ['SWORD']),
    ('NO FORTUNE COULD BUY ANOTHER DAY.', bar_t(17, 8), B(19) - 0.08, ['FORTUNE']),
    ('RICH OR POOR.', B(19) + 0.05, B(21) - 0.08, ['RICH', 'POOR.']),
    ('POWERFUL OR POWERLESS.', B(21) + 0.05, B(23) - 0.08, ['POWERFUL', 'POWERLESS.']),
    ('DEATH MADE NO EXCEPTIONS.', bar_t(25, 8), B(27) - 0.1, ['DEATH']),
    ('IN THE END, EVERYONE DANCES.', B(29), B(31) - 0.06, ['EVERYONE']),
    ("NOW IT'S YOUR TURN.", bar_t(33, 12), 60.5, ["YOUR", "TURN."]),
]


def _text(c, s, x, y, f, fillc, outline=14.0, alpha=1.0, shadow=True, grad=None):
    blob = skia.TextBlob.MakeFromString(s, f)
    if shadow:
        c.drawTextBlob(blob, x + 5, y + 7, fill('#000000', 0.55 * alpha, blur=6))
    c.drawTextBlob(blob, x, y, stroke('#0d0908', outline, alpha))
    if grad is not None:
        p = lin_grad((0, y - f.getSize() * 0.8), (0, y + f.getSize() * 0.1), grad)
        p.setAlphaf(alpha)
        c.drawTextBlob(blob, x, y, p)
    else:
        c.drawTextBlob(blob, x, y, fill(fillc, alpha) if isinstance(fillc, str) else fillc)


def wrap(words, f, maxw):
    lines, cur = [], []
    for w in words:
        test = ' '.join(cur + [w])
        if cur and f.measureText(test) > maxw:
            lines.append(cur)
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(cur)
    return lines


def narration(c, t):
    if t > NARR_END + 0.25:
        return
    out = clamp((NARR_END + 0.2 - t) / 0.2)
    f = font(FONT_CAP, 78)
    f.setEmbolden(True)
    y0 = 360
    for li, line in enumerate(NARR):
        widths = [f.measureText(w + ' ') for w, _, _ in line]
        x = W / 2 - sum(widths) / 2 + f.measureText(' ') / 2
        y = y0 + li * 104
        for (w, t0, col), wd in zip(line, widths):
            if t >= t0:
                u = ramp(t, t0, t0 + 0.12)
                s = lerp(1.35, 1.0, ease_out_back(u, 2.2))
                with Save(c):
                    cx = x + wd / 2
                    c.translate(cx, y - 26)
                    c.scale(s, s)
                    c.translate(-cx, -(y - 26))
                    _text(c, w, x, y, f, col or '#fbf3df', 16, out * clamp(u * 3))
            x += wd


def title(c, t):
    if t < TITLE[0][1] - 0.05 or t > TITLE_END + 0.6:
        return
    out = clamp((TITLE_END + 0.6 - t) / 0.6)
    fT = font(FONT_TITLE, 210)
    fS = font(FONT_TITLE, 120)
    # "The" small above, "Dance of Death" big
    y = 470
    # glow behind
    g = ramp(t, 4.86, 5.1)
    c.drawPath(ellipse(W / 2, y + 80, 520, 230), fill('#ffb347', 0.16 * g * out, blur=70))
    for i, (w, t0) in enumerate(TITLE):
        if t < t0:
            continue
        u = ramp(t, t0, t0 + 0.18)
        a = clamp(u * 2) * out
        if w == 'The':
            ww = fS.measureText(w)
            _text(c, w, W / 2 - ww / 2, y - 160, fS, '#efe4c8', 12, a)
            continue
        if w in ('Dance', 'of'):
            line = 'Dance of'
            f = fT if w == 'Dance' else fS
            fullw = fT.measureText('Dance ') + fS.measureText('of')
            x0 = W / 2 - fullw / 2
            x = x0 if w == 'Dance' else x0 + fT.measureText('Dance ')
            yy = y + 40
        else:
            f = font(FONT_TITLE, 270)
            ww = f.measureText(w)
            x = W / 2 - ww / 2
            yy = y + 300
        s = lerp(1.6 if w == 'Death' else 1.25, 1.0, ease_out_back(u, 1.8))
        with Save(c):
            c.translate(x + f.measureText(w) / 2, yy - 60)
            c.scale(s, s)
            c.translate(-(x + f.measureText(w) / 2), -(yy - 60))
            _text(c, w, x, yy, f, None, 16, a, True, ['#fff1c4', '#e8b84a', '#a8741c'])
    # ornament line
    if t > 4.86:
        u = ease_out(ramp(t, 4.86, 5.3))
        ww = 380 * u
        c.drawLine(W / 2 - ww, y + 350, W / 2 + ww, y + 350, stroke(GOLD, 4, out))
        c.drawPath(poly([(W / 2, y + 336), (W / 2 + 14, y + 350), (W / 2, y + 364), (W / 2 - 14, y + 350)]),
                   fill(GOLD, out * u))


def story(c, t):
    for text, t0, t1, keys in STORY:
        if t < t0 or t > t1 + 0.3:
            continue
        a_in = ramp(t, t0, t0 + 0.22)
        a_out = clamp((t1 + 0.3 - t) / 0.3)
        a = min(a_in, a_out)
        big = text.startswith('NOW')
        f = font(FONT_CAP, 92 if big else 74)
        f.setEmbolden(True)
        words = text.split(' ')
        lines = wrap(words, f, 900)
        y0 = (380 if big else 330)
        wi = 0
        for li, line in enumerate(lines):
            s_line = ' '.join(line)
            x = W / 2 - f.measureText(s_line) / 2
            y = y0 + li * (f.getSize() * 1.25)
            for w in line:
                # each word arrives with a tiny stagger on the 16th grid
                tw = t0 + wi * PERIOD / 4 * (0.6 if not big else 1.6)
                u = ramp(t, tw, tw + 0.18)
                dy = (1 - ease_out_back(u, 2.0)) * 40
                col = GOLD if w in keys else '#f6eedb'
                if big and w in keys:
                    col = '#e0484a'
                _text(c, w, x, y + dy, f, col, 16, a * clamp(u * 2))
                x += f.measureText(w + ' ')
                wi += 1


def draw(c, t):
    narration(c, t)
    title(c, t)
    story(c, t)
