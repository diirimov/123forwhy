import sys,numpy as np, soundfile as sf, scipy.signal as ss, librosa
y,sr=sf.read(sys.argv[1]); m=y.mean(1)
def band(lo,hi):
    sos=ss.butter(4,[lo,hi],'band',fs=sr,output='sos') if lo>0 else ss.butter(4,hi,'low',fs=sr,output='sos')
    x=ss.sosfilt(sos,m); env=np.abs(ss.hilbert(x)) if False else np.sqrt(ss.sosfilt(ss.butter(2,40,'low',fs=sr,output='sos'),x**2).clip(0))
    return env
step=60/128/4
# fine tempo: autocorrelation of full-band onset
o=librosa.onset.onset_strength(y=librosa.resample(m,orig_sr=sr,target_sr=22050),sr=22050,hop_length=128)
fr=22050/128
best=None
for bpm in np.arange(125,131,0.01):
    per=60/bpm*fr; idx=(np.arange(int(len(o)/per))*per).astype(int)
    s=max(o[(idx+k)%len(o)].sum() for k in range(0,int(per),2))
    if best is None or s>best[0]: best=(s,bpm)
print('fine BPM',best[1])
names={'sub<80':(0,80),'kick/bass 80-200':(80,200),'snare/clap 1-4k':(1000,4000),'hats 7-14k':(7000,14000)}
for sec,bars in [('intro',range(0,8)),('drop1',range(8,16)),('drop2',range(24,32)),('final',range(40,47))]:
    print('==',sec)
    for n,(lo,hi) in names.items():
        e=band(lo,hi); prof=np.zeros(16)
        for b in bars:
            for s in range(16):
                t=(b*16+s)*step; i=int(t*sr); prof[s]+=e[i:i+int(step*sr*0.5)].max()-e[max(0,i-int(0.01*sr)):i+1].min()
        prof/=prof.max(); print(f'{n:18s}',' '.join(f'{int(v*9)}' for v in prof))
# bass pitch over 8 bars of drop1
sos=ss.butter(6,250,'low',fs=sr,output='sos'); b=ss.sosfilt(sos,m)[int(8*1.875*sr):int(12*1.875*sr)]
b=librosa.resample(b,orig_sr=sr,target_sr=8000)
f0,vf,_=librosa.pyin(b,fmin=30,fmax=250,sr=8000,frame_length=1024,hop_length=int(8000*step/2))
notes=[librosa.hz_to_note(f) if not np.isnan(f) else '.' for f in f0[::2]]
for i in range(0,len(notes),16): print(' '.join(f'{n:4s}' for n in notes[i:i+16]))
