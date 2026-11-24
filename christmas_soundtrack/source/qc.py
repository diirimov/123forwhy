import numpy as np, soundfile as sf, librosa, render as R, compose as C, scipy.signal as ss
T=np.load('work/raw.npz')
SR=R.SR; STEP=R.STEP
def track_notes(x, bar0, nb):
    seg=x.mean(0)[int(R.st2t(C.B(bar0),False)*SR):int(R.st2t(C.B(bar0+nb),False)*SR)]
    seg=librosa.resample(seg,orig_sr=SR,target_sr=16000)
    f0,v,_=librosa.pyin(seg,fmin=180,fmax=2000,sr=16000,frame_length=2048,hop_length=int(16000*STEP/4))
    out=[]
    for st in range(nb*16):
        fr=f0[st*4+1:st*4+3]; fr=fr[~np.isnan(fr)]
        out.append(librosa.hz_to_note(np.median(fr)) if len(fr) else '.')
    return out
for name,bar,nb in (('fiddle',5,2),('glock',1,2),('pizz',17,1),('accordion',30,1)):
    got=track_notes(T[name],bar,nb)
    exp=['.']*(nb*16)
    for (s,d,p,v) in C.EV[name]:
        k=int(s)-C.B(bar)
        if 0<=k<nb*16: exp[k]=librosa.midi_to_note(p)
    print(name,'bar',bar); print(' exp:',' '.join(f'{e:4s}' for e in exp)); print(' got:',' '.join(f'{g:4s}' for g in got))
# kick timing check vs grid on the master
m,_=sf.read('work/master.wav'); mono=m.mean(1)
lo=ss.sosfilt(ss.butter(4,100,'low',fs=SR,output='sos'),mono)
on=librosa.onset.onset_detect(y=librosa.resample(lo,orig_sr=SR,target_sr=22050),sr=22050,units='time',hop_length=64,backtrack=True)
grid=np.arange(0,90,STEP*4)
d=[ (o-grid[np.argmin(abs(grid-o))])*1000 for o in on]
print('low onsets',len(on),'median offset ms',np.median(d),'p95 abs ms',np.percentile(np.abs(d),95))
