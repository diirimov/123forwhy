import main as M, film as F
from film import T
def tc(s): return f"{int(s//60)}:{s%60:06.3f}"
def fr(s): return int(round(s*60))
L=["# 3 DARK CHRISTMAS LEGENDS — Final Synchronization Timeline","",
"**Video:** CHRISTMAS_LEGENDS_FINAL_90S.mp4 · 1080×1920 · 60 fps · 5,400 frames · 90.000 s  ",
"**Audio:** approved FINAL_CHRISTMAS_DANCE_MASTER (unchanged arrangement, tempo and pitch) + opening narration 0:00.120–0:03.696 (music dipped 6 dB under the voice only; bit-identical to the master from 0:04.6 to the end)  ",
"**Grid:** 128 BPM · beat 0.46875 s = 28.125 frames · bar 1.875 s = 112.5 frames · all visual events are computed from the same bar/step grid as the soundtrack (off-beat 16ths carry the soundtrack's 8.2 ms swing).","",
"## 1. Shot list","","| # | Shot | Start | End | Start frame | Bars |","|---|---|---|---|---|---|"]
for i,(a,b,fn,name) in enumerate(M.SHOTS):
    b=min(b,90.0); L.append(f"| {i+1} | {name} | {tc(a)} | {tc(b)} | {fr(a)} | {a/1.875+1:.1f}–{b/1.875+1:.1f} |")
L+=["","## 2. Transitions","","| Time | Frame | Transition |","|---|---|---|",
f"| {tc(T(5))} | {fr(T(5))} | White flash + snow burst on the drop into Act 1 |",
f"| {tc(T(9))} | {fr(T(9))} | Flash + camera punch: Krampus reveal |",
*[f"| {tc(w)} | {fr(w)} | Whip pan (±0.13 s) |" for w in M.WHIPS],
f"| {tc(T(17)-0.55)}–{tc(T(17)+0.55)} | {fr(T(17))} | Swirling-snow white-out into Iceland |",
f"| {tc(T(28,13))}–{tc(T(29,3))} | {fr(T(29))} | Yule Cat's giant tail sweeps across the frame into Wales |",
f"| 1:14.000–{tc(T(41)+0.3)} | {fr(T(41))} | Spinning wreath portal (finale visible through the hole during the 0.47 s musical silence), wreath flies past the camera on the mega drop |",
"","## 3. Captions","","| In | Out | Text |","|---|---|---|"]
for (a,b,lines,y,sz) in M.CAPS:
    L.append(f"| {tc(a)} | {tc(min(b,90))} | {' / '.join(l.replace('*','').replace('+','').replace('^','') for l in lines)} |")
