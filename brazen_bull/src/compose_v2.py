"""THE BRAZEN BULL - V2: professional sound-design upgrade.

Same composition as V1 (hook, bass, drums, bouzouki/aulos, structure, 136 BPM, E Phrygian),
with every synthesised scream/roar/choir/chop/breath replaced by the supplied ElevenLabs
recordings, tuned, sliced and processed (samples.py).

Signature motif - the BRONZE BULL ROAR (tuned to E, sub-octave body, bronze resonance):
  * pre-drop tension rise, its explosive burst locked to the power accent (bar 15 beat 4)
  * gated low growl under the first bar of the main drop (follows the bass rhythm)
  * reversed rise into the final drop
  * identity hit + 2-bar gated growl on the final-drop downbeat
  * climax burst before the final silence, low tail under the final impact
"""
import json
import sys
import time
import numpy as np

import compose as C
from compose import (M, T, ev, RNG, HOOK, E1, F1, D2, STEP, BEAT, BAR, SR, N, k_, hats, shaker, darbuka,
                     metal_ticks, clap, snare_roll, tom_fill, davul, bassline, bass_impact, impact, bell, clank,
                     boom, rev_metal, whoosh, riser, chant, responses, brk, silence, play_hook, up_step, KICKS,
                     GROOVE_BASS, DROP_BASS, DARK_BASS, SHAK, CLAP, EVENTS, SILENCES, BREAKS)
from dsp import lp, hp, eq, pan, to_st, fade, softclip, convolve_st, pingpong
import instruments as I
import samples as S
from mixtools import compress

# --------------------------------------------------------------------------------------------
# placement helpers (all events logged with the isolated file they came from)
# --------------------------------------------------------------------------------------------


def put(bus, x, t, onset=0.0, g=1.0, p=None):
    x = to_st(x)
    if p is not None:
        x = pan(x.mean(0), p)
    M.add(bus, x, t - onset, g)


def roar_rise_to(t_burst, g=1.0, name="bull_roar_tension_rise"):
    y, bt = S.roar_signature()
    put("x_roar", y, t_burst, onset=bt, g=g)
    ev(t_burst - bt, "bull_roar_signature", name, burst_time=round(t_burst, 4), sfx_file="roar_signature_E.wav")


def roar_hit(t, g=1.0, name="bull_roar_identity_hit"):
    y, pre = S.roar_burst()
    put("x_roar", y, t, onset=pre, g=g)
    ev(t, "bull_roar_signature", name, sfx_file="roar_burst.wav")


def roar_growl(bar, n_bars=1, g=1.0):
    y = S.roar_bass_texture(n_bars, steps=tuple(s for s, *_ in DROP_BASS))
    put("x_roar_tex", y, T(bar, 0), g=g)
    ev(T(bar, 0), "bull_roar_signature", "roar_gated_bass_growl", bars=n_bars, end=round(T(bar + n_bars, 0), 4),
       sfx_file=f"roar_bass_texture_{n_bars}bar.wav")


def roar_reverse_into(t_end, length, g=1.0):
    y = S.roar_reverse(length)
    put("x_roar", y, t_end - y.shape[1] / SR, g=g)
    ev(t_end - length, "bull_roar_signature", "roar_reverse_rise", end=round(t_end, 4), sfx_file="roar_reverse_rise.wav")


def wail_answer(bar, step, g=1.0, p=0.25, stretch=0.5, semis=3.0):
    y = S.wail_answer(semis, stretch)
    put("wail", y, T(bar, step), g=g, p=p)
    ev(T(bar, step), "ritual_wail", "wail_answer_F5_to_E5", sfx_file=f"wail_answer_{semis:+.0f}st.wav",
       duration=round(y.shape[1] / SR, 3))


def wail_choir(bar, step, notes, g=1.0, len_s=0.75):
    y = S.wail_choir(list(notes), len_s)
    put("wail", y, T(bar, step), g=g)
    ev(T(bar, step), "choir_accent", "ritual_wail_choir", notes=list(notes),
       sfx_file="wail_choir_" + "_".join(str(n) for n in notes) + ".wav")


