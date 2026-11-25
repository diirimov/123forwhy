"""THE BRAZEN BULL - V3: vocal upgrade only.

Identical to V2 (music, bull roar, wail, horror FX, structure, mix, master) except that every
synthesised male chant ("HA" / "HEY" / "HO", gang shouts, power accents) is replaced by the supplied
ElevenLabs expressive ethnic male vocal, used as a melodic, rhythmic call-and-response hook.

Vocal hook (answers the instrumental hook an octave below, like a cantor):
  A bar  -> step 14: second syllable on G3 (rises naturally towards G#)
  C bar  -> step 14: second syllable on B3 (higher answer)
  V bar  -> step 14: syllable on A3
  D bar  -> steps 10, 12: short E3 attacks, step 14: the falling sigh from G3  (signature vocal phrase)
  S bar  -> 3-step cross-rhythm attacks E3/G3/E3/G3, then B3 syllable
  H1 bar -> the voice's own G -> G# rise (Phrygian-dominant turn)
Accents: pre-drop and climax power accents = doubled B3 syllable; breaks and the ending = falling sigh;
breakdown build = rising attacks E3-F3-G3-A3-B3.
Pitch is moved per slice only (formant-preserving, a few cents of random human variance); no pitch
correction, no distortion.
"""
import json
import sys
import time
import numpy as np

import compose as C
import compose_v2 as V2
from compose import T, ev, RNG, SR, STEP, EVENTS
from dsp import hp, eq, lp, to_st, convolve_st, pingpong
import samples as S
from mixtools import compress

VRNG = np.random.default_rng(303)   # vocal-only randomness (keeps the V2 random stream untouched)

VOX_RESP = {
    "A": [(14, "syl", 55, 0.55)],
    "C": [(14, "syl", 59, 0.55)],
    "V": [(14, "syl", 57, 0.55)],
    "D": [(10, "att", 52, 0.2), (12, "att", 52, 0.2), (14, "fall", 55, None)],
    "Ds": [(10, "att", 52, 0.2)],
    "S": [(2, "att", 52, 0.2), (5, "att", 55, 0.2), (8, "att", 52, 0.2), (11, "att", 55, 0.2), (14, "syl", 59, 0.55)],
    "H1": [(14, "rise", 55, 0.9)],
    "H2": [],
}


def voc(bar, step, kind, midi, len_s, g=1.0, double=False, p=None, name=None, cat="ethnic_vocal"):
    t = T(bar, step)
    cents = float(VRNG.choice([-7.0, -3.0, 0.0, 4.0, 8.0]))
    y = S.vox_slice(kind, midi, len_s, cents)
    pan_ = float(VRNG.uniform(-0.18, 0.18)) if p is None else p
    V2.put("vox3", y, t + float(VRNG.normal(0, 0.003)), g=g, p=pan_)
    if double:   # natural double-track: second take, other slice variance, slightly late, opposite side
        y2 = S.vox_slice(kind, midi, len_s, -cents * 0.8 + 3.0)
        V2.put("vox3", y2, t + 0.017, g=g * 0.5, p=-pan_ - 0.35)
        V2.put("vox3", y2, t + 0.009, g=g * 0.4, p=-pan_ + 0.35)
    ev(t, cat, name or f"vocal_{kind}_{['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'][midi % 12]}{midi // 12 - 1}",
       slice=kind, midi=midi, sfx_file=f"ethnic_vocal_{kind}_{midi}.wav")


def responses_v3(bar, pat, size=8, g=1.0):
    for _ in C.RESP.get(pat, []):      # consume the same draws the V2 gang chants did
        RNG.integers(1e9)
    for st, kind, m, ln in VOX_RESP.get(pat, []):
        voc(bar, st, kind, m, ln, g=g * (1.0 if kind != "att" else 0.9), double=size >= 12)


BUILD_PITCH = {0: 52, 4: 53, 8: 55, 10: 57, 12: 59}


