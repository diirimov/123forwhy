"""Write deliverables: master, cue-marked WAV, click guide, CSV/JSON/SRT markers."""
import sys, os, struct, json, csv
import numpy as np, soundfile as sf

SR = 48000; SPB = 22500; BAR = 90000; S16 = 5625; NB = 48; N = BAR * NB
src, outdir, base = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(outdir, exist_ok=True)
y, sr = sf.read(src, dtype='float64')
assert sr == SR and len(y) == N, (sr, len(y))

SECTIONS = [(1, 8, 'INTRO HOOK', 'Hook + groove from frame 0; fiddle, bass & hand drums join at bar 5'),
            (9, 16, 'DROP 1', 'Full drop: kick + sub bass + fiddle/lute hook, bass answers in bars 10 & 14'),
            (17, 24, 'VARIATION', 'Call & response: fiddle calls (17/19/21), lute+bass answer (18/20/22); percussive fill bar 24'),
            (25, 32, 'DROP 2', 'Bigger drop: fiddle harmony, lute 16th drive, recorder counter-line, hurdy-gurdy drone+buzz, offbeat synth stabs, rolling bass'),
            (33, 40, 'TWIST', 'Mysterious Phrygian turn (Dm-Eb), hurdy-gurdy lead, 2-beat break bar 36, build 37-40'),
            (41, 48, 'FINAL', 'Key lift to E minor, everything in; stop-time ending bar 48, final hit at 89.531 s')]


def sec_of(bar):
    for a, b, n, _ in SECTIONS:
        if a <= bar <= b:
            return n


def t_of(bar, step=0):
    return ((bar - 1) * BAR + step * S16) / SR


EVENTS = [  # (bar, step, kind, description)
    (1, 0, 'START', 'Hook + kick + stomp/clap groove start on frame 0'),
    (5, 0, 'DEVELOPMENT', 'Fiddle doubles hook, bass & darbuka enter, light cymbal'),
    (8, 8, 'FILL', 'Darbuka roll + riser into drop'),
    (8, 14, 'GAP', 'Half-beat silence (pre-drop breath) - ideal hard cut'),
    (9, 0, 'DROP', 'DROP 1 impact (sub boom + crash) - camera punch'),
    (10, 12, 'ANSWER', 'Bass answer lick (call-and-response)'),
    (13, 0, 'DEVELOPMENT', 'Cymbal accent, hook variation'),
    (14, 12, 'ANSWER', 'Bass answer lick'),
    (16, 12, 'FILL', 'Kick/clap pickup into variation'),
    (17, 0, 'SECTION', 'Variation: fiddle CALL'),
    (18, 0, 'ANSWER', 'Lute + bass ANSWER'),
    (19, 0, 'CALL', 'Fiddle CALL (higher)'),
    (20, 0, 'ANSWER', 'Lute + bass ANSWER'),
    (21, 0, 'CALL', 'Fiddle CALL + claps return, cymbal'),
    (22, 0, 'ANSWER', 'Lute + bass ANSWER'),
    (23, 0, 'ACCENT', 'Stomp hits on 3-3-2 rhythm (steps 0/3/6/8/11) - object transformations'),
    (24, 0, 'FILL', 'Percussive fill: unison hits + clap/frame-drum roll'),
    (24, 14, 'GAP', 'Half-beat silence - hard cut'),
    (25, 0, 'DROP', 'DROP 2 impact - biggest camera punch so far'),
    (26, 12, 'ANSWER', 'Bass answer lick'),
    (29, 0, 'DEVELOPMENT', 'Cymbal accent, hook variation'),
    (30, 12, 'ANSWER', 'Bass answer lick'),
    (31, 0, 'ACCENT', 'Stomp hits on 3-3-2'),
    (33, 0, 'SECTION', 'TWIST: downlifter + impact, dark Phrygian harmony'),
    (36, 0, 'BREAK', 'A-chord hit then 2-beat break with woodblock ticks (beats 2-3)'),
    (36, 12, 'PICKUP', 'Lute pickup run back into the groove'),
    (37, 0, 'BUILD', 'Build starts: claps + hats return, bass filter opens'),
    (39, 0, 'BUILD', 'Clap 8th-note roll'),
    (40, 0, 'BUILD', 'Clap 16th roll + rising pivot melody to B major'),
    (40, 12, 'GAP', 'One-beat silence - hard cut'),
    (41, 0, 'DROP', 'FINAL drop, key change up to E minor - biggest hit'),
    (42, 12, 'ANSWER', 'Bass answer lick'),
    (45, 0, 'DEVELOPMENT', 'Cymbal accent'),
    (46, 12, 'ANSWER', 'Bass answer lick'),
    (47, 0, 'ACCENT', 'Stomp hits on 3-3-2'),
    (48, 0, 'STOP-TIME', 'Ending hit 1 (C chord)'),
    (48, 3, 'STOP-TIME', 'Ending hit 2 (C chord)'),
    (48, 6, 'STOP-TIME', 'Ending hit 3 (B chord, tense hold)'),
    (48, 8, 'FILL', 'Darbuka crescendo roll'),
    (48, 12, 'FINAL HIT', 'Final E open-fifth hit, rings to the last frame'),
]

FPS = [24, 25, 30, 60]


def frames(t):
    return {f'frame_{f}fps': int(round(t * f)) for f in FPS}


