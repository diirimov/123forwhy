"""Shared arrangement grid + helpers for all four candidates."""
from studio import *

# Section start beats (144 beats = 65.0 s @ 132.92 BPM)
INTRO, D1, BRK, S2, FAKE, S3, FIN, END = 0, 6, 42, 44, 80, 82, 118, 142


def bars(start, n):
    return [start + 4 * i for i in range(n)]


def std_cues(S):
    S.cue(INTRO, 'INTRO: hook enters, vintage filtered (voice-over space)', 'section')
    S.cue(4, 'pickup: brass stab + fill', 'section')
    S.cue(D1, 'DROP 1: full groove + clarinet hook', 'section')
    S.cue(BRK, 'RHYTHMIC BREAK (stop-time)', 'section')
    S.cue(S2, 'SECTION 2: royal brass + heavier bass', 'section')
    S.cue(FAKE, 'FAKE-OUT (tape stop / gotcha)', 'section')
    S.cue(S3, 'SECTION 3: minor-key mystery groove', 'section')
    S.cue(FIN - 4, 'riser into final drop', 'section')
    S.cue(FIN, 'FINAL DROP: biggest section, hook returns', 'section')
    S.cue(END, 'loop pickup -> back to 0:00', 'section')


def turnaround_fill(S, b, roll=True, riser=True, crash_next=True, s=0.5):
    """Bar-9 style transition: snare roll + riser + crash on next downbeat."""
    if roll:
        S.drum("........gooxxxXX", b, 'snare', gain=0.55)
    if riser:
        S.place('fx', S.I.riser(4 * SPB), S.t(b))
    if crash_next:
        S.place('drums', S.I.crash(0.9), S.t(b + 4), 0.0, 0.45)
        S.place('fx', S.I.impact(0.9), S.t(b + 4), 0.0, 0.7)


# pre-master section levels (dB): final drop is the peak, section 3 sits back a little
AUTO = [(0, 0.0), (D1, -1.5), (S2, -1.0), (S3, -3.0), (FIN - 4, -2.0), (FIN, 0.5)]

BASE_MIX = {
    'kick': dict(gain=0.75, eq=[('hp', 28, 0.7), ('peak', 58, 1.0, 2.0), ('peak', 350, 1.2, -3)]),
    'drums': dict(gain=1.0, sc=0.12, rv2=0.14, eq=[('hp', 160), ('lp', 12500)], haas=0.007),
    'bass': dict(gain=0.66, sc=0.5, eq=[('lp', 3200), ('hp', 38)], drive=1.6),
    'sub': dict(gain=0.36, sc=0.8, eq=[('lp', 1500), ('hp', 30)]),
    'lead': dict(gain=0.34, sc=0.18, rv=0.22, dl=0.13, eq=[('hp', 170), ('peak', 2800, 1.0, 1.5)]),
    'brass': dict(gain=0.30, sc=0.3, rv=0.18, rv2=0.12, eq=[('hp', 110), ('peak', 1200, 0.9, 1.5)], drive=1.4, haas=0.009),
    'keys': dict(gain=0.19, sc=0.45, rv=0.2, rv2=0.1, eq=[('hp', 140)], haas=0.013),
    'vox': dict(gain=0.28, sc=0.3, rv=0.28, dl=0.2, eq=[('hp', 200), ('peak', 3500, 1, 2)], haas=0.011),
    'tex': dict(gain=0.4, sc=0.35, rv=0.45, dl=0.1, eq=[('hp', 200)], haas=0.017),
    'fx': dict(gain=0.32, rv=0.3),
    'vintage': dict(gain=0.39, eq=[('hp', 360, 0.8), ('lp', 4300, 0.8), ('peak', 1400, 1, 3)], rv2=0.25),
    'post': dict(gain=0.22),
}


def mixcfg(**over):
    cfg = {k: dict(v) for k, v in BASE_MIX.items()}
    for k, v in over.items():
        cfg.setdefault(k, {}).update(v)
    return cfg