def wail_chops(bar, pat, g=1.0, octave=12):
    for (st, m, ln, v) in HOOK[pat]:
        if v >= 0.95:
            y = S.wail_chop(m + octave, min(ln, 1.5))
            put("wail", y, T(bar, st), g=g * v, p=float(RNG.uniform(-0.45, 0.45)))
    ev(T(bar, 0), "vocal_chop", f"wail_chops_{pat}", bar=bar)


def shriek(t, kind="distant", g=1.0, p=0.0, name=None):
    y = S.shriek(kind)
    put("x_hor", y, t, g=g, p=p)
    ev(t, "horror_shriek", name or f"shriek_{kind}", sfx_file=f"shriek_{kind}.wav")


def shriek_stutter(bar, step, reps=3, g=1.0):
    y = S.shriek("stutter")
    for k in range(reps):
        put("x_hor", y, T(bar, step + k), g=g * 0.88 ** k, p=(-0.55, 0.55, 0.0)[k % 3])
    ev(T(bar, step), "horror_shriek", "shriek_stutter_chop", repeats=reps, sfx_file="shriek_stutter.wav")


def shriek_reverse_into(t_end, length, g=1.0):
    y = S.shriek_reverse(length)
    put("x_hor", y, t_end - y.shape[1] / SR, g=g)
    ev(t_end - length, "horror_shriek", "shriek_reverse_rise", end=round(t_end, 4), sfx_file="shriek_reverse_rise.wav")


def door(t, g=1.0, name="bronze_door_slam"):
    y, on = S.door()
    put("x_sfx", y, t, onset=on, g=g)
    ev(t, "structural_sfx", name, sfx_file="bronze_door_slam.wav")


def impact_s(t, g=1.0, semis=0.0, name="bronze_impact"):
    y, on = S.impact_sample(semis)
    put("x_sfx", y, t, onset=on, g=g)
    ev(t, "metallic_impact", name, sfx_file=f"bronze_impact{'' if not semis else f'_{semis:+.0f}st'}.wav")


def fire_ignite(t, g=1.0, name="fire_ignition"):
    y, on = S.fire()
    put("x_sfx", y, t, onset=on, g=g)
    ev(t, "structural_sfx", name, sfx_file="fire_ignition.wav")


def scan(t, g=1.0, name="anatomical_scan"):
    y, on = S.scan()
    put("x_sfx", y, t, onset=on, g=g)
    ev(t, "transition_sfx", name, sfx_file="anatomical_scan.wav")


def heart(bar, step, i, g=1.0):
    y, on = S.heart_unit(i)
    put("x_heart", y, T(bar, step), onset=on, g=g)
    ev(T(bar, step), "heartbeat", "lub_dub", sfx_file="heartbeat_unit.wav")


