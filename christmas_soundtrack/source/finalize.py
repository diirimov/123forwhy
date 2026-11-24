import os, struct, subprocess, pickle, json, numpy as np, soundfile as sf, scipy.signal as ss, pedalboard as pb
import render as R, compose as C
OUT='/home/user/123forwhy/christmas_soundtrack'; os.makedirs(OUT+'/stems',exist_ok=True)
SR=R.SR; N=R.N
master,_=sf.read('work/master.wav',dtype='float32')
mfile=f'{OUT}/FINAL_CHRISTMAS_DANCE_MASTER.wav'
sf.write(mfile,master,SR,subtype='PCM_24',format='WAV')
# ---- MP3 preview from the exact same master
subprocess.run(['ffmpeg','-y','-loglevel','error','-i',mfile,'-c:a','libmp3lame','-b:a','320k','-ar','48000',
                '-metadata','title=The Darkest Christmas Legends (Dance Anthem)','-metadata','bpm=128',f'{OUT}/FINAL_CHRISTMAS_DANCE_PREVIEW.mp3'],check=True)
# ---- markers
SECT={1:'INTRO HOOK',5:'KRAMPUS DROP',17:'YULE CAT',29:'MARI LWYD',37:'BUILD',41:'FINAL MEGA DROP'}
marks=[]
for b in range(1,49):
    marks.append((C.B(b),f'Bar {b:02d}'+(f' | {SECT[b]}' if b in SECT else ''), True))
for st,lab in C.MARK:
    if st%16==0 and any(m[0]==st for m in marks):
        continue
    marks.append((st,lab,False))
def samp(step, swing=True): return int(round(R.st2t(step, swing)*SR))
cues=sorted([(samp(s),l) for s,l,_ in marks])+[(N-1,'END 90.000s')]
cue=struct.pack('<I',len(cues))
for i,(p,l) in enumerate(cues,1): cue+=struct.pack('<II4sIII',i,p,b'data',0,0,p)
adtl=b'adtl'
for i,(p,l) in enumerate(cues,1):
    t=struct.pack('<I',i)+l.encode('ascii','replace')+b'\0'
    adtl+=b'labl'+struct.pack('<I',len(t))+t+(b'\0' if len(t)%2 else b'')
raw=open(mfile,'rb').read()
body=raw[12:]+b'cue '+struct.pack('<I',len(cue))+cue+b'LIST'+struct.pack('<I',len(adtl))+adtl
open(f'{OUT}/FINAL_CHRISTMAS_DANCE_MARKERS.wav','wb').write(b'RIFF'+struct.pack('<I',4+len(body))+b'WAVE'+body)
# ---- stems: group buses through the same energy curve + master EQ, same overall gain, no bus comp/limiter
G=pickle.load(open('work/groups.pkl','rb'))
ec=R.energy_curve()
eq=[pb.HighpassFilter(24), pb.PeakFilter(250,-1.0,0.8), pb.PeakFilter(2800,1.8,0.7), pb.HighShelfFilter(9500,1.5), pb.HighShelfFilter(15000,2.0)]
stems={k:R.fx((v*ec).astype(np.float32),eq)[:, :N] for k,v in G.items()}
tot=sum(stems.values())
# gain that matches the summed stems to the master in RMS
g=np.sqrt(np.mean(master**2))/np.sqrt(np.mean(tot**2))
pk=max(np.abs(s).max() for s in stems.values())*g
if pk>0.89: g*=0.89/pk
fade=int(0.30*SR); fc=(np.cos(np.linspace(0,np.pi/2,fade))**2).astype(np.float32)
for k,s in stems.items():
    s=s*g; s[:,-fade:]*=fc
    sf.write(f'{OUT}/stems/STEM_{k}.flac',s.T,SR,subtype='PCM_24')
json.dump({'stem_gain_vs_master_db':float(20*np.log10(g)),'cues':cues},open('work/final_meta.json','w'))
print('stem gain',20*np.log10(g),'max stem peak',pk)