def chant_v3(bar, step, name, size=8, g=1.0, effort=1.0, f0=None, fifth=0.0, cat="male_chant"):
    RNG.integers(1e9)                  # same draw the V2 gang chant consumed
    power = cat == "power_vocal_accent"
    if bar == 26 and name == "HA":                      # breakdown build: rising attacks
        voc(bar, step, "att", BUILD_PITCH.get(step, 52), 0.2, g=1.35 * g, name="vocal_build_attack")
    elif name == "HEY":                                 # power accent: doubled high syllable
        voc(bar, step, "syl", 59, 0.45, g=1.1 * g, double=True, name="vocal_power_accent", cat="power_vocal_accent")
    elif name == "HO" and bar == 33:                    # ending: long falling sigh into the loop
        voc(bar, step, "fall", 52, None, g=1.6 * g, double=True, name="vocal_final_sigh", cat="power_vocal_accent")
    elif name == "HO":                                  # breaks: falling sigh
        voc(bar, step, "fall", 52, 0.75, g=g, double=power, name="vocal_break_sigh")
    else:
        voc(bar, step, "att", 52, 0.2, g=g)


# swap ONLY the vocal functions used by the V2 arrangement
V2.responses = responses_v3
V2.chant = chant_v3

LV3 = dict(vox3=1.0)


def extra_v3(B, P):
    out = V2.extra(B, P)
    C.M.bus("vox3")
    v = hp(B["vox3"], 90, 2)
    v = eq(v, "peak", 300, 1.0, -1.5)
    v = eq(v, "peak", 2800, 0.9, 2.0)
    v = eq(v, "highshelf", 10000, 0.7, -1.5)
    v, _ = compress(v, thr=-20, ratio=2.5, att=0.006, rel=0.12, knee=8, makeup=2)
    v = v * (0.75 + 0.25 * P["lead"]) * LV3["vox3"]
    out["vox3"] = v
    out["x_vox3_plate"] = hp(convolve_st(0.28 * v, C.PLATE), 250) * 0.5
    out["x_vox3_room"] = hp(convolve_st(0.25 * v, C.ROOM), 150) * 0.45
    out["x_vox3_dly"] = pingpong(v, STEP * 3, 0.35, n_taps=4, lp_f=4500, hp_f=300) * 0.14
    return out


C.SECTIONS = [(n, a, b, d.replace("HEY/HA chants", "ethnic-vocal answers").replace("gang chants", "ethnic-vocal call-and-response")
               .replace("power HEY", "doubled vocal power accent").replace("HA build", "rising vocal build")
               .replace("+ HO +", "+ falling vocal sigh +")) for n, a, b, d in V2.C.SECTIONS]


if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    t0 = time.time()
    V2.arrange_v2()
    print(f"arranged in {time.time() - t0:.1f}s, events={len(EVENTS)}", flush=True)
    mixed, stems = C.mix(extra=extra_v3)
    np.save(f"{out_dir}/premaster.npy", mixed.astype(np.float32))
    for k in ("vox3", "vox", "wail", "bz", "x_roar", "x_hor"):
        np.save(f"{out_dir}/stem_{k}.npy", stems[k].astype(np.float32))
    print("synthetic chant bus energy (must be 0):", float(np.abs(stems["vox"]).max()))
    y, info = C.master(mixed)
    print("master:", info, flush=True)
    C.write_wav24(f"{out_dir}/BRAZEN_BULL_FINAL_V3.wav", y)
    bm_path = f"{out_dir}/BRAZEN_BULL_BEATMAP_V3.json"
    ver = C.build_beatmap(y, info, bm_path)
    names = S.export_isolated(f"{out_dir}/sfx_isolated_v3")
    bm = json.load(open(bm_path))
    bm["track"]["file"] = "BRAZEN_BULL_FINAL_V3.wav"
    bm["track"]["version"] = "V3 - ethnic male vocal hook replaces all synthesised chants"
    bm["isolated_sfx"] = dict(folder="sfx_isolated_v3", format="48 kHz / 24-bit stereo WAV, peak -1 dBFS",
                              files=[n + ".wav" for n in names],
                              note="Clean processed one-shots as used in the mix (before reverb/delay sends).")
    bm["signature_motif"] = dict(name="bronze bull roar", key="tuned G#3 -> E3 (+ E2 sub-body)",
                                 moments=bm["events"].get("bull_roar_signature", []))
    bm["vocal_hook"] = dict(source="An_expressive_haunt_2.wav (ElevenLabs)", slices={k: dict(start=v[0], end=v[1], description=v[3]) for k, v in S.VOX_SLICES.items()},
                            response_map=VOX_RESP,
                            events=bm["events"].get("ethnic_vocal", []) + bm["events"].get("power_vocal_accent", []))
    json.dump(bm, open(bm_path, "w"), indent=1)
    print("beatmap verification:", ver["detected_onset_offset_ms"], "isolated:", len(names))
    print(f"done in {time.time() - t0:.1f}s")
