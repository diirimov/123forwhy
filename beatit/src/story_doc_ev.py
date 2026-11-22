"""Writes output/MJ_EVOLUTION_STORYBOARD.md from the shot tables (times + each shot's own description)."""
import _paths  # noqa
import timing as T
import ev_a1, ev_a2, ev_a3, ev_a4
from pathlib import Path

ACTS = [('GARY -> JACKSON 5 -> OFF THE WALL -> THRILLER', ev_a1), ('MOTOWN 25 + BEAT IT', ev_a2),
        ('BAD -> SMOOTH CRIMINAL -> DANGEROUS', ev_a3), ('THE PRICE OF FAME + THE FINAL CHAPTER', ev_a4)]


def tc(t):
    return f'{int(t // 60)}:{t % 60:06.3f}'


out = ['# Michael Jackson - "The Evolution of a King" (60.000 s, Beat It master edit)', '',
       'Every shot starts on a measured downbeat, half-bar or named accent from `EVOLUTION_BEAT_MAP.md`.', '']
n = 0
for title, mod in ACTS:
    out += [f'## {title}', '', '| # | In | Out | Shot | Action / transformation |', '|---|---|---|---|---|']
    shots = mod.SHOTS
    ends = [s[0] for s in shots[1:]] + [mod.END]
    for (ts, fn), te in zip(shots, ends):
        n += 1
        doc = ' '.join((getattr(fn, '__doc__', None) or '').split()) or 'synchronised company dance (tracking camera)'
        name = getattr(fn, '__name__', 'shot')
        out.append(f'| {n} | {tc(ts)} | {tc(te)} | `{name}` | {doc} |')
    out.append('')
p = Path(__file__).resolve().parents[1] / 'output' / 'MJ_EVOLUTION_STORYBOARD.md'
p.write_text('\n'.join(out) + '\n')
print('wrote', p, n)
