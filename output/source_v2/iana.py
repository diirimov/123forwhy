import numpy as np, librosa, soundfile as sf, json
y,sr=sf.read('inst.wav'); y=y.mean(1)
H,P=librosa.decompose.hpss(librosa.stft(y,n_fft=2048,hop_length=256),margin=2.0)
yh=librosa.istft(H,hop_length=256); yp=librosa.istft(P,hop_length=256)
f=librosa.fft_frequencies(sr=sr,n_fft=2048)
# percussive: snare = broadband 1.5-6k + 150-300 body ; kick = <120
Sp=np.abs(librosa.stft(yp,n_fft=1024,hop_length=256)); fp=librosa.fft_frequencies(sr=sr,n_fft=1024)
tt=np.arange(Sp.shape[1])*256/sr
def flux(S,lo,hi):
    b=S[(fp>=lo)&(fp<hi)]; d=np.maximum(0,np.diff(np.log1p(b*50),axis=1)).sum(0); return np.concatenate([[0],d])
sn=flux(Sp,1500,7000); kk=flux(Sp,30,120)
def peaks(x,thr,mind=0.12):
    x=x/np.percentile(x,99); idx=librosa.util.peak_pick(x,pre_max=3,post_max=3,pre_avg=8,post_avg=8,delta=thr,wait=int(mind*sr/256)); return tt[idx], x[idx]
snt,sna=peaks(sn,0.25); kt,ka=peaks(kk,0.25)
# harmonic synth onsets in 600-4000Hz
Sh=np.abs(librosa.stft(yh,n_fft=1024,hop_length=256))
hf=flux(Sh,500,4000); ht,ha=peaks(hf,0.12,0.09)
json.dump({'snare':[(round(a,3),round(float(b),2)) for a,b in zip(snt,sna)],'kick':[(round(a,3),round(float(b),2)) for a,b in zip(kt,ka)],'synth':[(round(a,3),round(float(b),2)) for a,b in zip(ht,ha)]},open('inst_onsets.json','w'))
for name,(a,b) in {'snare':(snt,sna),'kick':(kt,ka)}.items():
    print(name, [round(x,2) for x,s in zip(a,b) if x<24 and s>0.35])
print('synth 0-20:',[round(x,2) for x in ht if x<20.5])