for (a,b,title,sub) in M.TITLES: L.append(f"| {tc(a)} | {tc(b)} | Title card: **{title}** — {sub} |")
for (a,b,txt,y,sz) in M.SMALL: L.append(f"| {tc(a)} | {tc(b)} | Small tag: {txt} |")
ev=[(0.0,'Beat 1: kick + crash, village fly-through starts, lights pulse on every kick'),
(0.14,'Narration begins; caption words pop with the voice'),
(T(3),'Saint Nicholas hands a present on every beat (kids hop)'),
(T(4),'Lights dim — KRAMPUS horns rise (silhouette, glowing eyes)'),(T(4,4),"YULE CAT's glowing eyes open"),(T(4,8),"MARI LWYD's skull rises, jaw snaps"),
(T(4,12),'Kick drops out — Nicholas looks back, sweating'),(T(5),'DROP: flash, snow burst, title 1. KRAMPUS'),
(T(5,4),'Present #1 (child hops)'),(T(5,12),'Present #2'),(T(6,4),'Present #3'),(T(6,12),'Brass growl: naughty boy peeks from behind snowman'),
(T(7),'Wind-up'),(T(7,4),'Snowball thrown (clap)'),(T(7,8),'Window shatters (shards + snow burst)'),(T(7,12),'Smug pose'),
(T(8),'Krampus shadow starts creeping up behind the boy'),(T(8,12),'Brass DUN-DUN: shadow eyes ignite, lights flicker'),
(T(9),'KRAMPUS REVEAL: rises into frame, flash, shake'),(T(9,4),'Stomp'),(T(9,10),'Stomp'),(T(9,12),'Stomp'),
(T(10,0),'Brass stab pose 1'),(T(10,3),'Brass stab pose 2 (tongue)'),(T(10,6),'Brass stab pose 3'),(T(10,12),'Stomp'),
(T(11),'Whip pan — boy slowly turns (eyes shift)'),(T(12),'Terror scream (brass stab 1), speed lines'),(T(12,3),'Hair stands up'),(T(12,6),'Hair fully up'),(T(12,9),'Boy runs'),
(T(13),'Whip pan into chase — footfalls 2 per beat, Krampus stomps on every kick'),(T(13,4),'Boy slides on ice'),(T(13,12),'Jumps the fence'),
(T(14),'Krampus smashes through the snowman'),(T(14,4),'Door 1 slams'),(T(14,8),'Door 2 slams'),(T(14,12),'Door 3 slams'),(T(15),'Door 4 slams'),
(T(15),'Good-boy montage: halo pose'),(T(15,4),'Repairs window (sparkles)'),(T(15,8),'Sweeps the street'),(T(15,12),'Carries basket for elderly lady'),
(T(16),'Krampus leans in, raises one eyebrow'),(T(16,4),'Nod'),(T(16,8),'Nod + grin (approval)'),(T(16,12),'Nod'),
(T(17),'Snow swirl → Iceland, aurora; title 2. THE YULE CAT'),(T(18),'Push into window → cosy interior'),(T(18,4),'Sweater unwrapped'),(T(18,8),'Clothes unwrapped'),(T(18,12),'Sweater unwrapped'),
(T(19),'Jón lifts the lid'),(T(19,4),'Peeks in'),(T(19,8),'Flips box — only a moth flies out'),(T(20),'Shrug'),(T(20,4),'Walks out'),(T(20,12),'Cat glide: glowing eyes open in the window'),
(T(21),'YULE CAT REVEAL: eyes open over the rooftops, camera tilts up'),(T(21,4),'Ear twitch'),(T(21,12),'Ear twitch'),(T(22),'Pupils dilate'),
(T(23),'Extreme close-up: eyes narrow'),(T(23,4),'Jón looks down at his patched sweater'),(T(23,8),'Realisation — eyes wide, sweat'),(T(24),'Runs'),(T(24,12),'Cat glide: cat licks its lips'),
*[(t_,f'Clothing item {i+1}: '+['sweater','another sweater','scarf','hat','more scarves','scarves + thick socks','oversized coat','giant clothes-ball'][i]) for i,t_ in enumerate(F.ITEM_T)],
(T(27),'Cat head lowers to sniff'),(T(27,4),'Sniffing on 16ths'),(T(27,12),'Confused "?"'),(T(28),'Loses interest, leaves'),(T(28,10),'BAND STOPS: clothes-ball topples into the snow'),
(T(29),'Tail wipe → Welsh cottage; title 3. MARI LWYD'),(T(29,8),'Sip'),(T(30,8),'Sip'),
(T(31,4),'KNOCK 1 (door rattles, impact ring)'),(T(31,12),'KNOCK 2'),(T(32,4),'KNOCK 3, he stands'),(T(32,8),'Footstep'),(T(32,12),'Footstep'),
(T(33),'DOOR OPENS: MARI LWYD REVEAL (jaw snaps on the fiddle melody)'),(T(35),'Rhyme contest: Mari verse (notes fly)'),(T(35,8),'Homeowner answers'),(T(36),'Mari verse'),(T(36,8),'Homeowner answers'),
(T(37),'Back-and-forth every beat, camera alternates sides'),(T(38),'Back-and-forth every 8th note'),(T(39),'Homeowner gives in'),(T(39,8),'Everyone dances round the fire'),
(T(40,12),'Musical silence: wreath portal fills the frame'),(T(41),'MEGA DROP: wreath flies past, square revealed, key change'),(T(41,4),'Krampus slides in (snow burst)'),(T(41,8),'Mari Lwyd rises in'),(T(41,12),'Yule Cat pops up behind the roofs'),
(T(42),'Group pose'),(T(43),'Dance: alternate wide / medium framing each bar'),(T(44,12),'Cat glide: cat mee-ow pose'),(T(45),'Payoff: fireworks, falling ornaments, presents bouncing on kicks'),
(T(46,12),'Bell toll'),(T(47),'All three turn to camera; final caption'),(T(48,0),'Stop-time hit 1'),(T(48,3),'Stop-time hit 2'),(T(48,6),'Stop-time hit 3'),(T(48,12),'FINAL HIT: flash, shake, poses'),(90.0,'End')]
L+=["","## 4. Beat-synchronized events","","| Time | Frame | Bar.step | Event |","|---|---|---|---|"]
for (t_,e) in ev:
    b=int(t_/1.875)+1; st=round((t_-(b-1)*1.875)/(1.875/16),1)
    L.append(f"| {tc(t_)} | {fr(t_)} | {b}.{st:g} | {e} |")
open('CHRISTMAS_LEGENDS_SYNC_TIMELINE.md','w').write('\n'.join(L)+'\n'); print(len(L))
