"""Writes output/AUDIO_BEAT_MAP.json: tempo, beats, downbeats, onsets, energy, section selection and visual cue sheet."""
import json
from pathlib import Path
import numpy as np
import timing as T
import scene1, scene2, scene3, scene4, scene5

ROOT = Path(__file__).resolve().parents[1]
a = json.load(open(ROOT / 'build/analysis.json'))
sel = json.load(open(ROOT / 'build/selection.json'))
D = T.db
r = lambda x: round(float(x), 3)
cues = [
    (0.0, 'piano glissando', 'Camera cranes down from the night sky over Gary steel mills to the house'),
    (D(0), 'band enters (downbeat)', 'Window lights up; brothers dance in silhouette; location card'),
    (D(1), 'downbeat', 'Push through the window into the living room (flash)'),
    (D(2), 'downbeat', 'Dancers lock into unison step-touch'),
    (D(3), 'downbeat accent', 'Group point-hit introduces the five brothers; camera push + shake'),
    (D(4) - 0.62, 'fill', 'Spin -> whip pan to the club'),
    (scene2.T0, 'vocal entrance', 'Club stage: Michael shy at the mic'),
    (D(5), 'downbeat', 'Spotlight snaps onto Michael; he sings with confidence'),
    (D(6), 'downbeat', 'Audience wakes up (bounce, hands up); brothers step-touch'),
    (D(7), 'phrase start', 'Curtains close on the beat and reopen in the grand theater'),
    (D(8), 'verse downbeat', 'Vinyl record drops; tonearm lands'),
    (D(9), 'downbeat', 'Recording studio; VU meters ride the real audio'),
    (D(10), 'downbeat', 'Close-up: Michael singing (lip movement from vocal envelope)'),
    (D(11), 'downbeat', 'Producers jump up, thumbs up'),
    (D(12), 'downbeat', 'Record turns gold, colour explosion builds'),
    (D(13), 'chorus build', 'White flash into the 1969 TV stage, op-art backdrop'),
    (D(14), 'downbeat', 'Tracking shot follows Michael sliding across the stage'),
    (D(15), 'downbeat', 'Return slide + kick, point hit'),
    (D(16), 'downbeat', 'Silhouette sequence against the orange sun disc'),
    (D(17), 'downbeat', 'Close-up on Michael singing, spin'),
    (D(18), 'downbeat', 'Match cut on Michael\'s face into the arena; pull back'),
    (D(19), 'downbeat', 'Group revealed; unison step-touch'),
    (D(20), 'downbeat', 'Wide arena: thousands of fans, beams'),
    (D(22), 'downbeat', 'Spin + point hit (camera shake)'),
    (D(24), 'final downbeat phrase', 'Golden lights, knee drop, title THE JACKSON 5'),
    (D(25), 'downbeat', 'Subtitle: A story of five brothers who changed music forever.'),
    (T.DURATION - T.FADE, 'last downbeat', 'Hold on golden wide; music fades'),
]
out = dict(
    source=dict(duration_s=r(a['duration']), tempo_bpm=round(a['tempo'], 2), beat_period_s=r(T.PERIOD),
                beats_song_time=a['beats'], downbeats_song_time=a['downbeats'], structural_boundaries=a['segments'],
                strong_onsets=a['strong_onsets'], bass_onsets=a['low_onsets'], snare_onsets=a['snare_onsets'],
                rms_per_second=a['rms_per_sec']),
    selection=dict(chosen=sel['chosen'], candidates_compared=sel['candidates'],
                   rationale='Highest score: iconic piano-glissando opening, positive energy development into the '
                             'first chorus, strong climax in the last 40%, ends on a downbeat 1.2 s from a structural '
                             'boundary. Runner-up (97.8-163.9 s) starts louder but has no development.'),
    edit=dict(song_in_s=T.SONG_IN, song_out_s=r(T.SONG_CUT + T.FADE), audio_fade_s=T.FADE, video_duration_s=T.DURATION,
              fps=T.FPS, beats_edit_time=[r(b) for b in T.BEATS if -1 < b < T.DURATION],
              downbeats_edit_time=[r(b) for b in T.DOWNBEATS if -1 < b < T.DURATION]),
    scenes=[dict(name='1 The Beginning (Gary, Indiana)', start=0.0, end=r(scene2.T0)),
            dict(name='2 The First Dream (club -> grand theater)', start=r(scene2.T0), end=r(scene3.T0)),
            dict(name='3 The Breakthrough (vinyl, studio, hit)', start=r(scene3.T0), end=r(scene4.T0)),
            dict(name='4 The World Discovers Them (TV stage)', start=r(scene4.T0), end=r(scene5.T0)),
            dict(name='5 Five Brothers, One Legend (arena, title)', start=r(scene5.T0), end=T.DURATION)],
    cue_sheet=[dict(t=r(t), frame=int(round(t * T.FPS)), music=m, visual=v) for t, m, v in cues],
)
(ROOT / 'output').mkdir(exist_ok=True)
json.dump(out, open(ROOT / 'output/AUDIO_BEAT_MAP.json', 'w'), indent=1)
print('cues', len(cues))
