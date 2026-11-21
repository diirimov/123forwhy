#!/usr/bin/env python3
"""
Skybound soundtrack pipeline:  compose -> render -> mix -> master -> export -> verify.

    python3 build.py              # full render (~1-2 min)

Outputs in ./output/ :
    soundtrack_final.wav            48 kHz / 24-bit / stereo, -14 LUFS, <= -1 dBTP
    soundtrack_narration_bed.wav    same mix, -6 dB with a presence dip for voice-over
    soundtrack_preview.mp3          320 kbps
    soundtrack_project.mid          editable multitrack MIDI (all parts, GM stand-ins for synths)
    stems/*.wav (+ .flac copies)    drums, bass, synths, lead, orchestra, fx (pre-master, 24-bit)
    cue_sheet.md / cue_sheet.csv    timestamped cue sheet
    verification.json               measured specs of every exported file
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pyloudnorm as pyln
import soundfile as sf
from pedalboard import (Pedalboard, Compressor, HighpassFilter, LowpassFilter, PeakFilter,
                        HighShelfFilter, LowShelfFilter, Gain)
from scipy.signal import resample_poly

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from engine import dsp                                     # noqa: E402
from engine.dsp import SR, Track, hz                       # noqa: E402
from engine.score import (compose, beat_to_sec, DURATION, SPB, BAR, CUES, SEED)  # noqa: E402
from engine import midi_export                             # noqa: E402

OUT = HERE / 'output'
BUILD = HERE / 'build'
SF2 = '/usr/share/sounds/sf2/FluidR3_GM.sf2'
TAIL = 4.0
N = int((DURATION + TAIL) * SR)
METER = pyln.Meter(SR)

# Active-region loudness targets (LUFS, pre-master). This is the gain-staging / balance table.
TARGET = {
    'kick': -15.5, 'snare': -21.5, 'clap': -25.0, 'hat_c': -30.0, 'hat_o': -31.5,
    'toms': -22.5, 'crash': -28.0,
    'bass_sub': -19.5, 'bass_mid': -21.5,
    'pad': -21.5, 'arp': -28.0,
    'pluck': -20.5, 'lead': -21.0, 'lead_hi': -28.0,
    'strings': -22.5, 'tremolo': -26.0, 'choir': -28.0, 'brass': -22.0, 'horns': -25.0,
    'timpani': -21.0, 'piano': -23.0, 'celesta': -28.5,
    'impact': -20.0, 'riser': -24.0, 'downlifter': -29.0, 'revcym': -28.0, 'subdrop': -24.5,
}
STEMS = {
    'drums': ['kick', 'snare', 'clap', 'hat_c', 'hat_o', 'toms', 'crash'],
    'bass': ['bass_sub', 'bass_mid'],
    'synths': ['pad', 'arp'],
    'lead': ['pluck', 'lead', 'lead_hi'],
    'orchestra': ['strings', 'tremolo', 'choir', 'brass', 'horns', 'timpani', 'piano', 'celesta'],
    'fx': ['impact', 'riser', 'downlifter', 'revcym', 'subdrop'],
}
ORCH = ['strings', 'tremolo', 'choir', 'brass', 'horns', 'timpani', 'piano', 'celesta']


def log(*a):
    print(*a, flush=True)


def vgain(v, curve=1.6):
    return (v / 127.0) ** curve


def loudness(x):
    try:
        return METER.integrated_loudness(x.T)
    except Exception:
        return -np.inf


def stage(x, target):
    L = loudness(x)
    if not np.isfinite(L):
        return x
    return x * 10 ** ((target - L) / 20)


def fx_chain(x, board):
    return board(x.astype(np.float32), SR).astype(np.float64)


# =============================================================================== render
def render_synths(S, rng):
    T = {k: Track(N) for k in TARGET}
    sec = beat_to_sec

    # --- drums
    kicks = [dsp.kick(rng, heavy=h) for h in (False, True)]
    for b, v in S.drums.get('kick', []):
        T['kick'].add(kicks[b >= 80], sec(b), vgain(v))
    for b, v in S.drums.get('snare', []):
        T['snare'].add(dsp.pan(dsp.snare(rng), 0.0), sec(b), vgain(v, 1.8))
    for b, v in S.drums.get('clap', []):
        c = dsp.clap(rng)
        T['clap'].add(np.stack([c, np.roll(c, int(0.007 * SR))]), sec(b), vgain(v))
    for b, v in S.drums.get('hat_c', []):
        T['hat_c'].add(dsp.pan(dsp.hat(rng), 0.28), sec(b) + rng.normal(0, 0.002), vgain(v, 1.3))
    for b, v in S.drums.get('hat_o', []):
        T['hat_o'].add(dsp.pan(dsp.hat(rng, True), -0.22), sec(b), vgain(v, 1.3))
    toms = {'tom_h': (155, 0.35), 'tom_m': (115, 0.0), 'tom_l': (82, -0.35)}
    for name, (f0, p) in toms.items():
        for b, v in S.drums.get(name, []):
            T['toms'].add(dsp.pan(dsp.tom(rng, f0), p), sec(b), vgain(v))
    for b, v in S.drums.get('crash', []):
        T['crash'].add(dsp.crash(rng), sec(b), vgain(v, 1.2))

    # --- bass
    for n in S.parts['bass']:
        sub, mid = dsp.bass(hz(n.pitch), int(n.dur * SPB * SR), drive=0.6 + 0.6 * n.vel / 127)
        T['bass_sub'].add(sub, sec(n.start), vgain(n.vel, 1.0))
        T['bass_mid'].add(mid, sec(n.start), vgain(n.vel, 1.4))

    # --- pad (supersaw chords)
    for (s, d, ps, v, cut, att) in S.pad:
        x = dsp.supersaw(hz(ps), int(d * SPB * SR), rng, cutoff=cut, attack=att,
                         release=0.35 if att > 0.1 else 0.18)
        T['pad'].add(x, sec(s), v)

    # --- arp, pluck, lead
    for n in S.parts['arp']:
        T['arp'].add(dsp.pluck(hz(n.pitch), int(n.dur * SPB * SR), rng, bright=0.7), sec(n.start), vgain(n.vel))
    for n in S.parts['pluck']:
        T['pluck'].add(dsp.pluck(hz(n.pitch), int(n.dur * SPB * SR), rng, bright=0.6 + 0.5 * n.vel / 127),
                       sec(n.start) + rng.normal(0, 0.002), vgain(n.vel))
    for part in ('lead', 'lead_hi'):
        for n in S.parts[part]:
            T[part].add(dsp.lead(hz(n.pitch), int(n.dur * SPB * SR), rng, cutoff=3200 + 2200 * n.vel / 127),
                        sec(n.start), vgain(n.vel))

    # --- fx
    for e in S.fx:
        k, b, size = e['kind'], e['beat'], e['size']
        if k == 'impact':
            T['impact'].add(dsp.impact(rng, size), sec(b), size)
        elif k == 'riser':
            L = sec(e['end'] - b)
            T['riser'].add(dsp.riser(rng, L, size), sec(b))
        elif k == 'downlifter':
            T['downlifter'].add(dsp.downlifter(rng, sec(e['end'] - b), size), sec(b))
        elif k == 'revcym':
            L = sec(e['end'] - b)
            T['revcym'].add(dsp.revcym(rng, L, size), sec(b))
        elif k == 'subdrop':
            T['subdrop'].add(dsp.subdrop(size), sec(b))
    return {k: t.buf for k, t in T.items()}


def render_orchestra(S):
    out = {}
    for part in ORCH:
        mid = BUILD / f'{part}.mid'
        wav = BUILD / f'{part}.wav'
        midi_export.write_orchestral_part(S, part, mid)
        subprocess.run(['fluidsynth', '-ni', '-q', '-R', '0', '-C', '0', '-g', '0.5', '-r', str(SR),
                        '-O', 'float', '-T', 'wav', '-F', str(wav), SF2, str(mid)],
                       check=True, capture_output=True)
        x, sr = sf.read(wav, always_2d=True)
        if sr != SR:
            x = resample_poly(x, SR, sr, axis=0)
        x = x.T.astype(np.float64)
        buf = np.zeros((2, N))
        buf[:, :min(N, x.shape[1])] = x[:, :N]
        out[part] = buf
    return out


# =============================================================================== mix
def mix(raw, S):
    kick_times = [beat_to_sec(b) for b, v in S.drums['kick'] if v > 90]
    duck = lambda depth, rel: dsp.duck_env(kick_times, N, depth, rel)[None]

    hall = dsp.make_ir(2.6, 0.03, 3500, seed=SEED)
    plate = dsp.make_ir(1.3, 0.012, 6000, seed=SEED + 1)
    room = dsp.make_ir(0.8, 0.006, 5000, seed=SEED + 2)
    dotted8 = 0.75 * SPB

    t = {k: stage(v, TARGET[k]) for k, v in raw.items()}

    # ---- per-track tone shaping
    eq = lambda *p: Pedalboard(list(p))
    t['kick'] = fx_chain(t['kick'], eq(HighpassFilter(30), PeakFilter(65, 2.0, 0.9), PeakFilter(350, -3.0, 1.2),
                                        PeakFilter(4000, 1.5, 1.0)))
    t['snare'] = fx_chain(t['snare'], eq(HighpassFilter(120), PeakFilter(220, 1.5, 1.0), HighShelfFilter(9000, 1.5)))
    t['hat_c'] = fx_chain(t['hat_c'], eq(HighpassFilter(5000), LowpassFilter(15000)))
    t['hat_o'] = fx_chain(t['hat_o'], eq(HighpassFilter(5000), LowpassFilter(14000)))
    t['crash'] = fx_chain(t['crash'], eq(HighpassFilter(500), HighShelfFilter(10000, -2.0)))
    t['bass_sub'] = fx_chain(t['bass_sub'], eq(HighpassFilter(28), LowpassFilter(140)))
    t['bass_mid'] = fx_chain(t['bass_mid'], eq(HighpassFilter(100), PeakFilter(900, 2.0, 1.0), LowpassFilter(5000)))
    t['pad'] = fx_chain(t['pad'], eq(HighpassFilter(220), PeakFilter(450, -2.5, 1.0), PeakFilter(2800, -2.0, 1.2),
                                      HighShelfFilter(9000, -2.0)))
    t['arp'] = fx_chain(t['arp'], eq(HighpassFilter(400), PeakFilter(3000, -1.5, 1.0)))
    t['pluck'] = fx_chain(t['pluck'], eq(HighpassFilter(180), PeakFilter(2500, 2.0, 1.0), HighShelfFilter(11000, -1.5),
                                          Compressor(-18, 3, 3, 80)))
    for k in ('lead', 'lead_hi'):
        t[k] = fx_chain(t[k], eq(HighpassFilter(250), PeakFilter(400, -2.0, 1.0), PeakFilter(3200, 1.0, 1.0),
                                  HighShelfFilter(10000, -2.5)))
    for k in ('strings', 'tremolo', 'choir'):
        t[k] = fx_chain(t[k], eq(HighpassFilter(90), PeakFilter(300, -2.0, 1.0), HighShelfFilter(8000, 1.5)))
    for k in ('brass', 'horns'):
        t[k] = fx_chain(t[k], eq(HighpassFilter(100), PeakFilter(1800, 1.5, 1.0), HighShelfFilter(9000, -1.0)))
    t['piano'] = fx_chain(t['piano'], eq(HighpassFilter(60), PeakFilter(250, -2.0, 1.0)))
    t['timpani'] = fx_chain(t['timpani'], eq(HighpassFilter(40), PeakFilter(90, 2.0, 1.0)))
    for k in ('impact', 'subdrop'):
        t[k] = fx_chain(t[k], eq(HighpassFilter(28)))
    for k in ('riser', 'downlifter', 'revcym'):
        t[k] = fx_chain(t[k], eq(HighpassFilter(200), HighShelfFilter(10000, -2.0)))

    # ---- sidechain pumping
    t['bass_sub'] *= duck(0.85, 0.10)
    t['bass_mid'] *= duck(0.75, 0.10)
    t['pad'] *= duck(0.65, 0.16)
    t['arp'] *= duck(0.40, 0.12)
    t['strings'] *= duck(0.22, 0.15)
    t['choir'] *= duck(0.15, 0.15)

    # ---- buses (each stem contains its own reverb return, so stems sum to the mix)
    stems = {}

    def bus(names, sends, post):
        dry = sum(t[k] for k in names)
        wet = np.zeros_like(dry)
        for ir, amounts in sends:
            src = sum(t[k] * a for k, a in amounts.items() if a > 0)
            if np.any(src):
                wet += dsp.convolve(src, ir)
        return fx_chain(dry + wet, post)

    stems['drums'] = bus(STEMS['drums'],
                         [(room, {'snare': .32, 'clap': .35, 'toms': .3, 'hat_o': .1}),
                          (hall, {'snare': .12, 'clap': .15, 'crash': .1})],
                         Pedalboard([Compressor(-12, 2.5, 8, 120), Gain(0.5)]))
    stems['bass'] = bus(STEMS['bass'], [], Pedalboard([Compressor(-14, 3, 5, 80), HighpassFilter(26)]))
    # arp gets its ping-pong delay inside the synths bus
    t['arp'] = t['arp'] + dsp.pingpong(t['arp'], dotted8, fb=0.4, taps=5) * 0.5
    stems['synths'] = bus(STEMS['synths'], [(hall, {'pad': .22, 'arp': .3})], Pedalboard([Gain(0)]))
    pl = t['pluck']
    t['pluck'] = pl + dsp.pingpong(pl, dotted8, fb=0.35, taps=4) * 0.32
    stems['lead'] = bus(STEMS['lead'], [(plate, {'pluck': .25, 'lead': .28, 'lead_hi': .35}),
                                        (hall, {'pluck': .12, 'lead': .18, 'lead_hi': .25})],
                        Pedalboard([Compressor(-16, 2, 10, 150)]))
    stems['orchestra'] = bus(STEMS['orchestra'],
                             [(hall, {'strings': .35, 'tremolo': .4, 'choir': .55, 'brass': .3, 'horns': .4,
                                      'timpani': .3, 'piano': .45, 'celesta': .5})],
                             Pedalboard([Compressor(-18, 1.8, 20, 200)]))
    stems['fx'] = bus(STEMS['fx'], [(hall, {'impact': .25, 'riser': .3, 'downlifter': .4, 'revcym': .2})],
                      Pedalboard([Gain(0)]))
    return stems


# =============================================================================== master
def true_peak_db(x):
    up = resample_poly(x, 4, 1, axis=1)
    return 20 * np.log10(np.max(np.abs(up)) + 1e-12)


def master(stems, target_lufs=-14.0, ceiling_dbtp=-1.0):
    n_out = int(DURATION * SR)
    mixbus = sum(stems.values())
    mixbus = stage(mixbus, -18.0)
    stems = {k: v * (10 ** ((-18.0 - loudness(sum(stems.values()))) / 20)) for k, v in stems.items()}
    chain = Pedalboard([HighpassFilter(30), LowShelfFilter(55, -1.0), PeakFilter(280, -1.2, 0.8),
                        PeakFilter(4200, -0.8, 1.2), HighShelfFilter(12000, 0.8),
                        Compressor(-20, 1.7, 25, 220)])
    m = fx_chain(mixbus, chain)
    for _ in range(4):   # converge integrated loudness through the limiter
        L = loudness(m[:, :n_out])
        m = m * 10 ** ((target_lufs - L) / 20)
        lim, g = dsp.limiter(m, ceiling_dbtp - 0.3)
        Ll = loudness(lim[:, :n_out])
        if abs(Ll - target_lufs) < 0.1:
            break
        m = m * 10 ** ((target_lufs - Ll) / 20)
    log(f'   limiter max gain reduction: {20 * np.log10(g.min()):.2f} dB')
    m = lim[:, :n_out]
    tp = true_peak_db(m)
    if tp > ceiling_dbtp:
        m *= 10 ** ((ceiling_dbtp - 0.05 - tp) / 20)
    # end fade (tail is already decaying; guarantee exact silence at 60.000 s)
    fade = int(1.4 * SR)
    m[:, -fade:] *= np.cos(np.linspace(0, np.pi / 2, fade)) ** 2
    stems = {k: v[:, :n_out] for k, v in stems.items()}
    for v in stems.values():
        v[:, -fade:] *= np.cos(np.linspace(0, np.pi / 2, fade)) ** 2
    return m, stems


def narration_bed(m):
    """Voice-over friendly version: presence dip where speech intelligibility lives, -6 dB."""
    return fx_chain(m, Pedalboard([PeakFilter(2500, -4.0, 0.7), PeakFilter(1000, -2.0, 0.8), Gain(-6.0)]))


# =============================================================================== export + verify
def write_wav(path, x):
    sf.write(path, x.T.astype(np.float32), SR, subtype='PCM_24')


def probe(path):
    info = sf.info(str(path))
    x, sr = sf.read(str(path), always_2d=True)
    x = x.T
    return {
        'file': path.name, 'duration_s': round(info.frames / info.samplerate, 4), 'sample_rate': info.samplerate,
        'channels': info.channels, 'subtype': info.subtype,
        'sample_peak_dbfs': round(float(20 * np.log10(np.max(np.abs(x)) + 1e-12)), 2),
        'true_peak_dbtp': round(true_peak_db(x), 2),
        'integrated_lufs': round(float(loudness(x)), 2),
        'clipped_samples': int(np.sum(np.abs(x) >= 0.99997)),
    }


def section_report(m, S):
    rows = []
    for (b0, b1, name, _) in S.sections:
        a, b = int(beat_to_sec(b0 * BAR) * SR), int(min(beat_to_sec(b1 * BAR), DURATION) * SR)
        seg = m[:, a:b]
        rows.append((name, round(beat_to_sec(b0 * BAR), 2), round(float(loudness(seg)), 1),
                     round(float(20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-12)), 1)))
    return rows


def spectrum_report(m):
    X = np.abs(np.fft.rfft(m.mean(0) * np.hanning(m.shape[1]))) ** 2
    f = np.fft.rfftfreq(m.shape[1], 1 / SR)
    bands = [(20, 60), (60, 120), (120, 250), (250, 500), (500, 1000), (1000, 2000), (2000, 4000),
             (4000, 8000), (8000, 16000)]
    e = [10 * np.log10(X[(f >= lo) & (f < hi)].sum() + 1e-20) for lo, hi in bands]
    ref = max(e)
    return [(f'{lo}-{hi}', round(v - ref, 1)) for (lo, hi), v in zip(bands, e)]


def write_cue_sheet(S, report):
    secs = lambda b: beat_to_sec(b)
    lines = ['# Skybound - cue sheet', '',
             'Original cinematic-electronic cue - 144 BPM - 4/4 - D minor -> E minor -> E major ending - 60.000 s',
             '', 'One bar = 1.667 s, one beat = 0.417 s (at 30 fps: 50 frames per bar, 12.5 frames per beat).', '',
             '## Sections', '', '| Time | Bars | Section | Chords | What happens |', '|---|---|---|---|---|']
    csv = ['type,start_s,end_s,bar,name,detail']
    for (b0, b1, name, desc) in S.sections:
        ch = ' '.join(S.chords[b0:b1]) if name != 'ENDING' else 'E (major)'
        lines.append(f'| {secs(b0 * BAR):05.2f}-{min(secs(b1 * BAR), DURATION):05.2f} | {b0 + 1}-{b1} | **{name}** | {ch} | {desc} |')
        csv.append(f'section,{secs(b0 * BAR):.3f},{min(secs(b1 * BAR), DURATION):.3f},{b0 + 1},{name},"{desc}"')
    lines += ['', '## Sync points (hit these with cuts / impacts)', '',
              '| Time (s) | Frame @30fps | Bar.beat | Musical event | Suggested visual |', '|---|---|---|---|---|']
    for b, ev, vis in CUES:
        s = secs(b)
        lines.append(f'| {s:06.3f} | {round(s * 30)} | {int(b // 4) + 1}.{b % 4 + 1:g} | {ev} | {vis} |')
        csv.append(f'cue,{s:.3f},,{int(b // 4) + 1},{ev},"{vis}"')
    lines += ['', '## Narration windows', '',
              '- **00.00-06.67** intro: no drums, light texture - good for the opening line.',
              '- **26.67-33.33** breakdown: piano + choir only - best spot for the key story line.',
              '- Busy sections (33.3-50.0) - keep narration sparse or use `soundtrack_narration_bed.wav` '
              '(-6 dB, 1-2.5 kHz presence dip).', '',
              '## Measured loudness per section (final master)', '', '| Section | Start (s) | LUFS | RMS dBFS |',
              '|---|---|---|---|']
    for name, s, L, r in report:
        lines.append(f'| {name} | {s:.2f} | {L} | {r} |')
    (OUT / 'cue_sheet.md').write_text('\n'.join(lines) + '\n')
    (OUT / 'cue_sheet.csv').write_text('\n'.join(csv) + '\n')


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / 'stems').mkdir(exist_ok=True)
    BUILD.mkdir(exist_ok=True)
    rng = np.random.default_rng(SEED)

    log('1/6 compose');   S = compose()
    midi_export.write_project(S, OUT / 'soundtrack_project.mid')
    log('2/6 render synths + drums + fx');  raw = render_synths(S, rng)
    log('3/6 render orchestra (FluidSynth / FluidR3_GM)');  raw.update(render_orchestra(S))
    log('4/6 mix');       stems = mix(raw, S)
    log('5/6 master');    m, stems = master(stems)

    log('6/6 export')
    write_wav(OUT / 'soundtrack_final.wav', m)
    write_wav(OUT / 'soundtrack_narration_bed.wav', narration_bed(m))
    for k, v in stems.items():
        write_wav(OUT / 'stems' / f'{k}.wav', v)
        sf.write(OUT / 'stems' / f'{k}.flac', v.T.astype(np.float32), SR, subtype='PCM_24')  # lossless, git-friendly
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(OUT / 'soundtrack_final.wav'),
                    '-codec:a', 'libmp3lame', '-b:a', '320k', '-ar', '48000', str(OUT / 'soundtrack_preview.mp3')],
                   check=True)

    rep = section_report(m, S)
    write_cue_sheet(S, rep)
    files = [OUT / 'soundtrack_final.wav', OUT / 'soundtrack_narration_bed.wav'] + \
        sorted((OUT / 'stems').glob('*.wav'))
    ver = {'files': [probe(p) for p in files]}
    mp3 = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                                     'format=duration,bit_rate:stream=sample_rate,channels,codec_name',
                                     '-of', 'json', str(OUT / 'soundtrack_preview.mp3')],
                                    capture_output=True, text=True, check=True).stdout)
    ver['mp3'] = mp3
    ver['sections'] = rep
    ver['spectrum_rel_db'] = spectrum_report(m)
    ver['stem_sum_vs_master_lufs'] = round(float(loudness(sum(stems.values()))), 2)
    (OUT / 'verification.json').write_text(json.dumps(ver, indent=2))
    log(json.dumps(ver, indent=2))


if __name__ == '__main__':
    main()
