"""Generates output/JACKSON5_V3_STORYBOARD.md from the actual V3 timing constants."""
from pathlib import Path
import timing as T
import v3_open as A, v3_mid as B, v3_end as C
f = lambda x: f"{int(x // 60)}:{x % 60:05.2f}"
rows = [
 ("HOOK", A.H_FACE, A.H_FEET, "NEW", "Close-up: young Michael's nervous face, eyes sliding to the doorway.", ""),
 ("HOOK", A.H_FEET, A.H_JOE, "NEW", "His shoes stop moving; a long shadow slides across the floorboards and swallows them.", ""),
 ("HOOK", A.H_JOE, A.H_FLASH, "NEW (V2 set)", "Low angle: Joe in the bright doorway gestures - keep going.", "HE MADE THEM STARS..."),
 ("HOOK", A.H_FLASH, A.H_BACK, "NEW", "Graphic match cut (same eye-line): the same face years later, grown, under a stadium's worth of light.", "(caption continues)"),
 ("HOOK", A.H_BACK, A.H_RESUME, "NEW", "Back to the frightened child.", "BUT AT WHAT COST?"),
 ("HOOK", A.H_RESUME, A.P_POV, "NEW", "He dances again, stiffly; his father's shadow on the wall behind the brothers.", "(caption continues)"),
 ("PRESSURE", A.P_POV, A.P_OVER, "V2 reuse", "Brothers' POV: Joe claps and points them back to their marks.", "THEIR CHILDHOOD WAS / FILLED WITH REHEARSALS."),
 ("PRESSURE", A.P_OVER, A.P_TIRED, "V2 reuse", "Over Joe's shoulder: the routine again, in unison.", ""),
 ("PRESSURE", A.P_TIRED, A.P_CLOCK, "V2 reuse", "Exhaustion; nervous glances; Michael wipes his brow and resets.", ""),
 ("PRESSURE", A.P_CLOCK, A.P_WINDOW, "V2 reuse", "The clock races toward 11 pm.", "AND THEIR FATHER / DEMANDED PERFECTION."),
 ("PRESSURE", A.P_WINDOW, A.P_CALL, "V2 reuse", "Michael at the window; other kids play outside.", ""),
 ("PRESSURE", A.P_CALL, A.P_WORK, "NEW", "Joe in the doorway points him back to rehearsal.", ""),
 ("PRESSURE", A.P_WORK, A.END, "V2 reuse", "Michael alone in the lamplight, practising again.", ""),
 ("RISE", B.R_APOLLO, B.R_INSIDE, "V2 reuse", "Harlem: the Apollo marquee.", "1967: AMATEUR NIGHT / AT THE APOLLO."),
 ("RISE", B.R_INSIDE, B.R_SING, "V2 reuse", "Inside the Apollo: the house on its feet.", "THEN FIVE BROTHERS / BECAME STARS."),
 ("RISE", B.R_SING, B.R_DJ, "V2 reuse", "Motown studio close-up: Michael sings.", ""),
 ("RISE", B.R_DJ, B.R_STORE, "V2 reuse", "A DJ drops the needle - ON AIR.", ""),
 ("RISE", B.R_STORE, B.R_CITY, "V2 reuse", "Record-store window fills with the singles.", "THEIR FIRST FOUR MOTOWN / SINGLES ALL HIT NO. 1."),
 ("RISE", B.R_CITY, B.R_TV, "V2 reuse", "Radio waves over the city.", ""),
 ("RISE", B.R_TV, B.M_LEAVE, "V2 reuse", "TV stage: the five in unison.", ""),
 ("OWN PATH", B.M_LEAVE, B.M_GROW, "NEW", "The brothers walk off into the wings; teenage Michael stays at the mic and looks across the dark stage at a single waiting spotlight.", "BUT MICHAEL WANTED / HIS OWN PATH."),
 ("OWN PATH", B.M_GROW, B.M_STUDIO, "NEW", "He walks through three pools of light and grows up as he goes: 1972 (teen, big afro) -> 1979 (tuxedo, white socks) -> 1982 (curls, sequined jacket, one glove).", ""),
 ("OWN PATH", B.M_STUDIO, B.M_STAGE79, "NEW", "Recording his own music: headphones, eyes closed, a producer listening behind the glass.", "AND SOON, THE WORLD / KNEW HIS NAME."),
 ("OWN PATH", B.M_STAGE79, B.S_RECORD, "NEW", "His own stage (late-70s look): spin, kick, a crowd there for him.", ""),
 ("SUPERSTAR", B.S_RECORD, B.S_SIL, "NEW", "A record turns (plain label: MICHAEL JACKSON - THRILLER - 1982; no album artwork).", "1982: THRILLER / CHANGED EVERYTHING."),
 ("SUPERSTAR", B.S_SIL, B.S_DANCE, "NEW", "Spotlights blast on: fedora-and-sequins silhouette, the single glove sparkling.", ""),
 ("SUPERSTAR", B.S_DANCE, B.S_CROWD, "NEW", "He glides backward across the stage, spins, rises onto his toes.", ""),
 ("SUPERSTAR", B.S_CROWD, B.S_TVWALL, "NEW", "A tiny figure in one spotlight above an enormous crowd and flashbulbs.", "HE WAS NOW A / GLOBAL SUPERSTAR."),
 ("SUPERSTAR", B.S_TVWALL, B.S_GLOVE, "NEW", "A wall of television sets, every screen showing his silhouette.", ""),
 ("SUPERSTAR", B.S_GLOVE, B.END, "NEW", "Close-up: the glove raised into the light.", ""),
 ("LAST TOUR", C.T_BACK, C.T_FOLLOW, "NEW", "1984 backstage corridor (road cases: THE JACKSONS / VICTORY TOUR 84). Michael alone in the foreground watches his five brothers walk toward the stage light; Joe, older and greying, watches the preparations.", "BUT IN 1984..."),
 ("LAST TOUR", C.T_FOLLOW, C.T_STADIUM, "NEW", "Behind Michael as he follows them into the light.", "HE RETURNED FOR / ONE MORE TOUR."),
 ("LAST TOUR", C.T_STADIUM, C.T_FINISH, "NEW", "Dodger Stadium: four tiers of fans, scalloped outfield roofs, light standards, palms and the hills; a Victory-scale stage with lighting towers and an arched truss; six Jacksons perform.", "LOS ANGELES / DECEMBER 9, 1984"),
 ("ANNOUNCEMENT", C.T_FINISH, C.T_SPEAK, "NEW", "The last song ends; the stadium roars; the camera drifts toward Michael at the microphone.", ""),
 ("ANNOUNCEMENT", C.T_SPEAK, C.T_REACT, "NEW", "Stillness (music -10 dB). He looks to his brothers, then out to the crowd, and speaks.", "THIS WILL BE OUR / LAST TOUR TOGETHER. (paraphrase)"),
 ("ANNOUNCEMENT", C.T_REACT, C.T_JOE, "NEW", "Restrained reactions: Jermaine looks down, Tito and Marlon nod slowly, Jackie's hand to his chest, Randy watches.", "(caption continues)"),
 ("ANNOUNCEMENT", C.T_JOE, C.T_EXIT, "NEW", "Joe at the side of the stage, watching - his face hard to read.", "(caption continues)"),
 ("DECISION", C.T_EXIT, C.T_SHOE, "NEW", "Music returns. Michael lowers the microphone, one last look at his brothers, and walks into the dark wing.", ""),
 ("DECISION", C.T_SHOE, C.T_CHILDSHOE, "NEW", "His black loafer and white sock step into the dark corridor...", "HE GREW UP / IN THE GROUP."),
 ("DECISION", C.T_CHILDSHOE, C.T_ROOM, "NEW", "...match cut: the same step, a child's shoe on the rehearsal-room boards.", "(caption continues)"),
 ("DECISION", C.T_ROOM, C.T_FINAL, "NEW (V2 set)", "The rehearsal room, empty; the practice lamp slowly dims.", "(caption continues)"),
 ("DECISION", C.T_FINAL, T.DURATION, "NEW", "Adult Michael alone beneath one brilliant spotlight - the answer to the frightened boy of the first shot. Music fades.", "BUT HIS FUTURE / WAS HIS OWN."),
]
L = ["# The Jackson 5 - Story V3: THE FINAL DECISION - storyboard", "",
     f"Film length {T.DURATION:.3f} s, 1080x1920, 60 fps. Music: song {T.SONG_IN:.2f}-{T.SONG_CUT:.3f} s + {T.FADE:.2f} s fade "
     "(same analysed section; ~99.4 BPM). Every cut sits on a tracked downbeat or half bar.", "",
     "Spine: in the first shot a frightened boy is told to keep dancing; in the last, the grown man chooses when to walk away.", "",
     "| Time | Chapter | Source | Picture | Caption |", "|---|---|---|---|---|"]
