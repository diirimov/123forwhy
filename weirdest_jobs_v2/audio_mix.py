"""Final audio: approved soundtrack (unchanged) + one-line narration + visually-synced SFX from the library.
Writes audio/FINAL_MIX.wav (48 kHz 24-bit) and SFX_SYNC_MAP.json."""
import json, os, sys
import numpy as np, soundfile as sf
from scipy.signal import resample_poly

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
SR = 48000
music, sr = sf.read(os.path.join(ROOT, 'medieval_v2', 'MEDIEVAL_JOBS_V2_FINAL.wav'), always_2d=True)
assert sr == SR
music = music.T.copy()                      # (2, N)
N = music.shape[1]
LIB = os.path.join(ROOT, 'medieval_v2', 'SFX_LIBRARY')

# ---------------------------------------------------------------- narration (Kokoro am_fenrir), music ducked gently under it
vo, vsr = sf.read(os.path.join(HERE, 'audio', 'NARRATION_OPENING.wav'))
vo = resample_poly(vo, SR, vsr)
VO_AT = 0.20
duck = np.ones(N)
t = np.arange(N) / SR
vo_end = VO_AT + len(vo) / SR
duck -= (1 - 10 ** (-4.5 / 20)) * np.clip(np.minimum((t - (VO_AT - .12)) / .12, (vo_end + .15 - t) / .2), 0, 1)
mix = music * duck
vo_sig = vo * 10 ** (-1.0 / 20) / (np.abs(vo).max() + 1e-9)
i0 = int(VO_AT * SR)
mix[:, i0:i0 + len(vo_sig)] += vo_sig * 0.80

# ---------------------------------------------------------------- SFX cues: (time, file, gain_dB, pan, why)
CUES = [
    (6.42, '01_Knocker_Up/KU_snore_cartoon_01.wav', -17, -.2, 'worker snoring (inhale/exhale with the Zzz)'),
    (9.58, '01_Knocker_Up/KU_wake_up_gasp.wav', -12, 0, 'worker jolts awake on the call downbeat'),
    (11.18, '01_Knocker_Up/KU_window_open.wav', -20, -.3, 'first sash window flies open'),
    (12.30, '01_Knocker_Up/KU_reaction_surprised.wav', -18, .3, 'frantic neighbour in window 5'),
    (13.00, '01_Knocker_Up/KU_reaction_annoyed_hmph.wav', -16, .2, 'annoyed neighbour close-up'),
    (14.55, '02_Groom_of_the_Stool/GS_coin_jingle.wav', -18, .25, 'coin lands in palm #1'),
    (14.85, '02_Groom_of_the_Stool/GS_coin_jingle.wav', -19, .25, 'coin lands in palm #2'),
    (15.25, '02_Groom_of_the_Stool/GS_coin_jingle.wav', -18, .25, 'coin lands in palm #3'),
    (15.75, '02_Groom_of_the_Stool/GS_coin_jingle.wav', -17, .25, 'coin lands in palm #4'),
    (17.60, '01_Knocker_Up/KU_footsteps_fast_run.wav', -22, -.2, 'workers hurry to the mill'),
    (25.90, '02_Groom_of_the_Stool/GS_fanfare_tada.wav', -26, .3, 'close-stool lid opens (sparkle sting, tucked under the fanfare)'),
    (27.20, '02_Groom_of_the_Stool/GS_footsteps_royal_chamber.wav', -22, 0, 'groom dances across the chamber'),
    (30.42, '02_Groom_of_the_Stool/GS_coin_shower.wav', -18, 0, 'prestige transformation sparkle'),
    (33.62, '02_Groom_of_the_Stool/GS_crowd_gasp.wav', -20, .2, 'nobles blocked by crossed halberds'),
    (37.15, '02_Groom_of_the_Stool/GS_coin_jingle.wav', -16, 0, 'coin flipped at the camera'),
    (41.90, '03_Sin_Eater/SE_door_creak_wooden.wav', -20, -.4, 'villagers pull back / shutters close'),
    (44.60, '03_Sin_Eater/SE_bread_crunch_bite.wav', -10, 0, 'the bite (layered on the song\'s crunch)'),
    (46.40, '03_Sin_Eater/SE_ghost_gasp.wav', -18, 0, 'symbolic smoke rises from the coffin'),
    (47.20, '03_Sin_Eater/SE_supernatural_accent.wav', -17, 0, 'shadow swells - hit lands on 48.0 downbeat'),
    (49.85, '02_Groom_of_the_Stool/GS_coin_jingle.wav', -19, -.2, 'payment drops into his palm'),
    (52.95, '03_Sin_Eater/SE_crow_caw_02.wav', -20, .4, 'crows cross the moon'),
]
log = []
for tt, f, gdb, pan, why in CUES:
    s, ssr = sf.read(os.path.join(LIB, f), always_2d=True)
    s = s.T
    if ssr != SR:
        s = np.stack([resample_poly(ch, SR, ssr) for ch in s])
    g = 10 ** (gdb / 20)
    gl, gr = np.cos((pan + 1) * np.pi / 4) * np.sqrt(2), np.sin((pan + 1) * np.pi / 4) * np.sqrt(2)
    i = int(tt * SR); n = min(s.shape[1], N - i)
    mix[0, i:i + n] += s[0, :n] * g * gl
    mix[1, i:i + n] += s[1, :n] * g * gr
    log.append(dict(time=tt, file='medieval_v2/SFX_LIBRARY/' + f, gain_db=gdb, pan=pan, visual=why))

# ---------------------------------------------------------------- safety limiter (only touches peaks above -1 dBFS)
pk = np.abs(mix).max(0)
from scipy.ndimage import maximum_filter1d, uniform_filter1d
env = maximum_filter1d(pk, 241)
g = np.minimum(1, 0.89 / np.maximum(env, 1e-9))
g = uniform_filter1d(np.minimum.accumulate(g[::-1])[::-1] * 0 + g, 120)
mix = np.clip(mix * g, -0.98, 0.98)
os.makedirs(os.path.join(HERE, 'audio'), exist_ok=True)
sf.write(os.path.join(HERE, 'audio', 'FINAL_MIX.wav'), mix.T, SR, subtype='PCM_24')
json.dump(dict(narration=dict(time=VO_AT, end=round(vo_end, 3), text='Three of the weirdest jobs in history!', voice='Kokoro am_fenrir', music_duck_db=-4.5),
               sfx=log, note='All musical vocals, chants and the soundtrack itself are unchanged; SFX sit 10-26 dB below the music.'),
          open(os.path.join(HERE, 'SFX_SYNC_MAP.json'), 'w'), indent=1)
print('mix peak dBFS %.2f, gain reduction max %.2f dB' % (20 * np.log10(np.abs(mix).max()), 20 * np.log10(g.min())))
