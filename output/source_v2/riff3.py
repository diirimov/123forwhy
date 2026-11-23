import numpy as np, librosa, soundfile as sf, json
y,sr=sf.read('inst.wav'); y=y.mean(1)[:int(22*sr)]
D=librosa.stft(y,n_fft=4096,hop_length=256); Hh,Pp=librosa.decompose.hpss(D,margin=(1.0,3.0)); yh=librosa.istft(Hh,hop_length=256)
hop=128
C=np.abs(librosa.cqt(yh,sr=sr,hop_length=hop,fmin=librosa.note_to_hz('A4'),n_bins=30,bins_per_octave=12))
L=np.log1p(C*30); t=np.arange(C.shape[1])*hop/sr
B=np.array(json.load(open('beats_tracked.json'))); B=B[(B>-0.4)&(B<22)]
grid=[]
for i in range(len(B)-1): grid+=[B[i],(B[i]+B[i+1])/2]
rows=[]
for g in grid:
    a=(t>=g-0.015)&(t<g+0.06); b=(t>=g-0.08)&(t<g-0.02)
    if a.sum()==0 or b.sum()==0: continue
    inc=np.maximum(0,L[:,a].max(1)-L[:,b].mean(1)); lvl=L[:,a].max(1)
    k=int(np.argmax(inc*lvl)); rows.append((float(g), 69+k, float(inc.sum()), float(lvl.max())))
on=np.array([r[2] for r in rows]); thr=np.percentile(on,50)
s=''
for i,(g,n,tot,lv) in enumerate(rows):
    s+=f"{g:5.2f}:{librosa.midi_to_note(n,unicode=False) if tot>thr else '..':>4}({tot:4.1f}) "
    if i%8==7: s+='\n'
print(s); json.dump(rows,open('riff_h.json','w'))
