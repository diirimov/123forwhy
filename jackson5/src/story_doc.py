"""Generates output/STORY_TIMELINE.md from the actual V2 timing constants."""
from pathlib import Path
import timing as T
import v2_home as A, v2_rise as B, v2_fame as C
f = lambda x: f"{int(x // 60)}:{x % 60:05.2f}"
rows = [
 ("FEAR", 0, A.A_SLIP, "Dim living room, night. The brothers rehearse; Michael dances front and centre.", "BEFORE THE FAME…", "Piano glissando"),
 ("FEAR", A.A_SLIP, A.A_DOOR, "Michael misses a step - slips, flails, catches himself.", "", "Glissando peak"),
 ("FEAR", A.A_DOOR, A.A_JOE, "Door opens off-screen: hallway light floods the floor; a man's shadow rises on the wall behind Michael. Everyone freezes.", "", "-12 dB hush begins"),
 ("FEAR", A.A_JOE, A.A_EYES, "Low angle: Joe Jackson framed in the bright doorway, fedora, arms folded, stern.", "", "Band enters (downbeat 1), hushed"),
 ("FEAR", A.A_EYES, A.B_CLAP, "Extreme close-up: Michael's frightened eyes dart to the door and back.", "THERE WAS FEAR.", "Hushed"),
 ("FATHER", A.B_CLAP, A.B_WIDE, "Brothers' POV: Joe claps once (music returns full on the clap), points them back to their marks.", "THEIR FATHER / DEMANDED PERFECTION.", "Downbeat 2 - full volume"),
 ("FATHER", A.B_WIDE, A.B_TIRED, "Over Joe's shoulder (hands clasped behind his back): the five run the routine again in unison.", "(caption continues)", "Downbeat 3"),
 ("FATHER", A.B_TIRED, A.C0, "Final pose on the downbeat, then exhaustion: panting, sweat. Jackie & Marlon glance nervously at their father; his shadow looms on the wall. Michael wipes his brow, sets his jaw, starts again.", "", "Downbeat 4"),
 ("REHEARSALS", A.C_SHOTS[0], A.C_SHOTS[1], "Montage 1: Michael's feet on the floorboards.", "WHILE OTHER KIDS PLAYED…", "Half-bar cuts"),
 ("REHEARSALS", A.C_SHOTS[1], A.C_SHOTS[2], "Montage 2: the wall clock races from 7:36 to 11:00 pm; dancers' shadows on the wallpaper.", "", ""),
 ("REHEARSALS", A.C_SHOTS[2], A.C_SHOTS[3], "Montage 3: the brothers still rehearsing, tired, sweating.", "", ""),
 ("REHEARSALS", A.C_SHOTS[3], A.C_SHOTS[4], "Montage 4: Michael at the window, hand on the glass; outside, kids jump rope and kick a ball at sunset.", "THEY KEPT REHEARSING.", ""),
 ("REHEARSALS", A.C_SHOTS[4], A.C_SHOTS[5], "Montage 5: Joe in the doorway (low angle).", "", ""),
 ("REHEARSALS", A.C_SHOTS[5], A.END, "Montage 6: Michael alone in a pool of lamplight, determined, practising again.", "", ""),
 ("ONE DREAM", B.D_WALK, B.D_SPOT, "Amateur night: the brothers walk on one by one; Joe watches from the wings; Michael glances at him.", "", "Downbeat 7"),
 ("ONE DREAM", B.D_SPOT, B.D_CONF, "The spotlight snaps onto Michael; nervous, he begins to sing.", "", "Downbeat 8"),
 ("ONE DREAM", B.D_CONF, B.D_CROWD, "Confidence: spin, point hit, the whole group locks in.", "THEN THE WORLD / STARTED NOTICING.", "Downbeat 9"),
 ("ONE DREAM", B.D_CROWD, B.E_APOLLO, "Reverse angle: the audience rises. In the wings, Joe gives a small nod.", "", "Downbeat 10"),
 ("BREAKTHROUGH", B.E_APOLLO, B.E_INSIDE, "Harlem at night: APOLLO blade sign, AMATEUR NIGHT - THE JACKSON 5 on the marquee.", "HARLEM, 1967", "Downbeat 11"),
 ("BREAKTHROUGH", B.E_INSIDE, B.E_CONTRACT, "Inside the Apollo's gold proscenium: the brothers perform, the house on its feet.", "", "Downbeat 12"),
 ("BREAKTHROUGH", B.E_CONTRACT, B.E_STUDIO, "Joe signs a recording agreement at the kitchen table; five heads peek round the door.", "1968 — / THE ROAD TO MOTOWN.", "Downbeat 13"),
 ("BREAKTHROUGH", B.E_STUDIO, B.END, "A professional studio: tape reels, VU meters riding the real audio, producers at the console.", "(caption continues)", "Downbeat 14"),
 ("A NEW SOUND", C.F_SING, C.F_DJ, "Close-up: Michael sings at the microphone.", "1969 — / I WANT YOU BACK.", "Downbeat 15"),
 ("A NEW SOUND", C.F_DJ, C.F_CITY, "A radio DJ drops the needle on the record; ON AIR.", "", "Downbeat 16"),
 ("A NEW SOUND", C.F_CITY, C.F_STORE, "Radio waves ripple over the city; silhouettes dance in lit windows.", "", ""),
 ("A NEW SOUND", C.F_STORE, C.F_HOME, "Record-store window fills with the single's sleeves; kids point.", "THEIR FIRST / MOTOWN HIT.", "Downbeat 17"),
 ("A NEW SOUND", C.F_HOME, C.G_TV, "At home the brothers hear themselves on the radio - disbelief, then they jump for joy. Joe, in the doorway, almost smiles.", "(caption continues)", ""),
 ("GLOBAL FAME", C.G_TV, C.G_SIL, "TV stage, op-art backdrop: spin + point hit in unison.", "FIVE BROTHERS.", "Downbeat 19"),
 ("GLOBAL FAME", C.G_SIL, C.G_ARENA, "Silhouettes against the blazing orange disc: arm rolls, kicks.", "", "Downbeat 20"),
 ("GLOBAL FAME", C.G_ARENA, C.G_SOLO, "Arena crane shot: thousands of fans, flashbulbs, sweeping beams; Michael slides.", "ONE WORLDWIDE / SENSATION.", "Downbeat 21"),
 ("GLOBAL FAME", C.G_SOLO, C.H_SMILE, "Closer: kick, spin, point hit - camera shake on the accent.", "", "Downbeat 22"),
 ("PRICE OF FAME", C.H_SMILE, C.H_MIRROR, "On stage, a huge smile; the camera pushes into Michael's face.", "THE WORLD SAW / THEIR SMILES.", "Downbeat 23"),
 ("PRICE OF FAME", C.H_MIRROR, C.H_GOLD, "Match cut, same framing: the boy alone in the rehearsal room, staring at his reflection; pull back to his small figure before the mirror.", "", "-6 dB, cool grade"),
 ("PRICE OF FAME", C.H_GOLD, T.DURATION, "Back on stage: five brothers under golden light, confetti; the camera pulls back as their smiles settle.", "BUT FEW SAW THE / PRESSURE BEHIND THEM.", "Downbeat 25 -> music fade"),
]
L = ["# The Jackson 5 - Story V2: timeline", "",
     f"Music: song {T.SONG_IN:.2f}-{T.SONG_CUT:.3f} s + {T.FADE:.2f} s fade (same analysed section as V1; ~99.4 BPM). "
     f"Film length {T.DURATION:.3f} s, 1080x1920, 60 fps. All times are film time; cuts sit on tracked downbeats or half-bars.", "",
     "Arc: FEAR -> PRESSURE -> HARD WORK -> HOPE -> BREAKTHROUGH -> FAME -> REFLECTION", "",
     "| Time | Chapter | Picture | Caption | Music |", "|---|---|---|---|---|"]