for ch, a, b, src, pic, cap in rows:
    L.append(f"| {f(a)}-{f(b)} | {ch} | {src} | {pic} | {cap} |")
L += ["", "## Audio", "",
      "- Original recording, untouched except volume automation (no EQ/pitch/tempo change, no added voice).",
      f"- -12 dB from {A.H_FEET + 0.1:.2f} to {A.H_FLASH - 0.08:.2f} s (the shadow, Joe's gesture); the full band hits on the flash-forward.",
      f"- -10 dB from {C.T_SPEAK - 0.35:.2f} to {C.T_EXIT - 0.1:.2f} s (the announcement); the music swells back as he lowers the microphone.",
      f"- {T.FADE:.2f} s fade on the final spotlight.", "",
      "## Historical basis", "",
      "- Gary, Indiana; long rehearsals managed by their father Joe Jackson. Michael Jackson later spoke publicly about fearing his father; the film only implies this.",
      "- 1967 Apollo Amateur Night win; Motown 1968-69; the group's first four Motown singles (I Want You Back, ABC, The Love You Save, I'll Be There) all reached No. 1 on the Billboard Hot 100.",
      "- Michael released solo records while still in the group from 1971-72; Off the Wall (1979); Thriller (1982). The film never presents 1984 as the start of his solo career.",
      "- 1984: the brothers toured as The Jacksons (Victory Tour) with six brothers including Randy. The tour ended on December 9, 1984 at Dodger Stadium, Los Angeles, where Michael told the crowd it was their last show together.",
      "- The caption THIS WILL BE OUR LAST TOUR TOGETHER is a paraphrase, not a verbatim quote. No archival audio or speech is recreated. It was the end of that tour, not the last time the brothers ever performed together.",
      "- Costumes and staging are stylised impressions (sequined military-style jacket, single glove, white socks; a large lighting rig), not recreations of specific archival footage.",
      "- Dramatised moments (the stopped shoes, the clock, the window, the backstage walk, the brothers' and Joe's reactions) are visual storytelling, not documented incidents."]
Path(__file__).resolve().parents[1].joinpath('output', 'JACKSON5_V3_STORYBOARD.md').write_text('\n'.join(L) + '\n')
print('ok')