# --------------------------------------------------------------------------------------------
# ARRANGEMENT V2
# --------------------------------------------------------------------------------------------
def arrange_v2():
    N_ = N
    fire_bed = I.fire_bed(N_, seed=11)
    fire_lvl = np.interp(np.arange(N_) / SR, [0, 3.5, 14, 24.7, 26.4, 40.6, 41, 47.6, 58.2, 60],
                         [0.55, 0.35, 0.3, 0.45, 0.7, 0.35, 0.85, 0.9, 0.4, 0.6])
    M.bus("fire")[:] += fire_bed * fire_lvl * 0.5
    drone = I.drone_resonance(N_, root=E1, seed=5)
    dlev = np.interp(np.arange(N_) / SR, [0, 3.5, 4, 24.7, 26.4, 26.5, 40.6, 47.0, 47.6, 58.2, 60],
                     [0.6, 0.6, 0.15, 0.3, 0.8, 0.12, 0.85, 0.9, 0.15, 0.4, 0.6])
    M.bus("drone")[:] += drone * dlev * 0.45

    # ================= INTRO (bars 0-1) =================
    impact_s(0.0, 0.9, name="opening_bronze_impact")
    bell(0.0, 329.63, g=0.6, name="opening_bell")
    for b in (0, 1):
        for s in (0, 4, 8, 12):
            k_(b, s, g=0.95 if s == 0 else 0.75, kind="filt")
        shaker(b, 0.55)
        hats(b, 0.35, closed=True, open_=False)
    k_(1, 14, 0.6, kind="filt")
    play_hook(0, "A", ["bzi"], gains={"bzi": 0.9}, tag="teaser")
    play_hook(1, "C", ["bzi", "aul"], gains={"bzi": 0.85, "aul": 0.3}, tag="teaser")
    wail_answer(1, 13, g=0.3, p=0.35)                 # first call-and-response, distant
    clank(T(1, 6), 740, 0.6, 0.4)
    shriek_reverse_into(T(2, 0), BEAT * 2, g=0.13)
    whoosh(T(2, 0), BEAT * 2, up=True)

    # ================= GROOVE (bars 2-7) =================
    gpats = ["A", "B", "C", "D", "A", "B"]
    for i, b in enumerate(range(2, 8)):
        for s in (0, 4, 8, 12):
            k_(b, s, 0.95 if s == 0 else 0.88)
        hats(b, 0.55 + 0.08 * i, closed=True, open_=i >= 1)
        shaker(b, 0.6 + 0.04 * i)
        darbuka(b, 0.8, busy=0 if i < 3 else 1)
        if i >= 2:
            clap(b, 0.75 + 0.05 * i)
        if i >= 3:
            metal_ticks(b, 0.6)
        root = [E1, E1, F1, E1, E1, E1][i]
        bassline(b, root, GROOVE_BASS, "groove", 0.8 + 0.03 * i)
        layers = ["bz", "pl"] + (["aul"] if i >= 2 else [])
        play_hook(b, gpats[i], layers, gains={"bz": 0.8, "pl": 0.55, "aul": 0.55})
        if gpats[i] == "B":
            wail_answer(b, 14, g=0.75, p=0.3 if i < 3 else -0.3)
        else:
            responses(b, gpats[i], size=5 + i // 2, g=0.75)
    bass_impact(T(2, 0), E1, 0.8, 0.8)
    door(T(2, 0), 0.85, name="groove_entry_door_slam")
    clank(T(4, 0), 659.25, 0.7, -0.3)
    scan(T(6, 0), 0.8, name="scan_groove_second_half")
    tom_fill(7, (12, 13, 14, 15), 0.9)
    whoosh(T(8, 0), BEAT, up=True)

    # ================= ESCALATION (bars 8-13) =================
    epats = ["A", "B", "V", "C", "A", "D"]
    fire_ignite(T(8, 0), 0.8, name="fire_ignition_escalation")
    for i, b in enumerate(range(8, 14)):
        until = 12 if b == 9 else (14 if b == 11 else 16)
        for s in (0, 4, 8, 12):
            if s < until:
                k_(b, s, 1.0 if s == 0 else 0.94)
        hats(b, 0.95)
        shaker(b, 0.8)
        darbuka(b, 1.0, busy=1 if i < 4 else 2)
        clap(b, 1.0)
        metal_ticks(b, 0.85, dense=i >= 3)
        davul(b, [7, 10] if i % 2 == 0 else [3, 10], 0.75)
        root = [E1, E1, F1, E1, E1, D2 - 12][i]
        bassline(b, root, GROOVE_BASS if i < 3 else DROP_BASS, "groove", 1.0, until=until)
        lay = ["bz", "pl", "aul"] + (["aul8"] if i in (2, 4) else [])
        play_hook(b, epats[i], lay, gains={"bz": 0.9, "pl": 0.55, "aul": 0.7, "aul8": 0.35})
        if i >= 3:
            wail_chops(b, epats[i], g=0.3)
        if b not in (9, 11):
            responses(b, epats[i], size=8, g=0.78)
    pad = I.dark_pad([40, 47, 52], 6 * BAR + 0.5, seed=3)
    M.add("pad", pad, T(8, 0), 0.22)
    brk(T(9, 12), T(10, 0))
    chant(9, 12, "HO", size=10, g=1.0, effort=1.1)
    door(T(9, 12), 0.9, name="break_door_slam")
    whoosh(T(10, 0), BEAT, up=True, g=0.8)
    brk(T(11, 14), T(12, 0))
    shriek(T(11, 14), "distant", g=0.7, p=0.45, name="shriek_break")
    clank(T(11, 14), 987.77, 0.6, -0.4)
    scan(T(12, 0), 0.8, name="scan_after_break")
    snare_roll(13, 8, 0.9, density=(1, 1, 0.5))
    riser(T(15, 0), BAR * 2)
    tom_fill(13, (14, 14.5, 15, 15.5), 0.7)

    # ================= PRE-DROP (bar 14) =================
    b = 14
    impact(T(b, 0), size=0.75, name="predrop_impact")
    bass_impact(T(b, 0), E1, 1.3, 1.0)
    for (st, m, ln, v) in HOOK["A"][:5]:
        M.add("bz", lp(I.bouzouki(m, ln * STEP * 0.9, v, seed=int(RNG.integers(1e9))), 1800), T(b, st), 0.7 * v, 0.0)
    for s in range(0, 12, 2):
        M.add("perc", SHAK[s % 4], T(b, s), 0.2)
    # SIGNATURE 1: the roar swells out of the escalation, its burst lands on the power accent
    roar_rise_to(T(b, 12), g=0.3, name="roar_predrop_tension_burst")
    rev_metal(T(b, 12), length=BEAT * 1.6, g=0.9)
    shriek_reverse_into(T(b, 12), BEAT * 1.5, g=0.16)
    chant(b, 12, "HEY", size=12, g=1.2, effort=1.2, fifth=0.3, cat="power_vocal_accent")
    wail_choir(b, 12, (52, 59, 64, 71), g=0.6, len_s=0.5)
    silence(T(b, 14.25), T(15, 0))

    # ================= MAIN DROP (bars 15-22) =================
    dpats = ["A", "B", "C", "D", "A", "B", "C", "Ds"]
    roots = [E1, E1, F1, D2 - 12, E1, E1, F1, D2 - 12]
    for i, b in enumerate(range(15, 23)):
        until = 12 if b == 18 else 16
        for s in (0, 4, 8, 12):
            if s < until:
                k_(b, s, 1.0)
        hats(b, 1.0)
        shaker(b, 0.85)
        darbuka(b, 1.05, busy=2 if i >= 4 else 1)
        clap(b, 1.05)
        metal_ticks(b, 1.0, dense=True)
        davul(b, [7, 10], 0.8)
        bassline(b, roots[i], DROP_BASS, "drop", 1.05, until=until)
        lay = ["bz", "pl", "aul"] + (["ss"] if i >= 4 else [])
        play_hook(b, dpats[i], lay, gains={"bz": 1.0, "pl": 0.75, "aul": 0.75, "ss": 0.55})
        if i >= 4:
            wail_chops(b, dpats[i], g=0.4)
        if dpats[i] == "B":
            wail_answer(b, 14, g=0.9, p=(0.3, -0.3)[i // 4])
        elif b != 18:
            responses(b, dpats[i], size=9, g=1.0)
    impact_s(T(15, 0), 1.0, name="drop1_bronze_impact")
    fire_ignite(T(15, 0), 0.6, name="fire_ignition_drop1")
    bass_impact(T(15, 0), E1, 1.0, 1.0)
    boom(T(15, 0), 0.7)
    roar_growl(15, 1, g=1.0)                          # SIGNATURE 2: roar as gated bass texture
    wail_choir(15, 0, (52, 59, 64), g=0.75)
    brk(T(18, 12), T(19, 0))
    door(T(18, 12), 1.0, name="break_door_slam_drop1")
    chant(18, 14, "HO", size=10, g=0.95)
    impact(T(19, 0), size=0.8, name="drop1_half_impact")
    scan(T(19, 0), 0.85, name="scan_drop1_second_half")
    wail_choir(19, 0, (52, 59, 64), g=0.65)
    clank(T(17, 0), 659.25, 0.8, 0.4)
    clank(T(21, 0), 740, 0.8, -0.4)
    whoosh(T(23, 0), BEAT, up=True)
    tom_fill(22, (14, 14.5, 15, 15.5), 0.6)

    # ================= DARK BREAKDOWN (bars 23-26) =================
    door(T(23, 0), 1.0, name="breakdown_door_slam")
    impact_s(T(23, 0), 0.8, semis=-3.0, name="breakdown_deep_bronze_impact")
    bell(T(23, 0), 164.81, 0.7, name="breakdown_deep_bell")
    whoosh(T(23, 0), BEAT * 2, up=False)
    hb = [(23, 0), (23, 8), (24, 0), (24, 8), (25, 0), (25, 4), (25, 8), (25, 12),
          (26, 0), (26, 4), (26, 8), (26, 10), (26, 12)]
    for k, (b, s) in enumerate(hb):
        heart(b, s, k, g=1.0)
    for b in range(23, 27):
        shaker(b, 0.55)
        hats(b, 0.4, closed=True, open_=(b >= 25))
        darbuka(b, 0.5, busy=0)
        bassline(b, E1, DARK_BASS, "dark", 0.75, until=14 if b == 26 else 16)
        metal_ticks(b, 0.45)
    for b0, pat in ((23, "A"), (25, "C")):
        for (st, m, ln, v) in HOOK[pat]:
            s2 = st * 2
            t = T(b0 + int(s2 // 16), s2 % 16)
            dur = ln * 2 * STEP * 0.95
            M.add("aul", I.aulos(m - 12, dur, v, seed=int(RNG.integers(1e9)), grace=up_step(m - 12) if ln >= 2 else None),
                  t, 0.85 * v, 0.1)
            if ln >= 2:
                M.add("bz", I.bouzouki(m, dur, v * 0.7, seed=int(RNG.integers(1e9)), tremolo=True), t, 0.45, -0.3)
            if v >= 0.95:
                ev(t, "melodic_accent", f"breakdown_{pat}", midi=int(m - 12))
        ev(T(b0, 0), "hook_phrase", f"breakdown_halftime_{pat}", bar=b0)
    # the wail transformed: slowed + lowered ritual voice under the half-time hook, then it answers
    wd = S.wail_dark(-9.0, 1.45)
    put("wail", fade(wd[:, : int(BAR * 2.9 * SR)], 0.3, 0.8), T(23, 2), g=0.45)
    ev(T(23, 2), "ritual_wail", "wail_dark_transformed", sfx_file="wail_dark_breakdown.wav")
    wail_answer(24, 12, g=0.24, p=-0.35)
    shriek(T(25, 8), "low", g=0.55, p=0.55, name="ghost_shriek_breakdown")
    for s in (0, 4, 8, 10, 12):
        chant(26, s, "HA", size=7, g=0.75 + 0.03 * s)
    snare_roll(26, 0, 0.95, density=(2, 1, 0.5))
    for s in (8, 10, 12, 13):
        k_(26, s, 0.75)
    riser(T(26, 14), BAR * 1.75)
    roar_reverse_into(T(26, 14), BAR * 1.25, g=0.95)   # SIGNATURE 3: reversed roar peaks into the silence
    silence(T(26, 14), T(27, 0))

    # ================= FINAL DROP (bars 27-32) =================
    fpats = ["A", "B", "C", "S", "H1", "H2"]
    roots = [E1, E1, F1, D2 - 12, E1, F1]
    for i, b in enumerate(range(27, 33)):
        until = 12 if b == 32 else 16
        for s in (0, 4, 8, 12):
            if s < until:
                k_(b, s, 1.0)
        hats(b, 1.05, steps=range(until))
        shaker(b, 0.95, steps=range(until))
        darbuka(b, 1.1, busy=2)
        if until == 16:
            clap(b, 1.1)
        else:
            M.add("perc", CLAP[0], T(b, 4), 0.68)
        metal_ticks(b, 1.1, dense=True)
        davul(b, [3, 7, 10] if i % 2 else [7, 10, 11], 0.9)
        bassline(b, roots[i], DROP_BASS, "final", 1.1, until=until)
        lay = ["bz", "bzlow", "pl", "aul", "aul8", "ss"]
        play_hook(b, fpats[i], lay, gains={"bz": 1.0, "bzlow": 0.45, "pl": 0.8, "aul": 0.75, "aul8": 0.35,
                                           "ss": 0.65}, tag="final")
        wail_chops(b, fpats[i], g=0.45)
        if fpats[i] == "B":
            wail_answer(b, 14, g=1.0, p=0.0)
        else:
            responses(b, fpats[i], size=12, g=1.1)
    impact_s(T(27, 0), 1.0, name="final_drop_bronze_impact")
    bell(T(27, 0), 329.63, 0.5)
    bass_impact(T(27, 0), E1, 1.2, 1.1)
    boom(T(27, 0), 0.5)
    roar_hit(T(27, 0), g=2.1, name="roar_final_drop_identity_hit")     # SIGNATURE 4
    roar_growl(27, 2, g=1.0)
    wail_choir(27, 0, (40, 52, 59, 64), g=0.65)
    wail_choir(29, 0, (41, 53, 60, 65), g=0.7)
    wail_choir(31, 0, (40, 52, 56, 64), g=0.8)        # E major colour (G#) for the Hijaz turn
    clank(T(29, 0), 659.25, 0.9, 0.35)
    shriek_stutter(29, 6, reps=3, g=0.8)
    impact(T(31, 0), size=0.8, name="hijaz_turn_impact")
    scan(T(31, 0), 0.85, name="scan_hijaz_turn")
    for b in (28, 30):
        tom_fill(b, (12, 13, 14, 15), 0.8)
    roar_hit(T(32, 12), g=1.0, name="roar_climax_burst")             # SIGNATURE 5
    shriek(T(32, 12) + 0.02, "climax", g=0.55, p=0.5, name="climax_shriek")
    chant(32, 12, "HEY", size=14, g=1.2, effort=1.25, fifth=0.3, cat="power_vocal_accent")
    rev_metal(T(32, 12), BEAT * 1.4, g=0.8)
    silence(T(32, 14.75), T(33, 0))

    # ================= FINAL IMPACT / LOOP LINK (bar 33) =================
    b = 33
    impact_s(T(b, 0), 1.0, name="final_bronze_impact")
    impact(T(b, 0), size=0.9, nominal=164.81, name="final_metallic_layer")
    bell(T(b, 0), 329.63, 0.9, name="final_bell")
    bass_impact(T(b, 0), E1, 1.6, 1.1)
    k_(b, 0, 1.0, kind="long")
    y = S.roar_low_tail(1.6)
    put("x_roar", y, T(b, 0) + 0.02, g=1.0)
    ev(T(b, 0), "bull_roar_signature", "roar_low_tail_ending", sfx_file="roar_low_tail_ending.wav")
    chant(b, 0, "HO", size=14, g=1.15, effort=1.2, cat="power_vocal_accent")
    wail_choir(b, 0, (40, 52, 59, 64), g=0.8, len_s=1.2)
    for s in (4, 8, 12):
        k_(b, s, 0.85, kind="filt")
    shaker(b, 0.5, steps=range(4, 16))
    for (st, m, ln, v) in HOOK["A"][:5]:
        if st >= 3:
            M.add("bz", I.bouzouki(m, ln * STEP * 0.9, v, seed=int(RNG.integers(1e9))), T(b, st + 4), 0.5 * v, 0.0)
    ev(T(b, 7), "hook_phrase", "loop_teaser", bar=b)
    rev_metal(60.0, BEAT * 2.2, g=0.85)
    whoosh(60.0, BEAT, up=True, g=0.7)


# --------------------------------------------------------------------------------------------
# MIX EXTENSION for the sample buses
# --------------------------------------------------------------------------------------------
LV = dict(x_roar=2.5, x_roar_tex=0.95, wail=1.25, x_hor=1.4, x_sfx=0.6, x_heart=0.8)


def extra(B, P):
    for k in ("x_roar", "x_roar_tex", "wail", "x_hor", "x_sfx", "x_heart"):
        M.bus(k)
    out = {}
    r, _ = compress(B["x_roar"], thr=-18, ratio=3, att=0.004, rel=0.12, knee=6)
    r = eq(r, "peak", 2400, 1.0, 1.5)
    out["x_roar"] = r * LV["x_roar"]
    tx = B["x_roar_tex"].mean(0)
    out["x_roar_tex"] = to_st(lp(tx, 900, 2)) * P["kick"] * LV["x_roar_tex"]
    w = hp(B["wail"], 200, 2)
    w = eq(w, "peak", 380, 1.0, -2.0)
    w = eq(w, "highshelf", 9500, 0.7, -2.0)
    w, _ = compress(w, thr=-20, ratio=3, att=0.004, rel=0.1, knee=6, makeup=2)
    w = w * P["lead"] * LV["wail"]
    out["wail"] = w
    h = hp(B["x_hor"], 300, 2) * LV["x_hor"]
    sfx = B["x_sfx"] * LV["x_sfx"]
    out["x_sfx"] = sfx
    out["x_heart"] = lp(B["x_heart"], 5000) * LV["x_heart"]
    out["x_wail_plate"] = hp(convolve_st(0.35 * w, C.PLATE), 250) * 0.5
    out["x_hall"] = hp(convolve_st(0.3 * w + 0.15 * out["x_roar"] + 0.12 * sfx, C.HALL), 200) * 0.5
    out["x_wail_dly"] = pingpong(w, STEP * 3, 0.4, n_taps=5, lp_f=5000, hp_f=400) * 0.22
    out["x_hor_dark"] = hp(convolve_st(h, C.DARK_HALL), 200) * 0.6
    out["x_hor_dly"] = pingpong(h, STEP * 3, 0.45, n_taps=6, lp_f=4000, hp_f=500) * 0.3
    out["x_hor"] = h * 0.65
    return out


C.SECTIONS = [
    ("intro_opening_hook", 0, 2, "Bronze impact + bell, filtered pulse, hook teaser on dark bouzouki answered by the distant ritual wail; voice-over space"),
    ("first_groove", 2, 8, "Door slam entry, kick, rolling bass, darbuka, hook; HEY/HA chants and the wail answering every B phrase"),
    ("escalation", 8, 14, "Fire ignition, gang chants, wail vocal chops, hook variation, door-slam and shriek breaks, crescendo; the roar starts swelling at the end"),
    ("pre_drop", 14, 15, "Bull roar tension rise -> burst on the power HEY, reverse metal + reverse shriek, wail choir, hard silence"),
    ("main_drop", 15, 23, "Bronze impact + fire, roar gated bass growl, full hook stack, wail answers/chops/choir; door-slam break before bar 20"),
    ("dark_breakdown", 23, 27, "Door slam, recorded heartbeat accelerating, half-time low aulos hook, slowed/lowered ritual wail, ghost shriek, HA build, reversed roar into silence"),
    ("final_drop", 27, 33, "Roar identity hit + 2-bar roar growl, strongest hook, shriek stutter, Phrygian-dominant (G#) twist with scan, roar climax burst"),
    ("final_impact_loop", 33, 34, "Bronze impact + roar low tail + HO + wail choir, teaser returns, reverse metal swell into 0:00 for seamless replay"),
]


if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    t0 = time.time()
    arrange_v2()
    print(f"arranged in {time.time() - t0:.1f}s, events={len(EVENTS)}", flush=True)
    mixed, stems = C.mix(extra=extra)
    print(f"mixed in {time.time() - t0:.1f}s", flush=True)
    np.save(f"{out_dir}/premaster.npy", mixed.astype(np.float32))
    for k in ("x_roar", "x_roar_tex", "wail", "x_hor", "x_sfx", "x_heart", "vox", "bz", "kick", "sub", "bmid",
              "x_hor_dark", "x_hall"):
        np.save(f"{out_dir}/stem_{k}.npy", stems[k].astype(np.float32))
    y, info = C.master(mixed)
    print("master:", info, flush=True)
    C.write_wav24(f"{out_dir}/BRAZEN_BULL_FINAL_V2.wav", y)
    ver = C.build_beatmap(y, info, f"{out_dir}/BRAZEN_BULL_BEATMAP_V2.json")
    iso_dir = f"{out_dir}/sfx_isolated_v2"
    names = S.export_isolated(iso_dir)
    bm = json.load(open(f"{out_dir}/BRAZEN_BULL_BEATMAP_V2.json"))
    bm["track"]["file"] = "BRAZEN_BULL_FINAL_V2.wav"
    bm["track"]["version"] = "V2 - ElevenLabs sound-design upgrade"
    bm["isolated_sfx"] = dict(folder="sfx_isolated_v2", format="48 kHz / 24-bit stereo WAV, peak -1 dBFS",
                              files=[n + ".wav" for n in names],
                              note="Clean processed one-shots exactly as used in the mix (before reverb/delay sends). "
                                   "Each event in 'events' that used one carries 'sfx_file'.")
    bm["signature_motif"] = dict(name="bronze bull roar", key="tuned G#3 -> E3 (+ E2 sub-body)",
                                 moments=[e for e in bm["events"].get("bull_roar_signature", [])])
    json.dump(bm, open(f"{out_dir}/BRAZEN_BULL_BEATMAP_V2.json", "w"), indent=1)
    print("beatmap verification:", ver["detected_onset_offset_ms"], "isolated:", len(names))
    print(f"done in {time.time() - t0:.1f}s")
