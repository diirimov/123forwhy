import sys, numpy as np, soundfile as sf, librosa, scipy.signal as ss
y,sr=sf.read(sys.argv[1]); 
print('shape',y.shape,'sr',sr,'dur',len(y)/sr)
m=y.mean(1); 
print('peak dBFS',20*np.log10(np.abs(y).max()+1e-12))
rms=np.sqrt((m**2).mean()); print('RMS dBFS',20*np.log10(rms))
# true-ish LUFS via pyloudnorm-free approx: K-weight skip; give crest
L,R=y[:,0],y[:,1]; print('stereo corr',np.corrcoef(L,R)[0,1], 'side/mid dB',20*np.log10(np.std(L-R)/np.std(L+R)))
y22=librosa.resample(m,orig_sr=sr,target_sr=22050)
tempo,beats=librosa.beat.beat_track(y=y22,sr=22050); print('tempo',tempo, 'first beats',librosa.frames_to_time(beats[:4],sr=22050))
# band energies
f,P=ss.welch(m,sr,nperseg=8192)
bands=[(20,60),(60,120),(120,250),(250,500),(500,2000),(2000,6000),(6000,12000),(12000,20000)]
tot=P.sum()
for a,b in bands: print(f'band {a}-{b}: {10*np.log10(P[(f>=a)&(f<b)].sum()/tot):.1f} dB')
# key
ch=librosa.feature.chroma_cqt(y=y22,sr=22050).mean(1); names='C C# D D# E F F# G G# A A# B'.split()
print('chroma',' '.join(f'{n}:{v:.2f}' for n,v in zip(names,ch)))
# per-bar rms (bar = 1.875s)
bar=60/128*4
for b in range(48):
    seg=m[int(b*bar*sr):int((b+1)*bar*sr)]
    lo=ss.sosfilt(ss.butter(4,120,'low',fs=sr,output='sos'),seg)
    print(f'bar{b+1:02d} rms {20*np.log10(np.sqrt((seg**2).mean())+1e-9):6.1f} low {20*np.log10(np.sqrt((lo**2).mean())+1e-9):6.1f}', end=' |' if b%4!=3 else '\n')
