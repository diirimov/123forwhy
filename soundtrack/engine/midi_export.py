"""MIDI export: full editable project file + per-instrument files for FluidSynth rendering."""
import zlib
import numpy as np
import mido
from .score import BPM, SEED

PPQ = 480

# part -> (channel, GM program, name). Synth parts get a GM stand-in so the file plays anywhere.
GM = {
    'pluck':   (0, 81, 'Pluck Hook (synth)'),
    'lead':    (1, 81, 'Supersaw Lead (synth)'),
    'lead_hi': (2, 81, 'Supersaw Lead +8va (synth)'),
    'arp':     (3, 84, 'Arp (synth)'),
    'bass':    (4, 38, 'Bass (synth)'),
    'pad':     (5, 90, 'Supersaw Chords (synth)'),
    'strings': (6, 48, 'Strings'),
    'tremolo': (7, 44, 'Tremolo Strings'),
    'choir':   (8, 52, 'Choir Aahs'),
    'drums':   (9, 0, 'Drums'),
    'brass':   (10, 61, 'Brass Section'),
    'horns':   (11, 60, 'French Horns'),
    'timpani': (12, 47, 'Timpani'),
    'piano':   (13, 0, 'Piano'),
    'celesta': (14, 8, 'Celesta'),
}
DRUM_MAP = {'kick': 36, 'snare': 38, 'clap': 39, 'hat_c': 42, 'hat_o': 46,
            'tom_h': 50, 'tom_m': 47, 'tom_l': 43, 'crash': 49}


def _track(name, ch, prog, notes, ccs=(), humanize=0.0, rng=None):
    """notes: [(start_beat, dur_beat, pitch, vel)]"""
    tr = mido.MidiTrack()
    tr.append(mido.MetaMessage('track_name', name=name, time=0))
    if ch != 9:
        tr.append(mido.Message('program_change', channel=ch, program=prog, time=0))
    tr.append(mido.Message('control_change', channel=ch, control=7, value=110, time=0))
    tr.append(mido.Message('control_change', channel=ch, control=11, value=127, time=0))
    ev = []
    for (s, d, p, v) in notes:
        jit = rng.uniform(-humanize, humanize) if (rng is not None and humanize) else 0
        t0 = max(0, int(round((s + jit) * PPQ)))
        t1 = max(t0 + 1, int(round((s + jit + d) * PPQ)))
        ev.append((t0, 1, mido.Message('note_on', channel=ch, note=int(p), velocity=int(v))))
        ev.append((t1, 0, mido.Message('note_off', channel=ch, note=int(p), velocity=0)))
    for (b, c, val) in ccs:
        ev.append((int(round(b * PPQ)), 0, mido.Message('control_change', channel=ch, control=c, value=int(val))))
    ev.sort(key=lambda e: (e[0], e[1]))
    now = 0
    for t, _, m in ev:
        tr.append(m.copy(time=t - now))
        now = t
    tr.append(mido.MetaMessage('end_of_track', time=PPQ))
    return tr


def _tempo_track():
    tr = mido.MidiTrack()
    tr.append(mido.MetaMessage('track_name', name='Skybound - 144 BPM - D minor', time=0))
    tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(BPM), time=0))
    tr.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))
    tr.append(mido.MetaMessage('key_signature', key='Dm', time=0))
    return tr


def part_notes(score, part):
    return [(n.start, n.dur, n.pitch, n.vel) for n in score.parts.get(part, [])]


def write_project(score, path):
    mf = mido.MidiFile(ticks_per_beat=PPQ, type=1)
    mf.tracks.append(_tempo_track())
    for part, (ch, prog, name) in GM.items():
        if part == 'drums':
            notes = [(b, .1, DRUM_MAP[d], v) for d, hits in score.drums.items() for (b, v) in hits]
        elif part == 'pad':
            notes = [(s, d, p, int(v * 127)) for (s, d, ps, v, _, _) in score.pad for p in ps]
        else:
            notes = part_notes(score, part)
        if notes:
            mf.tracks.append(_track(name, ch, prog, notes, score.cc.get(part, ())))
    mf.save(path)


def write_orchestral_part(score, part, path, humanize_beats=0.012):
    ch, prog, name = GM[part]
    ch = 0
    mf = mido.MidiFile(ticks_per_beat=PPQ, type=1)
    mf.tracks.append(_tempo_track())
    rng = np.random.default_rng(SEED + zlib.crc32(part.encode()) % 1000)
    mf.tracks.append(_track(name, ch, prog, part_notes(score, part), score.cc.get(part, ()),
                            humanize=humanize_beats, rng=rng))
    mf.save(path)