def tc30(t):
    fr = int(round(t * 30)); return '%02d:%02d:%02d:%02d' % (fr // 108000, fr // 1800 % 60, fr // 30 % 60, fr % 30)


# ---------------- beat CSV / JSON
rows = []
for k in range(NB * 4):
    bar, beat = k // 4 + 1, k % 4 + 1
    t = k * SPB / SR
    ev = [e for e in EVENTS if e[0] == bar and e[1] == (beat - 1) * 4]
    row = dict(beat_index=k + 1, bar=bar, beat=beat, time_s=f'{t:.6f}', sample_48k=k * SPB, timecode_30fps=tc30(t),
               section=sec_of(bar), downbeat=int(beat == 1), section_start=int(beat == 1 and any(bar == s[0] for s in SECTIONS)),
               event='; '.join(f'{e[2]}: {e[3]}' for e in ev))
    row.update(frames(t)); rows.append(row)
with open(os.path.join(outdir, base + '_BEATS.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

events_out = [dict(bar=b, step_16th=s, time_s=round(t_of(b, s), 6), sample_48k=(b - 1) * BAR + s * S16, timecode_30fps=tc30(t_of(b, s)),
                   type=k, description=d, **frames(t_of(b, s))) for b, s, k, d in EVENTS]
meta = dict(title='The Craziest Medieval Diseases (instrumental)', bpm=128, time_signature='4/4', bars=48, duration_s=90.0,
            sample_rate=SR, bit_depth=24, beat_s=0.46875, bar_s=1.875, sixteenth_s=0.1171875, key='D minor (Phrygian twist bars 33-40) -> E minor from bar 41',
            sections=[dict(name=n, bars=[a, b], start_s=t_of(a), end_s=t_of(b + 1), description=d) for a, b, n, d in SECTIONS],
            events=events_out, beats=[dict(bar=r['bar'], beat=r['beat'], time_s=float(r['time_s'])) for r in rows])
json.dump(meta, open(os.path.join(outdir, base + '_MARKERS.json'), 'w'), indent=1)

# ---------------- SRT bar overlay (one caption per bar)
def srt_t(t):
    ms = int(round(t * 1000)); return '%02d:%02d:%02d,%03d' % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)
with open(os.path.join(outdir, base + '_BARS.srt'), 'w') as f:
    for b in range(1, NB + 1):
        evs = [e for e in EVENTS if e[0] == b]
        txt = f'BAR {b}/48 · {sec_of(b)}' + ''.join(f"\n{e[2]} @ step {e[1]}" for e in evs[:2])
        f.write(f'{b}\n{srt_t(t_of(b))} --> {srt_t(t_of(b + 1) - 0.001)}\n{txt}\n\n')


# ---------------- WAV writers
def to24(x):
    q = np.clip(np.round(x * 8388607), -8388608, 8388607).astype(np.int32)
    b = q.astype('<i4').tobytes()
    a = np.frombuffer(b, dtype=np.uint8).reshape(-1, 4)[:, :3]
    return a.tobytes()


def write_wav(path, x, cues=None):
    data = to24(x)
    fmt = struct.pack('<HHIIHH', 1, 2, SR, SR * 6, 6, 24)
    chunks = b'fmt ' + struct.pack('<I', len(fmt)) + fmt
    chunks += b'data' + struct.pack('<I', len(data)) + data + (b'\0' if len(data) % 2 else b'')
    if cues:
        cue = struct.pack('<I', len(cues))
        adtl = b''
        for i, (smp, label) in enumerate(cues, 1):
            cue += struct.pack('<II4sIII', i, smp, b'data', 0, 0, smp)
            lb = label.encode('utf-8') + b'\0'
            if len(lb) % 2: lb += b'\0'
            adtl += b'labl' + struct.pack('<I', 4 + len(label.encode('utf-8')) + 1) + struct.pack('<I', i) + lb
        chunks += b'cue ' + struct.pack('<I', len(cue)) + cue
        lst = b'adtl' + adtl
        chunks += b'LIST' + struct.pack('<I', len(lst)) + lst
    with open(path, 'wb') as f:
        f.write(b'RIFF' + struct.pack('<I', 4 + len(chunks)) + b'WAVE' + chunks)


write_wav(os.path.join(outdir, base + '.wav'), y)
cues = []
for b in range(1, NB + 1):
    lab = f'Bar {b:02d}'
    for a, _, n, _ in SECTIONS:
        if a == b:
            lab += f' | {n}'
    cues.append(((b - 1) * BAR, lab))
for b, s, k, d in EVENTS:
    if s != 0:
        cues.append(((b - 1) * BAR + s * S16, f'{k} (bar {b} step {s})'))
cues.append((N - 1, 'END 90.000s'))
cues.sort()
write_wav(os.path.join(outdir, base + '_MARKERS.wav'), y, cues)

# click guide: music -4 dB + metronome (bar downbeat high, beats mid, section starts double)
t = np.arange(int(0.03 * SR)) / SR
def blip(f, a): return np.sin(2 * np.pi * f * t) * np.exp(-t / 0.008) * a
click = np.zeros(N)
for k in range(NB * 4):
    p = k * SPB; bar = k // 4 + 1
    c = blip(2400, 0.5) if k % 4 == 0 else blip(1200, 0.28)
    e = min(N, p + len(c)); click[p:e] += c[:e - p]
    if k % 4 == 0 and any(bar == s[0] for s in SECTIONS) and bar > 1:
        c2 = blip(3200, 0.45); p2 = p + int(0.06 * SR); e2 = min(N, p2 + len(c2)); click[p2:e2] += c2[:e2 - p2]
g = y * 10 ** (-4 / 20) + click[:, None]
g /= max(1.0, np.abs(g).max() / 0.95)
write_wav(os.path.join(outdir, base + '_CLICKGUIDE.wav'), g, cues)
print('wrote', os.listdir(outdir))