for ch, a, b, pic, cap, mus in rows:
    L.append(f"| {f(a)}-{f(b)} | {ch} | {pic} | {cap} | {mus} |")
L += ["", "## Audio treatment", "",
      "- Recording kept intact (no pitch/tempo change, no filtering).",
      f"- Volume dip -12 dB from {A.A_DOOR + 0.25:.2f} to {A.B_CLAP - 0.12:.2f} s (Joe in the doorway), 120 ms ramps; full band returns on Joe's clap at the {A.B_CLAP:.2f} s downbeat.",
      f"- Volume dip -6 dB from {C.H_MIRROR + 0.05:.2f} to {C.H_GOLD - 0.12:.2f} s (mirror shot).",
      f"- {T.FADE:.2f} s fade-out after the last downbeat.", "",
      "## Historical notes", "",
      "- Gary, Indiana family home; long rehearsals under their father Joe Jackson, who also managed the group.",
      "- Michael Jackson publicly described fear of his father and physical punishment; the film only implies this "
      "(shadow, posture, reactions) and depicts no violence or invented dialogue.",
      "- Joe is shown as demanding and controlling but also ambitious for and proud of his sons (the nod in the wings, the near-smile at the radio).",
      "- Apollo Theater Amateur Night win: 1967. Motown audition/signing: 1968. \"I Want You Back\": first Motown single, released 1969.",
      "- Specific scenes (the slip, the clock, the window, the kitchen-table signing, the radio) are dramatisations, not documented incidents."]
Path(__file__).resolve().parents[1].joinpath('output', 'STORY_TIMELINE.md').write_text('\n'.join(L) + '\n')
print('ok')
