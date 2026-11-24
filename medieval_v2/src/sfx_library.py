"""Action-specific SFX library (48 kHz / 24-bit), one folder per profession + index."""
import json
from inst_v2 import *  # noqa
from studio import reverb

OUT = os.path.join(HERE, '..', 'SFX_LIBRARY')
I = Inst2(777)
rng = np.random.default_rng(778)
INDEX = []


def stereo(y, width=0.0):
    if y.ndim == 2:
        return y
    if width:
        d = int(0.012 * SR); s = np.zeros_like(y); s[d:] = y[:-d]
        return np.stack([y, 0.6 * y + 0.4 * s])
    return np.stack([y, y])


def room(y, wet=0.25, t60=0.9, lo=200):
    y = stereo(y)
    pad = np.zeros((2, int(t60 * 1.2 * SR)))
    y = np.concatenate([y, pad], axis=1)
    return y + reverb(y, t60=t60, predelay=0.012, damp=0.5, lo_cut=lo) * wet


def save(folder, name, y, desc, sync='', wet=None, t60=0.9):
    y = stereo(y)
    if wet:
        y = room(y, wet, t60)
    # trim trailing silence, fade, normalise to -3 dBFS
    a = np.abs(y).max(0)
    idx = np.where(a > 10 ** (-70 / 20) * a.max())[0]
    y = y[:, :idx[-1] + int(0.02 * SR)] if len(idx) else y
    n = min(480, y.shape[1] // 4)
    y[:, -n:] *= np.linspace(1, 0, n)
    y = y / (np.abs(y).max() + 1e-9) * 10 ** (-3 / 20)
    d = os.path.join(OUT, folder); os.makedirs(d, exist_ok=True)
    write_wav24(os.path.join(d, name + '.wav'), y)
    INDEX.append(dict(file=f'{folder}/{name}.wav', seconds=round(y.shape[1] / SR, 3), description=desc, sync_point=sync))


def cat(*parts, gaps=None):
    out = []
    for i, p in enumerate(parts):
        out.append(p)
        if gaps:
            out.append(np.zeros(int(gaps[min(i, len(gaps) - 1)] * SR)))
    return np.concatenate(out)


def at(length, items):
    """items: (time_s, signal, gain) -> mono"""
    y = np.zeros(int(length * SR))
    for t, s, g in items:
        i = int(t * SR); n = min(len(s), len(y) - i)
        y[i:i + n] += s[:n] * g
    return y


def solo(cons, vw, midi, dur, contour, effort, female=False, breath=0.15):
    return syllable(rng, cons, vw, midi, dur, contour, effort, female, rng.uniform(0.95, 1.05), breath=breath)


# ======================================================= 1. KNOCKER-UP
F = '01_Knocker_Up'
for i, p in enumerate((1.0, 1.06, 0.93)):
    save(F, f'KU_stick_tap_glass_{i+1:02d}', I.glass_tap(1.0, p), 'Single wooden-stick tap on a window pane', 'transient at 0.000 s')
save(F, 'KU_window_knock_rhythm_150bpm', at(1.7, [(t * SPB, I.glass_tap(v, 1 + 0.03 * (k % 2)), 1) for k, (t, v) in
     enumerate([(0, 1), (0.5, 0.8), (1.5, 1), (2.25, 0.8), (2.75, 0.9), (3.5, 1)])]),
     'Rhythmic tap-tap pattern locked to 150 BPM (one bar)', 'taps on the 1/8 grid from 0.000 s')
save(F, 'KU_door_knock_x3', at(1.0, [(0, I.door_knock(1.0), 1), (0.2, I.door_knock(0.9, 1.02), 1), (0.4, I.door_knock(1.0, 0.98), 1)]),
     'Three knuckle knocks on a wooden door', 'knocks at 0.0 / 0.2 / 0.4 s', wet=0.15, t60=0.5)
save(F, 'KU_snore_cartoon_01', I.snore(1.8), 'Cartoon snore: rattly inhale + whistling exhale', 'inhale 0-1.0 s, whistle 1.0-1.8 s')
save(F, 'KU_snore_cartoon_02_loopable', cat(I.snore(1.6), I.snore(1.6)), 'Two snore cycles (3.2 s = 2 bars at 150 BPM)', 'cycle every 1.6 s')
gasp = at(1.0, [(0, solo('h', '@a', 55, 0.25, 'rise', 1.0, breath=0.5), 1.0), (0.05, I.slide_whistle(True, 0.4), 0.6)])
save(F, 'KU_wake_up_gasp', gasp, 'Sudden awakening: sharp "HUH!" gasp + slide whistle up', 'gasp onset 0.05 s')
save(F, 'KU_wake_up_startle_bonk', at(0.9, [(0, I.bonk(1.0), 1), (0.03, solo('w', 'a', 60, 0.3, 'shout', 1.0), 0.9)]),
     'Startled jump: bonk + "WAH!"', 'impact 0.000 s')
wo = at(1.4, [(0, I.creak(0.7, 1.0, 50, 140) * 6, 1), (0.7, I.stick_click(1.0), 0.8), (0.72, I.swoosh(0.45, 1.0), 0.5)])
save(F, 'KU_window_open', wo, 'Wooden shutter creaks open, latch click, air whoosh', 'latch click 0.70 s', wet=0.1)
save(F, 'KU_reaction_surprised', solo('w', 'a', 62, 0.35, 'rise', 0.9), 'Surprised "WHAAA?"', 'onset 0.000 s')
ann = cat(solo('m', 'm', 48, 0.25, 'sung', 0.5), solo('h', '@', 50, 0.18, 'shout', 0.8), gaps=[0.05])
save(F, 'KU_reaction_annoyed_hmph', ann, 'Annoyed "Mm-HMPH!"', 'accent at ~0.30 s')
save(F, 'KU_reaction_annoyed_grumble', cat(*[solo('m', 'm@', 45 + rng.normal(0, 1), 0.16, 'sung', 0.4) for _ in range(5)], gaps=[0.03]),
     'Grumpy wordless grumbling', '')
steps = at(1.6, [(k * 0.1, I.footstep(rng.uniform(0.7, 1.0), True), 1) for k in range(15)])
save(F, 'KU_footsteps_fast_run', steps, 'Fast cartoon running steps (10 steps/s; 4 per beat at 150 BPM)', 'step every 0.100 s', wet=0.1)
save(F, 'KU_impact_comedic_bonk', I.bonk(1.0), 'Comedic wooden bonk with pitch drop', 'impact 0.000 s')
save(F, 'KU_impact_comedic_boing', at(0.6, [(0, I.boing(nn('C3'), 1.0), 1), (0, I.wood(1.0, 600), 0.6)]), 'Cartoon boing impact', 'impact 0.000 s')

# ======================================================= 2. GROOM OF THE STOOL
F = '02_Groom_of_the_Stool'
def fanfare(seq_str, beat_len=SPB):
    ev = seq(seq_str, 0)
    L = (ev[-1]['t'] + ev[-1]['d']) * beat_len + 1.0
    y = np.zeros(int(L * SR))
    for harm, g in ((0, 1.0), (-4, 0.7), (-7, 0.5)):
        for e in ev:
            d = e['d'] * beat_len * (0.55 if e['stac'] else 0.92)
            s = I.fanfare_note(e['n'] + harm, d, e['v'])
            i = int(e['t'] * beat_len * SR); n = min(len(s), len(y) - i)
            y[i:i + n] += s[:n] * g
    return y
save(F, 'GS_fanfare_short', fanfare("!C5:1' E5:1' G5:1' C6:4"), 'Short royal trumpet fanfare (ta-ta-ta-TAAA), 150 BPM', 'last note at 0.300 s', wet=0.3, t60=1.4)
save(F, 'GS_fanfare_tada', fanfare("!C5:1' C5:1' r:2 !C6:6"), 'Royal "TA-DA!"', 'hit at 0.400 s', wet=0.3, t60=1.4)
save(F, 'GS_fanfare_announcement', fanfare("!G4:2 G4:1 G4:1 C5:4 E5:2 C5:2 G5:4"), 'Longer herald fanfare (1 bar)', 'downbeat 0.000 s', wet=0.3, t60=1.4)
door = at(2.4, [(0, I.creak(1.2, 1.0, 25, 70) * 7, 1), (1.15, I.door_slam(1.0), 1)])
save(F, 'GS_palace_door_heavy', door, 'Heavy palace door: long creak then boom', 'slam at 1.150 s', wet=0.35, t60=2.0)
save(F, 'GS_palace_door_slam_only', I.door_slam(1.0), 'Heavy palace door slam', 'impact 0.000 s', wet=0.35, t60=2.0)
save(F, 'GS_footsteps_royal_chamber', at(2.6, [(k * 0.4, I.footstep(1.0, True), 1) for k in range(6)]),
     'Slow footsteps on stone in a reverberant chamber (on the beat at 150 BPM)', 'step every 0.400 s', wet=0.5, t60=1.8)
save(F, 'GS_coin_jingle', I.coins(1.0, n=10, dur=0.15) * 3, 'Coin purse jingle', 'onset 0.000 s')
save(F, 'GS_coin_shower', I.coins(1.0, n=40, dur=0.8) * 3, 'Cascade of coins', 'onset 0.000 s', wet=0.15)
for nm, (vw, cons, midi, ctr) in {'GS_crowd_ooh': ('u', '', 64, 'fall'), 'GS_crowd_cheer_hey': ('ei', 'h', 62, 'shout'),
                                  'GS_crowd_gasp': ('@a', 'h', 60, 'rise')}.items():
    c = crowd(rng, cons, vw, midi, 0.6 if ctr == 'fall' else 0.3, n_m=8, n_f=7, spread=0.03, contour=ctr, effort=0.8, oct_f=False)
    save(F, nm, c, {'GS_crowd_ooh': 'Crowd "OOOOH" (impressed, falling)', 'GS_crowd_cheer_hey': 'Crowd cheer "HEY!"',
                    'GS_crowd_gasp': 'Crowd shocked gasp "HAH?"'}[nm], 'onset ~0.05 s', wet=0.3, t60=1.4)
roy = cat(solo('ʔ', 'o', 50, 0.55, 'laugh', 0.8), solo('h', 'a', 55, 0.3, 'shout', 0.9), gaps=[0.08])
save(F, 'GS_royal_exclamation_ohoho', roy, 'Pompous royal "OH-HO-HO-HO... HA!"', 'final HA at ~0.65 s', wet=0.3, t60=1.6)
save(F, 'GS_royal_exclamation_ahem', cat(solo('ʔ', '@', 48, 0.12, 'shout', 0.6, breath=0.4), solo('h', 'Em', 50, 0.3, 'sung', 0.6), gaps=[0.02]),
     'Royal throat-clear "a-HEM"', '', wet=0.3, t60=1.6)
wah = at(1.5, [(0, I.brass_voice(nn('Bb3'), 0.35, 0.8, kind='tbn', fall=True), 1), (0.45, I.brass_voice(nn('A3'), 0.35, 0.8, kind='tbn', fall=True), 1),
               (0.9, I.brass_voice(nn('Ab3'), 0.4, 0.8, kind='tbn', fall=True), 1)])
save(F, 'GS_comedic_sad_trombone', wah, 'Comedic "wah-wah-waaah" trombone', 'notes 0.0 / 0.45 / 0.9 s', wet=0.2)
save(F, 'GS_comedic_slide_whistle_down', I.slide_whistle(False, 0.5), 'Slide whistle falling (embarrassment)', '')
save(F, 'GS_rhythmic_impact_timpani', at(1.6, [(0, I.timpani(nn('C2'), 1.0), 1), (0, I.door_slam(0.7), 0.5)]), 'Timpani + thud royal impact', 'impact 0.000 s', wet=0.3, t60=1.6)

# ======================================================= 3. SIN-EATER
F = '03_Sin_Eater'
save(F, 'SE_church_bell_toll_big', I.church_bell(nn('A2'), 1.0, ring=4.0, big=True), 'Large church bell toll (A)', 'strike 0.000 s', wet=0.4, t60=3.0)
save(F, 'SE_church_bell_toll_x3', at(5.0, [(k * 1.6, I.church_bell(nn('A3'), 1.0, ring=2.5), 1) for k in range(3)]),
     'Three tolls, one per bar at 150 BPM', 'tolls at 0.0 / 1.6 / 3.2 s', wet=0.4, t60=2.5)
save(F, 'SE_handbell_small', I.handbell(nn('E5'), 1.0), 'Small hand bell (E)', 'strike 0.000 s', wet=0.3, t60=1.5)
for k in range(2):
    save(F, f'SE_crow_caw_{k+1:02d}', I.crow(1.0), 'Crow calls (2-3 caws)', 'first caw 0.05 s', wet=0.25, t60=1.6)
wh = np.concatenate([np.r_[I.whisper(1.0, rng.choice(['s', 'sh', 'h']), rng.uniform(0.1, 0.35)), np.zeros(int(rng.uniform(0.05, 0.3) * SR))] for _ in range(10)])
save(F, 'SE_whispers_ghostly', wh, 'Mysterious unintelligible whispers (s / sh / h)', '', wet=0.5, t60=2.0)
save(F, 'SE_door_creak_wooden', I.creak(1.4, 1.0, 30, 90) * 7, 'Slow wooden door creak', '', wet=0.25, t60=1.2)
bite = at(0.8, [(0, I.crunch(1.0, 0.18), 1), (0.32, I.crunch(0.7, 0.12), 1), (0.55, I.crunch(0.5, 0.1), 1)])
save(F, 'SE_bread_crunch_bite', bite, 'Crusty bread bite + two chews', 'bite at 0.000 s')
ghost = at(4.5, [(0, I.ghost_swell(4.0, 1.0, nn('A4')), 1), (0, bp(I.noise(int(4.5 * SR)), 500, 0.5) * 0.15 * np.sin(np.linspace(0, np.pi, int(4.5 * SR))), 1)])
save(F, 'SE_ghost_atmosphere', ghost, 'Ghost choir "oooh" + wind bed (4.5 s)', '', wet=0.6, t60=3.0)
sup = at(2.5, [(0, I.reverse_swell(0.8, 1.0), 1), (0.8, I.church_bell(nn('A3'), 0.8, ring=1.5), 0.8), (0.8, I.impact(1.0), 0.8)])
save(F, 'SE_supernatural_accent', sup, 'Reverse swell into bell + boom (supernatural sting)', 'hit at 0.800 s', wet=0.4, t60=2.5)
tr = at(2.6, [(0, I.swoosh(0.8, 1.0), 1), (0.8, I.impact(1.0), 1), (0.8, I.crash(0.6, 1.0), 0.3)])
save(F, 'SE_transition_impact', tr, 'Whoosh into a deep transition impact', 'hit at 0.800 s', wet=0.3, t60=2.0)
save(F, 'SE_ghost_gasp', crowd(rng, 'h', 'u', 64, 0.6, n_m=3, n_f=4, spread=0.05, contour='fall', effort=0.3, breath=0.8, oct_f=False),
     'Breathy ghostly "hooo"', '', wet=0.6, t60=2.5)

with open(os.path.join(OUT, 'SFX_INDEX.json'), 'w') as f:
    json.dump(dict(sample_rate=SR, bit_depth=24, peak='-3 dBFS', count=len(INDEX), files=INDEX), f, indent=1)
print(len(INDEX), 'sfx written')
