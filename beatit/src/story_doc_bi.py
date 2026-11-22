"""Writes output/MICHAEL_BEAT_IT_STORYBOARD.md from the shot tables (times + each shot's own description)."""
import _paths  # noqa
import timing as T
import bi_act1, bi_act2, bi_act3, bi_act4
from pathlib import Path

ACTS = [('THE HOOK + THE CHALLENGE', bi_act1, 0.0), ('THE SECRET WEAPON', bi_act2, T.db(10)),
        ('THE DARING MUSIC VIDEO', bi_act3, T.db(17)), ('THE LEGEND IS BORN + THE ENDING', bi_act4, T.db(24))]
CAPTIONS = [(0.35, 4.55, 'THE WORLD KNEW HIM / AS A CHILD STAR…'), (5.63, 9.07, 'BUT HE WAS ABOUT TO / CHANGE MUSIC FOREVER.'),
            (9.39, 12.56, '1982. ONE ALBUM. / ONE HUGE AMBITION.'), (12.76, 16.01, 'PRODUCER QUINCY JONES / WANTED A ROCK SONG.'),
            (18.08, 22.69, 'THEN EDDIE VAN HALEN / JOINED THE RECORD.'), (30.08, 33.29, '1983 · LOS ANGELES (location stamp)'),
            (33.59, 38.48, 'REAL GANG MEMBERS. / ONE MESSAGE: / STOP THE VIOLENCE.'),
            (49.11, 54.03, 'BEAT IT BECAME / A WORLDWIDE HIT.'), (55.96, 59.90, 'FROM THE JACKSON 5…'),
            (57.74, 59.90, 'TO THE KING OF POP.')]


def tc(t):
    return f'{int(t // 60)}:{t % 60:06.3f}'


def clean(doc):
    return ' '.join((doc or '').split())


lines = ['# Michael Jackson - "The Song That Changed Michael Jackson Forever" (the making of Beat It)', '',
         'Vertical 9:16 animated biography short, 1080x1920, 60 fps, exactly 60.000 s, cut to the supplied 60 s edit of "Beat It".',
         'Every cut sits on a tracked downbeat (bar = 1.729 s at ~138.4 BPM) or a half-bar; act boundaries match the edit\'s own breaks.', '',
         '## Music map', '',
         '| Edit time | Musical event (measured) | Picture |', '|---|---|---|',
         '| 0:00.000 | song starts at full energy | open mid-performance on the Jackson 5 stage, push-in starts at once |',
         '| 0:08.25 | short break (RMS dip) | overhead light flickers as Michael decides; swells into 0:09.185 |',
         '| 0:09.185 | downbeat, vocal re-entry | cut to the Thriller-session machines |',
         '| 0:23.0-0:25.5 | loudest vocal hooks of the edit | Eddie playing / tapping close-ups |',
         '| 0:28.75-0:29.25 | break | Michael lifts an ear-cup in disbelief at the playback |',
         '| 0:29.933 | strong "Beat it" vocal accent | hard cut to 1983 Los Angeles |',
         '| 0:43.5 | break (near silence) | doorway light dims, his silhouette in the door |',
         '| 0:43.770 | the hit after the break | full company strikes the first point on the downbeat |',
         '| 0:56.5-0:57.25 | break | the adult hands become the child\'s hands for one breath |',
         '| 0:57.591 | downbeat after the break | he raises his head; the pull-back begins; "TO THE KING OF POP." |',
         '| 0:59.321 | last downbeat | picture fades to black by 1:00.000; audio tail faded over the final second |', '']
for title, mod, t0 in ACTS:
    lines += [f'## {title}', '', '| # | In | Out | Shot | Action / camera |', '|---|---|---|---|---|']
    shots = mod.SHOTS
    nxt = [s[0] for s in shots[1:]] + [mod.END if hasattr(mod, 'END') else 60.0]
    for (ts, fn), te in zip(shots, nxt):
        lines.append(f'| | {tc(ts)} | {tc(te)} | `{fn.__name__}` | {clean(fn.__doc__)} |')
    lines.append('')
n = 0
out = []
for ln in lines:
    if ln.startswith('| | '):
        n += 1
        ln = f'| {n} | ' + ln[4:]
    out.append(ln)
out += ['## On-screen text (English only, inside TikTok/Shorts safe zones, clear of the right-hand button rail)', '',
        '| In | Out | Text |', '|---|---|---|'] + [f'| {tc(a)} | {tc(b)} | {s} |' for a, b, s in CAPTIONS]
out += ['', '## Characters', '',
        '- **Michael, Jackson 5 era**: the child design from the Jackson 5 film (same face, afro, purple fringe stage outfit).',
        '- **Michael, 1982-83**: the adult design that closes the Jackson 5 V3 film (same face/curls) in three wardrobes: '
        'studio sweater, the red zippered leather jacket over black, and the black sequined stage jacket with one glove.',
        '- **Quincy Jones**: producer; glasses, mustache and short beard, sweater vest.',
        '- **Eddie Van Halen**: feathered shoulder-length hair, big grin, striped red/white/black guitar (a generic striped design).',
        '- **Dancers, the two street groups, film crew, fans**: 16 distinct supporting designs + 3 kids.',
        '- Model sheet: `MODEL_SHEET_BEAT_IT.png`.', '',
        '## Historical notes', '',
        '- Beat It was written by Michael Jackson for *Thriller* (1982); producer Quincy Jones wanted a rock song on the album.',
        '- Eddie Van Halen played the guitar solo. The film never shows Eddie and Michael in the same room: Eddie is shown at home and '
        'recording; Michael is shown later, hearing the playback.',
        '- The 1983 music video was shot in Los Angeles and featured real gang members alongside professional dancers; its message '
        'was against violence.',
        '- Beat It reached No. 1 on the Billboard Hot 100 in 1983. Other chart entries are shown as anonymous bars (no invented titles).',
        '- No dialogue is quoted, no conflicts or rejections are invented; record sleeves are plain typographic designs, not the real artwork.',
        '- This is a biographical story about the making of the song, not a recreation of the music video\'s shots or choreography.']
p = Path(__file__).resolve().parents[1] / 'output' / 'MICHAEL_BEAT_IT_STORYBOARD.md'
p.write_text('\n'.join(out) + '\n')
print('wrote', p, n, 'shots')
